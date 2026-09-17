# Coupled optical exposure and absorption

The coupled rotor dynamics give a substantially smaller optical encounter
allowance than the earlier nominal-transfer bound. Replacing the converter
estimate while retaining the guide, useful flight, recirculation loop and
reaction-path endpoints reduces final exposure by at least 34% in the first
fine history and 37% in the second fine history.

Both 19- and 20-unit rotor inventories then pass all four conditional energy
and retained rotor heat screens at the assigned absorption of 0.62 ppm.
The 19-unit allocation retains more energy for additional hardware, while
the 20-unit allocation has greater spin margin. The heat calculation uses
the model's separate zero-angular-momentum radiation population; transferring
heat from a moving absorbing facet into that population is a distinct
interface requirement.

## Encounters from the actual coupled forcing

The [coupled holding certificate](COUPLED_HOLDING_AND_CAPACITOR_DYNAMICS.md)
establishes

\[
\int_0^t |q|\,dt\le 2.85\int_0^t |F|\,dt,\qquad
F=N-(1+c)\dot W-c\dot\Pi_g-P_{\rm baseline}.
\]

All integrals used here retain their node capacities and proper flight
times. A delayed receipt has the bounded-variation estimate

\[
\int |A(t)-A(t-\delta)|\,dt\le\delta\,{\rm TV}(A).
\]

Within each history panel, the archived derivative bound supplies its
continuous variation. Exact positive-power endpoint jumps and the zero
extensions at the beginning and end supply the remaining variation.
The positive-part map preserves the original Lipschitz bound.

Similarly, the guide contribution
\(Q(t-\delta/2)-U(t+\delta/2)\), with \(U=Q+\dot H_g\), costs at most
\(\delta\,{\rm TV}(Q)+{\rm TV}(H_g)\). Each complete converter event
pays \(2\ell_{\rm converter}B_{\max}\) of photon-energy variation.
Each two-path reaction event pays
\(6\ell(B_{\rm peak}-B_{\rm pilot})\). Guide-trace and changing-baseline
work enter separately. Entire upcoming edges are prepaid in every cumulative
panel bound.

For a perfectly reflecting rotor,
\(X_{\rm rotor}\le\int|q|\,dt/j_{\min}\). The updated rail exposure is

\[
X=3X_{\rm guide}+X_{\rm useful}+X_{\rm loop}
  +X_{\rm reaction\ endpoints}+X_{\rm rotor}.
\]

The converter fill/drain contribution already occurs in \(F\), so its earlier
separate restart estimate is replaced together with the earlier converter
net-power estimate. All other encounter classes remain counted.

| History | Revised maximum final exposure | Earlier maximum final exposure | Largest revised/earlier ratio across labels |
|---|---:|---:|---:|
| First, 16 labels | 364.753 | 623.778 | 0.586180 |
| First, 32 labels | 500.299 | 760.874 | 0.658275 |
| Second, 16 labels | 83.2420 | 163.247 | 0.509914 |
| Second, 32 labels | 136.505 | 217.424 | 0.627829 |

These exposures are integrated energies in the inherited label units.
Their ratios compare the same guide, useful-flight and reaction construction.

## Absorbing rotor ports

Let \(a\) be absorption in the instantaneous tangential mirror rest frame,
\(s=\operatorname{sign}q\), and \(j\) the radial-comoving tangential speed.
The reflected powers obey

\[
P_{\rm out}=(1-a)\frac{1-sj}{1+sj}P_{\rm in},\qquad
q=P_{\rm in}-P_{\rm out}.
\]

Their signed tangential impulse per radius is
\(s(P_{\rm in}+P_{\rm out})\). Removing its ordered rotational work
leaves generalized heating power

\[
H=q-js(P_{\rm in}+P_{\rm out})
  =a(1-sj)P_{\rm in}\ge0.
\]

In the radially comoving thermal specialization, the corresponding changes
relative to the reflecting rotor equations are

\[
\Delta\dot b=\frac{xH}{\gamma_r M},\qquad
\Delta\dot j=-\frac{\Delta\dot b}{j}.
\]

These terms preserve \(j^2+2b\), total rotor energy input, radial momentum
input, and the full photon torque. Therefore the radial invariant and
support-work law remain the same; absorption consumes spin through its added
thermal action. A moving facet's local comoving heat has its own momentum,
so this bath specialization prescribes an additional internal transfer.

On \(j\ge j_{\min}=0.3\), discharge bounds both signs:

\[
\frac{H}{|q|}\le
\xi(a)=\frac{a(1-j_{\min}^2)}
 {2j_{\min}-a(1+j_{\min})},\qquad
P_{\rm in}+P_{\rm out}\le\frac{1+\xi(a)}{j_{\min}}|q|.
\]

The denominator is positive for the assigned absorption. With
\(x\le1.32+0.01140\), this gives

\[
\Delta b_{\rm absorption}
\le\frac{1.33140}{M}\,\xi(a)\,2.85\int|F|\,dt .
\]

The history audit reconstructs spin using the sum of radial-damping heat
and this absorption contribution, preserving node-by-node differences.

## Coupled heat and energy results

The table uses \(a=0.62\times10^{-6}\) for rotor absorption. Separately,
the common encounter-energy allowance uses
\(\alpha=0.62\times10^{-6}\) per incident-plus-departing energy.
These coefficients have distinct frame and encounter definitions. They
are assigned screens; a physical mirror needs its own spectrum and
angle-dependent law.

| History | Minimum spin, 19 units | Minimum spin, 20 units | Energy reserve, 19 units | Energy reserve, 20 units |
|---|---:|---:|---:|---:|
| First, 16 labels | 0.417055 | 0.447847 | \(2.766343\times10^{-4}\) | \(2.278997\times10^{-4}\) |
| First, 32 labels | 0.325277 | 0.371767 | \(1.226230\times10^{-4}\) | \(7.356901\times10^{-5}\) |
| Second, 16 labels | 0.443258 | 0.468967 | \(2.954043\times10^{-3}\) | \(2.944843\times10^{-3}\) |
| Second, 32 labels | 0.428873 | 0.456811 | \(2.257016\times10^{-3}\) | \(2.235281\times10^{-3}\) |

The 19-unit sufficient rotor-absorption ceiling is 4.22826 ppm over all
histories; for 20 units it is 6.04197 ppm. These ceilings concern the
conditional rotor bath model alone. The 18-unit first fine case still exceeds
its sufficient spin bound, with minimum spin bound 0.263291.

For other losses, the scalar replacement allowance accounts for additional
rotor encounters through

\[
E_{\rm replace}\le
\frac{\alpha X_0}{1-\alpha\,2.85(1+\xi)/j_{\min}}.
\]

This is an energy allocation under a specified feedback bound. Peak delivery,
replacement routing, finite stored energy, and heat in guides, splitters,
electrodes and reaction endpoints require their own physical construction.
Charging the common allowance to all encounter classes also conservatively
charges the retained rotor heat, whose total energy already stays in its
rotor state.

## Evidence

Seven tests check the absorbing port's energy and torque identities, its
independent energy gradient, integrated radial equivalence, the thermal
ceiling inversion, delayed receipt variation, resolved guide dynamics and
the replacement fixed point. Four independent history jobs reconstruct
the original power panels and verify linked evidence hashes. The retained
archives include every cumulative exposure and energy allowance, together
with per-node absorption and spin bounds.

~~~sh
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_coupled_optical_losses.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests/test_coupled_optical_losses.py -q
~~~

Source snapshots and manifests are in
[the optical-loss evidence directory](data/coupled_optical_losses/).
