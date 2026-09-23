#!/usr/bin/env python3
"""Probe axial tube walls with exact radial jets; emit data only.

Each probe holds z-independent fields log alpha = a(sigma) chi_a(r),
log A = b(sigma) chi_b(r) and beta = c(sigma) chi_s(r), where every chi is the
flattened minimum-jerk wall blend with its own start radius and width, and the
sigma dependence is linear at the evaluation instant. Translation probes move
one common profile in r at a fixed coordinate speed instead. The orthonormal
tensor comes from the generated axial Einstein kernel, and 8000 radii resolve
thin Type IV bands. Narrative interpretation is maintained manually in
supporting_reports.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adm_harness import axial_einstein_generated as generated
from adm_harness import axial_track as ax
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
LOG_ALPHA, LOG_A = math.log(858.), math.log(800.)
CORE = (1.75, 2.)
ENVELOPE = (1.75, 4.)


def blend(r, wall):
    return ax.wall_blend(r, ax.AxialTrackDesign(core_radius=wall[0], wall_width=wall[1]))


def tensor(r, jet):
    fields = {key: np.broadcast_to(np.asarray(value, dtype=float), r.shape) for key, value in jet.items()}
    fields.update(C=r, C_r=np.ones_like(r), C_rr=np.zeros_like(r))
    out = np.zeros((len(r), 4, 4))
    for (i, k), function in {(0, 0): generated.wall_nn, (0, 1): generated.wall_nz, (1, 1): generated.wall_zz,
                             (0, 2): generated.wall_nr, (1, 2): generated.wall_zr}.items():
        out[:, i, k] = function(fields)
    out[:, 2, 2] = generated.product_rr(fields)+generated.wall_rr(fields)
    out[:, 3, 3] = generated.product_rr(fields)+generated.wall_pp(fields)
    out[:, 1, 0], out[:, 2, 0], out[:, 2, 1] = out[:, 0, 1], out[:, 0, 2], out[:, 1, 2]
    return out/ax.EIGHT_PI


def staged_jet(r, a0=0., b0=0., c0=0., a_rate=0., b_rate=0., c_rate=0., lapse=CORE, stretch=CORE, shift=CORE):
    """Jets of exp(a chi_a), exp(b chi_b) and c chi_s with a = a0 + a_rate sigma etc., at sigma = 0."""
    jet = {}
    for name, amplitude, rate, wall in (("alpha", a0, a_rate, lapse), ("A", b0, b_rate, stretch)):
        chi, d1, d2 = blend(r, wall)
        value = np.exp(amplitude*chi)
        jet[name] = value
        jet[f"{name}_r"] = value*amplitude*d1
        jet[f"{name}_rr"] = value*(amplitude*d2+(amplitude*d1)**2)
        jet[f"{name}_s"] = value*rate*chi
        jet[f"{name}_ss"] = value*(rate*chi)**2
        jet[f"{name}_sr"] = value*rate*d1*(1+amplitude*chi)
        for key in ("z", "sz", "zz", "zr"):
            jet[f"{name}_{key}"] = 0.
    chi, d1, d2 = blend(r, shift)
    jet.update(beta=c0*chi, beta_r=c0*d1, beta_rr=c0*d2, beta_s=c_rate*chi, beta_sr=c_rate*d1)
    for key in ("z", "ss", "sz", "zz", "zr"):
        jet[f"beta_{key}"] = 0.
    return jet


def translating_jet(r, speed, wall=(4., 2.)):
    """Jets of exp(A0 chi(r + speed sigma)) for both alpha and A at sigma = 0, with zero shift."""
    chi, d1, d2 = blend(r, wall)
    jet = {}
    for name, amplitude in (("alpha", LOG_ALPHA), ("A", LOG_A)):
        value = np.exp(amplitude*chi)
        f_r, f_rr = amplitude*d1, amplitude*d2
        f_s, f_ss, f_sr = speed*f_r, speed*speed*f_rr, speed*f_rr
        jet[name] = value
        jet[f"{name}_r"], jet[f"{name}_rr"] = value*f_r, value*(f_rr+f_r*f_r)
        jet[f"{name}_s"], jet[f"{name}_ss"], jet[f"{name}_sr"] = value*f_s, value*(f_ss+f_s*f_s), value*(f_sr+f_s*f_r)
        for key in ("z", "sz", "zz", "zr"):
            jet[f"{name}_{key}"] = 0.
    for key in ("", "_s", "_z", "_r", "_ss", "_sz", "_sr", "_zz", "_zr", "_rr"):
        jet[f"beta{key}"] = 0.
    return jet


def record(family, label, r, jet, **parameters):
    t = tensor(r, jet)
    kinds = ax.classify(t, floor=1e-12)
    iv = kinds["type"] == ax.TYPE_IV
    plus, minus = (t[:, 0, 0]+sign*2*t[:, 0, 2]+t[:, 2, 2] for sign in (1, -1))
    radial = t[:, 0, 0]+t[:, 2, 2]
    crossings = np.flatnonzero(np.sign(radial[:-1])*np.sign(radial[1:]) < 0)
    widths = []
    for i in crossings:
        weight = radial[i]/(radial[i]-radial[i+1])
        flux = t[i, 0, 2]+weight*(t[i+1, 0, 2]-t[i, 0, 2])
        slope = (radial[i+1]-radial[i])/(r[i+1]-r[i])
        widths.append(2*abs(flux)/abs(slope))
    return {"family": family, "probe": label, **parameters, "radii": len(r),
            "nonvacuum": int((kinds["type"] != ax.VACUUM).sum()), "type_iv": int(iv.sum()),
            "type_iv_inner": float(r[iv].min()) if iv.any() else math.nan,
            "type_iv_outer": float(r[iv].max()) if iv.any() else math.nan,
            "opposite_radial_null": int(((plus < 0) != (minus < 0)).sum()),
            "radial_null_sum_crossings": len(crossings),
            "estimated_radial_band_width": float(max(widths)) if widths else 0.,
            "min_null": float(ax.min_null_energy(t).min()), "max_abs_flux_nr": float(np.max(np.abs(t[:, 0, 2]))),
            "max_abs_flux_nz": float(np.max(np.abs(t[:, 0, 1])))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/axial_wall_probes")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []
    band = np.linspace(4.0005, 5.9995, 8000)
    for rate in (.01, .05, .3, 1.):
        rows.append(record("band_width", "amplitude decay", band,
                           staged_jet(band, LOG_ALPHA, LOG_A, a_rate=-rate*LOG_ALPHA, b_rate=-rate*LOG_A,
                                      lapse=(4., 2.), stretch=(4., 2.)), rate=rate))
    for speed in (.01, .05, .3, .9, 1., 1.5):
        rows.append(record("band_width", "translation", band, translating_jet(band, speed), rate=speed))
    core = np.linspace(1.7505, 3.7495, 8000)
    rows += [
        record("attribution", "shift only, static", core, staged_jet(core, c0=.6)),
        record("attribution", "shift only, moving", core, staged_jet(core, c0=.6, c_rate=1.)),
        record("attribution", "lapse only, time dependent", core, staged_jet(core, a0=6.4, a_rate=-2.)),
        record("attribution", "stretch only, static", core, staged_jet(core, b0=6.7)),
        record("attribution", "stretch only, decaying", core, staged_jet(core, b0=6.7, b_rate=-2.)),
        record("attribution", "lapse and stretch, static", core, staged_jet(core, a0=6.4, b0=6.7)),
        record("attribution", "all three co-located, static", core, staged_jet(core, a0=6.4, b0=6.7, c0=.6)),
    ]
    wide = np.linspace(1.7505, 9.9995, 8000)
    staged = {
        "shift and lapse co-located": dict(a0=6.4, c0=.6),
        "shift inside lapse envelope": dict(a0=6.4, c0=.6, lapse=ENVELOPE, shift=(2.75, 1.)),
        "shift inside lapse envelope, beta 1.6, moving": dict(a0=6.4, c0=1.6, c_rate=1.5, lapse=ENVELOPE,
                                                             shift=(2.75, 1.)),
        "stretch co-located with shift inside envelope": dict(a0=6.4, b0=6.7, c0=.6, lapse=ENVELOPE,
                                                              stretch=(2.25, 1.5), shift=(2.75, 1.)),
        "shift before stretch inside envelope": dict(a0=6.4, b0=6.7, c0=.6, lapse=ENVELOPE, stretch=(3.5, 1.5),
                                                     shift=(2., .8)),
        "stretch before shift inside envelope": dict(a0=6.4, b0=6.7, c0=.6, lapse=ENVELOPE, stretch=(1.75, 1.),
                                                     shift=(3., 1.)),
        "stretch before shift, beta 1.6, moving": dict(a0=6.4, b0=6.7, c0=1.6, c_rate=1.5, lapse=ENVELOPE,
                                                       stretch=(1.75, 1.), shift=(3., 1.)),
        "stretch before shift, stretch decaying 0.3": dict(a0=6.4, b0=6.7, c0=.6, b_rate=-.3, lapse=ENVELOPE,
                                                           stretch=(1.75, 1.), shift=(3., 1.)),
        "stretch before shift, stretch and lapse decaying 0.3": dict(a0=6.4, b0=6.7, c0=.6, a_rate=-.3,
                                                                     b_rate=-.3, lapse=ENVELOPE, stretch=(1.75, 1.),
                                                                     shift=(3., 1.)),
        "stretch before shift, weak lapse 2": dict(a0=2., b0=2.2, c0=.6, lapse=ENVELOPE, stretch=(1.75, 1.),
                                                   shift=(3., 1.)),
        "stretch before shift, weak lapse 4": dict(a0=4., b0=4.2, c0=.6, lapse=ENVELOPE, stretch=(1.75, 1.),
                                                   shift=(3., 1.)),
    }
    for label, parameters in staged.items():
        rows.append(record("staged", label, wide, staged_jet(wide, **parameters),
                           **{key: (json.dumps(value) if isinstance(value, tuple) else value)
                              for key, value in parameters.items()}))
    table = pd.DataFrame(rows)
    table.to_csv(args.output/"probes.csv", index=False)
    manifest = {"completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "log_alpha_core": LOG_ALPHA, "log_a_core": LOG_A, "default_wall": CORE, "lapse_envelope": ENVELOPE,
                "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
                    "adm_harness/axial_track.py", "adm_harness/axial_einstein_generated.py",
                    "scripts/run_axial_wall_probes.py")}}
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1)+"\n")
    pd.set_option("display.width", 250)
    print(table[["family", "probe", "rate", "nonvacuum", "type_iv", "type_iv_inner", "type_iv_outer",
                 "opposite_radial_null", "radial_null_sum_crossings", "estimated_radial_band_width",
                 "min_null"]].to_string())


if __name__ == "__main__":
    main()
