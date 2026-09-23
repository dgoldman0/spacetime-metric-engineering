# Constant-Radius Track and the Boundary Gate

Date: 23 September 2026.

**Verdict: PASS for the geometry-demand boundary gate.** A track whose areal
radius is constant along its entire service length carries the complete
beta075 service program with a certified Hawking–Ellis Type I demanded tensor
at every evaluated point. The regularity-repaired beta075 geometry has 13,587
Type IV points on the same 141,661-point map; the constant-radius candidates
have none, through static end transitions that join an exactly flat exterior.
The packet, carrier, bundle and service-time audits reproduce the beta075
results.

Along the track both radial null energies vanish identically at every service
time, so the radial block is an exact string cloud with zero current and
saturated radial null energy. The service dynamics enter the angular pressure
alone. The remaining null-energy requirements are an angular deficit from the
service dynamics, dominated by the scheduled decompression of the standing
support, and a static radial deficit in the two end transitions, where the
two-ended spherical model widens the track into its asymptotic ends.

The redesign changes only the angular metric channel of the reduced model.
"Throat" below refers to that channel's minimal-radius profile; the transport
itself takes place along the track, where the packet is carried by the shift
through the stretched support.

## Why the frozen geometry fails

For a spherically symmetric spacetime written as a two-dimensional metric
\(g_{ab}\) on the \((\sigma,\ell)\) quotient times spheres of areal radius
\(R\), every radial null vector \(k\) satisfies

\[
8\pi\,T(k,k) = G(k,k) = -\frac{2}{R}\,k^a k^b \nabla_a\nabla_b R .
\]

With \(k_\pm=n\pm e_\ell\), the orthonormal radial block has
\(\rho+p_\ell=\tfrac12[T(k_+,k_+)+T(k_-,k_-)]\) and
\(j_\ell=\tfrac14[T(k_-,k_-)-T(k_+,k_+)]\), so

\[
\Delta_{\rm rad}=(\rho+p_\ell)^2-4j_\ell^2=T(k_+,k_+)\,T(k_-,k_-).
\]

The demanded tensor is therefore Type IV exactly where the outgoing and
ingoing radial null energies have opposite signs. Both are second derivatives
of the areal radius along the two radial null directions. A static geometry
has equal values and a zero current; time dependence acting on a varying
radius separates them.

The beta075 standing support stretches the radial metric by a factor of about
600 and holds its areal radius nearly fixed, so its support region is close to a long
cylinder with \(T(k_\pm,k_\pm)\approx0\). The decompression schedule \(q(\sigma)\)
then relaxes that stretch during service. An attribution run on the
regularity-repaired geometry evaluated the same certified classifier with
individual features switched off (grid spacing 0.1 over
\(\sigma\in[-1.5,2.9]\), \(\ell\in[-4,4]\)):

| Control | Type IV points | Integrated imaginary eigenvalue |
| --- | ---: | ---: |
| Repaired beta075 | 842 | \(3.37\times10^{-2}\) |
| Support decompression alone (no shift, packet windows, shell or receiver) | 874 | \(3.58\times10^{-2}\) |
| Decompression removed | 252 | \(6.69\times10^{-4}\) |
| Static support with moving packet windows, zero shift | 236 | \(8.06\times10^{-4}\) |
| Static support with carrying flow, packet windows removed | 19 | \(2.01\times10^{-7}\) |

Decompression of the standing support carries about 98% of the integrated
burden, and the moving packet-local windows carry the remainder. Both act on
an areal radius that varies along the rail through the throat profile
\(\ell^2+R_{\rm th}^2\), the time-dependent angular jacket and the receiver's
angular flange.

## Design rule

**Hold the areal radius constant wherever the service metric evolves, and
confine every variation of the radius to regions where the geometry is
static.** Where \(R\) is constant its Hessian vanishes, so the radial block is
exactly

\[
\rho=-p_\ell=\frac{1}{8\pi R^2},\qquad j_\ell=0,
\]

the stress of a radial Nambu–Goto string cloud with constant areal flux. The
two-dimensional dynamics of lapse, shift and radial stretch enter only the
angular pressure,

\[
p_\Omega=\frac{1}{8\pi}\left(\frac{\Box R}{R}-K\right)=-\frac{K}{8\pi},
\]

where \(K\) is the Gaussian curvature of \(g_{ab}\). A string's worldsheet
stress is invariant under boosts along the string, so motion along the rail
leaves this radial block unchanged. In a static region the current vanishes
identically, and both radial null energies equal \(-R''/(4\pi R)\) for unit lapse.

The candidate geometry realizes the rule with four parts:

1. **Track.** \(R=R_b=1.75\) for \(|\ell|\le L_b=5\), at every service time.
2. **Service cutoff.** The service metric \((\alpha,\beta,\gamma_{\ell\ell})\) is
   blended to \((1,0,1)\) between \(|\ell|=4\) and \(|\ell|=5\) with a C∞ step,
   so every time-dependent field vanishes identically where the radius varies.
   The beta075 support bump is below \(2.3\times10^{-6}\) at \(|\ell|=4\).
3. **Static end transitions.** For \(x=|\ell|-L_b\) between 0 and \(\Delta=1.5\),
   \(R=R_b+\Delta\,\Phi(x/\Delta)\) with \(\Phi(t)=\int_0^t\psi\) and
   \(\psi(t)=[1+\exp(1/t-1/(1-t))]^{-1}\). The slope \(R'\) rises from 0 to 1
   with every derivative continuous.
4. **Flat exterior.** Beyond \(|\ell|=6.5\), \(R=|\ell|-L_b-\Delta/2+R_b\) with
   unit lapse, zero shift and unit radial metric: Minkowski space in spherical
   coordinates, an exact vacuum.

The service metric keeps the complete beta075 program: catch and rematch,
matched-hold release, trailing-edge rematch sleeve, compact handoff, packet-local
radial support, support-shell overlay, lapse cushion, standing stretch and its
decompression. Packet norms, radial null speeds, the carrying flow and the
service schedule depend only on \((\alpha,\beta,\gamma_{\ell\ell})\). The
time-dependent angular jacket and the receiver's angular flange acted only
through \(\gamma_{\Omega\Omega}\); the static track radius replaces both. The end
transitions exist because the reduced spherical model gives the two-sided
track two asymptotic ends; their consequences are quantified below.

### C∞ primitives

The C∞ candidate rebuilds the service metric with smooth joins throughout.
Each minimum-jerk and seventh-order polynomial step keeps its exact interior
profile on \([\delta,1-\delta]\) with \(\delta=0.1\) and is multiplied by
\(\psi(t/\delta)\) on the end fractions, so every derivative vanishes at both
ends. The support-shell Gaussian cap uses a monotone C∞ cap that is the identity
below 0.75, and \(|\ell|\) in the lapse shoulder and shell window becomes
\(\ell\tanh(\ell/0.02)\). With its legacy primitives selected, the same
reconstruction reproduces the frozen kernel's \(\alpha\), \(\beta\) and
\(\gamma_{\ell\ell}\) bitwise at 24,000 sampled points. With the C∞ primitives,
it differs from the regularity-repaired beta075 metric by at most 0.39% in
\(\alpha\), 1.3% in \(\gamma_{\ell\ell}\) and 0.0093 in \(\beta\) over 9,000
sampled points. Two candidates are evaluated: the constant-radius track
carrying the regularity-repaired service metric, and the constant-radius track
carrying the C∞ service metric, which is the proposed reference.

## Evaluator

The gate uses a warped-product evaluator that computes the Einstein tensor
from the Hessian of \(R\), its trace and the Gaussian curvature of the
two-dimensional metric:

\[
G_{ab}=-\frac{2}{R}\nabla_a\nabla_b R+g_{ab}\left[\frac{2}{R}\Box R+\frac{(\nabla R)^2-1}{R^2}\right],
\qquad
G^\theta{}_\theta=\frac{\Box R}{R}-K .
\]

It uses the same nested central differences as the frozen curvature kernel and
passes every tensor to the repaired, certified Hawking–Ellis classifier. Where
\(R\) is constant on the stencil, its derivatives are exact zeros and the radial
block is the exact string cloud. Validation covers the Ellis throat, a dust
cosmology with time-dependent radius, Painlevé–Gullstrand Schwarzschild with
nonzero shift, and agreement with the four-dimensional frozen kernel on the
beta075 geometry: at three witnesses the channel differences fall by a factor
of four per step halving and stay below \(5\times10^{-5}\) of the tensor scale.

## Gate results

Each geometry was evaluated with the warped-product evaluator at derivative
step 0.0025 on \(\sigma\in[-1.5,4]\), \(\ell\in[-8,8]\) with spacing 0.025, which
contains the whole service, the decompression and both end transitions.
Supplementary evaluations cover late static slices at \(\sigma=6,10,15\), static
holding controls at the eight phases of the original diagnostic, the exterior
out to \(|\ell|=96\), a derivative-refinement ladder and six design variations.

| Evaluation | Repaired beta075 | Constant-radius track, repaired service | Constant-radius track, C∞ service |
| --- | ---: | ---: | ---: |
| Map points, Type IV, uncertified | 141,661, 13,587, 0 | 141,661, 0, 0 | 141,661, 0, 0 |
| Minimum \(T(k_+,k_+)\,T(k_-,k_-)\) | \(-2.079\times10^{-3}\) at (1.875, −1.8) | 0 | 0 |
| Integrated imaginary eigenvalue | 0.0338 | 0 | 0 |
| Maximum \(|j_\ell|\) | 0.0230 | 0 | 0 |
| Late static slices: points, Type IV | 963, 0 | 963, 0 | 963, 0 |
| Ladder witnesses Type IV at the finest step | 34 of 129 | 0 of 129 | 0 of 129 |

The 5,128 holding controls of the C∞ track are Type I with zero current. The
exterior samples, at \(|\ell|\) from 6.6 to 96 and five service times, are vacuum
to \(5.5\times10^{-9}\) with both evaluators, the finite-difference rounding of a
linear areal radius. Every one of the 40,071 points in each of the six design
variations is Type I: end-transition widths 0.75 and 3.0, track half-lengths
4.5 and 6.0, and track radii 1.4 and 2.14. The transition width sets the peak
static radial deficit, −0.118, −0.058 and −0.028 for widths 0.75, 1.5 and 3.0,
while the integrated opening measure stays fixed.

The refinement ladder holds 129 points per geometry: the 13 witness positions
of the original diagnostic, the 28 static-enthalpy roots of the repair study
and 88 join samples at \(\ell=0\) and the cutoff, transition start, middle and
end (\(|\ell|=4,4.5,5,5.75,6.5\)) over the eight phases. Each point is evaluated
at derivative steps 0.0025, 0.00125, 0.000625 and 0.0003125 with both
evaluators. On the reference, the two evaluators assign identical classes at
every step. On the C∞ track, the warped-product evaluator certifies all 516
ladder rows as Type I. The demanded tensor converges at every join: successive
differences shrink by a factor of about 16 across two step halvings at
\(\ell=0\), 4 and 5.75; the values at \(|\ell|=5\) and 6.5 are exact to rounding;
and the two evaluators agree to \(2.6\times10^{-9}\) inside the end transition.

The frozen four-dimensional kernel returns the track's \(\rho+p_\ell\) and
\(j_\ell\) as truncation residuals that fall by a factor of four per step halving.
At 17 of the 129 witnesses the residual signs give a Type IV label at all four
steps, while the discriminant itself falls by a factor of 16.0 per halving
(median) to \(\sqrt{|\Delta_{\rm rad}|}\le7.9\times10^{-5}\) of the energy-density
scale at the finest step. At \(\ell=0\), ±4 and ±4.5 the residuals reach rounding
level and the classifier returns its indeterminate label (84 rows over the four
steps). These labels belong to a discriminant converging to zero; the
warped-product evaluator computes that zero exactly.

Against the handoff's deliverables:

| Deliverable | Result |
| --- | --- |
| Classification and discriminant maps | Complete demanded tensor for the three geometries, with the null-energy product shown in the [comparison figure](data/constant_radius_gate/classification_comparison.png). |
| Holding and active controls | The track is Type I in both; the reference reproduces the original active Type IV and static Type I split. |
| Convergence at fixed widths | Refinement ladder above, with convergent joins and exact track zeros. |
| Physical-width sweeps | Transition width, track half-length and track radius variations, all Type I. |
| Edge migration | No interface carries Type IV; the only radial null deficit lies in the static end transitions. |
| Outermost boundary | The end transitions join an exact vacuum with convergent curvature. |
| Layer-by-layer stack | Requires independent component tensors. The demanded tensor separates into a radial string cloud, an angular stress and the static end transitions, each diagonal. |

## Service checks

The candidates were replayed through the existing service audits on the
representative `rematch_w6_t1p5` grid at \(s=15\): 189 × 121 points over
\(\sigma\in[-1.5,15]\), \(\ell\in[-6,6]\). Each candidate ledger keeps the
reference grid with its stage, region and live-packet labels, and recomputes
every metric and demanded-source column from the candidate geometry. The audit
scripts run unchanged, with the reference trace table and schedule manifest
supplying the same bundle centers and service window to every ledger.

| Audit | beta075 reference | Constant-radius track, repaired service | Constant-radius track, C∞ service |
| --- | --- | --- | --- |
| Live packet points, positive packet norms, maximum norm | 238, 0, −9.935129 | 238, 0, −9.935129 | 238, 0, −9.935129 |
| Radial escape: expected, escaped, stalled traces | 1,696, 1,696, 0 | 1,696, 1,696, 0 | 1,696, 1,696, 0 |
| Entry-to-live-packet hits, service and carry stages | 0, 0 | 0, 0 | 0, 0 |
| Trace expansion: escaped of 235 | 224 | 224 | 224 |
| Traces entering a both-shrinking interval | 77 | 0 | 0 |
| Maximum integrated trapped-like strength | 0.203368 | 0 | 0 |
| Dense bundles from the reference centers: escaped rays | 136/136 | 136/136 | 136/136 |
| Caustic-like flags, ordering crossings | 0, 0 | 0, 0 | 0, 0 |
| Worst common \(\ell\)-width ratio, adjacent-gap ratio | 0.275792, 0.156579 | 0.275792, 0.156579 | 0.275780, 0.156558 |
| Service-time advantage: schedule, packet-coordinate proxy | 2.568962, 1.233312 | 2.568962, 1.233312 | 2.568952, 1.233306 |
| With request-triggered setup | 2.487278, 1.194097 | 2.487278, 1.194097 | 2.487269, 1.194091 |

Every service-relevant escape family reaches an exterior radial boundary in
all three ledgers: live packet, packet geometry, main carrier, support plant,
live branch band, and post-release packet and carrier seeds. The 136
boundary-seeded rays that end at \(\sigma=15\) are the same in each ledger.
The scheduled-probe replay, which selects its own seeds from each ledger,
records 223 of 235 escaping traces on the reference and 224 on both
candidates.

The pointwise both-null-focusing patch of the reference is absent from the
candidates: with the areal radius constant, both areal expansions vanish
along the whole track. The dense-bundle audit therefore finds no
both-shrinking centers of its own on the candidates. Tracing the reference
centers reproduces the reference bundle widths to five digits. When the audit
instead selects its centers without the both-shrinking requirement, all 136
rays escape with zero ordering crossings and a worst common \(\ell\)-width ratio
of 0.181; one of those eight bundles carries a caustic-like flag from its
areal-radius width criterion, because an initial radius spread of
\(2.2\times10^{-16}\) (one rounding unit on a constant radius) yields a
width ratio of zero.

Inside the live packet corridor the demanded source changes as follows:

| Live corridor, 238 points | beta075 reference | Constant-radius track, C∞ service |
| --- | ---: | ---: |
| Minimum radial null contraction \(T_{kk}\) | −0.656 | 0 |
| Maximum \(|j_\ell|\) | \(5.97\times10^{-3}\) | 0 |
| Minimum packet-comoving energy density | \(-1.33\times10^{-3}\) | +0.012992 |
| Share of the grid's negative radial null burden | 14.4% | 0% |
| Minimum \(\rho+p_\Omega\) | −0.0819 | −0.0741 |
| Maximum \(|p_\Omega|\) | 0.133 | 0.133 |

The passenger corridor carries no radial null-energy violation, and the
packet sees the positive string density \(1/(8\pi R_b^2)\). The angular channel
inside the corridor is essentially unchanged.

## Remaining null-energy requirements

### Along the track

Both radial null energies vanish identically along the track at every service
time, so radial null energy is saturated there: \(\rho=-p_\ell\). The angular null
energy is

\[
\rho+p_\Omega=\frac{1}{8\pi}\left(\frac{1}{R_b^2}-K\right),
\]

which turns negative wherever the Gaussian curvature of the service metric
exceeds \(1/R_b^2\approx0.33\). A budget run evaluated the C∞ track under five
decompression schedules on \(\sigma\in[-1.5,16]\), \(|\ell|<5\) at spacing 0.1.
Every sample is Type I with \(\rho+p_\ell\) and \(j_\ell\) exactly zero.

| Decompression schedule | Minimum \(\rho+p_\Omega\) at \((\sigma,\ell)\) | Track samples below zero | Integrated angular deficit | Live-corridor minimum | Packet-coordinate proxy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Current, \(\sigma=-0.4\) to 2.6 | −0.270 at (1.6, 2.1) | 2.53% | 0.373 | −0.065 | 1.2368 |
| After the live window, same rate | −0.179 at (4.7, 0.0) | 2.52% | 0.311 | −0.052 | 1.1989 |
| After the live window, half rate | −0.052 at (−0.6, −0.5) | 3.42% | 0.118 | −0.052 | 1.1989 |
| After the live window, quarter rate | −0.052 at (−0.6, −0.5) | 1.19% | 0.0063 | −0.052 | 1.1989 |
| Removed | −0.052 at (−0.6, −0.5) | 0.14% | 0.0037 | −0.052 | 1.1989 |

The decompression relaxes a radial stretch of about 600 and produces the
largest curvature of the service metric. As scheduled, it overlaps catch,
carry and release, with its steepest rate at \(\sigma=1.1\). A reset after the
live window at a quarter of the rate lowers the integrated angular deficit by
98%; the catch-phase support-shell pulse and packet windows then set the floor
at −0.052. The design record places decompression in the service cycle as the
reset of the standing support before reuse: "relax/decompress the throat
support, reset the plant." The service metric runs independently of that
timing. Moving the reset after the live window keeps the schedule-factor
advantage at 2.568966 and changes the packet-coordinate proxy from 1.2368 to
1.1989 (both evaluated along \(\ell=\sigma\) over the scheduled service window).
The [reset comparison](RESET_SCHEDULE_OPTIONS.md) extends this table with
decompression fronts trailing the packet and with extended carries, and it
favours a front at half the current local rate.

### At the end transitions

The end transitions are static and ultrastatic, so both radial null energies
equal \(-R''/(4\pi R)\): minimum −0.058 for transition width 1.5, with energy
density down to −0.049 and angular null energy down to −0.021. The opening
measure \(4\pi\int R\max[-(\rho+p_\ell),0]\,d\ell\) is 2.000001 on the
\(\sigma=15\) slice, one per end. For any static region with lapse \(A\),

\[
\left(\frac{R'}{A}\right)'=-\frac{4\pi R}{A}(\rho+p_\ell),
\]

so widening a uniform track from \(R'=0\) to \(R'/A=1\) requires an integrated
radial null deficit of at least one per end, a uniform continuation requires
none, and a closing cap decreases \(R'/A\) with non-negative \(\rho+p_\ell\). The
end transitions follow from the reduced model's two asymptotic ends. How the
track terminates, whether by widening into asymptotic regions, continuing,
closing, or through a reduction suited to a track within one space, decides
this requirement. The [axial track](AXIAL_TRACK.md) realizes the one-space
reduction exactly. Its exterior is Minkowski with no end transitions, and
under the transplanted service its tube wall carries a Type IV layer from the
carry shift's transverse shear and the decompressing stretch.

### Source structure

- The radial block along the track is an exact constant-flux radial string
  cloud, \(\rho R_b^2=1/(8\pi)\), invariant under boosts along the track: the
  \(S_0\) role, now exact.
- The angular stress \(p_\Omega=-K/(8\pi)\) carries the service dynamics. Its
  deficit is the dynamic exotic requirement, set mainly by the reset schedule.
- The end-transition deficit is static, so static source calculations apply to
  it directly, including the
  [semiclassical opening comparison](SEMICLASSICAL_JOINT_INVESTIGATION.md),
  which supplies about \(5\times10^{-6}\) of its requirement at the recorded
  normalization.
- The radial current vanishes identically. The beta075 endpoint heat/current
  medium, its current regulator, the complementary exchange-current fit and
  the transport and energy estimates built on that current characterize the
  archived beta075 reference; this geometry assigns them no radial-current
  duty.
- The live corridor carries zero radial null energy and a positive
  packet-frame energy density.

### Next construction

1. Confirm the reset schedule. The reset comparison favours the half-rate
   trailing front: an 80% lower angular deficit and the −0.052 catch floor for
   a 4.1-unit velocity-reading delay.
2. Choose the termination path. The two-ended track keeps its static
   end-transition deficit. A one-space track needs a service revision with a
   standing stretch and lapse envelopes around every shear layer.
3. Specify component tensors for the string-cloud radial block, the angular
   stress sector and any end-transition source, and classify the
   layer-by-layer stack.
4. Resume the C1 finite-module work on this geometry: each module then holds a
   uniform radial string cloud with angular stress, and the module ends become
   the termination problem.

## Reproduction and evidence

Run from the repository root. Each script distributes independent evaluations
over worker processes with single-threaded BLAS; results are independent of
the worker count.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
MPLCONFIGDIR=/tmp/active-rail-matplotlib \
python toolkit/adm_harness_cli/scripts/run_type_iv_attribution.py --workers 6
MPLCONFIGDIR=/tmp/active-rail-matplotlib \
python toolkit/adm_harness_cli/scripts/run_constant_radius_gate.py --workers 6
python toolkit/adm_harness_cli/scripts/run_constant_radius_service_checks.py --workers 6
python toolkit/adm_harness_cli/scripts/run_track_null_energy_budget.py --workers 6
```

The service replay reads the local `rematch_w6_t1p5` point ledger and the
scheduled-probe seed table under `toolkit/adm_harness_cli/runs/`, verifies the
ledger's recorded SHA-256, and writes its audit outputs to
`toolkit/adm_harness_cli/runs/constant_radius_service/`; the retained comparison
tables and hashes are in the repository. The full harness suite passes with
both harness directories on the import path:

```bash
PYTHONPATH=toolkit/adm_harness_cli:toolkit/adm_harness_cli/scripts \
python -m pytest -q -p no:cacheprovider toolkit/adm_harness_cli/tests
```

- [Attribution controls](data/type_iv_attribution/summary.csv) and
  [point data](data/type_iv_attribution/attribution.csv.gz)
- [Gate summary](data/constant_radius_gate/summary.csv),
  [manifest](data/constant_radius_gate/manifest.json), classification maps
  (`map_*.npz`), [refinement ladder](data/constant_radius_gate/refinement_ladder.csv.gz),
  [holding controls](data/constant_radius_gate/holding_controls.csv.gz),
  [late static slices](data/constant_radius_gate/late_static_slices.csv.gz) and
  [exterior samples](data/constant_radius_gate/exterior_vacuum.csv.gz)
- Figures: [classification comparison](data/constant_radius_gate/classification_comparison.png),
  [angular channel](data/constant_radius_gate/angular_channel.png),
  [static profile and body refinement](data/constant_radius_gate/static_profile_and_body_refinement.png)
- [Service comparison](data/constant_radius_service/comparison_wide.csv) and
  [service manifest](data/constant_radius_service/manifest.json)
- [Null-energy budget by decompression schedule](data/track_null_energy_budget/summary.csv),
  [samples](data/track_null_energy_budget/samples.csv.gz) and
  [manifest](data/track_null_energy_budget/manifest.json)
- Implementation: [constant_radius_track.py](../toolkit/adm_harness_cli/adm_harness/constant_radius_track.py),
  [warped_product.py](../toolkit/adm_harness_cli/adm_harness/warped_product.py),
  with tests in `toolkit/adm_harness_cli/tests/test_constant_radius_track.py` and
  `test_warped_product.py`.
