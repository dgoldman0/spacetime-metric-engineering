# Joint support conservation and passive coupling

The support investigation now separates two requirements: a material stress
history that conserves energy and momentum between sample points, and a
constitutive mechanism that supplies that history. Coupling radial and angular
elasticity alone fails the registered convex-energy screens. Meanwhile, a
joint spacetime inverse retains admissible member inventories, although its
midpoint trajectories still contain substantial unresolved time variation.

## Coupled passive energy screen

For an elastic energy per material label `M(ell,R)`, the conjugate gradients are

```
M_ell = -P/ell,       M_R = -2Q/R.
```

A convex two-stretch energy requires its gradient increments to have a
nonnegative scalar product with the corresponding stretch increments.
This permits radial and angular work exchange and therefore broadens the
earlier uncoupled axial-stiffness test. A manufactured positive-definite
coupled energy passes the new screen even when its individual axial gradient
changes against the radial stretch.

Four linear-program controls retain the original pressure fluid and the
separate-member energy requirement. They impose neighboring gradient
monotonicity at member fractions 1 and 0.9, all-pair gradient monotonicity at
fraction 1, and supporting-plane inequalities for the stored energy at
fraction 1. All four are infeasible on the registered 32-cell/35-time grid.
The supporting-plane case also inherits the original discrete work
quadrature; the gradient-only comparisons provide the separate local test.

The original freely scheduled composite has 77.4% of the absolute coupled
gradient/stretch product on the negative side. Its convex supporting-plane
conditions fail at 80.6% of sampled pairs. Thus simple stable elastic coupling
offers little support for retaining that particular loading history.

Convexity of this reduced energy is a specific material-model assumption.
Internal state evolution, phase switching, externally regulated response,
and the full stability conditions of a prestressed relativistic solid remain
distinct constructions. Relativistic elasticity supplies an action and
stress framework, while longitudinal and transverse characteristics require
their own constitutive derivatives.
[Brown](https://arxiv.org/abs/2004.03641),
[Natário](https://arxiv.org/abs/1912.08221).

## Direct conservation projections

The direct projection fixes the angular history, prepared energy, and one
end-pressure history while solving radial pressure and energy. Every fixed
fluid, field, wave, and receiver divergence enters explicitly, including
temporal electric momentum. The additional local energy exchange, required
by the continuous interpolation of the archived fixed histories, is counted.
Its gross integral is approximately 0.31–0.36 in the registered normalization.

The first spatial march uses the left pressure history. Its errors grow
rapidly with refinement, reaching an unusable amplified solution. Here the
coefficient of the temporal pressure derivative has the sign of the material
velocity, which lies between approximately -0.202 and zero. Reversing the
radial orientation places the prescribed pressure history at the incoming
right cut and removes that numerical blow-up.

However, the incoming-boundary projection still fails the material-energy
requirement. At 256 spatial cells and the 258 original time nodes, its maximum
separate-member density deficit is 0.478; the weighted force and power
residuals are 10.8% and 5.12%. Preserving the old angular history and prepared
inventory therefore supplies an inadequate repair. Both spatial projections
are numerical diagnostics, with explicit failed acceptance conditions.

## Joint spacetime inverse

The next formulation frees `M`, `P`, and `Q` together. It integrates the
energy equation in time and the force equation across each radial cell,
using the complete fixed-component divergence. Bilinear per-label fields obey

```
|P| + max(-Q,2Q) <= f M
```

at every point when this inequality holds at the panel corners. Thus the
separate radial and angular members retain their own positive energy costs
throughout interpolation. Fraction `f=0.9` leaves a declared energy margin;
it specifies an inventory comparison rather than a stability theorem.

| Joint midpoint case | Exact sampled material null peak | Fade remainder | Weighted force residual | Weighted power residual |
| --- | ---: | ---: | ---: | ---: |
| 32 cells / stride 8, f=1 | 0.20507 | 0.35564 | 15.23% | 20.37% |
| 64 cells / stride 4, f=1 | 0.13995 | 0.34034 | 7.43% | 12.15% |
| 64 cells / stride 4, f=0.9 | 0.16808 | 0.36846 | 7.13% | 11.87% |
| 64 cells / stride 4, f=0.9, zero sharing | 0.15121 | 0.41536 | 4.31% | 11.23% |

The zero-sharing control retains the full capacitor field and adds the full
guide field. Their larger combined stress raises the fade source burden even
as removing the allocation gradient reduces part of the force mismatch.
Hence field sharing provides a real inventory benefit, with a spatial stress
shape that the support representation must resolve.

All four midpoint systems satisfy their original matrix equations and member
inequalities. Their dense independent audits resolve the original time and
allocation panels, exposing variation that midpoint equations alone leave
weakly constrained. The resulting trajectories provide construction targets
and numerical controls; a converged supplied material tensor remains open.

## Regulated response and evidence

A physical precedent for local powered stress control is the freestanding
piezoelectric metabeam of Chen and colleagues. Its local sensing and
actuation circuits couple two deformation modes, exchange electrical and
mechanical work, and preserve linear and angular momentum. This supplies an
engineering precedent for the controller and energy-port arrangement.
Its demonstrated elastic stresses and mass density are ordinary material
values; adapting the arrangement to the rail still requires the full
load-bearing material, stored energy, and relativistic response.
[Chen et al.](https://www.nature.com/articles/s41467-021-26034-z).

The current calculation continues by resolving temporal force variation and
the known allocation shape while preserving member margins. The technical
disclosure and its PDF retain their recognized design content.

Evidence: [coupled passive controls](data/joint_coupled_passivity),
[left-boundary projection](data/joint_support_projection),
[incoming-boundary projection](data/joint_support_inflow_projection), and
[joint midpoint inverse](data/joint_spacetime_support). The code is under
`toolkit/adm_harness_cli`, with `joint_support_projection.py`,
`joint_support_spacetime.py`, and their matching runners. Independent
manufactured covariant tensors test both discretizations, while static-force
controls require an explicit transmitted end reaction. The coupled-energy
test verifies that the screen admits cross-coupling which the axial-only
criterion would reject.
