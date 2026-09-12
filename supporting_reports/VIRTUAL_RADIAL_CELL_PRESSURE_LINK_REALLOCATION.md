# Joint thermal allocation in the existing pressure link

Jointly allocating the existing pressure-link fluid and heat receiver
clears the coherent finite-cell pilot at both tested locations. Reopening
the fluid alone clears `x=-2` and reduces the second pair's added-density
requirement from `0.00312356` to `0.00112186`. The combined result preserves
the original power duties, cold particle inventory, receiver capacity, and
receiver containment. It identifies a useful thermal allocation within the
existing assembly, with refinement and constitutive contact still open.

This continues the [thermal-exchange investigation](VIRTUAL_RADIAL_CELL_THERMAL_EXCHANGE.md)
on the scheduled active rail. The protected packet, geometry, capacitor,
existing work waves, and standing-support duties retain their registered
roles. These local tests concern two width-`0.0005` pairs within the backing;
their physical contacts and whole-patch continuation remain construction
requirements.

## Component ownership and reciprocal power

The original pressure link has conserved particle inventory `N_m(x)` and
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

Define `T_Z=alpha(x) Z^(1/4)`, with `alpha>0`, and use the registered fluid
temperature `T_f=U/(3N_m)`. The capacity fixes an energy ceiling; it supplies
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
