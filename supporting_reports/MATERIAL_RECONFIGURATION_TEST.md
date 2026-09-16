# Material reconfiguration with conserved elastic inventories

16 September 2026.

A driven relativistic elastic ensemble follows all four saved containment
histories with positive material-energy reserve and fixed reference material
inventories. Each constituent has a single strain-energy law, including a
positive energy at zero tension. The construction retains the original
fields and current costs, resolves the inherited radial interface duties,
and accounts for the work needed to change the internal strains.

This establishes a conditional constitutive and energy-budget result. The
added hoop field's current hosts, reconfiguration actuators, finite joints,
and end reactions remain separate construction requirements. The strain
law is a theoretical material model; its physical realization and operating
scale remain open. Peak strains are large, and the control-rate estimates
continue to change with time resolution.

The [preceding finite construction](FINITE_CONTAINMENT_HOSTS_AND_EVOLUTION.md)
found that five passive material populations, affinely carried by the rail,
exceeded the budget even when photons could adjust their tensions. The
present model adds internal strain coordinates and counts the auxiliary
support membrane among the evolving materials. Its reference inventories
stay fixed while elastic energy moves between components.

## Sharing fixed-size material

The first comparison grants every sheet and string arbitrary quasistatic
orientation and redistribution between duties. Rotation and transport have
zero cost, and finite interface restrictions are relaxed. Sheets retain
their proper areas and strings retain their proper lengths. Thus their
total ideal tensile energies, \(A\) and \(K\), remain constant.

Let \((\rho,p,q)\) denote the integrated residual target, with two equal
transverse pressures \(q\), and let \(f\) be the existing radial-field
floor. Eliminating the material orientations and the Maxwell, photon and
pressureless support energies gives

\[
2A+K\ge\max\{2(f-q),\ f-p-2q,\ 0\},
\]
\[
3A+2K\ge\max\{-2(p+q),0\},\qquad
3A+2K\le\rho-p-2q.
\]

For this relaxed comparison, sheets minimize the weighted inventory needed
to satisfy the first inequality. Consequently the full sheet/string pool
can pass a history only if the all-sheet interval has a common value:

\[
A_{\min}(t)=\max\left\{f-q,\frac{f-p-2q}{2},
                    -\frac{2(p+q)}3,0\right\},\qquad
A_{\max}(t)=\frac{\rho-p-2q}{3},
\]
\[
\max_t A_{\min}(t)\le\min_t A_{\max}(t).
\]

Every label at both resolutions violates this condition. Independent
two-time linear programs keep the individual material orientations and
support components explicitly; all 96 programs confirm infeasibility.

| Fine history | Range of incompatible fixed-inventory gaps across labels | Required all-sheet energy-range ratio |
| --- | ---: | ---: |
| First | 0.757335–0.762683 | 20.35–23.53 |
| Second | 0.502670–0.520548 | 9.71–26.77 |

At the first history's largest-gap label, the pool needs at least 0.797629
energy at time 0.496934, while time 0.5 permits at most 0.0349455. At the
second largest-gap label, those bounds are 0.546059 at time 1.27998 and
0.0255108 at time 0.0376465. All values use the existing ledger normalization.

These bounds apply to quasistatic reorientation of the specified ideal
tensile constituents. They motivate a change in stored strain energy or an
explicit material transport path. A moving relativistic material pool would
add its own kinetic stress and exchange equations.

## One constitutive law along each trajectory

The membrane trial uses the isotropically strained rigid-membrane family of
[Mourão, Natário and Vicente](https://arxiv.org/html/2409.10602v2), with shear
parameter \(\epsilon=0.1\). Let \(M>0\) be a constituent's conserved
reference energy and \(J\ge1\) its proper area divided by reference area.
Its integrated energy and tensile duty are

\[
E=\frac M2[(1-\epsilon)(J+J^{-1})+2\epsilon],\qquad
T=\frac M2(1-\epsilon)(J-J^{-1}).
\]

The one-dimensional analogue uses \(\epsilon=0\) and a length ratio \(J\).
The constitutive inversion is

\[
E(T)=\sqrt{T^2+[(1-\epsilon)M]^2}+\epsilon M,\qquad
\ln J=\operatorname{asinh}\frac{T}{(1-\epsilon)M}.
\]

Each unloaded constituent retains \(E(0)=M\). The identity
\(dE=T\,d\ln J\) fixes its strain work. In a tensile isotropic membrane
state, the local squared sound speeds are
\(c_L^2=1\), \(c_T^2=T/E\), and
\(c_{TT}^2=\epsilon/[\epsilon+(1-\epsilon)/J]\), within the causal range.
These local properties leave the assembled structure's stability as a
separate problem.

Six constituents receive their own conserved inventories: inner and outer
longitudinal sheets, inner and outer hoop strings, the annular transverse
sheet, and the auxiliary transverse support sheet. The last is already
present in the rail's support allocation. Its changing duty is included in
the same material and energy accounting.

The finite coaxial interface equations remain

\[
T_{Wi}+T_{Si}=H_i,\qquad
T_{Wo}+T_{So}+2T_M=H_o,\qquad T_M=R_\eta U,
\]

where \(U\) is added hoop-field energy and
\(R_\eta=(\eta^2-1)/(2\ln\eta)\), with \(\eta=1.01\).
The allocation first maximizes the ideal remaining reserve with these
finite interface constraints. The elastic constituents then supply the same
tensile duties, with their extra energy charged to that reserve.

Since \(0\le E(T)-T\le M\), a conserved total reference inventory below
the minimum ideal reserve gives an explicit uniform energy allowance. This
test prepares one quarter of that reserve as reference material. The
remaining margin stays positive throughout the replay.

Reference material is allocated once, before the motion, to minimize the
largest linear stretch across all constituents. A common linear-stretch
cap \(L\) requires

\[
M_j\ge\frac{2T_{j,\max}}
 {(1-\epsilon_j)(L^{d_j}-L^{-d_j})},
\]

with \(d_j=2\) for sheets and \(d_j=1\) for strings. The sum decreases
monotonically with \(L\), giving a scalar solution for the optimum within
the selected total inventory. A small positive inventory floor also counts
unloaded roles. Every chosen \(M_j\) stays fixed afterward.

| History | Minimum ideal reserve | Minimum reserve with elastic material counted | Largest linear stretch from the relaxed state |
| --- | ---: | ---: | ---: |
| First, coarse | 0.00250839 | 0.00242910 | 78.14 |
| First, fine | 0.00233303 | 0.00226065 | 81.51 |
| Second, coarse | 0.0142799 | 0.0112553 | 20.11 |
| Second, fine | 0.0129396 | 0.0101712 | 20.91 |

All 246,816 sampled states retain positive reserve. Equal reference-energy
allocations among the six components give maximum fine-history linear
stretches of 160.25 and 44.79. Allocating the reference material by duty
reduces those maxima to 81.51 and 20.91. The corresponding largest sheet
area ratios are approximately 6,643 and 437. This optimization addresses
stretch for a fixed prepared-energy allowance; actuator rate and joint
cost are additional objectives.

## Internal motion and reciprocal work

The material strain differs from the rail's affine deformation. For a
longitudinal sheet, the internal logarithmic stretches are

\[
q_z=\tfrac12\ln J-\ln\lambda_z,\qquad
q_\theta=\tfrac12\ln J-\ln\lambda_\perp.
\]

Both transverse-sheet coordinates use \(\lambda_\perp\), while a hoop
string has \(q=\ln J-\ln\lambda_\perp\). These coordinates specify the
local deformation that a reconfiguration mechanism must produce. Each
sheet coordinate has conjugate generalized force \(T\); the string has
the same single-coordinate force. Its actuator receives the opposite
reaction, which must enter the future frame and junction construction.

For each constituent, the archive records

\[
\Delta Q_i=\Delta E_i+
\overline{P_{z,i}}\,\Delta\ln\lambda_z+
\overline{P_{\theta,i}+P_{s,i}}\,\Delta\ln\lambda_\perp.
\]

The continuous replay uses linear tensile duties and field energies on each
panel, logarithmically interpolated macro stretches, and the fixed
constitutive function \(E(T)\). The pressure-work quadrature is then exact
for the defined interpolation. Convexity of \(E(T)\) leaves at least the
interpolated endpoint energy reserve between samples. Separate constitutive
work integrals verify \(\int T\,d\ln J=\Delta E\).

A deterministic exchange network routes panel energy from releasing
components to receiving components. The complementary rail port carries
the same net exchange implied by the retained target tensor. Each routed
transfer has equal sender and receiver entries; no component receives an
unpaired energy increment. This is a lossless exchange construction whose
power conversion and mechanical hardware remain to be supplied.

The internal activity is much larger than its net exchange. On the first
fine history, the auxiliary support sheet releases approximately
0.532–0.540 net energy per label over the stroke, while the annular sheet
receives approximately 0.0524–0.0589. At the second location the auxiliary
sheet instead receives approximately 0.242–0.264. Photons, fields and the
remaining inventory participate in the reciprocal transfers. Matching the
total target preserves its net exchange while changing the required
internal routing.

The model is an inverse driven replay: the required duties determine strains
through the fixed constitutive law, and the resulting work determines the
control ports. A coupled evolution must supply actuator forces, kinetic
stress, spatial compatibility and the original field solution between saved
samples.

## Geometric and rate requirements

For a patch with side lengths bounded by \(d\), the prescribed internal
logarithmic strain rates give a local corner control-speed bound

\[
v_{\rm control}\le\frac d2
\sqrt{\dot q_1^2+\dot q_2^2},
\]

with the single-coordinate version for strings. The calculation bounds
each entire interpolation panel using the exact constitutive derivative
\(d\ln J/d\tau=\dot T/\sqrt{T^2+[(1-\epsilon)M]^2}\).

Taking each patch's current dimensions no larger than the annular gap gives
maximum fine-history bounds of \(0.0394c\) and \(0.00170c\). The archive
also supplies the reference patch size required to retain that size bound
through its full stretch. Applying the same calculation at leg-sized patch
dimensions gives bounds above \(c\). A tiled or otherwise distributed
reconfiguration mechanism therefore warrants explicit geometric treatment.

The rate estimates have yet to converge: the coarse gap-sized bounds are
\(0.0181c\) and \(0.000779c\). Several peak work rates increase with
refinement as duties switch between components. A further allocation with
bounded rates and a resolved actuator model must address these transitions.
The present speed estimates provide local kinematic requirements; the
moving-material and actuator stress tensors remain open costs.

The independent-current-host obstruction from the finite construction also
persists. At the first fine history, ten samples already fail its favorable
all-speed host bound with ideal tensile constituents. The elastic replay
preserves that limitation. Shared current populations, end-force transfer
and torque transmission need to be solved together with the reconfiguration
hardware.

## Evidence and status

The result establishes a conserved-reference-material constitutive path
through the sampled duties, with positive energy reserve and explicit work
exchange. It identifies a substantial deformation requirement and an
unresolved transient-rate requirement. The remaining physical construction
is the joined, actuated assembly: finite patches, their reciprocal reactions,
their kinetic and hardware costs, and the current and end-load connections.

The [implementation](../toolkit/adm_harness_cli/adm_harness/material_reconfiguration.py),
[four-worker audit](../toolkit/adm_harness_cli/scripts/audit_material_reconfiguration.py)
and [tests](../toolkit/adm_harness_cli/tests/test_material_reconfiguration.py)
are accompanied by a [summary](data/material_reconfiguration/summary.json),
four state archives and a [manifest](data/material_reconfiguration/manifest.json).
The evidence includes parent hashes, the execution's base commit and exact
source snapshots, conserved inventories, strains, configuration coordinates,
component pressures, exchanges and routed transfer totals.

The focused suites pass 34 tests. Independent optimization formulations
check the finite allocation and the fixed-size pool bounds. The saved
histories include 96 two-time rejection certificates and 148 independent
constitutive work integrals. Maximum tensor reconstruction error is below
\(9\times10^{-16}\), forward constitutive error below
\(1.2\times10^{-15}\), and exchange-sum error below
\(1.2\times10^{-15}\). Every route's unmatched exchange is below
\(1.7\times10^{-16}\).

Reproduction uses a fresh output directory:

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_material_reconfiguration.py \
  --workers 4 --output /tmp/material_reconfiguration_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_material_reconfiguration.py \
  toolkit/adm_harness_cli/tests/test_finite_containment.py \
  toolkit/adm_harness_cli/tests/test_containment_ensemble.py
```
