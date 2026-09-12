# Charged capacitor construction for the active rail support

The charged-shell literature provides useful equilibria and radial stability
controls. Its economical examples require relativistic boundary stress; their
material law and integration with the scheduled rail remain construction
requirements. A separate magnetic-insulation calculation addresses a field
cell supported through the existing infrastructure.

The electrical store considered here is the remaining radial electric field
in the [finite work-interface assembly](FINITE_WORK_INTERFACE.md). It serves
the support actuator during the late interval x in [-2.1,-0.5], s in
[0,1.285], outside the protected moving packet. The standing substrate,
angular jacket, pressure medium, work delivery, and heat receiver retain
their distinct roles. Spherical electrovacuum examples below are boundary
analogues for a capacitor; the rail retains its prescribed active metric.

## Construction requirements

At full electrical recovery, the retained electric cells initially contain
71.33 material-frame energy units, with individual capacities summing to
80.59. Their net electrical work is +42.30 and their mechanical work is
-105.19 over this interval. At 90% recovery the corresponding values are
100.00, 111.85, +42.30, and -132.52. The negative mechanical term represents
field energy delivered through the changing cell geometry.

A candidate therefore supplies charge confinement, finite supporting
material, the aligned electric stress, reversible electrical coupling, and
the mechanical connection to the support system. Its complete tensor enters
the existing source comparison. Passive field-energy capacity alone covers
only part of this duty.

The previous additional co-moving mass comparison permits rest energy per
rated electric energy about 0.401 at full recovery or 0.324 at 90% recovery.
These figures preserve the earlier formal fade reference 0.262788. They are
selection comparisons for a specified tensor and material history. A wall
with pressure or tension requires its full tensor; shared structural material
requires a common load and energy balance. Consequently these mass ratios
provide context for the shell calculation, rather than a universal acceptance
threshold for every capacitor construction.

## Spherical charged boundaries

[Bičák and Gürlebeck](https://arxiv.org/abs/1008.1137) describe two oppositely
charged spherical shells with a flat center, an electric Reissner--Nordström
gap, and a neutral Schwarzschild exterior. Their junction formulation gives
each shell's surface energy and pressure. The later
[Ng, Choo, and Lim model](https://arxiv.org/abs/2302.03192) also supplies
explicit capacitor interfaces. These are gravitational matching models with
specified surface stresses; a finite material constitutive law is a further
input.

For f=1-2M/r+Q²/r², the static junction relations used here are

    sigma = (sqrt(f_inner)-sqrt(f_outer))/(4 pi r),
    p = (f_outer'/sqrt(f_outer)-f_inner'/sqrt(f_inner))/(16 pi)-sigma/2.

The calculation fixes inner radius a=1 and samples outer radii b/a of 1.05,
1.2, 1.5, 2, 4, 10, and 30. Positive shell rest masses parameterize the
ordinary outward-facing junction branch. The electric gap and neutral
exterior have positive metric factors throughout their respective domains.
The 22,104,621 deterministic samples cover charge 0.01--1.15 and logarithmic
and linear grids of the two shell inventories. This is a bounded numerical
envelope, with the full parameter grid recorded for reproduction.

Two restrictions are imposed on each surface: sigma >= |p| and existence of
a local sound slope eta=dp/dsigma in [0,1] giving positive radial potential
curvature. The potential follows the fixed-charge shell treatment of
[Eiroa and Simeone](https://arxiv.org/abs/1102.1683):

    V = (f_inner+f_outer)/2 - y²/4 - (f_inner-f_outer)²/(4 y²),
    y = 4 pi r sigma,     Rdot² + V = 0.

Surface conservation gives y'=-4 pi(sigma+2p) and
y''=8 pi(1+2 eta)(sigma+p)/r. Each shell's electrovacuum mass and charge
parameters are held fixed under its independent local radial perturbation.
The test checks V''>0 and allows each shell its own slope. A finite-thickness
material, angular perturbations, thermodynamics, and driven charging require
their own equations. The different charge/mass assumptions in
[Reyes, Chiapparini, and Perez Bergliaffa](https://doi.org/10.1140/epjc/s10052-022-10107-4)
are kept separate; their uncharged stability boundary provides an independent
analytical control for the implementation.

The electric proper energy is integrated as

    U_E = Q²/2 integral_a^b dr/(r² sqrt(f_gap)).

An adaptive integral resolves the narrow metric minimum of strongly
gravitating examples. A separate 1024-point Gaussian integral checks every
selected result, agreeing within 5.8e-13 relatively. The infinity-normalized
Killing energy is also recorded with the exterior matching clock factor.
Thus proper volume, material rest energy, and energy measured at infinity
remain distinguishable.

### Boundary cost and shape

| Outer/inner radius | Best sampled field/wall rest energy, DEC and radial slope | Weak-gravity subset | Compressive surface envelope |
| --- | ---: | ---: | ---: |
| 1.05 | 0.04791 | 0.04742 | 0.00436 |
| 1.2 | 0.17885 | 0.17736 | 0.01812 |
| 1.5 | 0.39347 | 0.39347 | 0.04777 |
| 2 | 0.65645 | 0.65123 | 0.10359 |
| 4 | 2.73450 | 1.17747 | 0.50995 |
| 10 | 3.15597 | 1.61531 | 1.26050 |
| 30 | 3.27238 | 1.85169 | 1.36202 |

The weak subset uses max(2M_gap/a,Q²/a²,2M_outer/b)<=0.01 as a
small-self-gravity comparison. The compressive envelope additionally uses
0<=p<=sigma/2 and 0<=eta<=1/2, motivated by a surface kinetic-pressure
range. It remains an envelope of allowed stresses and slopes, with a physical
surface gas and its normal confinement still to be constructed.

The small-self-gravity behavior has a direct explanation. The inner shell
carries tension Q²/(16 pi a³), while the outer shell carries compressive
pressure Q²/(16 pi b³), to leading order. Applying the componentwise energy
bound gives

    U_E/(M_inner+M_outer) <= 2(b-a)/(b+a).

Consequently closely spaced spherical shells have a substantial wall cost.
Widening the gap improves this ratio, approaching 2 in the weak-gravity
limit. The economical sampled inner shells have tension about 95--99% of
their surface rest-energy density, and their outer shells have pressure of
similar magnitude. The admitted sound slope establishes a radial response
at one equilibrium; it supplies no identified material with that stress law.

The large ratios in the unrestricted columns use strong self-gravity. The
selected b/a=30 example has minimum f_gap about 0.000442, inner p/sigma
about -0.997, and outer p/sigma about +0.997. Its field proper energy is
about 3.14, while its infinity-normalized field energy is about 0.527 and
its two shell rest energies sum to about 0.960. Its geometry and clock
variation are substantial parts of the construction. Such an object requires
a joint local geometry and material solution before it can be assigned a
role in the prepared rail.

There is also a tensor-shape restriction. The electric directions of a
complete small spherical cell average isotropically over that cell. The rail
uses a radially aligned Maxwell stress. Extracting only the favorable energy
ratio from a round cell would omit this difference and the wall stresses.
An elongated or open-load field cell needs its own boundary calculation.

These controls leave an integrated load-transmitting capacitor as the relevant
construction target. The spherical family has acceptable mathematical
equilibria, while the economical finite material and the required rail tensor
remain unprovided by those equilibria.

## Evidence

The shell evidence is in [data/charged_capacitor_shells](data/charged_capacitor_shells).
Its manifest records the producer, model, tests, grid, numerical envelopes,
and quadrature verification. Eight focused tests cover the junction mass
identity, static potential, independent finite-difference stability,
published uncharged stability boundary, proper energy quadrature, Maxwell
tensor boost, and transverse-field work identities. Narrative reporting is
maintained manually in this supporting document.
