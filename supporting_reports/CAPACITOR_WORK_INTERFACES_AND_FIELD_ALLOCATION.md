# Capacitor work interfaces and field allocation

## Boundary work of the loaded sheets

The reaction-work branch connects the store to an ensemble comprising
the two existing support sheets, their inline joints, and the local
Maxwell-field populations. A work interface must supply the sheet's
mechanical force as well as its net energy change.

For a sheet with integrated tensile duty \(T\) in each of two loaded
directions, let \(L\) be its complete core-plus-joint span. The
constitutive law gives

\[
\frac{dE}{dT}=2T\frac{d\log L}{dT},\qquad
F=\frac{T}{L},\qquad V=\frac{\dot L}{2}.
\]

There are four boundary facets, each carrying force \(F\) and moving
outward at speed \(V\). Their total mechanical power is
\(4FV=\dot E\). These identities retain the original material and
joint inventories.

For a direct load-bearing reflector, incident and departing powers at
each moving facet satisfy

\[
P_{\rm in}=\frac{F(1+V)}2,\qquad
P_{\rm out}=\frac{F(1-V)}2.
\]

Their difference supplies mechanical work; their sum is \(F\), even
when the support moves slowly. Thus four-facet optical exposure is
\(4\int F\,dt\). This class of interface continually processes
light to carry its preload.

The history screen grants signal speed \(c\), sheet span at most
\(0.1R_0=0.00265258\delta\), and the complete remaining endpoint
energy reserve for this extra loss alone. Using the original baseline
tension gives a lower bound on reflector exposure. The resulting
necessary loss-fraction ceilings are:

| History | Optimistic loss fraction per encountered energy |
| --- | ---: |
| First, 16 labels | \(2.71570\times10^{-14}\) |
| First, 32 labels | \(1.94474\times10^{-14}\) |
| Second, 16 labels | \(3.86956\times10^{-13}\) |
| Second, 32 labels | \(3.53857\times10^{-13}\) |

At the inherited 0.62 ppm optical-loss benchmark, every material label
exceeds this optimistic allowance by more than 600,000 times somewhere
in its history. The fine first history reaches a factor of 31.9 million.
Longer permitted response spans relax these ceilings proportionally.
Here exposure means incident plus departing energy. A coefficient charged
only to incident light has approximately twice the stated ceiling for
slowly moving facets.
The test applies to direct reflectors carrying the full sheet load;
separate mechanical transmissions and static-field interfaces have
different force and loss accounts.

## Short-gap electric cells

A vacuum capacitor with fixed effective electrode area has force
\(F=Q^2/(2\epsilon_0 A_e)\), gap
energy \(U=Fg\), and voltage \(V_e=Qg/(\epsilon_0 A_e)\), where
\(A_e\) is electrode area. A periodic row of equal support cells can
use the facing material boundaries of adjacent cells as return
electrodes. For fixed local pitch \(a\), the full gap is \(a-L\).
Each two-directional sheet cell receives two complete gaps, or
equivalently four shared half-gaps of length \(g=(a-L)/2\).

This assignment counts each physical gap once. With force and charge
following the constitutive load, the cell energies and powers are

\[
U_e=4Fg,\qquad P_e=4g\dot F,\qquad
P_m=2F\dot L,\qquad \dot U_e=P_e-P_m.
\]

The voltage of a complete gap is \(2Qg/(\epsilon_0 A_e)\); its
terminal power, summed over the two assigned gaps, gives \(P_e\).
The periodic interior supplies explicit opposing return surfaces.
Electrode carrier matter, finite-array boundaries and spatial response
remain parts of the physical construction.

The reaction displacement is small compared with the loaded sheet span.
The gap covers half the full local extension range plus 10% clearance.
A slower positioning stage follows the baseline rail configuration;
local pitch is fixed during the fast reaction replay. Its macro work and
finite electromagnetic leads require coupled evolution.

The electrode pads in this construction translate with fixed effective
overlap area. If an implementation changes that area with the supporting
facet, its terminal power acquires \(U_e\,d\log A_e/dt\), accompanied
by the same transverse mechanical work. That area port belongs in the
interface's complete work balance.

## Maxwell stress and the rail allocation

Electric-field pressure and tension contribute to the same Maxwell
tensor basis as the earlier magnetic populations. For outer-sheet gap
energy \(U_o\) and angular-sheet gap energy \(U_a\), the required
hoop and radial basis energies are

\[
H_e=U_o/2+U_a,\qquad B_e=U_o/2.
\]

Hence the capacitor contribution to \((\rho,p,2q)\) is
\((U_o+U_a,U_a,U_o)\). The complementary Maxwell populations carry
the remaining field energy and stress.

Let \(A=0.25120216644C\) bound the inherited dynamic trace, let
\(W_{\max}=0.05625C\) be the finite-path photon ceiling, and let
\(D\) be the constant reaction-field energy. The sheet increments
become \((D+\Pi_d+W)/3\) and \((D+\Pi_d+W)/6\). Their full
excursion widths are \((2A+W_{\max})/3\) and half that value.

Monotonic force provides a useful geometry-independent bound:

\[
F_+ (L_+-L_-)\le T_+-T_-,\qquad
U_e\le2(1.1)\Delta T.
\]

Together, both capacitor populations therefore need at most
\(0.61451977C\). Choosing \(D=0.62C\) supplies their complete
field tensor from the reaction bias, with a positive complementary
population. The four history screens require zero conversion of the
original standing photons for this purpose. A sharper constitutive
panel bound reduces the maximum assigned energy in several histories.

Increasing the bias also changes the support preload. Charging both
field preparation and the inherited conservative support-energy ceiling
leaves the following minimum reserves, including the existing finite
transfer-path loss screen:

| History | Minimum remaining rail reserve |
| --- | ---: |
| First, 16 labels | 0.0002277008 |
| First, 32 labels | 0.0000736838 |
| Second, 16 labels | 0.0029272318 |
| Second, 32 labels | 0.0022353943 |

These screens include the complete inherited rail allocation. The
electrode, lead, positioning and holding-loss duties use the same
remaining reserve.

## Reciprocal field work

The local replay uses the four archived finite-path reaction traces with
the enlarged bias. Maximum boundary speeds are
\(1.07\times10^{-7}c\) in the first support state and
\(9.18\times10^{-6}c\) in the second. Half-gap/span ratios range
from approximately \(2.03\times10^{-6}\) to
\(1.44\times10^{-3}\). These values describe the planar periodic
interior model.

In the first increasing trace, sheet energy changes through
\(0.0374161C\), whereas sheet-plus-capacitor energy changes through
only \(1.04059\times10^{-6}C\). The capacitors supply most of the
local mechanical exchange by releasing field energy. The fixed total
reaction-field allocation then requires the complementary population to
gain that same energy:

\[
U_b=D-U_e,\qquad
P_e+\dot U_b=P_m.
\]

Consequently the complete ensemble retains the sheet's work requirement.
The audit reproduces this identity to \(1.82\times10^{-12}C\).
The finite work branch must connect both electric terminals and the
complementary field population. This reciprocal account prevents the
local capacitor discharge from being counted as an additional energy
source.

The prescribed-trace replays establish the interface's energy and stress
relations. The changed preload shifts peak work by at most
\(0.001686P_*\) in the second support state. A coupled rotor replay
must use that updated work law. The physical completion also requires
charged electrode matter, finite leads, traction propagation, and a
holding-loss law evaluated over the service history.

## Reproduction

The [interface evidence](data/reaction_work_interfaces/summary.json)
contains four continuous allocation screens, four prescribed-trace
replays, source snapshots and verified parent hashes. Six tests check
sheet boundary work, the moving-reflector Doppler relation, capacitor
terminal work, tensor-preserving field assignment, continuous energy
ceilings, and periodic gap counting. This report was manually authored.

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_reaction_work_interfaces.py \
  --workers 4 --output /tmp/reaction_work_interfaces_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_reaction_work_interfaces.py
```
