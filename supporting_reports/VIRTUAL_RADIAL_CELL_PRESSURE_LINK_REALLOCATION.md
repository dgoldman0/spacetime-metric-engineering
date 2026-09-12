# Joint thermal allocation in the existing pressure link

Jointly allocating the existing pressure-link fluid and heat receiver
clears the coherent finite-cell pilot at both tested locations. Reopening
the fluid alone clears `x=-2` and reduces the second pair's added-density
requirement from `0.00312356` to `0.00112186`. The combined result preserves
the original power duties, cold particle inventory, receiver capacity, and
receiver containment. It identifies a useful thermal allocation within the
existing assembly. Resolving the actual midpoint stress and reconstructing
continuous heat-transfer rates subsequently clears the sampled curved
replay at `x=-1.975`, including its full thermal preparation. The first
location also has a verified refined finite allocation after disabling
solver presolve; its curved replay follows separately. Physical photon
contacts, reciprocal forces, and material constitutive closure remain the
next construction requirements.

This continues the [thermal-exchange investigation](VIRTUAL_RADIAL_CELL_THERMAL_EXCHANGE.md)
on the scheduled active rail. The protected packet, geometry, capacitor,
existing work waves, and standing-support duties retain their registered
roles. These local tests concern two width-`0.0005` pairs within the backing;
their physical contacts and whole-patch continuation remain construction
requirements.

## Component ownership and reciprocal power

The original pressure link has conserved rest-mass inventory `N_m(x)` and
thermal energy `U_0(t,x)` per material label. With `D=ell R^2`, its thermal
density is `B_0=U_0/D`, and its thermal tensor is
`B_0(1,1/3,1/3)`. The prior support target excludes this fluid. Reusing its
thermal state therefore enlarges the available target to

```
(rho_*,p_*,q_*) = (rho_support,p_support,q_support)
                 + B_0 (1,1/3,1/3).
```

The unknown `B=U/D` is the actual fluid thermal density, constrained by
`U>=0`. Its increment `U-U_0` may be negative. The cold energy `N_m/D`
stays assigned to the original fluid; it supplies zero comoving power and
retains its acceleration force. The 0.2% numerical reserve continues to
apply to the original support density before this component is added back.

Let `V=M W`, `M=(ell R)^2`, `K=D^(1/3)U`, and `K_0=D^(1/3)U_0`.
The balanced radial radiation includes drive, useful return, heat return,
and its complementary photons. Preserving the remaining auxiliary
backing's original power duty gives

```
V_t + ell^2 A_t + (M/D^(4/3)) (K_t-K_0,t) = 0.
```

Thus the phase, balanced photons, and changed fluid exchange energy
reciprocally. The baseline fluid power remains assigned exactly once.
The finite calculation uses midpoint geometric coefficients and endpoint
increments, matching the preceding semigroup comparison. Independent
integration of the actual evolving metric is a separate refinement check.

Changing the fluid also changes the force it requires. For
`deltaB=B-B_0`, the thermal force increment is
`(4/3)deltaB a + D_s(deltaB)/3`, with
`D_s=ell^(-1)partial_x+(v/N)partial_t`. Its opposite belongs to the
coupled material, field, and contact reactions. The positive remainder
cone supplies a tensor allowance; a constitutive realization must evolve
those reactions and heat-transfer laws.

## Pilot comparison

The [reallocated-fluid archive](data/virtual_cell_existing_fluid_pilot/summary.json)
retains 12 spatial samples, 132 time nodes, a shared phase, 98% beam/phase
conversion, separate heat return, the 0.5 guide comparison, finite interface
energy, and the original numerical reserve. Both numerical optimizations
and their secondary inventory minimizations succeed.

| Pair center | Separate added reservoir | Reallocated existing fluid |
| --- | ---: | ---: |
| -2 | Added density 0.00132490 | 0 within numerical tolerance |
| -1.975 | Added density 0.00312356 | Added density 0.00112186 |

The second location improves by approximately 64%. The largest cooling
increments are `0.0132570` and `0.0129102` in density, while the largest
heating increments are `0.0353571` and `0.0399759`. Both histories reach
zero thermal energy at some samples. These are permissive energy/stress
histories whose temperatures and finite contact rates require further
constraints.

The panel energy residual stays below `1.22e-14`; maximum scaled equality
and inequality residuals are below `2.88e-10` and `7.08e-10`. Tests cover
the preserved baseline power, full thermal tensor, allowed cooling, and
nonnegative actual fluid energy. Two worker processes use one solver
thread each; each pilot takes about 42 seconds.

The next comparison reopens the existing heat receiver with its rated
energy capacity retained. Its stored heat and containment energy have
separate ownership: the registered `heat_cap/3` is a wall-energy allowance,
while `heat` is the adjustable inventory. A reciprocal fluid/receiver
exchange must evolve both inventories and preserve their original feeds.

## Existing receiver with its capacity and containment retained

Let `Z_0` denote its archived stored heat and `C_Z` its rated energy capacity
per material label. The available density gains `Z_0/D`, while the actual
receiver contributes `Z/D` with `0<=Z<=C_Z`. Its compact, internally supported
cells retain their original effective dust tensor. The fixed wall energy
`C_Z/3` remains in the surrounding assembly's ledger.

Writing `chi=M/D=ell`, the combined local energy equation becomes

```
V_t + ell^2 A_t + psi (K_t-K_0,t) + chi (Z_t-Z_0,t) = 0,
psi = M/D^(4/3).
```

The additional receiver-to-fluid transfer is
`Q_added=-(Z_t-Z_0,t)/(N D)`. The changed fluid's power equals its original
power plus this contact transfer minus the new phase/radiation power.
The receiver's force changes by `(Z-Z_0)a/D`, with the opposite reaction
belonging to the connected support.

The [fluid-and-receiver pilot](data/virtual_cell_fluid_receiver_pilot/summary.json)
has zero optimal added density at both locations. Both secondary inventory
optimizations succeed. Independent reconstruction verifies actual receiver
energy within its unchanged capacity, exact shared phase, the complete
component cone, and the finite-panel wave ceilings. Maximum energy residual
is `1.38e-14`; the strongest midpoint density residual is below `9.7e-10`.
The optimized receiver histories reach both zero and rated capacity.

Independent Gauss integration of the baseline fluid and receiver power,
split at all their original knots, changes the reconstructed radiation
density by less than `2.7e-7`. A positive prepared-radiation adjustment
preserving every wave floor costs at most `1.4e-6` additional density.
The held 0.2% reserve covers that isolated forcing-quadrature correction.
Actual baseline-fluid midpoint interpolation has a separate error, and
the original curved transport still requires replay.

The [24-cell, 515-time attempt](data/virtual_cell_fluid_receiver_refined/summary.json)
reaches the primary interior-point time limit at both locations. Each primary
solve receives 180 seconds; the archive returns no primal state. These
are numerical limits on refinement, separate from the two verified pilot
solutions.

## Temperature and total heat transfer

A concrete receiver comparison uses photons in fixed proper-volume cells.
The equilibrium energy law `Z=a_R V_cell T_Z^4` follows from the
[photon-gas calculation in Tong's statistical physics notes](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S3.html).
Changing the macroscopic material volume changes cell spacing, while the
internally balanced cells retain their individual proper volume. Their
packing, wall response, and optical contacts require explicit construction.

Define `T_Z=alpha(x) Z^(1/4)`, with `alpha>0`, and use the fluid's caloric
comparison parameter `T_f=U/(3N_m)`. The capacity fixes an energy ceiling; it supplies
neither `alpha` nor a caloric heat capacity by itself. A finite passive
contact follows the ordering of these actual evolving temperatures.

Its thermodynamic test uses the total receiver-to-fluid transfer. The
original converter deposits `L_0=-(P_field+P_old_wave)>=0` into the receiver.
Therefore its proper-label contact power is

```
q_total = D L_0 - dZ/dtau,       dtau=N dt,
H_panel = integral(N D L_0 dt) - Delta Z.
```

The original contact is `L_0-P_receiver,0=P_fluid,0-P_fixed`; the remaining
backing retains the residual power assignment `P_support=-P_fixed`.
Testing only the additional contact would omit the established thermal
duties. For positive `q_total`, passivity requires
`alpha^4 > T_f^4/Z`; negative transfer requires the opposite strict bound.
Zero receiver energy cannot supply positive passive heat transfer.

The receiver extension and independent temperature-order tests bring the
focused validation to 78 tests. The execution-time test-file snapshots and
the corrected validation version are recorded separately in the two receiver
manifests; the numerical module and state identities remain preserved.

## Finite donor turnover and the temperature conflict

The [first contact audit](data/virtual_cell_receiver_contact_pilot/summary.json)
finds no admissible constant photon-receiver temperature coefficient at any
of the 12 spatial samples in either pilot. Some panels require positive heat
outflow from an empty receiver, while others return heat from fluid at zero
temperature. These are defects of the selected unrestricted histories.

The next optimization limits each donor's outgoing heat to ten times its
thermal energy per unit proper time. With panel heat `H`, proper duration
`Delta tau`, and actual fluid energy `U`, it requires

```
 H <= 10 Delta tau Z,
-H <= 10 Delta tau U
```

at both panel ends. The rate is a finite comparison in the project's time
unit. Its physical realization depends on the eventual scale and contact
geometry. These donor bounds permit heat exchange in either direction and
leave temperature ordering as an independent requirement.

Both [finite-turnover pilots](data/virtual_cell_fluid_receiver_rate10/summary.json)
fit the reserved target with zero added density. A direct budget solve fixes
that allowance at zero and minimizes counted inventory in one optimization.
The [temperature audit](data/virtual_cell_receiver_contact_rate10/summary.json)
then removes the empty-donor failures but retains incompatible ordering at
all 12 samples in each pair. At the sample just right of the second pair's
center, outgoing heat near `t=0.496` requires `alpha^4>124.95`; incoming heat
near `t=1.245` requires `alpha^4<1.694e-16`. The selected fluid reaches very
different temperatures through the schedule. These inequalities constrain
these particular controls; the passive-contact equations were absent from
their optimization.

This identifies a specific receiver architecture to test: separate hot and
cold banks, with the hot bank supplying heat and the cold bank accepting it.
Their separate fixed rated capacities must sum to at most the original
receiver rating. A pointwise bound on combined stored heat alone would allow
the two banks to reuse containment capacity at different times.

The direct-budget and finite-donor regression brings the focused suite to
79 passing tests.

## Two separately rated receiving banks

The [split-receiver pilot](data/virtual_cell_fluid_receiver_split10/summary.json)
fits both reserved stress budgets with zero added density. The hot bank
has energy `H`, receives the original converter losses, and sends positive
heat `Q_h` into the fluid. The cold bank has energy `C=Z-H` and receives
positive heat `Q_c` from the fluid:

```
Delta H = L_panel-Q_h,       Delta C = Q_c,
Q_h-Q_c = L_panel-Delta Z.
```

The actual total receiver energy remains `Z`; its tensor is counted once.
Cold inventory increases monotonically, so the separate fixed-rating
constraint is `H(t)+C_final<=C_Z` at every node. This is equivalent to
requiring the maximum hot and cold inventories to fit within the original
total rating. Both donor rates retain the ten-per-proper-time comparison.
The additional divider, insulation, and valve realization remain explicit
construction costs beyond the optimistic existing wall allowance.

Independent reconstruction checks the separate ratings, contact directions,
and `Q_h-Q_c` identity. The identity residual is below `1.4e-17`, and the
finite-donor residual is below `1.5e-12`. These endpoint rate bounds define
a conservative panel restriction; continuous contacts can charge and release
within a panel, so this restriction has a narrower scope than a general
finite-rate model.

Separate photon temperatures permit distinct constants:
`T_h^4=a_h H`, `T_c^4=a_c C`. Their passive-contact inequalities give a lower
bound on `a_h` and an upper bound on `a_c`. For equal photon content physics,
the corresponding proper volumes obey `V_c/V_h=a_h/a_c`. The pilot controls
allow this ordering, but require a volume ratio above about `2.68e19` at
the first pair and `4.69e21` at the second. This large ratio follows from
the nearly cold fluid state selected by inventory minimization. It is a
property of those controls, with fluid temperature still available as a
joint design variable.

The [single-receiver finite-rate temporal refinement](data/virtual_cell_fluid_receiver_rate10_refined/summary.json)
also passes at both locations with 12 spatial samples and all 515 original
time nodes. Its maximum density residual is below `9.7e-10`. The next
physical comparison keeps the fluid warm enough to reduce the cold bank's
required volume while retaining the complete stress and rated-capacity
constraints. The split-inventory regression brings the focused suite to
80 passing tests.

The [split-receiver temporal refinement](data/virtual_cell_fluid_receiver_split10_refined/summary.json)
clears the second pair with a maximum density residual below `9.6e-10`.
The first pair reaches its solver time limit without returning a primal
state. This leaves that particular refined optimization unresolved.

## Keeping the pressure-link fluid warm

The [warm-fluid pilot](data/virtual_cell_fluid_receiver_warm10/summary.json)
maximizes a common lower bound on `Theta_f=U/(3N_m)` across each pair and
the entire schedule. It retains zero added density, the split receiver's
separate ratings, both finite donor rates, and all existing stress duties.
A second optimization minimizes counted inventory while retaining 99% of
the maximum temperature floor. Both stages succeed at both locations.

| Pair center | Maximum uniform floor | Retained floor | Minimum cold/hot photon volume ratio |
| --- | ---: | ---: | ---: |
| -2 | 0.1243283 | 0.1230850 | 2.01e6 |
| -1.975 | 0.03420248 | 0.03386045 | 7.62e7 |

The [independent temperature audit](data/virtual_cell_split_contact_warm10/summary.json)
finds a common hot coefficient and a common cold coefficient for every
sample in each pair. Keeping the fluid warmer reduces the required volume
contrast by more than thirteen orders of magnitude compared with the
inventory-minimized split controls. Finite temperature gaps can be obtained
by doubling each hot lower bound and halving each cold upper bound; this
choice gives four times the minimum volume ratio. The computed nonnegative
radiative conductances describe the contact response required along these
histories. A material optical law must supply that response.

The numerical floor has a conditional temperature interpretation. The
registered fluid obeys `rho=n+3p` and conserves rest mass `N_m=D n`.
Identifying `Theta_f` with `k_B T/(m_eff c^2)` additionally requires a
thermal-particle count and `m_eff` equal to rest mass per thermal particle.
An ordinary monatomic gas has a thermal-energy coefficient approaching
`3/2` in its nonrelativistic regime and `3` in its relativistically hot
regime. A mixture carrying cold rest mass and relativistic light particles
could support the registered thermal relation, subject to its composition
and interaction law. The present comparison leaves that caloric closure
explicit.

Absolute photon-cell volume follows once this normalization and the rail's
length scale `L` are selected. With reduced normalization length
`lambda_eff=hbar/(m_eff c)`, Planck length `l_P`, and photon coefficients
`Theta_j^4=a_j Z_j`, blackbody thermodynamics gives

```
V_j/(L^3 D) = (15/pi^2) lambda_eff^4/(l_P^2 L^2 D a_j).
L >= (lambda_eff^2/l_P)
     sqrt[(15/pi^2)(1/a_h+1/a_c)/D_min].
```

The second expression is the conditional bound for both banks together
to occupy the available material volume. A bank packing fraction `f`
replaces `D_min` with `f D_min`. The whole patch requires the largest
bound over its material labels. The repository's stress unit is
`c^4/(G L^2)`; its Einstein tensor already includes the division by `8pi`.
Stored heat and material volume use the same per-label, per-solid-angle
normalization. Fluid, walls, insulation, guides, and valves also consume
volume and energy. Thus the improved volume contrast identifies a useful
control direction while absolute packing remains scale- and material-dependent.

The warm-floor regression and independent curved-replay adapter bring the
focused suite to 88 passing tests. The adapter separately evolves the
aggregate balanced-radiation energy and all six explicit work/heat beams
on the registered curved geometry, preserving the archived controls and
their prepared inventories. Its numerical results will determine how much
of the finite-panel allocation survives continuous metric evolution.

## Independent curved replay and the sampling repair

The [fourfold pilot replay](data/virtual_cell_thermal_replay_warm10/summary.json)
preserves the optimized phase, fluid, and receiver histories, evolves the
complete radiation inventory with the registered metric, and independently
propagates the six explicit beams. Both controls exceed the full density
budget between their coarse target samples:

| Pair center | Maximum full-density shortfall | Time of maximum | Maximum wave-floor violation |
| --- | ---: | ---: | ---: |
| -2 | 0.01008994 | 0.00501953 | 0.0000635184 |
| -1.975 | 0.02172730 | 0.49595703 | 0 |

The energy quadrature is well resolved: Gauss orders four and eight differ
by less than `2e-15` in radiation density, and explicit wave balance closes
within `1.9e-19`. Replacing the evolved radiation with the archived linear
inventory leaves the first shortfall unchanged and the second at
`0.02157522`. The principal discrepancy therefore belongs to the target's
time sampling. At the two worst samples, the exact radial stress differs
from the endpoint-averaged target by `+0.0102620` and `-0.0212212`.
Applying the averaged target to the very same replayed states produces
positive density margins of `0.000112567` and `0.00109504` there.

The replay also resolves short intervals with reversed hot-bank transfer
and donor-bound violations around `2e-5` in panel heat. The coarse linear
hot-energy history averages over variation in the original converter loss.
The separate bank ratings remain below the actual local receiver rating.
An overly restrictive diagnostic comparison between an interpolated unused
allowance and the local rating has been corrected to compare actual stored
heat with the original local rating; the independent split-rating check
continues to constrain both banks' maxima.

The [515-time warm-floor maximizations](data/virtual_cell_fluid_receiver_warm10_refined/summary.json)
reach their primary 300-second solver limits without returning states.
The next solve therefore uses a fixed positive temperature floor and one
inventory optimization. It also supplies the actual midpoint stress from
the registered history, including the baseline fluid and receiver credits
once. This retains the physical assembly while resolving known target
features and reducing the solver work. A manufactured capacity-dip test
demonstrates the difference between true midpoint stress and endpoint
averaging.

## Resolved time sampling with a fixed positive floor

The [515-time exact-midpoint solve](data/virtual_cell_fluid_receiver_floor001_exactmid/summary.json)
clears the second location with zero added density and `Theta_f>=0.01`.
Independent reconstruction matches the complete credited midpoint target
exactly. The maximum node and midpoint-envelope density residuals are
`4.15e-10` and `6.07e-10`; the energy-panel residual is `6.54e-14`.
The separate hot and cold ratings use 36.3011% of the original receiver
capacity, and contact directions and donor bounds hold within `5.4e-15`.
Thus the actual midpoint stress features permit a finite allocation at
this location.

The first location reaches its 600-second primary solver limit. An
[eight-position comparison](data/virtual_cell_fluid_receiver_floor001_exactmid_n8/summary.json)
retaining the same 515 time nodes and physical constraints returns HiGHS
status 0, exposed by SciPy as numerical status 4, without a usable state.
Both first-location outcomes are unresolved numerical cases. A further
bounded comparison disables interior-point crossover while retaining
the same equations and independently checked feasibility tolerances.

## Conserved preparation and guided thermal contact

The independent replay can test a small addition to the initially prepared
balanced radiation. For each material label, a constant increment
`deltaV>=0` changes `W` by `deltaV/M` and supplies zero additional proper
power. The complete stress remains counted throughout the schedule.
Two remainder-cone facets are independent of `W`; the third consumes
three times its added density. Thus a single preparation must satisfy

```
max_t {0, M [2 max(u_incident,u_returned)-W]} <= deltaV
deltaV <= min_t {M [rho_rem+2 p_rem+q_rem]/3}.
```

The other two facets retain their independent bounds. This interval tests
whether the held density margin can pay a wave-floor correction over the
entire history. It preserves the original energy equation and records the
added initial inventory explicitly.

Beyond stress and energy balance, the complementary photons have a
specific remaining contact duty. The prescribed phase and its drive,
useful-return, and heat-return waves satisfy `P_phase+P_wave=0`.
Consequently, with `q_R=L_0-P_Z`,

```
P_counter = P_fluid,0+P_Z,0-P_fluid-P_Z
          = P_fixed+q_R-P_fluid,
P_fluid   = q_R+P_fixed-P_counter.
```

The receiver contacts supply `q_R`, the retained support allocation
supplies `P_fixed`, and the complementary photons supply `-P_counter`
to the fluid. The support retains the opposite `-P_fixed`. Fluid
compression work is already included in the derivative of
`K=D^(1/3)U`; its physical heat and work partners must obey these separate
assignments.

A useful conditional photon model consists of fixed, gapless,
nondispersive one-dimensional channels. For `g` independent species,
including polarization and both propagation directions, integration of
Planck occupation gives proper-length energy
`e_1D=pi g (k_B T)^2/(6 hbar c)`. Its one-direction power agrees with
the temperature-squared single-mode result of
[Fohrmann et al., Single mode thermal emission](https://doi.org/10.1364/OE.23.027672).
For a fixed channel count per material solid angle `DeltaOmega`,

```
c_eq = a_2 Theta_f^2/R^2,
a_2  = pi g l_P^2/(6 DeltaOmega lambda_eff^2).
```

The rail scale cancels from this coefficient. Ideal fixed-number modes
with frequency independent of transverse area have radial pressure equal
to their energy density and zero thermodynamic transverse pressure.
Their guides, conductors, and terminations carry separate material
stresses. Actual cutoffs, dispersion, higher-mode occupation, and changes
in channel count require their corresponding energy and stress terms.

Passive grey absorption and emission require
`P_counter=kappa_a(c_eq-c)`, with `kappa_a>=0` and the complete complementary
population `c=W-u_incident-u_returned`. The required fixed coefficient
therefore lies in

```
max_(P_counter>0) [c R^2/Theta_f^2] < a_2
a_2 < min_(P_counter<0) [c R^2/Theta_f^2].
```

These are necessary power-ordering bounds for the specified guided mode
law. Positive but arbitrarily small populations remain admissible at a
finite, potentially large opacity. Force balance additionally constrains
absorption and scattering through the required counter-photon momentum
exchange, as in the comoving radiation-matter source structure of
[Sadowski et al., equations 17–18](https://arxiv.org/html/1212.5050v2#S2.SS1).
The optical coupling must also preserve the separately prescribed work
and heat beams. The support contact retains its own heat, work, and
entropy closure. The associated preparation and contact regressions
bring the focused suite to 100 passing tests.

## Continuous heat rates within the original budget

The second-location exact-midpoint solution contains a negative conversion
increment of `-1.95e-10`. The default replay rejects this input. An explicit
phase-preserving repair retains every positive overlap cycle, sets
`p=max(DeltaA,0)+overlap` and `m=max(-DeltaA,0)+overlap`, and records each
change. The applied correction is `1.95e-10`, within its declared `1e-8`
allowance; all six incident and returned beams are independently replayed.
The [corrected-conversion replay](data/virtual_cell_thermal_replay_floor001_repaired/summary.json)
clears the complete stress with margin `5.44496e-5`. Linear interpolation
of receiver energy leaves a small contact mismatch: the donor excess is
`4.36e-7` and the minimum hot withdrawal is `-1.67e-8` per replay panel.

The [continuous-contact replay](data/virtual_cell_thermal_replay_floor001_contacts/summary.json)
instead distributes each original nonnegative hot and cold heat total
uniformly in proper time within its parent panel. With lapse `N`, these
rates determine the bank histories through

```
H_t = L_coord - N q_h,
C_t = N q_c,
Z_t = L_coord - N q_h + N q_c.
```

The revised `Z_t` enters the independently integrated radiation equation
with its full factor `ell`. Small constant additions to `H`, `C`, and `K`
cover the refined donor bounds and the original temperature floor. Their
entire receiver and fluid stress enters the same available tensor. This
retains the original converter losses, receiver ratings, and baseline
component power duties.

At 24 spatial positions and 1,029 time nodes, the complete density margin
is `5.44436e-5`. The wave floor, thermal positivity, bank ratings, donor
bounds, and `Theta_f>=0.01` all hold. The largest added receiver density
is `8.63e-9`; the largest added fluid density is `4.95e-8`. Added balanced
radiation is zero. The initial 0.2% numerical reserve is partly consumed,
while the full physical density budget remains positive. The largest
aggregate energy-panel residual is `8.88e-15`, contact subtraction
residual is `1.88e-17`, and Gauss-4/Gauss-8 radiation-density difference
is `4.05e-16`. These separately reviewed identities substantiate this
sampled clearance. A subsequent acceptance refinement will require these
integrity checks directly in the combined pass flag.

## Retaining a solver state requires the original equations

The first-location [crossover-free comparison](data/virtual_cell_fluid_receiver_floor001_exactmid_nocross/summary.json)
and [normalized-objective comparison](data/virtual_cell_fluid_receiver_floor001_exactmid_scaled/summary.json)
both terminate with an unfinished interior-point solution. Normalizing
the inventory objective by a positive constant preserves its minimizer;
reducing the matrix drop threshold to `1e-12` retains most previously
discarded small coefficients. The internal solver log still lacks an
accepted optimum.

A [native-state comparison](data/virtual_cell_fluid_receiver_floor001_native/summary.json)
retrieves the candidate and independently checks every original matrix
row and variable bound. Although the backend marks its values valid and
reports zero primal infeasibility, the retrieved candidate has equality
residual `0.5094` and inequality excess `7.9125`. It is rejected. Internal
feasibility during an unfinished solve therefore provides insufficient
evidence for this location. The adapter keeps verified feasibility and
inventory optimality as separate results. Its solve-error acceptance
boundary and the replay integrity flag are identified for tightening
before the next refinement. The focused numerical suite has 115 passing
tests, including explicit contact conservation and native row checks.

## Refined acceptance and the physical photon contact

The [presolve-disabled native solve](data/virtual_cell_fluid_receiver_floor001_nopresolve/summary.json)
recovers a valid first-location allocation on the full 515-time grid.
Every original equality, inequality, and variable bound is independently
checked: the largest violation is `2.18e-9` and equality residual is
`1.33e-14`. Added density is fixed to zero, with independently evaluated
tensor excess `8.51e-10`. Inventory optimality remains uncertified; this
finite feasibility result suffices for the independent replay. Native
load and solve errors now explicitly reject retention.

At the second location, the [36-position, 1,543-time replay](data/virtual_cell_thermal_replay_floor001_contacts_refined/summary.json)
passes the combined tensor, capacity, contact, temperature, conservation,
and quadrature gates. Its minimum full density margin is `3.98277e-5`,
compared with `5.44436e-5` at the preceding resolution. The minimum
complementary-photon directional margin is `6.21768e-6`. Added receiver
and fluid densities are at most `1.16e-8` and `5.87e-8`, with zero added
radiation. The acceptance flag now requires all reported contact and
energy identities, parent heat reconstruction, and Gauss agreement to
be finite and within `1e-9`. The explicit sampled scope remains; these
two resolutions provide positive margins through the registered stress
transition.

The [separated-bank temperature audit](data/virtual_cell_split_contact_floor001_refined/summary.json)
admits hot and cold temperature coefficients across this history.
However, the [fixed grey guided-fluid contact](data/virtual_cell_guided_contact_floor001_refined/summary.json)
fails at every one of the 36 sampled positions. Its common coefficient
would require `a_2>18749.7` for emission and `a_2<0.0185387` for
absorption. The preceding resolution gives the same conflict, with
bounds `18745.1` and `0.0265452`. The fluid becomes hot around the sharp
stress transition and later returns to its low retained temperature;
the prescribed complementary-photon power demands an incompatible
sequence for this fixed equilibrium law. This confines the failed
closure to the specified grey photon-fluid contact.

An alternative within the existing components routes positive counter
power from the hot bank and negative counter power into the cold bank.
In proper-label units, let `p=D P_counter`, with current bank heat rates
`q_h,q_c>=0`. Setting `e=max(p,0)` and `a=max(-p,0)` leaves fluid branches
`q_h-e` and `q_c-a`. The bank inventories and full fluid power remain
unchanged exactly when

```
-q_c <= p <= q_h.
```

The photon temperature interval then uses the hot bank for emission and
the cold bank for absorption. Bank capacity, finite donor rates, and
the remaining fluid-support power continue to apply. The resulting
routing test separates a temperature mismatch from an insufficient
existing heat-transfer budget; a joint thermal reallocation can be
tested with linear panel constraints if the unchanged histories fail.
