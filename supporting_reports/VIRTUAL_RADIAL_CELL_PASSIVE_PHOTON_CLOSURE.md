# Passive photon exchange in the radial-cell assembly

Both tested locations admit a sampled curved-space allocation of the phase,
balanced radiation, existing pressure-link fluid, and separated receiver
banks within the original full stress budget. A physical photon contact is
the remaining local construction issue. The resolved histories distinguish
the required energy redistribution from the much smaller converter-loss
heat flow, allowing the next test to address their interaction directly.

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
admit passive bank routing when the omitted transport and contact
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

## Verification record

The focused suite contains 145 transport, thermal, native-solver,
contact, capacity, and local-relaxation tests at this stage. The independent source audit
checks every archived numerical product and input hash against current
files, recorded git versions, or separately hashed execution snapshots.
Three intermediate execution versions were recovered with exact matches
to their original recorded SHA-256 values. Their snapshots preserve the
original numerical products and input identities. Snapshot acceptance
also requires its independent output-manifest hash; the corresponding
validation regression rejects altered or unbound snapshots.
