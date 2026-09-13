# Passive photon exchange in the radial-cell assembly

The first tested location admits a refined curved-space allocation with
counted hot-bank, actual fluid, and photon donor comparisons within the
original stress budget. Joint bank temperatures add a large required
contrast between the hot and cold stores. At the second location, selective
cost comparisons isolate an observed solver restriction at electromagnetic
guide comparison `0.5` in the hot-bank routing gate. That gate passes at
guide comparison `0.8`. Earlier sampled
allocations at both locations remain useful energy and tensor histories.
The phase, balanced radiation, existing pressure-link fluid, and separated
receiver banks retain distinct duties throughout these comparisons.

This analysis continues the
[joint pressure-link allocation](VIRTUAL_RADIAL_CELL_PRESSURE_LINK_REALLOCATION.md).
It concerns material cells in the backing of the scheduled active rail.
The moving protected packet, endpoint work delivery, capacitor, and
standing-support assignments retain their existing roles.

## Counted curved-space histories

The first finite allocation uses the complete 515-time grid and a native
interior-point state checked against all original equations and bounds.
Disabling presolve recovers a valid primal with maximum violation
`2.18e-9`; its inventory optimum remains uncertified. The second finite
allocation has an accepted optimum on the same time grid. Both supply
actual midpoint stress targets from the registered geometry.

Independent replay preserves the phase history, explicitly repairs
conversion increments by less than `2.74e-10`, reconstructs nonnegative
heat-transfer rates, and integrates the radiation energy against the
changing metric. Small constant initial inventories cover the refined
thermal donor bounds. The full stress of this preparation is included.

| Curved replay | First location, `x=-2` | Second location, `x=-1.975` |
|---|---:|---:|
| Spatial positions / time nodes | 32 / 2,057 | 36 / 1,543 |
| Minimum full density margin | `1.01450e-4` | `3.98277e-5` |
| Largest added fluid density | `7.62e-8` | `5.87e-8` |
| Largest added receiver density | `2.10e-8` | `1.16e-8` |
| Largest added balanced radiation density | `1.04596e-4` | `0` |
| Minimum retained fluid temperature parameter | `0.01` | `0.01` |
| Aggregate energy-panel residual | `5.37e-15` | `8.88e-15` |

The [first replay](data/virtual_cell_thermal_replay_first_floor001_contacts_refined/summary.json)
and [second replay](data/virtual_cell_thermal_replay_floor001_contacts_refined/summary.json)
pass the sampled tensor, wave population, receiver capacity, separately
rated bank, donor, temperature, conservation, and quadrature checks. The
initial 0.2% numerical reserve is partly consumed in both cases. At the
first location, the added radiation brings one directional population to
its zero boundary; at the second, the minimum directional margin remains
`6.22e-6`. The preceding first-location resolution has density margin
`1.02761e-4`, while the preceding second-location resolution has margin
`5.44436e-5`. These histories establish the stated sampled budgets while
retaining physical contact and force closure as separate requirements.

## The complementary photons carry a separate power duty

Let `D=ell R^2`, `K=D^(1/3)U`, and `Z=H+C`, where `U` is the existing
fluid thermal inventory and `H,C` are the hot and cold bank energies.
The phase and its explicit drive, useful-return, and heat-return beams
balance their combined proper power. The remaining photons therefore
require

```
P_counter = P_fluid,0 + P_receiver,0 - P_fluid - P_receiver
          = P_fixed + q_R - P_fluid,
q_R       = L_0 - P_receiver.
```

The old fluid and receiver sources appear once. The retained support
supplies `P_fixed` to the fluid and carries its opposite reaction.
Consequently, the complementary-photon duty reflects the redistribution
of already counted energy during the changing stress demand. It can be
much larger than the converter losses `L_0`.

For fixed gapless one-dimensional photon channels, the conditional grey
equilibrium law is `c_eq=a_2 Theta_f^2/R^2`. The temperature-squared
single-mode law follows the channel thermodynamics discussed by
[Fohrmann et al.](https://doi.org/10.1364/OE.23.027672). Here `c` is the
full complementary density, including both directions; the separately
prescribed work and heat beams retain their own occupation and source.
Positive absorption/emission coefficients require

```
max_(P_counter>0) c R^2/Theta_f^2 < a_2
a_2 < min_(P_counter<0) c R^2/Theta_f^2.
```

At the second location, the [refined grey-contact audit](data/virtual_cell_guided_contact_floor001_refined/summary.json)
requires `a_2>18749.7` and `a_2<0.0185387`; every sampled position has an
empty interval. The preceding resolution gives the same conflict. The
fluid heats sharply around the stress transition and cools later, while
the required photon power changes direction. A single fixed grey
contact to that fluid cannot supply this sequence. The moment ledger
alone does not specify spectral occupations or a more general optical
coupling.

The [first-location contact audit](data/virtual_cell_guided_contact_first_floor001/summary.json)
also has an empty common interval, requiring `a_2>4747.87` and
`a_2<0.000238302`. Its separate receiver-bank temperature coefficients
remain admissible. The grey contact failure therefore occurs in both
tested local histories.

## Routing through the existing hot and cold banks

Use proper-label powers `p=D P_counter`, `f=D P_fluid`, and
`s=D P_fixed`. Let `q_h,q_c` be the original nonnegative bank rates.
The original power identity is

```
f = q_h - q_c + s - p.
```

Routing `e=max(p,0)` from the hot bank into the photons and
`a=max(-p,0)` from the photons into the cold bank leaves fluid contacts
`q_h-e` and `q_c-a`. It preserves every stored-energy history and the
fluid power precisely when `-q_c<=p<=q_h`. Adding simultaneous emission
and absorption increases both demands and cannot repair a negative
remaining branch.

The [refined bank-routing audit](data/virtual_cell_bank_routing_floor001_refined/summary.json)
admits the mixed-temperature channel interval
`1.33427<a_2<9.70902`, using the already selected bank temperatures.
However, its required hot and cold rates exceed the available traffic
by `214.419` and `300.765` in proper-label units. The hot witness occurs
at `t=0.4982113`; the cold witness occurs at `t=0.5017904`. These are
large physical deficits relative to the declared numerical tolerances.

Capacity also rejects rerouting this unchanged power history at turnover
10. The entire receiver rating is about `0.2555`, permitting hot
withdrawal at most about `2.555` if all its rating served the hot bank.
The required positive power instead demands hot inventory about
`21.44`, roughly 84 times the entire rating. This conclusion uses the
counted energy and rate allowance directly. It is independent of the
original hot/cold partition and its temperature coefficients.

## Total stored heat imposes a rate-independent bound

The continuous power source permits an independent storage calculation.
Its coordinate-time energy rate per material label is

```
S = N D P_counter
  = U_0,t + U_0 (log D)_t/3 + Z_0,t - Z_t - K_t/D^(1/3).
```

The reconstructed receiver derivative is
`Z_t=L_coord-N q_h+N q_c`. Integrating `max(S,0)` and `max(-S,0)`
separately gives cumulative photon emission `E_+` and absorption `E_-`.
The original converter supplies cumulative heat `L_cum`. Even allowing
all its heat to serve the photon duty and assigning zero initial cold
inventory, necessary bank ratings obey

```
H_initial >= max_t {0, E_+(t)-L_cum(t)},
C_cold,rated >= E_-(t_final),
C_hot,rated + C_cold,rated <= C_receiver,rated.
```

The [first](data/virtual_cell_bank_capacity_first_floor001/summary.json)
and [second](data/virtual_cell_bank_capacity_floor001_refined/summary.json)
integrated screens give the following worst capacity witnesses:

| Required stored energy | First location | Second location |
|---|---:|---:|
| Initial hot energy, favorable lower bound | `4.76495` | `6.93567` |
| Cold-bank rating, favorable lower bound | `4.80065` | `6.82266` |
| Combined separate-rating lower bound | `9.56560` | `13.75832` |
| Original combined receiver rating | `0.26812` | `0.25523` |
| Required / original combined rating | `35.68` | `53.91` |

The cold-bank requirement alone exceeds the entire original rating by
about 18 and 27 times. Thus reassigning the two bank ratings or increasing
contact speed leaves a storage deficit for these fixed histories.
Meanwhile, the maximum absolute final net photon transfer across the
sampled positions is only `0.04446` and `0.20007`, respectively. Net energy
therefore understates the opposed heat transfers by a large amount.

The source is integrated on the exact registered geometry with every
replay, control, contact, baseline, and metric knot included. Gauss-4 and
Gauss-8 cumulative energies differ by at most `1.13e-9` and `1.84e-9`.
These numerical comparisons are small relative to the measured capacity
deficits. They retain the stated sampled and quadrature scope. Cold-bank
export is absent in this local route; adding export would require its
own counted transport and reciprocal power terms.

## A joint linear test of the bank route

Changing the fluid and receiver histories changes `P_counter`, so the
unchanged-history rejection leaves a specific joint test. Within a
frozen panel, define `chi=M_m/D_m=ell_m`,
`psi=M_m/D_m^(4/3)`, and `F` as the sum of the original weighted fluid
and receiver source panels. With converter-loss panel energy `L`,

```
E_counter = (F - psi DeltaK - chi DeltaZ)/chi,
Q_hot     = L - DeltaH,
Q_cold    = DeltaZ - DeltaH.
```

The necessary routing interval `-Q_cold<=E_counter<=Q_hot` is exactly
the pair of linear inequalities

```
 psi DeltaK + chi DeltaH              <= F,
-psi DeltaK - chi DeltaZ + chi DeltaH <= chi L - F.
```

Thus phase, radiation, fluid, and bank inventories can be reallocated
under the existing stress and energy constraints with two extra rows
per panel. A necessary relaxation retains the original bank capacities,
hot donor limit, and nonnegative bank directions while leaving the
cold photon donor and optical laws open. The previous bound treating
all cold-bank input as fluid heat is relaxed because the photons now
provide part of that input. Its future physical bound applies to the
remaining fluid branch. This test addresses passive bank routing with
the original component resources; its feasibility alone supplies
neither an opacity law nor the reciprocal momentum and entropy closure.

The full 515-time, eight-position joint relaxation retains a shared
phase and the causal work-wave envelopes. Its
[interior-point comparison](data/virtual_cell_fluid_receiver_bank_counter_relaxation/summary.json)
returns an unfinished candidate whose largest original constraint
violation is `0.00156`; independent verification rejects it. A
[dual-simplex comparison](data/virtual_cell_fluid_receiver_bank_counter_dual/summary.json)
reaches its 180-second solver limit. Both outcomes leave joint
feasibility unresolved. The integrated storage bounds above apply to
the two resolved histories, while the changing joint histories require
their own feasibility result.

An additional favorable local relaxation isolates this question from
the large transport solve. It releases shared phase coherence, explicit
work-wave constraints, guide and interface costs, and contact-rate
bounds while retaining the local stress, energy, and bank-routing
equations. Its full physical budget and optional zero thermal floor
provide a bounded check of the underlying storage requirement.

The [zero-floor](data/virtual_cell_local_bank_floor0/summary.json) and
[warm-fluid](data/virtual_cell_local_bank_floor001/summary.json) local
comparisons both pass at both locations. Each problem has 2,577 variables,
514 energy equalities, and 7,203 inequalities on the complete 515-time
grid. Ordinary HiGHS solves each in less than one second; independent
verification of the archived original matrices and bounds gives maximum
violations between `6.95e-15` and `2.85e-14`. The warm comparison retains
the previously selected temperature floor `Theta_f=0.01`.

Thus the original local energy, stress, and receiver-capacity budgets
admit directional bank-power allocation when the omitted transport and contact
conditions are free. The much larger storage requirements of the two
earlier resolved histories depend on their particular allocation. These
local witnesses use the full receiver rating, and the zero-floor
witnesses expose the remaining physical freedoms directly: one drains
its hot bank to zero within a single panel, while another absorbs
photons during a panel with zero balanced radiation at both endpoints.
Finite donor rates and explicit work-wave populations therefore provide
the next discriminating constraints. The local result leaves the finite
cell assembly and its physical contacts to those stronger tests.

Restoring the original hot-bank donor comparison also
[passes locally](data/virtual_cell_local_bank_hot10/summary.json) at both
locations with the warm floor. Maximum original-row violations are
`3.56e-15` and `1.30e-14`. Thus finite hot withdrawal and initial preparation
fit the original local resource budgets when the histories are optimized
together.

The [four-position finite-pair comparison](data/virtual_cell_bank_transport_n4_fullbudget/summary.json)
restores shared phase, explicit causal work waves, their population
envelopes, the existing guide and interface charges, and the hot-donor
bound. The first location supplies an independently verified primal with
maximum constraint violation `2.82e-9`; inventory optimality remains
uncertified. At the second location the interior-point candidate has
violation `0.00122`, and a
[dual-simplex comparison](data/virtual_cell_bank_transport_n4_second_dual/summary.json)
also leaves feasibility unresolved. The original full physical budget
is used in these comparisons.

The first-location [curved replay](data/virtual_cell_bank_transport_n4_replay/summary.json)
applies the preceding conservative contact preparation, which assigns
all cold-bank receipts to the fluid. That preparation adds fluid density
`0.00223212` and produces a density shortfall `0.00224214`. Photon-supplied
cold receipts require their own partition before this comparison can
decide the bank route. Independently, the finite-pair history still has
a true remaining-fluid rate deficit even after allowing additional
hot-to-photon-to-cold circulation. This identifies a specific missing
donor constraint for the next joint allocation.

## Separating fluid cooling from photon absorption

The banks may supply photon emission and absorb photons simultaneously.
For a given counter-photon panel energy `E`, choose absorbed heat `a` and
emitted heat `e=E+a`. The remaining fluid contacts are

```
fluid heating = Q_hot - E - a,
fluid cooling = Q_cold - a.
```

All four branches are nonnegative precisely when
`max(0,-E)<=a<=min(Q_cold,Q_hot-E)`. A fluid donor allowance
`d_f=kappa_f Delta_tau min(U_start,U_end)` and an optional photon
allowance `d_gamma=kappa_gamma Delta_tau min(D_start c_start,D_end c_end)`
give the complete endpoint comparison

```
max(0, -E, Q_cold-d_f) <= a <= min(Q_cold, Q_hot-E, d_gamma).
```

Here the photon allowance is omitted when its rate remains unspecified.
Every transfer retains its original bank inventory and its opposite
component power. Extra photon circulation reallocates existing bank
traffic; its absorption and emission still require a physical optical
law.

Define the fluid's required net heat after the retained support as
`X=(psi DeltaK-F)/chi+L`. The minimum possible fluid cooling is
`max(-X,0)`. Consequently, the exact necessary fluid-donor rows are

```
-psi DeltaK - chi kappa_f Delta_tau K_endpoint/D_endpoint^(1/3)
    <= chi L - F.
```

These two endpoint rows allow photon-supplied cold receipts while
retaining the fluid's own cooling limit. The declared comparison
`kappa_f=10` is measured in the project's proper-time unit; its physical
realization depends on the eventual scale and contact geometry.

The [independent donor audit](data/virtual_cell_bank_donor_baseline/summary.json)
finds ten panels where the first finite-pair history exceeds that fluid
allowance even with unrestricted photon circulation. The largest witness
is at `x=-1.9998125`, from `t=1.2071973` to `1.2097070`. Its unavoidable
fluid cooling is `0.00366990`, while the endpoint allowance is
`0.000886210`. The necessary turnover for that history reaches `41.4112`.
At this witness, the hot bank already directs all its withdrawal to the
photons, leaving no additional circulation that could reduce fluid cooling.
The separately rated bank capacity still has margin above `0.2525` in
each sampled position.

The least photon absorption compatible with the existing bank and fluid
duties reaches an endpoint turnover requirement `548.011`. At its witness,
the proper cell crossing time is `ell Delta_x_cell=0.0014420–0.0014464`,
using `Delta_x_cell=0.00025`. Thus the product of the required photon rate
and a cell crossing time is about `0.7914`; the corresponding exchange
time is about 1.26 crossing times. Under a homogeneous pure-absorption
interpretation, that product is a nominal optical depth, giving about
55% absorption in one crossing. The analogous fluid exchange takes
about thirty crossing times. These conversions put the rate comparisons
on the existing cell scale; a microscopic absorption or fluid transport
law remains to be specified.

Such an optical response must distinguish the complementary photons from
the prescribed work and heat-return streams. Applying the same absorption
to those streams would change their delivered energy and momentum. The
registered transport assignments therefore require selective coupling and
its associated guide stress, recoil, and thermal balance in one material
model.

## Joint allocation with the actual fluid donor

The fixed-budget solve can seek feasibility directly by assigning a zero
objective. This preserves every physical matrix row and variable bound
while removing the separate inventory-minimization requirement. Original
constraints are verified independently for both ordinary and native solver
results; optimality of a zero objective carries no inventory-optimality
claim.

With the remaining-fluid donor rows included, the
[first-location comparison](data/virtual_cell_bank_fluid_donor_first/summary.json)
returns an optimal feasible state with maximum original constraint
violation `7.66e-16`. It retains the 515-time grid, four spatial positions,
shared phase, causal work-wave populations, the warm-fluid floor `0.01`,
both declared fluid and hot-bank turnover comparisons at 10, the original
separate bank capacities, and the 0.2% density reserve. The actual fluid
donor constraint therefore fits this finite-pair model through joint
redistribution of the existing components.

Its [independent donor audit](data/virtual_cell_bank_fluid_donor_first_rate10_audit/summary.json)
passes the hot, fluid, and photon endpoint comparisons at turnover 10.
The required photon turnover peaks at `3.10159`; the minimum necessary
fluid-cooling duty is zero throughout this selected finite history.
The chosen allocation retains hot-donor margin `0.000302443` and separate
bank-capacity margin `0.000410371`. The earlier comparison at photon
turnover 1000 is archived separately; the measured requirement supports
the original comparison value 10.

The [curved replay](data/virtual_cell_bank_fluid_donor_first_replay/summary.json)
also passes, with eight spatial positions and 1,029 time nodes. It retains
minimum full density margin `0.000134321`, counterstream margin
`0.0000527220`, and the original reserved density budget. It requires no
additional initial fluid, receiver, or radiation inventory. The reconstructed
bank branches remain nonnegative, and the actual fluid temperature parameter
stays above `0.02618`. Aggregate energy residual is `4.42e-15`, and the
Gauss-4/Gauss-8 panel difference is `2.00e-14`. Thus the first location now
supplies a counted curved allocation with actual fluid donor and bank
direction checks, followed by a separate finite-photon donor comparison.

At the second location, an otherwise unchanged
[zero-objective comparison](data/virtual_cell_bank_zero_objective_second/summary.json)
returns a native infeasibility status for the gate with hot turnover 10
and the full physical budget. It supplies no independently checked
infeasibility certificate. This is stronger numerical information than
the preceding unfinished solves, while the status alone leaves a
certificate and the dependence on the chosen rate comparison to further
checks.

Increasing the hot-bank turnover to 100 in an otherwise matched
[second-location comparison](data/virtual_cell_bank_zero_objective_second_rate100/summary.json)
also returns native infeasibility. The comparisons below isolate the
dependence on common phase, wave transport, and mechanical guide costs.

For comparison, applying the actual-fluid reconstruction to the older
first-location history still
[fails](data/virtual_cell_bank_transport_n4_actual_fluid_replay/summary.json):
the required preparation produces density shortfall `0.00224457`, and
the integrated bank-direction deficit is `0.0000726735`. Its positive-part
quadratures differ by `4.94e-9`, above the declared numerical-integrity
tolerance. The successful joint allocation above changes the history
itself, while retaining the original component budgets.

## Refinement and joint bank temperatures

The [finer first-location replay](data/virtual_cell_bank_fluid_donor_first_replay_refined/summary.json)
uses 16 spatial positions and 2,057 time nodes. Its minimum full density
margin is `0.000133322`, its minimum directional photon margin is
`0.0000502039`, and the original 0.2% reserve remains available. Added
fluid, bank, and radiation preparation inventories remain zero. Energy
residual is `4.44e-15`, and the Gauss-4/Gauss-8 difference is `2.71e-15`.
Thus the stronger first allocation preserves its sampled conservation,
stress, and donor margins under this refinement. A
[further replay](data/virtual_cell_bank_fluid_donor_first_replay_factor8/summary.json)
with 32 spatial positions and 4,113 time nodes also passes. Minimum density
margin is `0.000132823`, minimum directional photon margin is `0.0000489450`,
and all additional preparation inventories remain zero. The original
reserve is retained. Energy residual is `4.50e-15`, and the Gauss-4/Gauss-8
difference is `1.11e-15`.

The actual reconstructed branches separately specify hot-bank heat to
fluid and photons, and cold-bank receipt from fluid and photons. A joint
temperature comparison uses

```
Theta_h^4 = a_h H,       Theta_c^4 = a_c C,
c_eq = a_2 Theta^2/R^2,
a_h > L_f,              a_c < U_f,
a_h a_2^2 > L_g,        a_c a_2^2 < U_g.
```

Each limit is taken over the corresponding active heat branch. In this
first history the fluid receives heat throughout, so its cold-bank upper
bound is unbounded. Both photon branches remain active. The
[refined midpoint comparison](data/virtual_cell_bank_fluid_donor_first_joint_temperature/summary.json)
admits finite positive coefficients and reproduces the prescribed photon
power to `4.07e-20`. Its limits are `L_f=0.0297049`, `L_g=354.507`, and
`U_g=0.000115540`. With equal bank caloric normalization, the infimum of
the cold/hot proper-volume ratio is `3.06826e6`; the illustrative strict
selection uses four times that ratio. These coefficients establish sampled
temperature order and permit positive fitted transfer rates. Their
constitutive realization requires a material
opacity law, selective coupling, force and entropy evolution, and bank
packing.

The [coarser comparison](data/virtual_cell_bank_fluid_donor_first_joint_temperature_coarse/summary.json)
gives volume-ratio infimum `1.53248e6`. The near doubling arises mainly
from a smaller cold-photon temperature upper bound near `t=0.0449`,
where the complementary photon population becomes small while absorption
continues. Both midpoint-only coefficient selections fail the tighter
temperature bound at a known time knot. The endpoint-aware comparisons
below correct the selection while preserving these original diagnostics.
The archived [single-fluid grey comparison](data/virtual_cell_bank_fluid_donor_first_guided/summary.json)
also fails its common-coefficient interval. The
[separate fluid/bank comparison](data/virtual_cell_bank_fluid_donor_first_temperatures/summary.json)
omits the tighter joint photon temperature requirement.

The corrected audit imposes each active panel's temperature order at both
one-sided endpoints, its midpoint, and its quarter points. The
[factor-two comparison](data/virtual_cell_bank_fluid_donor_first_joint_temperature_endpoints_coarse/summary.json)
and [factor-four comparison](data/virtual_cell_bank_fluid_donor_first_joint_temperature_endpoints/summary.json)
both pass this sampled shape test. Their volume-contrast infima are
`7.20040e6` and `7.95009e6`, a change of approximately 10.4%. The limiting
knot is `t=0.04517578125`, where the finer history retains complementary
density `5.02059e-5` and cold-bank energy `0.00386679`. The additional
quarter samples give looser bounds. This identifies a positive minimum
missed by the earlier midpoint-only audit; a continuous-time temperature
certificate remains a further requirement.

The [factor-eight temperature comparison](data/virtual_cell_bank_fluid_donor_first_joint_temperature_endpoints_factor8/summary.json)
also passes. Its contrast infimum is `8.36587e6`, a further change of
5.23%, and its illustrative strict selection uses `3.34635e7`. The
limiting knot remains fixed, with positive photon density `4.89460e-5`.
The two successive changes in that density approximately halve. These
three resolutions support a positive limiting population while leaving a
continuous-time bound open. The volume contrast applies to this selected
energy history and the stated bank caloric laws; different bank responses
or gross heat allocations require their own conserved stress and contact
calculation.

The corrected audits also check the actual reconstructed gross heat
branches against endpoint donor energies. At factor four the photon-cold
turnover requirement peaks at `4.40113`, and total hot-bank withdrawal
peaks at `6.09050`; both fit the declared comparison value 10. Fluid-cold
withdrawal remains zero. At factor eight the corresponding maxima are
`4.51406` and `6.09061`, with fluid-cold withdrawal still absent and every
active donor retaining positive energy. The selected grey contact coefficients divide
heat by a temperature-dependent population gap, while these donor bounds
divide heat by the full available donor inventory. Consequently the
declared donor comparison and a microscopic opacity bound represent
different requirements.

## Isolating the second-location mechanical burden

A [four-position local comparison](data/virtual_cell_shared_phase_local_second/summary.json)
retains the complete 515-time history, exact local and midpoint targets,
original bank capacities, hot turnover 10, warm-fluid floor `0.01`, and a
single phase history shared by all positions. It passes the original
assembled matrix and bounds with maximum violation `4.23e-11`. Each
individual local block also passes. Coordinating those inventories through
a common phase is therefore feasible in this relaxation.

The [transport comparison with guide and interface costs removed](data/virtual_cell_bank_transport_only_second/summary.json)
restores explicit wave transport, wave population floors, and within-panel
wave envelopes. It also passes, with original maximum violation
`2.01e-13`. This favorable comparison uses the full physical budget and
the same hot-bank routing gate as the second-location infeasibility runs;
it leaves actual remaining-fluid and photon donor construction open.
Only the guide drift charge and interface tension coefficient are removed.
Their removal changes the observed solver outcome, isolating its dependence
on the mechanical costs of carrying and attaching the waves.
The successful relaxation supplies a diagnostic history whose missing
mechanical costs still require a counted construction.

Selective reoptimization distinguishes those two costs. With the original
interface allowance retained and the guide charge removed, the
[second cell passes](data/virtual_cell_bank_interface_only_second/summary.json)
with maximum original constraint violation `8.72e-16`. With the guide
comparison `0.5` retained and only the interface cost removed, the
[solver reports infeasibility](data/virtual_cell_bank_guide_only_second/summary.json).
As in the full-cost case, the latter status has no independently checked
infeasibility certificate. The selective outcomes identify the prescribed
guide allowance as the relevant restriction in these solver comparisons; the interface
allowance can coexist with the other retained duties in a relaxed guide
construction.

The [electromagnetic guide comparison](POYNTING_WORK_DELIVERY.md) uses
`g(v_d)=(v_d^(-2)-1)/2`, with required guide energy at least `g` times
the explicit travelling-wave energy. In the current decomposition its
stress constraint is

```
s/2 + rho_f + z + 3 g(v_d) (u_abs + u_rec) <= rho - p_r + p_t.
```

Here `s=A/R^2`, `rho_f` is the actual reopened thermal fluid density,
`z` is stored receiver energy density, and the right side is the credited
target. The existing core and auxiliary radial fields supply the guide
allowance. Raising the electromagnetic drift comparison from `0.5` to
`0.6` changes `g` from `1.5` to `0.888889`; comparison `0.8` gives
`g=0.28125`. These choices permit weaker magnetic guidance and a larger
local `E/B` drift. They leave prescribed rail bulk motion and causal wave
propagation fixed. Current-carrier inertia and a complete material guide
remain construction duties.

The [guide-0.6 comparison](data/virtual_cell_bank_guide06_second/summary.json)
returns native infeasibility. The otherwise matched
[guide-0.8 comparison](data/virtual_cell_bank_guide08_second/summary.json)
passes while retaining the original interface allowance. This brackets a
useful guide sensitivity inside the tested finite model. The successful
necessary routing gate still requires actual fluid and photon donor checks,
the restored numerical reserve, and an independent curved replay.

Adding the actual remaining-fluid donor rows and restoring the original
0.2% reserve gives feasible finite allocations at both
[guide comparison 0.7](data/virtual_cell_bank_fluid_donor_guide07_second/summary.json)
and [guide comparison 0.8](data/virtual_cell_bank_fluid_donor_guide08_second/summary.json).
Their maximum original constraint violations are `8.00e-16` and
`1.88e-14`, respectively. Both retain the original interface allowance,
separate bank ratings, hot and fluid turnover comparisons at 10, and warm
fluid floor `0.01`.

The [independent guide-0.7 replay](data/virtual_cell_bank_fluid_donor_guide07_second_replay/summary.json)
fails the full stress budget at factors two and four. Density shortfalls
are `2.16991e-5` and `8.29736e-5`, respectively. Bank directions, donor
bounds, ratings, and positive populations pass; additional preparation
inventories remain zero. The positive-part contact quadratures differ by
`4.63e-9` and `1.71e-9`, above the numerical-integrity tolerance. These
results retain the finite allocation while rejecting its curved replay
as a supplied stress construction.

The [guide-0.8 replay](data/virtual_cell_bank_fluid_donor_guide08_second_replay/summary.json)
also fails, with shortfalls `3.60416e-6` and `6.52422e-5` at factors two
and four. At guide `0.7`, the worst factor-four witness is
`t=0.04517578125, x=-1.974984375`. Its active failure is the
guide-independent facet

```
3 W + 2 rho_f + z - s <= rho + 2 p_r + p_t.
```

The additional guide demand is zero at that witness. Relative to the
nearest original right-cell sample, the parent control has density margin
`1.00844e-4`; the actual target change toward the interface consumes
`1.56845e-4`. Reconstruction changes the radiation contribution by
approximately `2.599e-5`, and other component-density changes contribute
`9.85e-7`. The witness lies at an original time node. Finer spatial replay
approaches the interface beyond the innermost original sample, where the
controls have constant extension. Its larger deficit therefore identifies
an unresolved spatial margin. Separately, a guide-facet deficit
`2.18880e-5` occurs at `t=0.5` at the same position. The positive-part
quadrature discrepancy belongs to the fluid-heating split elsewhere;
radiation-density quadrature disagreement is only `3.21e-16`.

## Verification record

The focused suite contains 196 transport, thermal, native-solver,
contact, capacity, and local-relaxation tests at this stage. The independent source audit
checks every archived numerical product and input hash against current
files, recorded git versions, or separately hashed execution snapshots.
Three intermediate execution versions were recovered with exact matches
to their original recorded SHA-256 values. Their snapshots preserve the
original numerical products and input identities. Snapshot acceptance
also requires its independent output-manifest hash; the corresponding
validation regression rejects altered or unbound snapshots.
