# Finite cavities and short magnetic circuits: source comparison

Date: 9 September 2026.

Both evaluated assemblies supply useful quantum stress, but their counted
material or field costs make the net opening negative. The finite scalar
mirrors dominate the cavity interaction. The magnetic field at a closed
circuit's turns dominates its longitudinal vacuum. These results support
shelving the specified cavity construction and end the local magnetic-circuit
parameter search. Magnetic channels remain the more informative literature
analogue, with a concrete requirement for any further adaptation: change the
global return geometry or the relation between mode count and confining stress.

## Common geometry and component responsibilities

Both calculations use the repaired native static rail at phase 0.745 from
the [retained metric](data/archived_geometry_opening/reference_metric.npz),
with gravitational conversion
\(\eta=2.4127904527582454\times10^{-5}\). Its complete opening requirement
is approximately 2. The common diagnostic is

\[
B=-4\pi\int\frac{R}{A}(\rho+p_r)\,dl,
\]

with \(\eta\) applied when converting microscopic tensors. A positive
contribution helps the opening. The backbone, angular response, transport
and reservoir retain the roles set out in the
[component architecture](RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md).
Their additional radial-null cost is granted the favorable value zero in
these screens. Each proposed quantum component must first overcome the
positive null stress of its own explicitly counted mirrors or magnetic field.

The two computations have different levels of quantum resolution. The cavity
uses a spherical scattering determinant and its metric derivative for the
finite interaction stress. The magnetic screen grants ideal longitudinal
channels and includes their Casimir term and Weyl anomaly, then counts the
Maxwell field over every segment of the closed path. Its full transverse
spectrum and supporting currents remain construction requirements.

## Results

| Candidate | Useful supplied effect | Counted obstacle | Bounded outcome |
| --- | --- | --- | --- |
| [Finite curved cavities](NARROW_CURVED_CAVITY_EVALUATION.md) | Every selected curved cavity has helpful proximity-induced quantum opening. | Canonical gradients of the material fields that make the mirrors. | All nine curved placements fail at portal couplings 1, 4 and 10. Crossing couplings are approximately 17,438–24,191. |
| [Short magnetic circuits](SHORT_MAGNETIC_CIRCUIT_EVALUATION.md) | 303 of 440 paths have helpful longitudinal quantum opening on the native rail. | Magnetic radial-null stress where the complete field path turns. | All 23,760 source combinations fail for each of two field prescriptions. The best load-to-vacuum ratio in the preferred coupling ladder is approximately 355. |

For the cavities, decreasing the gap at fixed optical shape increases both
the useful interaction and the mirror gradients at nearly the same rate.
Keeping the physical mirror height and thickness fixed gives a modest gain:
a sixteenfold gap reduction increases integrated interaction support by only
about 1.67. Finite transparency limits the improvement. Wider planar mirror
profiles lower the inferred crossing coupling to approximately 11,467, still
far above the registered values. The uncomputed isolated-layer absolute
vacuum is a separate mechanism from the proximity enhancement measured here.

For the magnetic loops, the short optical paths resolve the quantum-sign
problem on many geometries. Their field still carries positive radial-null
stress at each turn. Allowing local field spreading reduces this cost by
more than 99.9% on some long paths, yet the best complete threshold changes
only slightly. Its required \(N_fe^2/(16\pi^2)\) is 17.971, compared with
the preferred perturbative limit 0.1. A flat circular loop independently
requires a value above 18 under the most favorable registered flux and
bend margin, explaining why shrinking a loop gives little improvement.

The cavity portal coupling and the magnetic loop-expansion measure belong
to different field theories. Their numerical thresholds express each
model's deficit; the direct physical comparison is the useful quantum
opening against that model's counted positive load.

## What remains interesting about the magnetic analogue

[Maldacena, Milekhin and Popov](https://arxiv.org/html/1807.04726v3)
provide a concrete relation between magnetic flux and the number of light
quantum channels. Their flux threads the wormhole and closes through the
exterior. That global arrangement and its clock profile differ from the
contractible local circuits evaluated here. The rail adaptation therefore
has a specific design question: can a complete path preserve short optical
length and useful light modes while placing sufficiently little weighted
magnetic stress in its turns?

The present scans identify no such arrangement. They also show why simply
adding flux, shrinking capsules, or allowing their fields to spread is
insufficient in this family. Another useful magnetic evaluation requires an
explicitly different global return construction or a different microscopic
relation between modes and confinement. Reassigning the same Maxwell load
to a separate support component leaves the integrated result unchanged.
The larger-channel Randall–Sundrum construction remains a different theory
with its own geometry and service-matching requirements, as recorded in the
[literature comparison](LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md).

Consequently neither assembly supplies a complete rail source or advances
to the full An–T–Le construction. The magnetic analogue gives the sharper
next selection criterion; a viable candidate satisfying it remains to be
identified. This is the stopping point for both bounded local searches.

## Evidence and resource use

Each calculation passes five scientific tests and independent convergence
checks. The cavity's largest measured outer-boundary sensitivity is 0.180%,
with its material deficit intact. The magnetic refinement preserves every
source failure; the best thresholds change by less than
\(7.50\times10^{-8}\) under the final quadrature check. Full controls and
reproduction commands accompany the individual reports.

The retained numerical evidence occupies approximately 11.40 MB in total:
3.60 MB for cavities and 7.81 MB for magnetic circuits. The largest observed
worker resident sets are approximately 87 MiB and 71 MiB respectively.
The cavity model and results are committed in `e2dc588` and `92b997b`;
the initial magnetic model is committed in `283a91e`. Source hashes in both
audits connect the retained calculations to their implementations.
