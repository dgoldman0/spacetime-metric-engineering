# White Casimir Source-Function Audit Method Note

Status: `stage2_scalar_proxy_smoke_pass_with_method_limits`.

## Purpose

The White et al. Casimir/Alcubierre-shell intersection is a useful external
test of the engineering habits developed in the active-rail work. The point of
this side audit is not to reframe the White geometry as an active rail, and it
is not to import active-rail service ratings, packet ledgers, beta-collar
provenance, or operating-point claims. The point is narrower and cleaner:
apply the general spacetime metric engineering discipline to a separate
Casimir-geometry question and see whether it sharpens the interpretation.

The transferable engineering idea is source-function auditing. A stress pattern
is treated as an engineered subsystem with roles, channels, controls, and
observables. A visual negative-energy morphology is therefore not enough by
itself. The audit asks what source channel the morphology supplies, whether the
channel is tensorially aligned with the comparison target, whether the scale is
even remotely competitive with the target source demand, whether the proposed
readout path couples to that channel, and whether ordinary electromagnetic
readout effects dominate the measurement.

## Engineering Transfer

The White audit now uses an explicit claim manifest. It states the paper,
architecture under test, geometries, proposed observable, and provenance
quarantine. This keeps the simulation from drifting into hidden active-rail
assumptions.

The geometry layer is role-labeled before any physics calculation. The
plate-pillar and sphere-cylinder systems are separated into boundary
infrastructure, stress-shaping body, source-shell candidate, transit/readout
channel, ordinary electromagnetic competitor region, and far-field control.
That role map is an engineering object: it says what each physical feature is
supposed to do before the numerical field is interpreted.

The readout channel is modeled separately. White et al. propose comparing a
current, photon, or electron transit path through the center of an array against
a control path. In this audit that path is not treated as evidence implied by
the Casimir torus. It is a first-class readout/ordinary-EM channel, and it must
earn any spacetime interpretation through later metric, null-channel, and
ordinary-competitor checks.

The scoring ladder is also stricter than a reproduction-only project. Density
morphology can support a Casimir-shaping result. Finite-difference stress
proxies can support only a proxy-level source-function label. A stronger
source-function label requires tensor-channel output, and Alcubierre-shell
relevance additionally requires a source-demand magnitude ratio. Transport
relevance requires non-negligible transit/readout coupling and an ordinary-EM
competitor audit that does not dominate.

This is the distinct contribution of the spacetime engineering approach. It
does not replace the White worldline calculation. It gives the calculation a
claim ladder with role-specific controls and interpretation gates.

## Current Implementation

The first committed stage created:

- the revised protocol under `white_casimir_intersection/`;
- the source paper archive;
- an experiment package at
  `white_casimir_intersection/experiments/white_casimir_source_function_audit/`;
- geometry and role-labeling code;
- a conservative scoring module;
- a claim manifest and role metadata;
- role figures for the plate-pillar and sphere-cylinder systems.

The second working stage adds a scalar worldline smoke path. It uses
Brownian-bridge closed loops and labels all output as a reproduction proxy, not
as the exact White et al. v-loop method. The exact v-loop/C++ path remains the
next reproduction-grade requirement.

## Stage 2 Smoke Read

The scalar proxy smoke passes the first validation checks:

```text
plate mean proxy negative: true
plate midplane symmetry relative error: 0.102105
gap scaling pass: true
gap 2 um mean negative magnitude: 1.087966
gap 4 um mean negative magnitude: 0.107803
gap 8 um mean negative magnitude: 0.009735
```

This is a useful sanity result. The proxy detects a negative plate interaction,
keeps the plate result approximately symmetric at smoke resolution, and weakens
as the gap increases. It therefore exercises the loop generator, body
intersection, grid accumulation, metadata, plotting, and validation path.

The sphere-cylinder smoke field is not yet an interpretation-grade morphology
result:

```text
sphere-cylinder proxy minimum: -5.861237
sphere-cylinder proxy mean: -0.442956
negative proxy pixels: 625 / 625
```

That output is interesting mostly as a harness diagnostic. It confirms that the
current proxy sees loop intersections in the sphere-cylinder geometry, but the
coarse Brownian-bridge smoke setup and thickened boundary model make the field
too globally negative to claim a resolved toroidal shell. The next useful
physics step is to make the scalar reproduction spatially discriminating, not
to interpret the current smoke image as support for the Alcubierre analogy.

The throughput estimate is also informative. The current Python proxy estimates
a paper-sized `100 x 100`, `2000` loop, `1000` point run at about `3` hours
on the local machine. This says a full Python proxy run is plausible as a
diagnostic, but it should not be confused with the exact v-loop calculation or
a high-performance reproduction. The exact method still deserves its own
benchmark and likely a C++/MPI path if the audit moves beyond smoke/proxy
scope.

## Current Interpretation

The current evidence supports the audit method and the software path, not the
White/Alcubierre physical claim. The role-labeling and scoring structure are
now in place, the plate validation behaves in the expected direction, and the
sphere-cylinder geometry is wired through the same proxy machinery.

The stronger scientific question remains open. To earn a Casimir morphology
result, the scalar worldline calculation must reproduce a localized
sphere-cylinder shell/torus robustly across seeds and grid assumptions. To earn
source-function relevance, the audit needs stress or tensor channels, not just
negative density. To earn Alcubierre-shell relevance, those channels must match
the source-demand target in sign, placement, tensor content, and magnitude. To
earn transport relevance, the proposed readout path must show a non-negligible
metric/null/shift-source channel that survives ordinary EM competitor tests.

This is exactly why this intersection is worth doing. It gives a concrete case
where spacetime metric engineering is not a specific active-rail design, but a
disciplined way to ask what a stress pattern actually does.

## Next Gates

The next implementation gate is exact loop-generation alignment. The v-loop
method described in the White paper should replace or stand beside the current
Brownian-bridge smoke generator, with both methods labeled in metadata.

The next validation gate is spatial discrimination. The sphere-cylinder proxy
should resolve whether the negative region is actually toroidal/lenticular and
whether that morphology is robust under seed, grid, scale-grid, wall-thickness,
and assumed cylinder-length changes.

The next interpretation gate is source-channel accounting. Stress proxies can
be explored by virtual displacements, but the report-grade source-function
claim requires tensor-channel output or an imported validated worldline
energy-momentum tensor calculation for the same geometry.

The next observable gate is ordinary-EM competition. Capacitance, impedance,
waveguide/dispersion, contact loading, patch potentials, and material response
must be estimated before a transit-time result can be interpreted as spacetime
relevant.
