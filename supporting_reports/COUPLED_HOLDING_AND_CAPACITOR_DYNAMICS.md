# Coupled holding and capacitor dynamics

The scheduled rail admits a conditional nonlinear holding construction with
19 units of rotor reference inventory per local capacity \(C=P_{\rm peak}\delta\),
radial damping \(k=0.8\), and reaction-field bias \(D=0.62C\). All four archived
histories satisfy its energy, constitutive-rate, and thermal spin bounds.
Finite reaction paths and periodic capacitor work ports also conserve the
complete energy ledger in eight resolved local transition trials.

The construction retains the guide, rotor, series elastic supports, joints,
Maxwell fields, and finite optical routes as separate components. Their
individual duties and energy exchanges enter the same allocation.

## Partition and coupled equations

Each receiving node receives the fixed fraction \(C_i/\sum_j C_j\) of the
original two support populations, their joints, baseline duties, and field
bias. The series constitutive law is homogeneous in all extensive arguments.
Consequently, this partition preserves the summed reference inventories,
baseline stresses, and energies, while giving each active node the same
normalized constitutive functions. Spatial packing and the mechanical
connection between these cells remain geometry requirements.

Write \(h=E_{\rm rotor}/M\), \(w=x-h\), \(y=p\), and \(s=t/R_0\), with

\[
R_0=\frac{1}{12\pi},\qquad
v=\frac{y}{h},\qquad S=\sqrt{1-v^2},\qquad
d_0=k+\frac{Sv}{x(1+S)}.
\]

The rotor pressure trace has derivative
\(\Pi_{\rm rotor}'/M=f\cdot(w,y)+a h'\), where

\[
a=1-kxv,\qquad
f=\left(kS-\frac{v}{h},
-\frac{S+ky}{h}-x\left(\frac{v}{hS}-k\right)d_0\right).
\]

For support derivative \(c=\partial E_{\rm support}/\partial\Pi\), finite-line
photon energy \(W\), guide trace \(\Pi_g\), and scheduled network power \(N\),
the exact reduced input is

\[
n=\frac{R_0}{M}
\left[N-(1+c)\dot W-c\dot\Pi_g-P_{\rm baseline}\right],
\qquad h'=u=\frac{n-c f\cdot(w,y)}{1+ca}.
\]

Changing macro duties contribute

\[
P_{\rm baseline}
=\sum_i\left[E_i'(T_i+\Delta T_i)-E_i'(T_i)\right]\dot T_i.
\]

The remaining equations are

\[
w'=v-u,\qquad
y'=-\frac{S}{x}w-d_0y+vu,\qquad
b'=\frac{kx}{hS}y^2.
\]

Thus the support work changes the rotor forcing directly, and the stored
photon energy contributes both energy and pressure. The constitutive history
enclosures include baseline variation throughout each panel.

## Nonlinear bounds

Two parameter-dependent quadratic storage functions give a thermal inequality
and an invariant domain. Their derivatives include both \(P_hh'\) and \(P_cc'\).
Exact outward integer intervals with denominator \(10^{18}\) verify the
matrix inequalities on

\[
1.08\le h\le1.32,\quad 0\le c\le0.5001,\quad
|w|,|v|\le0.012,\quad |u|,|c'|\le0.006.
\]

For a cold prepared radial state, the thermal inequality integrates to

\[
b(t)\le b(0)+2.7\frac{R_0}{M^2}
\int_0^t\left|N-(1+c)\dot W-c\dot\Pi_g-P_{\rm baseline}\right|^2dt.
\]

The invariant estimate closes within the assumed rectangle:
\(|w|\le0.011393\), \(|v|\le0.009038\), \(|u|\le0.005839\), and
\(|c'|\le0.005660\). The history bounds separately check the forcing,
constitutive curvature, baseline rate, and reconstructed lower and upper rotor
energies. A second exact interval calculation supplies

\[
\int_0^t|q|\,dt
\le2.85\int_0^t
\left|N-(1+c)\dot W-c\dot\Pi_g-P_{\rm baseline}\right|dt,
\]

which can price the revised rotor's reflective encounters.

The two reaction paths have lengths \(\delta/64\) and \(\delta/32\), peak
normalized power 1.2, and prepared pilot power 0.001. Their maximum photon
inventory is \(0.05625C\). The history screen includes their fill/drain forcing
and endpoint exposure, together with the changing support energy. The earlier
scheduled optical exposure remains a comparison allowance pending the new
rotor encounter calculation.

| History | Maximum thermal action bound, \(M=19\) | Minimum spin bound | Reserve after counted state and comparison optical losses |
|---|---:|---:|---:|
| First, 16 labels | 0.03151494 | 0.4229569 | \(1.976190\times10^{-4}\) |
| First, 32 labels | 0.05861399 | 0.3274756 | \(4.340482\times10^{-5}\) |
| Second, 16 labels | 0.01171477 | 0.4495469 | \(2.921553\times10^{-3}\) |
| Second, 32 labels | 0.01927825 | 0.4296658 | \(2.221978\times10^{-3}\) |

The operational spin floor is 0.3. For the first fine history, the 18-unit
inventory gives thermal action bound 0.06530757 and minimum spin bound
0.2661532. The 20-unit inventory gives minimum spin bound 0.3735963, while
its comparison energy allowance reaches \(-5.649214\times10^{-6}\).
These are sufficient bounds with different conservatism; their failures
identify an unresolved screen for that allocation.

## Capacitor ports in the local dynamics

The periodic capacitor construction uses existing material endpoints as
opposing plates. Fixed effective overlap area gives

\[
U_e=4Fg,\qquad P_e=4g\dot F,\qquad
P_m=2F\dot L,\qquad \dot U_e=P_e-P_m.
\]

The complementary Maxwell allocation has energy \(U_b=D-U_e\). Its work
completes the support input through \(P_e+\dot U_b=P_m\). The local simulator
evaluates both terms and rejects any negative complementary field channel.
Fixed overlap area is a kinematic assumption; a varying area adds its own
electrical and transverse mechanical work.

Four 19-unit trials cover rising and falling full-power transitions at the
largest first-location constitutive gain and the smallest second-location
gain. Two refined first-location trials and two 18-unit comparisons complete
the audit. The selected trials give minimum spins 0.509435–0.512815 and peak
thermal energies \(0.001268C\)–\(0.001420C\). All emitted powers, incident-light
margins, capacitor gaps, and complementary field channels remain positive.
Across all eight trials, the maximum complete-ledger error is

\[
2.13\times10^{-11}C.
\]

Refinement changes the final normalized state by at most
\(6.04\times10^{-14}\) and the rotor input-squared integral by at most
\(3.50\times10^{-12}\). These trials freeze the macro support duty while
resolving the local transition. The separate history certificate includes
varying baseline duties through continuous panel enclosures.

## Scope and reproducibility

The whole-history result certifies the coupled lossless scalar holding
equations under the declared allocation and input assumptions. Physical
electrode and elastic hosts, finite electrical leads, charge returns,
spatial traction work, whole-history endpoint positivity, and absorption heat
require their own component constructions. Optical replacement energy is an
allowance in the table; its altered forcing and retained heat still require
coupling to the dynamical bounds.

The implementation and evidence are:

- `toolkit/adm_harness_cli/adm_harness/coupled_holding_certificate.py`
- `toolkit/adm_harness_cli/adm_harness/hosted_reaction_dynamics.py`
- `supporting_reports/data/coupled_holding_certificate/`
- `supporting_reports/data/hosted_reaction_dynamics/`

Each evidence directory includes source snapshots, runtime versions, parent
hashes, numerical archives, and a manifest. From the repository root:

```sh
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_coupled_holding_certificate.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_hosted_reaction_dynamics.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests/test_coupled_holding_certificate.py toolkit/adm_harness_cli/tests/test_hosted_reaction_dynamics.py -q
```
