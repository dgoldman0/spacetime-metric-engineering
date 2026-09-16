#!/usr/bin/env python3
"""Parallel comparison of internal fields and two-boundary magnetic jackets."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil
import subprocess
import sys
import time

import numpy as np

from adm_harness.magnetic_geometry import (
    jacket_requirements, jacket_currents, straight_sheet_fraction,
    radial_sleeve_projection, radial_sleeve_interval, radial_sleeve_threshold,
)
from adm_harness.magnetic_load_balance import (
    loop_field, loop_currents, attached_bank, sleeve_at_inventory, support_cone, loop_work,
)
from adm_harness.source_ledger import sha256_file
from evaluate_magnetic_load_balance import limits, witness
from run_poynting_delivery import ROOT, BASE, write_json

ASPECT, FILL, TUBE_RATIO = .01, .1, .1
RADII = (1.01, 1.05, 1.1, 1.25, 1.5, 2.)
INTERNAL = (0., .0025, .01, .04, .1, .25, .5, 1.)


def geometries():
    yield "original", 1., 0., 1.
    yield "zero_field_wall_control", 0., 0., 1.
    for e in (.5, 1., 1.5):
        yield "partial_external", 1., e, 1.1
    for eta in RADII:
        for b in INTERNAL:
            yield "balanced_jacket", b, 1+b, eta


def tensor_work(tensor, state):
    pressure = tensor[1:]*state["D"]
    return (-.5*(pressure[0, 1:]+pressure[0, :-1])*np.diff(np.log(state["ell"]), axis=0)
            -(pressure[1, 1:]+pressure[1, :-1])*np.diff(np.log(state["radius"]), axis=0))


def evaluate(spec):
    parent, path, output, chi, order = spec
    started = time.monotonic()
    meta = json.loads(path.read_text())
    with np.load(parent/(meta["label"]+"_states.npz")) as archive:
        previous = {k: archive[k] for k in archive.files}
    with np.load(ROOT/meta["input"]) as archive:
        state = {k: archive[k] for k in archive.files}
    E, D = previous["evolved_cold_energy"], state["D"]
    lr, lt = state["ell"]/state["ell"][0], state["radius"]/state["radius"][0]
    if (np.any(lr > lt+1e-12) or not np.array_equal(previous["t"], state["t"])
            or not np.array_equal(previous["x"], state["x"])):
        raise ValueError("registered radial, compressed capsule histories required")
    reference_field = loop_field(E, lr, lt, aspect=ASPECT, angle=0.)
    cell_width = state["edges"][-1]-state["edges"][0]
    leg0 = .5*cell_width*state["ell"][0]/(1+2*ASPECT*(1+TUBE_RATIO))
    references = {}
    fractions = {}
    for n in (order, 2*order):
        references[n] = loop_currents(E, D, lr, lt, leg0, aspect=ASPECT, angle=0.,
            fill_fraction=FILL, tube_ratio=TUBE_RATIO, order=n)
        fractions[n] = straight_sheet_fraction(E, D, lr, lt, references[n],
                                               aspect=ASPECT, fill_fraction=FILL)
    reference = references[2*order]
    reconstruction = float(np.max(abs(
        reference["unit_tensor"]*meta["selected"]["tested_current_coefficient"]
        -previous["current_tensor"])))
    if reconstruction > 1e-10:
        raise ValueError("parent current tensor failed reconstruction")

    zero_field = dict(radial=np.zeros_like(D), transverse=np.zeros_like(D))
    zero_budget = attached_bank(state, E, zero_field)
    available = zero_budget["residual_target"][0]
    if np.any(available <= 0):
        raise ValueError("positive remaining density required for the raw material bound")
    unavoidable_hoop = 2*E/(3*D*(1+np.pi*ASPECT))
    absolute_bound = unavoidable_hoop/available
    rows, retained = [], dict(t=state["t"], x=state["x"], evolved_cold_energy=E)
    baseline_original_threshold = None
    for family, b, e, eta in geometries():
        if FILL*eta*eta > 1:
            raise ValueError("outer magnetic jacket overfills cell")
        requirements = jacket_requirements(E,D,aspect=ASPECT,inner_pressure=b,
                                            outer_pressure=e,radius_ratio=eta)
        g = requirements["field_energy_factor"]
        field = {key: reference_field[key]*g for key in ("radial","transverse","energy")}
        carriers = jacket_currents(reference,D,inner_pressure=b,outer_pressure=e,
            radius_ratio=eta,straight_fraction=fractions[2*order],aspect=ASPECT,tube_ratio=TUBE_RATIO)
        coarse = jacket_currents(references[order],D,inner_pressure=b,outer_pressure=e,
            radius_ratio=eta,straight_fraction=fractions[order],aspect=ASPECT,tube_ratio=TUBE_RATIO)
        unloaded = attached_bank(state,E,field)
        loaded = attached_bank(state,E,field,carrier_tensor=chi*carriers["unit_tensor"])
        magnetic_hoops = [requirements["inner_hoop"],requirements["outer_hoop"]]
        complete_hoops = [part+chi*carriers["families"][name]["unit_straight_hoop"]
                          for part,name in zip(magnetic_hoops,("inner_sheet","outer_sheet"))]
        H = sum(complete_hoops)
        zero_projection = radial_sleeve_projection(unloaded["facets"],D,sum(magnetic_hoops),
                                                   boundary_hoops=magnetic_hoops)
        projection = radial_sleeve_projection(loaded["facets"],D,H,boundary_hoops=complete_hoops)
        threshold = radial_sleeve_threshold(projection)
        if family == "original":
            old_projection=radial_sleeve_projection(loaded["facets"],D,sum(magnetic_hoops))
            baseline_original_threshold=radial_sleeve_threshold(old_projection)
        intervals = {str(k):radial_sleeve_interval(projection,k) for k in (.5,.1,.01,1e-10)}
        key=f"{family}_b{b:g}_e{e:g}_eta{eta:g}"
        row=dict(key=key,family=family,inner_pressure=b,outer_pressure=e,radius_ratio=eta,
            field_energy_factor=g,outer_volume_fraction=FILL*eta*eta,
            inner_interface_pressure_ratio=requirements["inner_pressure_ratio"],
            outer_interface_pressure_ratio=requirements["outer_pressure_ratio"],
            inner_interface_pressure_ratio_minimum=float(min(1+b-e,
                np.min(1+(b-e)*(lt/lr)**2))),
            inner_interface_pressure_ratio_maximum=float(max(1+b-e,
                np.max(1+(b-e)*(lt/lr)**2))),
            minimum_stress_fraction_zero_currents=radial_sleeve_threshold(zero_projection),
            minimum_stress_fraction_counted_currents=threshold,
            current_rest_inventory=limits(chi*carriers["unit_rest_inventory"]),
            current_sheet_factor=carriers["sheet_factor"],current_bend_factor=carriers["bend_factor"],
            maximum_field_energy=float(field["energy"].max()),
            maximum_magnetic_hoop_inventory=float((D*sum(magnetic_hoops)).max()),
            maximum_carrier_hoop_inventory=float((D*(H-sum(magnetic_hoops))).max()),
            current_tensor_relative_quadrature_difference=float(np.max(abs(
                coarse["unit_tensor"]-carriers["unit_tensor"]))/max(np.max(abs(carriers["unit_tensor"])),1e-300)),
            passing_labels_at_strength={k:int(v["feasible"].sum()) for k,v in intervals.items()},
            fixed_inventory_gaps_at_strength={k:v["minimum_gap"] for k,v in intervals.items()})

        # Keep concrete finite-gap witnesses, with separate wall inventories.
        keep=(b==0 and eta in (1.01,1.1)) or (b==.1 and eta==1.01)
        if family=="balanced_jacket" and keep and threshold is not None:
            k=.85 if threshold<=.85 else 1.
            interval=radial_sleeve_interval(projection,k)
            M=interval["lower"]+.05*(interval["upper"]-interval["lower"])
            sleeve=sleeve_at_inventory(loaded["facets"],D,H,np.ones_like(D),M,stress_fraction=k)
            peaks=np.max(np.asarray(complete_hoops)*D,axis=1)
            fractions_M=peaks/peaks.sum(axis=0)
            inventories=fractions_M*M
            complete=support_cone(*(loaded["residual_target"]-sleeve["tensor"]),
                                  loaded["radial_field_floor"])
            if complete["shortfall"].max()>1e-11:
                raise RuntimeError("retained jacket witness fails tensor budget")
            remaining=np.stack([complete["field"]+complete["radial_wave"]
                                +complete["angular_wave"]+complete["membrane"]+complete["spare"],
                                -complete["field"]+complete["radial_wave"],
                                complete["field"]+.5*complete["angular_wave"]-complete["membrane"]])
            error=float(np.max(abs(remaining+sleeve["tensor"]-loaded["residual_target"])))
            split_tensors=[]
            for i,hoop in enumerate(complete_hoops):
                split_tensors.append(np.stack([inventories[i]/D,
                    fractions_M[i]*sleeve["axial_stress"],-hoop/2]))
            if np.max(abs(sum(split_tensors)-sleeve["tensor"]))>1e-12:
                raise RuntimeError("separate boundary stresses failed reconstruction")
            margin=min(float((k*inventories[i]/D-part).min()) for i,part in enumerate(complete_hoops))
            if margin < -1e-12:
                raise RuntimeError("individual sleeve lacks hoop capacity")
            field_work=loop_work(state["t"],field["energy"],field["radial"],state["ell"],state["radius"])
            sleeve_work=tensor_work(sleeve["tensor"],state)
            carrier_tensor=chi*carriers["unit_tensor"]
            carrier_work=tensor_work(carrier_tensor,state)
            carrier_transfer=np.diff(D*carrier_tensor[0],axis=0)-carrier_work
            row["witness"]=dict(stress_fraction=k,total_sleeve_inventory=limits(M),
                inner_sleeve_inventory=limits(inventories[0]),outer_sleeve_inventory=limits(inventories[1]),
                minimum_individual_hoop_margin=margin,tensor_reconstruction_error=error,
                worst_density=witness(state,complete["shortfall"]),
                complete_loop_electrical_input=limits(np.maximum(field_work["electrical"],0).sum(axis=0)),
                complete_loop_electrical_output=limits(np.maximum(-field_work["electrical"],0).sum(axis=0)),
                current_carrier_control_input=limits(np.maximum(carrier_transfer,0).sum(axis=0)),
                current_carrier_control_output=limits(np.maximum(-carrier_transfer,0).sum(axis=0)),
                sleeve_control_input=limits(np.maximum(-sleeve_work,0).sum(axis=0)),
                sleeve_control_output=limits(np.maximum(sleeve_work,0).sum(axis=0)))
            prefix="shared_candidate" if b==.1 else ("thin" if eta==1.01 else "finite")
            retained.update({prefix+"_"+name:value for name,value in dict(
                loop_radial_field_energy=field["radial"],loop_transverse_field_energy=field["transverse"],
                carrier_tensor=carrier_tensor,inner_sleeve_tensor=split_tensors[0],
                outer_sleeve_tensor=split_tensors[1],inner_hoop=complete_hoops[0],outer_hoop=complete_hoops[1],
                sleeve_inventories=inventories,remaining_support_tensor=remaining,
                density_shortfall=complete["shortfall"],field_electrical_transfer=field_work["electrical"],
                carrier_control_transfer=carrier_transfer,sleeve_mechanical_work=sleeve_work).items()})
        rows.append(row)
    summary=dict(label=meta["label"],input=meta["input"],time_samples=len(state["t"]),
        spatial_samples=len(state["x"]),current_coefficient=chi,
        current_reference_reconstruction_error=reconstruction,
        original_threshold_without_carrier_hoop=baseline_original_threshold,
        archived_original_threshold=meta["selected"]["straight_sleeve_minimum_stress_fraction"]["counted_currents"],
        geometry=dict(aspect=ASPECT,radial_pitch=0.,core_fill_fraction=FILL,
                      inner_tube_to_bend_radius=TUBE_RATIO,whole_outer_span_fraction=.5),
        current_quadrature_orders=[order,2*order],
        absolute_pointwise_strength_lower_bound=witness(state,absolute_bound),cases=rows,
        scope=dict(full_closed_loop_field_energy=True,inner_outer_and_bend_currents=True,
            outer_reaction_hoop_counted=True,straight_current_carrier_hoop_counted=True,
            separate_boundary_inventories_conserved=True,cold_compression_retained=True,
            phase_field_overlap_granted=True,bend_mechanical_equilibrium_supplied=False,
            current_host_constitutive_law_supplied=False,induction_field_supplied=False,
            exterior_field_beyond_outer_sleeve_assumed_zero=True,
            mechanical_and_electrical_transfers_routed=False,
            field_exclusion_and_opacity_supplied=False,stability_supplied=False,
            full_material_storage_solution_supplied=False),elapsed_seconds=time.monotonic()-started)
    np.savez_compressed(output/(meta["label"]+"_states.npz"),**retained)
    write_json(output/(meta["label"]+"_summary.json"),summary)
    chosen=next(r for r in rows if r["family"]=="balanced_jacket" and r["inner_pressure"]==0 and r["radius_ratio"]==1.1)
    print(json.dumps(dict(label=meta["label"],finite_jacket_threshold=chosen["minimum_stress_fraction_counted_currents"],
        absolute_pointwise_lower_bound=summary["absolute_pointwise_strength_lower_bound"]["value"],
        elapsed_seconds=summary["elapsed_seconds"])),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent",default="magnetic_load_balance")
    parser.add_argument("--output-name",required=True)
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--current-order",type=int,default=32)
    args=parser.parse_args()
    if not 1<=args.workers<=6 or args.current_order<8:
        parser.error("one through six workers and current order >=8 required")
    parent,output=BASE/args.parent,BASE/args.output_name
    if output.exists():raise RuntimeError("preserve completed magnetic geometry comparison")
    manifest_path=parent/"manifest.json"
    manifest=json.loads(manifest_path.read_text())
    hashes=dict(manifest["input_sha256"])
    hashes.update({str((parent/name).relative_to(ROOT)):value for name,value in manifest["output_sha256"].items()})
    hashes[str(manifest_path.relative_to(ROOT))]=sha256_file(manifest_path)
    for name,want in hashes.items():
        if sha256_file(ROOT/name)!=want:raise RuntimeError("parent archive authentication failed: "+name)
    paths=sorted(parent.glob("*_summary.json"))
    finest={}
    for path in paths:
        meta=json.loads(path.read_text());loc=meta["label"].split("_")[0]
        if loc not in finest or meta["time_samples"]>finest[loc]["time_samples"]:finest[loc]=meta
    coefficients={loc:meta["selected"]["tested_current_coefficient"] for loc,meta in finest.items()}
    runtime=[Path(__file__),ROOT/"toolkit/adm_harness_cli/tests/test_magnetic_geometry.py"]
    for module in list(sys.modules.values()):
        filename=getattr(module,"__file__",None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix==".py" and path.is_relative_to(ROOT):runtime.append(path)
    hashes.update({str(path.relative_to(ROOT)):sha256_file(path) for path in runtime})
    output.mkdir()
    workers=min(args.workers,len(paths))
    specs=[(parent,path,output,coefficients[path.name.split("_")[0]],args.current_order) for path in paths]
    with ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context("spawn")) as pool:
        cases=list(pool.map(evaluate,specs))
    fine=[case for case in cases if case["spatial_samples"]==max(c["spatial_samples"] for c in cases)]
    candidates=[]
    for row in fine[0]["cases"]:
        if row["family"]!="balanced_jacket":continue
        matched=[next(r for r in case["cases"] if r["key"]==row["key"]) for case in fine]
        thresholds=[r["minimum_stress_fraction_counted_currents"] for r in matched]
        if all(k is not None for k in thresholds):
            candidates.append(dict(key=row["key"],maximum_required_stress_fraction=max(thresholds),
                                    thresholds=dict(zip([c["label"] for c in fine],thresholds))))
    candidates.sort(key=lambda r:r["maximum_required_stress_fraction"])
    write_json(output/"summary.json",dict(cases=cases,common_geometry_ranking=candidates,
        current_coefficient_by_location=coefficients))
    for name,want in hashes.items():
        if sha256_file(ROOT/name)!=want:raise RuntimeError("input changed during geometry comparison: "+name)
    snapshots={}
    for path in (Path(__file__),ROOT/"toolkit/adm_harness_cli/adm_harness/magnetic_geometry.py",
                 ROOT/"toolkit/adm_harness_cli/tests/test_magnetic_geometry.py"):
        name="execution_"+path.name;shutil.copyfile(path,output/name)
        snapshots[str(path.relative_to(ROOT))]=name
    write_json(output/"manifest.json",dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        workers=workers,parent_manifest=str(manifest_path.relative_to(ROOT)),input_sha256=hashes,
        source_snapshot=snapshots,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=="__main__":main()
