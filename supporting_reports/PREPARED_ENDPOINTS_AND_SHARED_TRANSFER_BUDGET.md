# Prepared endpoints and the shared transfer budget

The finite reaction paths admit positive emitter and rotor-incident powers
through both switching directions and the intervals between them. A
per-cell holding pilot supplies the quiet work associated with changing
receipt and material preload. Its additional encounters fit inside the
shared energy allocation for all four histories at store inventories
19 and 20. The first fine history retains spin bounds 0.325048 and 0.371577,
with respective energy reserves \(1.05770\times10^{-4}\) and
\(5.67162\times10^{-5}\) in its inherited ledger units.

The construction retains separate mechanical stores, optical guide loops,
two-delay reaction paths, original material cores and joints, standing
Maxwell fields, and thermal receivers. Fixed capacity fractions partition
the existing supports among cells. Opposed copies and three orientations
preserve the assigned mean tensor. Their spatial placement and electrical
current hosts have separate physical requirements.

## Continuous endpoint comparison

Let \(z=(x-h,p)\), \(n_0=R_0N/M\), and
\(z_*=(-kh^2n_0,hn_0)\), where \(N\) is the prescribed net guide and
receipt drive. The coupled contraction inequality also bounds tracking of
this instantaneous reference. A receipt jump contributes exactly
\(h|\Delta N|\) to the scaled comparison state
\(\mathcal E=(M/R_0)\sqrt{V(z-z_*)}\). Between jumps, the comparison includes
the changing guide, baseline support work, converter fill, and reaction
flight inventory.

Exact integer interval arithmetic checks the coefficients on 16,384 boxes
covering the inherited energy, velocity, displacement and constitutive-gain
domain. The declared tracking/output bounds are

\[
L_f=0.349,\quad K_g=0.0243,\quad K_h=1.950,\quad
L_s=0.0101,\quad K_c=0.334806,\quad K_w=0.00429.
\]

For example, an additional photon-trace derivative enters the comparison
with coefficient \(\chi(1+c_{\max})/R_0\), where
\(\chi=1.008465\). The support-power output receives
\(L_f\mathcal E+K_w|\dot W|\).

The reaction inverse has impulse recurrence
\(h_0=1,\ h_1=-1/2,\ h_n=-(h_{n-1}+h_{n-2})/2\), with
\(\sum|h_n|\le2.638292563\). Ninety-six rationally computed taps and
an analytic tail bound control the source commands. Positive scalar
recurrences enclose complete time bins, including ramp interiors,
receipt jumps, delayed returns, and settling tails. The coarser retained
comparison gives event commands below 0.911368 at peak power 1.2.

A separation of \(784\delta\) suffices for the induction between
events. The smallest observed panel exceeds \(21532\delta\).
The allocated remote-command tail is \(10^{-12}\), while the
geometric-series bound is \(1.25\times10^{-24}\). A second bin resolution
also passes.

## Prepared holding pilots

For each cell, the smooth receipt derivative and support-baseline work
give a quiet support-power bound \(P_{\rm quiet}\). The selected pilot is

\[
B_0=\max\left(0.001,\frac{2.638292563}{j_f}P_{\rm quiet}\right),
\qquad j_f=0.3,
\]

with outward numerical guards. This supplies quiet emitter positivity
and the rotor's signed incident-power requirement. In particular, source
return is bounded below by \(B_0-|a_{\rm delayed}|-|\Delta B|\);
the required incident power is bounded above using
\((1+j_f)/(2j_f)\) times the absolute rotor input. The calculation keeps
these sign-dependent ports separately.

| History | Largest cell pilot | Largest capacity-weighted pilot | Added endpoint exposure |
|---|---:|---:|---:|
| First, 16 labels | 0.0103822 | 0.00248204 | 44.3481 |
| First, 32 labels | 0.0109388 | 0.00275103 | 52.7402 |
| Second, 16 labels | 0.00293104 | 0.00104456 | 0.347072 |
| Second, 32 labels | 0.00364684 | 0.00153248 | 6.85739 |

The peak remains 1.2, so the reaction-flight ceiling remains
\(3(\delta/64)1.2\) in normalized units. Each initial pilot and its
support-field response are included under the previously priced combined
state ceiling. The main converter's baseline photons are paid from its
existing store preparation. The initial rotor is reset to a cold radial
equilibrium with the correspondingly reduced spin. Thus changing the
preparation preserves the total dynamic energy.

The earlier common pilot 0.001 falls below this sufficient quiet bound
in each history. The revised per-cell pilots supply a constructive
endpoint allocation.

## Finite thermal flight at the same endpoints

The passive paired relay adds photon inventory \(W_h\), with
\(\|\dot W_h\|_\infty\le X=\kappa q_{p,\max}\). Its bounded influence
on the tracking comparison and support work is

\[
\Delta\mathcal E\le
\frac{\chi(1+c_{\max})}{\alpha}X,\qquad
\Delta P\le L_f\Delta\mathcal E+K_wX,\quad \alpha=0.22.
\]

The emitted margin loses at most \(2.638292563\Delta P\).
The rotor incident margin loses at most
\([2.638292563+(1+j_f)/(2j_f)]\Delta P\).
The direct \(W_h\) term cancels from
\(q_p=N-\dot W_{\rm reaction}-P_{\rm support}\), while its effect on
the support remains in \(\Delta P\).

At inventory 19, the thermal derivative bound is
\(4.44097\times10^{-6}\). The resulting endpoint decrements are
about \(2.82\times10^{-5}\) for emission and
\(5.13\times10^{-5}\) for rotor incidence. Both leave positive
margins after the additional incident allowance for the 0.62 ppm
rotor-rest absorption model. The finite thermal energy, radiation
pressure, delayed bath arrival and radial damping are carried forward
from the [thermal budget](FINITE_THERMAL_TRANSFER_BUDGET.md).

## Combined history results

The additional pilot exposure is charged over the complete holding
duration plus its finite preparation and drain allowance:

\[
\Delta X=4\sum_i (B_{0i}-0.001)C_i(T_i+800).
\]

The [coupled encounter bound](COUPLED_OPTICAL_EXPOSURE_AND_ABSORPTION.md)
supplies the other optical interactions. The common 0.62 ppm encounter
coefficient and its energy-replacement feedback are included together
with the finite thermal route allowance.

| History | Spin lower bound, 19 | Spin lower bound, 20 | Energy reserve, 19 | Energy reserve, 20 |
|---|---:|---:|---:|---:|
| First, 16 labels | 0.415872 | 0.446802 | \(2.62460\times10^{-4}\) | \(2.13726\times10^{-4}\) |
| First, 32 labels | 0.325048 | 0.371577 | \(1.05770\times10^{-4}\) | \(5.67162\times10^{-5}\) |
| Second, 16 labels | 0.442639 | 0.468411 | \(2.95404\times10^{-3}\) | \(2.94484\times10^{-3}\) |
| Second, 32 labels | 0.428792 | 0.456739 | \(2.25299\times10^{-3}\) | \(2.23126\times10^{-3}\) |

These bounds use prescribed feedforward wave commands, lossless
two-delay reaction propagation, and the matched passive thermal relay.
Replacement of losses elsewhere remains a scalar energy allowance.
Its actual replacement pulses, absorption locations, heat destinations,
electrical conversion, finite charge leads, and material stress response
complete the physical implementation. Moving thermal collection adds the
separate work and variable-delay terms of its explicit geometry.

## Reproduction and retained evidence

Eight endpoint tests check the tracking identities, exact coefficient
enclosures, off-grid ramp bounds, signed Doppler branches, quiet pilots,
both event directions and the separated-event tail. Three integration
tests check paid preparation against the independent rotor energy,
the thermal tracking comparison against a driven differential equation,
and spin reconstruction with unchanged heat and motion penalties.

~~~sh
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_reaction_endpoint_certificate.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_prepared_transfer_budget.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests/test_reaction_endpoint_certificate.py toolkit/adm_harness_cli/tests/test_prepared_transfer_budget.py -q
~~~

The [endpoint evidence](data/reaction_endpoint_certificate/) and
[combined budgets](data/prepared_transfer_budget/) retain source
snapshots, numerical bounds and provenance manifests.
