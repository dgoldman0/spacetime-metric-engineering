# Spacetime Metric Engineering Protocol: Source-Function Audit of the White et al. Casimir/Alcubierre-Shell Claim

## Codex task

Implement a reproducible simulation protocol that tests the White et al. Casimir-geometry design on its own architecture.

Do **not** model the White et al. device as an active rail. Do **not** import throat, handoff, reset, packet-corridor, branch, rail-scheduling, or beta-collar machinery.

Do apply the portable spacetime-engineering method developed during active-rail work: **source-function auditing**. A stress-energy pattern is evaluated as an engineered subsystem with roles, channels, controls, and observables. The purpose is to test whether White et al.'s Casimir geometry behaves like an Alcubierre-shell source candidate, or only like a shaped Casimir energy-density morphology.

No active-rail candidate manifest, service-rating table, packet-safety ledger, beta-collar provenance record, or operating-point result is an input to this White/Alcubierre-shell audit. The only imported item is the engineering habit of separating role, channel, source demand, controls, and observable scale.

## Target architecture

White et al. propose that custom Casimir geometries can produce negative vacuum-energy patterns that intersect with Alcubierre warp-metric source requirements.

The protocol tests two geometries from their paper:

1. **Parallel-plate cavity with pillar**
   - Approximate plate gap: `4 um`.
   - Approximate plate footprint: `40 um x 40 um`.
   - Approximate pillar diameter: `1 um`.
   - Purpose in the paper: test whether a pillar can sample or modify the negative-energy region rather than screening it away.

2. **Sphere-in-cylinder toy model**
   - Sphere diameter: `1 um`.
   - Cylinder diameter: `4 um`.
   - Sphere centered in cylinder.
   - Purpose in the paper: produce a toroidal negative Casimir energy-density section and compare it qualitatively with the negative-energy shell of an Alcubierre metric.

The paper also proposes a transit/readout test in which a current, photon, or electron path through an array is compared against a control path. This protocol treats that proposed observable as a separate channel, not as automatically implied by the Casimir energy-density morphology.

## Balance rule

Keep new engineering concepts when they describe a real function in the White/Alcubierre-shell design. Rename or constrain them when they sound like active-rail machinery. Remove them when they require active-rail-specific dynamics.

### Portable engineering concepts to keep

- **Source-function audit**: test what the stress pattern does, not merely what it resembles.
- **Role-locked sweeps**: vary geometry features according to assigned physical roles and check whether the intended channel responds.
- **Boundary infrastructure**: the plates and cylinder wall as Casimir boundary-condition surfaces.
- **Stress-shaping body**: the pillar or sphere as a body that shapes the Casimir distribution.
- **Source-shell candidate**: the negative-energy toroidal/shell-like region compared to Alcubierre.
- **Transit/readout channel**: the current, photon, or electron path used for the proposed measurement.
- **Ordinary EM competitor channel**: capacitance, impedance, dispersion, leakage, contact effects, patch potentials, surface roughness, and material response.
- **Alcubierre source channel**: energy density, momentum flux, pressure/stress channels, null projections, and any shift-source behavior required by the comparison target.

### Active-rail-specific concepts to avoid

Do not use the following unless a future section explicitly reframes the White et al. device as a different architecture:

- throat support;
- branch handoff;
- catch/rematch;
- reset cycle;
- rail scheduling;
- protected service corridor;
- packet-norm gate;
- beta-collar;
- support plant;
- transport rail.

If a collar-like stress concentration appears in the White geometry, call it an **edge-stress concentration** or **source-shell edge concentration**, not a beta-collar.

## Core audit question

The audit asks:

> Does the White et al. Casimir boundary geometry produce source-channel behavior that supports an Alcubierre-shell interpretation, or does it produce a visually suggestive negative-energy morphology without the tensor channels or observable scale required for a spacetime-transport claim?

The protocol must allow both outcomes. It must preserve evidence that supports the narrower Casimir-geometry claim, while preventing morphology-only evidence from being reported as a transport-relevant spacetime result.

## Implementation location

Create inside the intersection-work folder:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/
```

Use this structure:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/
  README.md
  configs/
    paper_plate_pillar.yaml
    paper_sphere_cylinder.yaml
    role_sweeps.yaml
    smoke.yaml
  white_casimir_audit/
    __init__.py
    constants.py
    geometry.py
    loop_gen.py
    worldline_scalar.py
    stress_tensor_proxy.py
    alcubierre_target.py
    linearized_metric.py
    em_proxy.py
    role_sweeps.py
    scoring.py
    report.py
  scripts/
    run_smoke.sh
    run_reproduction.sh
    run_role_sweeps.sh
  outputs/
    .gitkeep
  reports/
    .gitkeep
  tests/
    test_geometry.py
    test_loop_gen.py
    test_parallel_plate_scaling.py
    test_scoring.py
```

Use Python for the first version. Keep interfaces clean enough that a C++/MPI worldline kernel can replace the Python kernel later.

## Units and output categories

Geometry inputs are in micrometers. Observability estimates are in SI.

Internally store:

```python
length_um
length_m
energy_density_J_m3
stress_J_m3
metric_dimensionless
travel_time_s
```

Every result must state which output category it belongs to:

```text
normalized_morphology_proxy
scalar_dirichlet_energy_density
stress_tensor_proxy
source_demand_tensor
linearized_metric_estimate
ordinary_em_proxy
SI_estimate
```

Never mix categories in a plot, score, or report table without explicit conversion metadata.

## Stage 0: Claim manifest

Create `outputs/claim_manifest.json` with:

```json
{
  "paper": "White et al. 2021, EPJC, Worldline numerics applied to custom Casimir geometry generates unanticipated intersection with Alcubierre warp metric",
  "architecture_under_test": "Casimir boundary geometry plus Alcubierre-shell interpretation",
  "not_modeled_as": "active rail",
  "geometry_plate_pillar": {
    "plate_gap_um": 4.0,
    "plate_width_um": 40.0,
    "plate_height_um": 40.0,
    "pillar_diameter_um": 1.0
  },
  "geometry_sphere_cylinder": {
    "sphere_diameter_um": 1.0,
    "cylinder_diameter_um": 4.0,
    "sphere_position": "centered"
  },
  "reported_worldline_setup": {
    "sphere_cylinder_grid": "100 x 100",
    "unit_loop_ensemble": 2000,
    "cpu_count_reported": 660
  },
  "claimed_observable": "transit-time difference through current/photon/electron path routed through center of sphere-cylinder array",
  "audit_goal": "distinguish Alcubierre-shell source relevance from visual Casimir morphology and ordinary EM propagation effects"
}
```

## Stage 1: Geometry engine

Implement signed-distance or occupancy geometry functions in `geometry.py`.

Required geometries:

```python
ParallelPlates(gap_um, width_um, height_um, thickness_um=None)
PillarMidplaneCavity(gap_um, plate_width_um, plate_height_um, pillar_diameter_um, pillar_axis="z")
SphereInCylinder(sphere_diameter_um, cylinder_diameter_um, cylinder_length_um, bore_radius_um=0.0)
SphereOnlyControl(sphere_diameter_um)
CylinderOnlyControl(cylinder_diameter_um, cylinder_length_um)
EmptyBoreControl(cylinder_length_um, bore_radius_um)
OffsetSphereInCylinder(sphere_diameter_um, cylinder_diameter_um, cylinder_length_um, offset_um)
CentralReadoutPath(length_um, radius_um, mode="open_bore", conductor_radius_um=0.0, participates_as_casimir_boundary=False)
```

The readout path is a first-class role object, not an implied consequence of the Casimir morphology. It follows the White et al. proposed measurement channel: a current, photon, or electron path through the center of the sphere-cylinder array, compared against a matched control path without the external tube. For the first reproduction run, the readout path is labeled and used by the observable/ordinary-EM audit but does not participate as a Casimir boundary unless a later conductor-sensitivity run explicitly turns that on and logs it.

For each geometry expose:

```python
contains_body(point) -> bool
body_id(point) -> int | None
intersects_segment(p0, p1) -> set[int]
intersects_loop(points) -> set[int]
role_regions(grid) -> dict[str, np.ndarray]
```

Use these role labels:

```text
boundary_infrastructure
stress_shaping_body
source_shell_candidate
transit_readout_channel
far_field_control
ordinary_em_competitor_region
```

Generate role-label figures before running any physics calculation.

Required outputs:

```text
reports/fig_roles_plate_pillar.png
reports/fig_roles_sphere_cylinder.png
outputs/geometry_role_metadata.json
```

## Stage 2: Worldline scalar reproduction

Implement `worldline_scalar.py`.

Use either:

- the v-loop method described in the White et al. paper; or
- a Brownian-bridge closed-loop generator for the first smoke version.

If Brownian bridge is used, mark every result as a reproduction proxy rather than an exact White-method reproduction.

Minimum API:

```python
def generate_loops(n_loops: int, n_points: int, seed: int) -> np.ndarray:
    ...

def estimate_density_proxy(geometry, grid, loops, scale_grid) -> dict:
    ...
```

Engine behavior:

1. Generate closed loops reproducibly.
2. Translate each loop to each grid point.
3. Scale the loop over declared scale values.
4. Record whether the scaled loop intersects two or more distinct bodies.
5. Accumulate a local negative-energy morphology proxy.
6. Save all run metadata.

Metadata required in every output:

```json
{
  "loop_method": "v_loop or brownian_bridge",
  "n_loops": 2000,
  "n_points_per_loop": 1000,
  "scale_grid": "declared explicitly",
  "random_seed": 12345,
  "geometry_config_hash": "...",
  "normalization": "normalized_morphology_proxy"
}
```

### Validation before White geometries

Run these validation tests first:

1. **Parallel-plate sign/symmetry test**
   - The proxy between plates should be negative.
   - The map should be symmetric across the mid-plane.

2. **Gap scaling test**
   - Run gaps `2 um`, `4 um`, and `8 um`.
   - The integrated magnitude must weaken as gap increases.
   - If SI normalization is implemented, compare against the expected `d^-4` trend for parallel-plate Casimir energy density using the scalar/Dirichlet coefficient being modeled.

3. **Sphere-plate sanity test**
   - The strongest interaction should localize near closest approach.
   - The force proxy should point along the expected surface-normal direction.

If validation fails, stop and write:

```text
reports/validation_failure.md
```

## Stage 3: Reproduce White et al. geometry morphology

### 3A: Plate-pillar run

Config:

```yaml
geometry: pillar_midplane_cavity
plate_gap_um: 4.0
plate_width_um: 40.0
plate_height_um: 40.0
pillar_diameter_um: 1.0
grid:
  type: section_2d
  x_min_um: -4.0
  x_max_um: 4.0
  y_min_um: -4.0
  y_max_um: 4.0
  nx: 35
  ny: 35
loops:
  n_loops: 2000
  n_points_per_loop: 1000
  seed: 20210731
```

Outputs:

```text
outputs/plate_pillar_density_proxy.npy
outputs/plate_pillar_density_proxy.csv
outputs/plate_pillar_metadata.json
reports/fig_plate_pillar_density.png
reports/fig_plate_pillar_role_overlay.png
```

Required analysis:

- Determine whether the pillar screens the background region or concentrates the negative proxy near itself.
- Report concentration ratio:

```text
min_density_near_pillar / median_negative_density_between_plates
```

- Report robustness across at least five seeds.

### 3B: Sphere-cylinder run

Config:

```yaml
geometry: sphere_in_cylinder
sphere_diameter_um: 1.0
cylinder_diameter_um: 4.0
cylinder_length_um: 8.0   # default assumption if paper length is not specified
bore_radius_um: 0.0
grid:
  type: section_2d
  x_min_um: -3.0
  x_max_um: 3.0
  r_min_um: 0.0
  r_max_um: 3.0
  nx: 100
  nr: 100
loops:
  n_loops: 2000
  n_points_per_loop: 1000
  seed: 20210731
```

Outputs:

```text
outputs/sphere_cylinder_density_proxy.npy
outputs/sphere_cylinder_density_proxy.csv
outputs/sphere_cylinder_metadata.json
reports/fig_sphere_cylinder_density.png
reports/fig_sphere_cylinder_role_overlay.png
```

Required analysis:

- Detect whether the negative proxy forms a toroidal/lenticular source-shell candidate.
- Compute morphology scores against declared torus/shell masks.
- Report sensitivity to assumed cylinder length.
- Report robustness across at least five seeds.

## Stage 4: Alcubierre-shell source-demand target

Implement `alcubierre_target.py`.

This target is not an active rail. Use a canonical Alcubierre-style 3+1 metric first:

```text
alpha = 1
gamma_ij = delta_ij
beta_x = -V * f(r)
beta_y = 0
beta_z = 0
```

Use the smooth shell function:

```text
f(r) = [tanh(sigma * (r + R)) - tanh(sigma * (r - R))] / [2 * tanh(sigma * R)]
```

Run a declared grid search over:

```yaml
R_um: [0.5, 0.75, 1.0, 1.5, 2.0]
shell_thickness_um: [0.1, 0.25, 0.5, 1.0]
V: [0.01, 0.1, 1.0]
```

Do not tune parameters silently to maximize visual match. Every target choice must be logged.

For each target compute, or import from an existing ADM/tensor harness:

```text
rho_H or equivalent energy density channel
j_x, j_y, j_z momentum channels
S_xx, S_yy, S_zz stress/pressure channels if available
Tkk_plus_x and Tkk_minus_x along the transit/readout path
```

If a finite-difference evaluator is implemented from scratch, add a warning block in the report explaining accuracy limits.

Required outputs:

```text
outputs/alcubierre_target_grid_<id>.npz
outputs/alcubierre_target_metadata_<id>.json
reports/fig_alcubierre_energy_density_<id>.png
reports/fig_alcubierre_null_channels_<id>.png
```

## Stage 5: Stress-tensor and source-channel proxy

Implement `stress_tensor_proxy.py`.

The source-function audit needs more than energy-density morphology. Use two levels.

### Level 1: finite-difference force/stress proxy

Estimate role-level stress channels by virtual displacements:

```text
Move cylinder wall outward/inward.
Move sphere axially.
Move sphere radially.
Move plate boundaries.
Change pillar radius.
```

Use changes in integrated scalar worldline proxy to estimate:

```text
P_radial_proxy ~ -dE/dA_radial
P_axial_proxy  ~ -dE/dL_axial
F_sphere_axial_proxy ~ -dE/dx_sphere
F_sphere_radial_proxy ~ -dE/dr_sphere
```

These are proxies, not full stress-energy tensor components.

### Level 2: worldline energy-momentum tensor method

Add an interface for a worldline energy-momentum tensor implementation. When implemented, output tensor components rather than only finite-difference proxies.

Required rule:

- Density-only results may support `casimir_morphology_supported`.
- Well-labeled finite-difference stress proxies may support `source_function_proxy_supported`.
- `source_function_partially_supported` requires tensor-channel output from a worldline energy-momentum tensor implementation, or an imported/validated tensor calculation with matching geometry metadata.
- A transport-relevance claim requires a non-negligible source channel along or coupled to the transit/readout path.

Outputs:

```text
outputs/stress_proxy_<geometry>_<run_id>.npz
reports/fig_stress_channels_<geometry>_<run_id>.png
reports/stress_tensor_limitations.md
```

## Stage 6: Linearized metric and timing estimate

Implement `linearized_metric.py`.

Goal: estimate the largest plausible spacetime timing effect implied by the Casimir source scale.

Tasks:

1. Convert the Casimir energy-density estimate to SI where possible.
2. Compute a conservative linearized gravitational potential estimate from the energy density.
3. Compute an upper-bound Shapiro-like timing perturbation along the transit/readout path.
4. Estimate any shift-like or gravitomagnetic contribution only if a momentum/flux channel exists.
5. Explicitly report that static scalar Casimir energy density alone does not produce an Alcubierre shift channel.
6. Report the source-demand magnitude ratio against each Alcubierre target:

```text
source_demand_ratio = representative_Casimir_energy_density_J_m3 / representative_Alcubierre_source_demand_J_m3
```

This ratio is a hard interpretation gate. Morphological overlap cannot compensate for a source-demand magnitude ratio that is too small by declared audit thresholds.

Required output record:

```json
{
  "delta_t_gr_upper_bound_s": "...",
  "path_length_um": "...",
  "energy_density_scale_J_m3": "...",
  "alcubierre_source_demand_scale_J_m3": "...",
  "source_demand_ratio": "...",
  "assumptions": ["..."],
  "has_shift_source_channel": true,
  "has_flux_channel": false
}
```

Implement `em_proxy.py` for ordinary propagation/readout competitors:

```text
capacitance estimate
impedance/path-length estimate
waveguide cutoff or dispersion warning
surface/patch-potential sensitivity flag
conductor versus open-bore distinction
contact/readout loading warning
```

Report:

```text
abs(delta_t_gr_upper_bound_s) / abs(delta_t_em_proxy_s)
```

This ratio is a central interpretation gate.

## Stage 7: Role-locked sweep suite

Implement `role_sweeps.py`.

This is where the portable engineering strategy matters most. Do not run unstructured parameter sweeps. Each sweep must state which White/Alcubierre-shell role it targets and which channel should respond.

### Role assignment for sphere-in-cylinder

| Audit role | White et al. feature | Claimed or tested function |
|---|---|---|
| boundary infrastructure | cylinder wall | imposes Casimir boundary conditions and defines the shell environment |
| stress-shaping body | suspended sphere | shapes the toroidal negative Casimir region |
| source-shell candidate | toroidal negative region | compared to Alcubierre negative-energy shell |
| transit/readout channel | current/photon/electron path through center or array | proposed observable path |
| ordinary EM competitor channel | conductor, bore, surfaces, contacts, materials | mundane timing/voltage effects |
| Alcubierre source channel | demanded source tensor and shift-source structure | GR comparison target |

### Sweep family A: boundary geometry changes while transit/readout path is held fixed

Purpose: test whether the source-shell candidate responds to Casimir boundary geometry while the central propagation/readout geometry is held as constant as possible.

Runs:

```yaml
sphere_diameter_um: [0.5, 0.75, 1.0, 1.25, 1.5]
cylinder_diameter_um: [3.0, 4.0, 5.0]
cylinder_length_um: [4.0, 8.0, 16.0]
bore_radius_um: fixed
central_conductor_radius_um: fixed
```

Scores:

```text
source-shell morphology change
Alcubierre target overlap change
stress-proxy channel change
central-path metric/timing estimate
ordinary EM proxy stability
```

Interpretation:

- If source-shell morphology changes while ordinary EM proxy stays approximately fixed, the Casimir source-shaping claim gains support.
- If the predicted readout effect barely changes, the transit interpretation weakens even if the morphology is real.

### Sweep family B: transit/readout path changes while Casimir shell geometry is held fixed

Purpose: test whether the proposed observable follows the transit/readout channel rather than the source-shell candidate.

Runs:

```yaml
sphere_diameter_um: fixed at 1.0
cylinder_diameter_um: fixed at 4.0
cylinder_length_um: fixed at 8.0
bore_radius_um: [0.0, 0.05, 0.1, 0.25, 0.5]
central_conductor_radius_um: [0.0, 0.025, 0.05, 0.1]
```

Scores:

```text
change in source-shell morphology
change in ordinary EM proxy
change in GR timing upper bound
whether observable sensitivity tracks EM geometry or source-shell geometry
```

Interpretation:

- If the observable proxy follows bore/conductor properties, ordinary EM interpretation dominates.
- If the observable proxy follows the source-shell candidate while EM geometry is decorrelated, the Alcubierre-shell interpretation gains weight.

### Sweep family C: symmetry-breaking controls

Purpose: test whether the Alcubierre-shell analogy depends on a fine-tuned centered torus and whether off-center geometries degrade in a role-consistent way.

Runs:

```yaml
offset_radial_um: [0.0, 0.1, 0.25, 0.5, 1.0]
offset_axial_um: [0.0, 0.25, 0.5, 1.0]
```

Scores:

```text
torus/shell symmetry score
central path exposure score
Alcubierre target mismatch score
ordinary EM asymmetry estimate
```

Interpretation:

- A real source-function connection should degrade in a coherent source-channel way as symmetry is broken.
- A visual analogy may lose the torus without producing a coherent tensor/observable story.

### Sweep family D: dummy geometry controls

Purpose: separate toroidal Casimir morphology from transport-relevant observability.

Runs:

```text
sphere only
cylinder only
sphere in very large cylinder, weak Casimir coupling
cylinder with no sphere but similar central readout path
sphere-cylinder with large gap but same conductor/readout path
matched-length/matched-impedance readout path with no external tube
```

Scores:

```text
source morphology score
stress-channel proxy score
ordinary EM proxy score
timing-estimate score
```

Interpretation:

- If dummy geometries reproduce the observable proxy, the transit claim is probably ordinary readout physics.
- If only the full sphere-cylinder boundary geometry reproduces both source-shell and source-channel signatures, the source-function claim gains weight.

### Sweep family E: array scaling

Purpose: test whether arraying improves measurement viability or merely amplifies ordinary readout effects.

Runs:

```yaml
array_count: [1, 10, 100, 1000, 10000]
connection_mode: [parallel, series, independent_time_average]
```

For each mode estimate:

```text
GR timing scale if effects add coherently
EM/capacitive scale if readout effects dominate
noise and timing-resolution requirements
whether arraying changes source physics or only readout statistics
```

## Stage 8: Scoring

Implement `scoring.py`.

### Morphology score

```text
M = normalized_cross_correlation(casimir_negative_region, alcubierre_negative_region)
```

Also compute thresholded intersection-over-union.

### Role-specificity score

For each sweep parameter `p`:

```text
RSI(p) = intended_channel_response / (unintended_channel_response + epsilon)
```

Examples:

```text
cylinder-radius sweep should mainly alter boundary/source-shell channels
bore-radius sweep should mainly alter transit/readout and EM channels
sphere-offset sweep should alter symmetry and source-shell coherence
```

### Channel-sign score

Compare signs and presence of available channels:

```text
energy density sign
radial pressure proxy sign
axial pressure proxy sign
momentum/flux channel presence
null-channel sign along transit/readout path
```

### Observable-ratio score

```text
OR = abs(delta_t_gr_upper_bound_s) / abs(delta_t_em_proxy_s)
```

Report this on a log scale.

### Source-demand magnitude score

```text
SDR = abs(representative_Casimir_energy_density_J_m3) / abs(representative_Alcubierre_source_demand_J_m3)
```

Default interpretation gates:

```text
source_function_proxy_supported: stress proxy present and labeled, no tensor claim
source_function_partially_supported: tensor channels present and SDR >= declared partial threshold
alcubierre_shell_relevance_supported: tensor channels, channel signs, morphology, and SDR all pass declared thresholds
transport_relevance_supported: Alcubierre relevance plus transit/readout coupling, OR above declared threshold, and ordinary EM not dominant
```

If thresholds are changed from defaults, the report must show the old and new thresholds and explain why.

### Interpretation labels

Use these labels:

```text
casimir_morphology_supported
source_function_proxy_supported
source_function_partially_supported
alcubierre_shell_relevance_supported
transport_relevance_supported
ordinary_em_explanation_dominant
inconclusive_due_to_model_limits
```

A run may carry multiple labels, but every label must cite the scores that produced it.

## Stage 9: Report generation

Implement `report.py` to produce:

```text
reports/white_casimir_source_function_audit.md
reports/white_casimir_source_function_audit_summary.json
reports/figures/*.png
```

The report must include:

1. **Architecture disclaimer**
   - This is a White/Alcubierre-shell audit.
   - It uses portable source-function engineering.
   - It does not model the device as an active rail.

2. **Claim reconstructed**
   - what White et al. claim;
   - which parts are simulated;
   - assumptions introduced by this implementation.

3. **Reproduction result**
   - plate-pillar morphology;
   - sphere-cylinder morphology;
   - seed robustness;
   - validation status.

4. **Source-function audit**
   - role map;
   - tensor/stress proxy results;
   - source-demand comparison to Alcubierre target;
   - transit/readout channel exposure.

5. **Observable audit**
   - GR timing upper bound;
   - ordinary EM timing/readout proxy;
   - ratio and interpretation.

6. **Role-sweep results**
   - which changes affected the source-shell candidate;
   - which changes affected the transit/readout channel;
   - whether the two channels stayed separable or locked together.

7. **Allowed interpretation**
   - strongest interpretation supported by the simulation;
   - weaker interpretations supported by morphology only;
   - specific evidence required for stronger claims.

## Required final tables

### Table 1: Claim ladder

| Claim | Required evidence | Result |
|---|---|---|
| custom Casimir geometry sculpts negative energy | reproduced scalar worldline morphology | pass/fail/inconclusive |
| sphere-cylinder geometry produces toroidal negative region | robust torus/shell morphology across seeds | pass/fail/inconclusive |
| torus/shell matches Alcubierre source demand | tensor/channel agreement and source-demand magnitude ratio, not just density overlap | pass/fail/inconclusive |
| transit/readout path sees spacetime-relevant source channel | non-negligible metric/null/shift-source channel coupled to path | pass/fail/inconclusive |
| transit-time measurement indicates spacetime effect | GR timing estimate competes with ordinary EM/readout effects | pass/fail/inconclusive |

### Table 2: Role-sweep audit

| Sweep | Intended role | Intended channel changed? | Other channels changed? | Interpretation |
|---|---|---:|---:|---|
| sphere diameter | stress-shaping body | yes/no | yes/no | ... |
| cylinder diameter | boundary infrastructure | yes/no | yes/no | ... |
| bore radius | transit/readout channel | yes/no | yes/no | ... |
| sphere offset | source-shell symmetry/coherence | yes/no | yes/no | ... |
| dummy controls | EM/source separation | yes/no | yes/no | ... |

### Table 3: Observable scale

| Path | GR timing upper bound | EM proxy scale | Ratio | Dominant channel |
|---|---:|---:|---:|---|
| baseline sphere-cylinder | ... | ... | ... | ... |
| no-cylinder control | ... | ... | ... | ... |
| cylinder-only control | ... | ... | ... | ... |
| array N=1000 | ... | ... | ... | ... |

## Smoke-test target

First complete run:

```bash
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_smoke.sh
```

Smoke config:

```yaml
grid:
  nx: 25
  ny: 25
loops:
  n_loops: 128
  n_points_per_loop: 200
seeds: [1, 2]
sweeps: minimal
```

Smoke output must include:

```text
geometry role plots
one plate validation plot
one sphere-cylinder density proxy plot
one simple morphology score
stub timing estimate with assumptions
```

## Full-run target

After smoke passes:

```bash
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_reproduction.sh
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_role_sweeps.sh
python -m white_casimir_audit.report
```

Full run should use:

```yaml
loops:
  n_loops: 2000
  n_points_per_loop: 1000
seeds: [101, 102, 103, 104, 105]
```

Parallelize by grid point or seed. Keep each run restartable. Save partial outputs.

Do not start a full Python reproduction until the smoke run records an estimated grid-point/loop throughput and the report states whether the requested full run is feasible on the local machine. If the estimate is unfavorable, freeze the Python output at proxy/smoke scope and use it to drive a later C++/MPI worldline kernel.

## Guardrails for Codex

1. Preserve the distinction between Casimir morphology, stress tensor, Alcubierre source demand, transit/readout channel, ordinary EM channel, and observable timing.
2. Never use visual agreement as a substitute for tensor-channel agreement.
3. Never report `transport_relevance_supported` unless the transit/readout path has a non-negligible metric/null/shift-source channel and the ordinary EM proxy is not dominant.
4. Treat ordinary EM effects as first-class competitors.
5. If a calculation is only a proxy, label it as a proxy in filenames, metadata, figures, and report text.
6. If a result supports White et al.'s narrower Casimir-geometry claim, state that clearly.
7. If a result only supports the narrower claim, keep the interpretation there.
8. If role-sweep results surprise the audit, preserve the surprise and add follow-up tests rather than tuning it away.
9. Do not introduce active-rail components into the model.
10. Do preserve portable source-function engineering if it gives a sharper test of the White/Alcubierre-shell claim.

## Bibliography and source anchors

- Harold White et al., "Worldline numerics applied to custom Casimir geometry generates unanticipated intersection with Alcubierre warp metric," *European Physical Journal C* 81, 677 (2021). https://link.springer.com/article/10.1140/epjc/s10052-021-09484-z
- Marco Schafer, Idrish Huet, and Holger Gies, "Worldline Numerics for Energy-Momentum Tensors in Casimir Geometries," arXiv:1509.03509. https://arxiv.org/abs/1509.03509
- Alexey Bobrick and Gianni Martire, "Introducing Physical Warp Drives," arXiv:2102.06824. https://arxiv.org/abs/2102.06824
