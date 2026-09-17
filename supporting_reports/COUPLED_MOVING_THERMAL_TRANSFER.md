# Coupled moving thermal transfer

The moving paired relay and its finite radial work-photon leads fit within
the existing conditional holding and transfer budget. At inventory 19,
the tighter first-location history retains spin at least 0.325047,
emitter margin \(6.70988\times10^{-4}\), and rotor incident margin
\(9.42820\times10^{-4}\). The energy reserve remains
\(1.05770\times10^{-4}\) in the inherited ledger normalization.

The [geometric construction](MOVING_THERMAL_RELAY_AND_WORK_PORTS.md)
supplies retarded heat arrival, guide recoil, radial actuator work,
and two distinct photon inventories. This coupled calculation selects
those radial work-photon leads. Their field energy enters the same
support trace as the thermal flight photons.

## Common energy port

Let \(q_p\) be power entering the absorbing rotor port,
\(P_w\) the net power entering the separate radial work leads, and
\(q_s=q_p+P_w\) their common source input. The two photon inventories
satisfy

\[
W_{\rm total}=W_h+V_w,\qquad
\dot W_{\rm total}=Q_e-Q_a+P_w,\qquad
q_r=q_s-\dot W_{\rm total}.
\]

Thus the intermediate guide work transfers energy between the two
photon populations. Its finite source/return power remains part of the
source splitting requirement.

For \(r=(1+v_*^2)/(1-v_*^2)\), define \(f_1\) and \(f_\infty\) as
the relay's integrated radial-force and remote-power coefficients.
The positive ray construction gives

\[
\int Q_a\le r^3\int Q_e,\qquad Q_{a,\max}\le r^5Q_{e,\max},
\quad \|P_w\|_1\le f_1\|Q_e\|_1,\quad
\|P_w\|_\infty\le f_\infty Q_{e,\max}.
\]

Writing \(d_1=1+r^3+f_1\) and \(d_\infty=r^5+f_\infty\),
the actual absorption law \(Q_e\le\kappa|q_p|\) implies

\[
\|\dot W_{\rm total}\|_1\le\kappa d_1\|q_p\|_1,\qquad
\|\dot W_{\rm total}\|_\infty\le\kappa d_\infty q_{p,\max}.
\]

The parent rotor gain \(G=2.85\), applied to the added forcing
\(-(1+c)\dot W_{\rm total}\), then gives

\[
\|q_p\|_1\le
\frac{G\|F_0\|_1}
 {1-\kappa[G(1+c_{\max})d_1+1+r^3]}.
\]

The denominator is 0.999988855 and the resulting gain is 2.850031763.
The simultaneous peak bound is
\(q_{p,\max}\le MU_{\max}/[R_0(1-\kappa r^5)]\).
Multiplying the flight-rate peak and integrated bound controls its
input-squared contribution. Minkowski's inequality combines this term
with the existing forcing history. Bath heat uses the arriving-energy
bound \(\kappa r^3\|q_p\|_1\).

## Inventory and endpoint duties

For inventory 19, thermal flight energy is at most
\(6.94157\times10^{-8}C\), and work-lead photons add
\(1.78990\times10^{-9}C\). The combined support and photon allowance is
\(1.06815\times10^{-7}C\). These bounds use
\(L=\delta/128\), \(|v|\le0.00905\), and maximum work gap
\(0.00735296\,c\delta\).

The [endpoint comparison](PREPARED_ENDPOINTS_AND_SHARED_TRANSFER_BUDGET.md)
receives the full flight-rate perturbation. Source splitting also
reserves incoming work-lead photons, whose peak is
\(1.22825\times10^{-7}C/\delta\). The actual rotor input differs from
the common source input by the signed remote work power. Both effects
are included in the incident margin.

The thermal encounter allowance is increased by the retarded energy
ratios. Source and return encounters of the work leads are also priced.
The existing 0.62 ppm common encounter coefficient still supplies a
scalar energy-replacement allowance for those interactions.

| History | Spin lower bound, 19 | Spin lower bound, 20 | Energy reserve, 19 | Energy reserve, 20 |
|---|---:|---:|---:|---:|
| First, 16 labels | 0.415865 | 0.446795 | \(2.62460\times10^{-4}\) | \(2.13726\times10^{-4}\) |
| First, 32 labels | 0.325047 | 0.371576 | \(1.05770\times10^{-4}\) | \(5.67162\times10^{-5}\) |
| Second, 16 labels | 0.442635 | 0.468408 | \(2.95404\times10^{-3}\) | \(2.94484\times10^{-3}\) |
| Second, 32 labels | 0.428791 | 0.456738 | \(2.25299\times10^{-3}\) | \(2.23126\times10^{-3}\) |

All eight variants retain the nonlinear forcing and energy domain,
positive endpoint powers, the assigned spin floor, and positive energy
reserve. The largest extra reserve debit relative to the frozen-relay
budget is \(2.11\times10^{-13}\) in the inherited ledger units.

## Material connection and evidence

The added radial photon actuators cancel thermal recoil on guides
following the common radial trajectory. Guide rest inventory, inertial
work, axial forces, transmitted torques and their material supports
remain separate duties. Finite aperture, aiming, reciprocal thermal
emission and physical coatings determine the actual optical and heat
laws. The energy-replacement allowance also needs its own delivery
waveforms and heat destinations.

Four coupling tests recover the frozen-relay result at zero radial
speed, independently iterate the absolute-work feedback equations,
remove both paths at zero absorption, and compare the budget coefficients
with the selected geometric routes. The geometric milestone supplies
13 additional tests and four trajectory replays.

~~~sh
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_moving_thermal_budget.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests/test_moving_thermal_budget.py -q
~~~

The [four-history evidence](data/moving_thermal_budget/) records the
node bounds, reserves, source snapshots and parent/output hashes.
