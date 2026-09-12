# Joint thermal allocation in the existing pressure link

Reopening the pressure-link fluid's existing thermal energy clears the
coherent finite-cell pilot at `x=-2` and reduces the second pair's added-density
requirement from `0.00312356` to `0.00112186`. The comparison preserves the
fluid's original power duty and cold particle inventory. It changes the
thermal allocation within the existing assembly, with the full isotropic
pressure counted alongside phase control and causal work delivery.

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
