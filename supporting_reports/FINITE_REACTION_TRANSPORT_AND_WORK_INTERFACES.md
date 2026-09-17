# Finite reaction transport and support work

## Two prepared paths

The local store can exchange work with the existing longitudinal and
angular support sheets through two photon paths of different lengths.
The construction includes the energy and stress of the photons in
flight, the corresponding additional sheet strain, and the store power
needed to change both inventories. The support sheets retain their
original core and joint populations.

Use local transfer time \(\delta\), peak transfer power \(P_*\), and
\(C=P_*\delta\). The short path has travel time \(\ell\); the second
has travel time \(2\ell\). Each receives half the emitted power. At
the source and support endpoints, respectively, prescribe

\[
A_k(t)=\tfrac12[B(t)+a(t)],\qquad
D_k(t)=\tfrac12[B(t)-a(t)],\qquad k=1,2.
\]

The paths are prepared with a positive pilot \(B_0\). Their total
flight energy and its derivative are

\[
W(t)=\sum_{k=1}^2\int_{t-k\ell}^{t}B(s)\,ds,
\qquad
\dot W=2B(t)-B(t-\ell)-B(t-2\ell).
\]

For required support work \(P_s\), the causal modulation equation is

\[
a(t)+\tfrac12a(t-\ell)+\tfrac12a(t-2\ell)
=P_s(t)+\dot W(t)/2.
\]

Substitution into the delayed endpoint balances gives support absorption
\(P_s\) and source draw \(P_s+\dot W\). Each emitted stream remains
physical when \(|a|\le B\). The inverse filter has poles of modulus
\(1/\sqrt2\). An exact rational sum of its first 64 impulse
coefficients, followed by an outward analytic tail, bounds its
\(\ell^1\) norm by 2.63829256156. The remaining tail is below
\(8.50\times10^{-10}\).

The pilot carries \(W_0=3\ell B_0\) before service begins. Preparation
also supplies the sheet strain caused by this initial photon population.
The positive pilot is a physical initial condition: an initially empty
path has a propagation interval before its first incident power arrives.

The directed streams are partitioned among spatially opposed paths and
three equal axis populations. The resulting integrated momentum is zero
and integrated stress is \(W/3\) in each direction. This partition
preserves the stated total photon inventory. Fixed relay ports define
the path delays; a moving mechanical transducer has a separate geometry.

## Shared stress and exact work

Let \(A=0.25120216644C\) be the inherited local dynamic-trace envelope,
and let \(\Pi_d\) include the rotor and guide. The positive isotropic
field bias retains energy \(A\). The support increments are

\[
\Delta T_{\rm outer}=\frac{A+\Pi_d+W}{3},\qquad
\Delta T_{\rm angular}=\frac{A+\Pi_d+W}{6}.
\]

Evaluating the two conserved core/joint laws at these loads gives the
additional support energy \(E_s(\Pi_d+W)\). Write
\(c=\partial E_s/\partial(\Pi_d+W)\),
\(\dot\Pi_{\rm rotor}=F_r+a_q q\), and
\(a_q=1-kxv\). With external network power \(N\) and guide trace
rate \(F_g\), exact coupled work requires

\[
q=\frac{N-\dot W-c(F_r+F_g+\dot W)}{1+c a_q},
\qquad P_s=c(F_r+F_g+\dot W+a_q q).
\]

Consequently \(q+P_s+\dot W=N\). The dynamic equations retain the
rotor's separate radial, rotational and thermal states. Within the
stated trace envelope, the combined additional energy satisfies

\[
E_s+W\le3A+2W_{\max},\qquad W_{\max}=3\ell B_{\max}.
\]

The local trials remain inside the charged envelope. A continuous
whole-service invariant and heat certificate must use these coupled
equations; the earlier certificate for an externally prescribed rotor
input has a different forcing law.

## Numerical construction

The default short delay is \(\delta/64\), the pilot is
\(0.001P_*\), and the peak bias is \(1.2P_*\). Septic ramps fill
and drain the paths over \(256\delta\). Peak flight inventory is
\(0.05625C\); its combined photon and support energy allowance is
\(0.1125C\). Including the shared reaction envelope gives an
additional continuous ceiling of \(0.8661065C\).

The audit follows both directions of a unit receipt step in two support
states drawn from the fine rail histories. It integrates the nonlinear
store, computes the actual delayed endpoint streams, and closes the
guide, converter, useful-path, store, photon and support ledger.

| Support state and receipt | Minimum sampled spin | Peak thermal energy / \(C\) | Maximum \(|a|/B\) |
| --- | ---: | ---: | ---: |
| First, high support gain, increasing | 0.4871641 | 0.000788994 | 0.278193 |
| First, high support gain, decreasing | 0.4884431 | 0.000712732 | 0.277959 |
| Second, low support gain, increasing | 0.4905489 | 0.000773372 | 0.101527 |
| Second, low support gain, decreasing | 0.4910089 | 0.000697994 | 0.101527 |

The first increasing step was also evaluated at short delays
\(\delta/16\) and \(\delta/256\). Their minimum spins were
0.4541840 and 0.4951298. Thus longer residence consumes more temporary
rotor energy; all evaluated cases remain above the 0.30 operating floor.
Every emitted stream stays positive, and the router retains its required
incident power. Across eight trials the maximum complete-ledger residual
is \(6.94\times10^{-11}C\). Halving the integration step and sampling
interval changes final state components by at most
\(1.57\times10^{-13}\) and integrated squared rotor input by
\(4.63\times10^{-10}\).

Both endpoints process every emitted photon. The increasing-step trial
therefore has total endpoint exposure \(1863.76C\), despite net support
work being much smaller. This distinction matters when assigning actual
transducer and routing losses.

## Rail energy screen

The four complete receipt histories supply an upper bound on event
windows. Charging the new pilot throughout service, the active path
bias during those windows, the extra photon/support inventory, and the
inherited 0.62 ppm optical replacement loss gives these minimum panel
reserves in the original rail normalization:

| History | Minimum reserve |
| --- | ---: |
| First, 16 labels | 0.0002552463 |
| First, 32 labels | 0.0001014098 |
| Second, 16 labels | 0.0029324318 |
| Second, 32 labels | 0.0022476793 |

This is an energy screen under the inherited endpoint-loss assumption.
The calculation preserves the complete rail allocation, including the
packet, standing supports, guide, store, joints and existing transfer
paths. Standing-field holding losses, physical mechanical conversion and
the whole-history coupled heat estimate share the remaining reserve.

The constructed endpoint schedules are synchronized feedforward
commands. Their stability and positivity are properties of the stated
delay equation and evaluated commands. Distributed feedback, local
traction propagation and a mechanical endpoint law require their own
construction. These are distinct component duties alongside field
hosting and confinement.

## Reproduction

The [finite-path evidence](data/finite_reaction_transport/summary.json)
contains four history screens, eight local trials, refinement comparisons,
source snapshots and parent hashes. Six focused tests cover the stable
inverse, delayed balances, preparation, analytic flight inventory,
independently differentiated support work, and scalar/vector agreement.
Together with the existing shared and coupled reaction tests, 15 tests
pass. This report was manually authored.

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_finite_reaction_transport.py \
  --workers 4 --output /tmp/finite_reaction_transport_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_finite_reaction_transport.py \
  toolkit/adm_harness_cli/tests/test_coupled_rail_reactions.py \
  toolkit/adm_harness_cli/tests/test_shared_rail_reactions.py
```
