# Vacuum Stress and Supporting Material Selection

Date: 8 September 2026.

## Question and registered comparisons

The [two-current calculation](COMER_TWO_CURRENT_EVOLUTION_ROUND.md) supplies
independent ordinary particle and entropy evolution. Its explicit radial
tension has zero radial enthalpy, while the retained initial rail requires
negative radial enthalpy throughout the annulus. This investigation examines
vacuum stress as the additional signed sector and includes the stress of
the material associated with it.

The initial metric and all three diagonal Einstein-tensor channels remain
fixed. The source reference and its interpolation are the same as in the
two-current calculation. Four initial ordinary states are registered:
zero preload; preload fraction 0.01 with zero drift; fraction 0.01 with
particle drift amplitude 0.04; and fraction 0.1 with drift amplitude 0.04.
The entropy current initially opposes the particle current. Thus the net
initial current is zero in every case.

Round one compares a radial planar Casimir stress, a superposition with two
equal angular orientations, and the mechanical cost of independently
supported planar cells. For each vacuum split, the material remainder must
have nonnegative energy and principal pressures bounded in magnitude by
either its energy or half its energy. The first is the static dominant
energy condition; the second reserves a finite stress margin. Both are
necessary algebraic conditions, with constitutive and characteristic
conditions assessed separately.

The optimization minimizes the magnitude of the negative vacuum energy at
each radius. It uses 513, 1,025, and 2,049 evaluation points. These grids
refine the sampling and quadrature of the retained interpolant. The source
reference itself stays frozen. Independent linear programs will check the
vertex solver, including infeasible cases and controls. All split energies,
pressures, orientation weights, and material margins will be retained.

A second round is conditional on finding complete algebraic tensor fits.
It will examine the local constitutive dynamics of the same vacuum-plus-
material family, using a covariant stored-energy action and its quadratic
perturbations. Any failure of a necessary kinetic condition ends that
family before a new global evolution. Further fitted components and
changes to the rail's initial geometry fall outside these two rounds.

The computation uses four independent worker processes, single-thread
numerical libraries, a 600-second compute allowance, a 1,536 MiB address-space
limit per worker, and a 30 MB evidence allowance. Narrative findings are
written manually after each completed round.

## Source models and scope

[Brown and Maclay](https://www.quantumfields.com/old/brownmaclay.pdf), equations
(6)–(9), give the electromagnetic vacuum stress between ideal, static,
parallel conducting plates. With the plate normal radial, its source-frame
channels are
\[
(E_Q,P_{r,Q},P_{t,Q})=(-C,-3C,C),\qquad
C=\frac{\pi^2\hbar c}{720a^4}>0.
\]
Two equal angular orientations and one radial orientation give the
algebraic family
\[
E_Q=-C_r-2C_t,\quad P_{r,Q}=-3C_r+2C_t,\quad
P_{t,Q}=C_r-2C_t,\qquad C_r,C_t\geq0.
\]
Its radial and angular enthalpies are respectively \(-4C_r\) and
\(-4C_t\). These independent weights provide an optimistic tensor family.
Actual intersecting cavities require their own field calculation; their
vacuum stresses generally depend on the complete boundary geometry.

[Schwartz Perlov and Olum](https://arxiv.org/abs/hep-th/0307067v2) calculate
a minimally coupled scalar vacuum outside a reflecting spherical boundary.
That model has negative radial null projection and nonnegative azimuthal
null projection. Its directional signs make it a useful radial comparison;
regions of negative required angular enthalpy require additional structure.

[Costa and Matsas](https://arxiv.org/abs/2112.08881v3), equations (12)–(16),
include the auxiliary matter sustaining the planar vacuum. The normal
pressure needed to oppose its attraction is \(3C\). Matter satisfying the
dominant energy condition carries at least that much energy, leaving a
positive total energy of at least \(2C\) per cavity volume before adding
further plate mass. We apply this bound to independent static cells in
their locally flat limit. A curved structure carrying external traction
requires its own balance equations and lies beyond that cell argument.
