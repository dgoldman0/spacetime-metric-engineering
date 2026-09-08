#!/usr/bin/env python3
"""Check the residual lapse shoulder at ell=0 after the local receiver repair."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import json
import multiprocessing
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.receiver_regularity import repaired_receiver_scalars
from adm_harness.source_ledger import SourceParams, sha256_file

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "supporting_reports/data/le_receiver_c2_repair"


def point(task):
    parameters, sigma, level, holding, shoulder_off = task
    params = SourceParams(**parameters)
    if shoulder_off:
        params = replace(params, eta_N=0.)
    h = .0025/2**level
    result = evaluate_demand(sigma, 0., params, h, h, holding=holding, scalar_evaluator=repaired_receiver_scalars)
    result.update({"level": level, "shoulder_off": shoulder_off})
    return {key: value for key, value in result.items() if not isinstance(value, np.ndarray)}


if __name__ == "__main__":
    reference = ROOT / "supporting_reports/data/le_geometry_boundary/manifest.json"
    manifest = json.loads(reference.read_text())
    params = manifest["params"]
    tasks = [(params, manifest["phases"][phase], level, holding, off)
             for phase in ["held_carry", "reset_decompression"] for level in range(8)
             for holding in [False, True] for off in [False, True]]
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context("spawn")) as pool:
        frame = pd.DataFrame(pool.map(point, tasks, chunksize=8))
    if not frame.full_eigensystem_certified.all():
        raise ArithmeticError("throat eigensystem failed certification")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT / "throat_regularity.csv", index=False)
    (OUTPUT / "throat_manifest.json").write_text(json.dumps({
        "points": len(frame), "reference_manifest_sha256": sha256_file(reference),
        "control": "eta_N=0 removes the lapse shoulder; all other candidate parameters retained",
        "software_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in [Path(__file__).resolve(),
            ROOT / "toolkit/adm_harness_cli/adm_harness/receiver_regularity.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/geometry_boundary.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/source_ledger.py"]},
    }, indent=2)+"\n")
    print(frame[(frame.level == 7) & frame.holding][["s", "h_l", "shoulder_off", "rho", "p_omega"]].to_string(index=False))
