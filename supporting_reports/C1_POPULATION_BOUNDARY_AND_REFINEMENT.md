# C1 population boundaries, radial refinement and finite coverage

17 September 2026. Normalized source continuation from the
[joint population and mesh comparison](C1_JOINT_SOURCE_MESH_SCREEN.md).

**Separate radial and angular placement changes remove the measured
nine-coordinate obstruction using the existing two quantum source laws.**
Four subdivisions in each radial cavity adjoining coordinate 0.51785,
combined with an angular boundary at 0.30, admit sampled bulk allocations.
Their continuous spatial coverage and finite material/exterior completion
remain open. A resolved residual immediately beyond the new angular endpoint
identifies the next construction duty.

This comparison applies the [source-feasibility workflow](SOURCE_FEASIBILITY_WORKFLOW.md)
and the provisional [C1 topology](RAIL_BUILD_TOPOLOGY_DECISION.md).
Independent source extents and confinement scales are active design variables.
The results support a bounded placement revision as a source-feasibility
trial; the finite assembly remains under construction.

## Geometry, placement and overlap

The archived static reference, its normalization, Maxwell solution and outer
material envelopes are retained. The two quantum laws remain the radial
1+1 conformal strip and the four-dimensional conformal scalar. Radial walls
are transparent to the scalar sector. Each scalar cavity uses its actual
Dirichlet interior solution, including the calculated change of state when
its boundary changes.

The representative allocation below is refinement case 35: four subdivisions
per old radial cell, a common population across the refined pair, and the
fixed global curvature-coupling case with reference logarithm 2.

| Quantity | Earlier six-coordinate grouped allocation | Representative expanded trial |
|---|---|---|
| Geometry and static slice | Archived reference | Unchanged |
| Outer material envelopes | Left \([-3,2.5]\), right \([0.5,3]\) | Unchanged |
| Electric overlap | \([0.5,2.5]\) | Unchanged |
| Left radial partition | 32 cavities | 38 cavities: two existing cavities become eight |
| Added radial reflector coordinates | None in this comparison | 0.282463, 0.356946, 0.434808, 0.607777, 0.704411, 0.807541 |
| Adjustable radial groups | Five | Six; the eight refined cavities share one population |
| Occupied left radial extent | \([-1.654425,0.517851]\) | \([-1.654425,0.916173]\) |
| Occupied right radial extent | \([0.55,2.95]\) | \([1.501608,2.95]\) |
| Overlap of occupied radial populations | Empty | Empty |
| Occupied left scalar interior | \([-2.95,2.45]\) | \([-2.95,0.30]\) |
| Occupied right scalar interior | \([0.55,2.95]\) | Unchanged |
| Overlap of occupied scalar interiors | \([0.55,2.45]\) | Empty |
| Left radial / right scalar overlap | No positive-width interval | \([0.55,0.916173]\) |

The trial at logarithm 1 also populates the left scalar cavity
\([0.30,2.45]\), preserving its overlap with the right scalar. Consequently
the angular boundary at 0.30 acts as an internal division for that allocation,
whereas it becomes the occupied left scalar endpoint in the logarithm-2
allocation. The stored case records specify both possibilities.

Occupied interior intervals describe supplied terms in the source ledger.
The exterior quantum state and reflector material supply separate terms.
In particular, the interval \(0.30<x<0.55\) retains radial and Maxwell
contributions while its exterior scalar contribution remains to be calculated.

## Normalized source at the population boundary

The added absolute scalar calculations use coordinates 0.2768310546875,
0.4 and 0.5178507081509361. Together with the previous six coordinates they
give nine distinct bulk locations. Both radial limits are evaluated at
0.4 and 0.5178507081509361, giving eleven bulk samples. A radial wall
leaves the scalar interior solution continuous; each radial limit uses its
own occupied cavity and optical length.

The following tensors are per real scalar field, after multiplication by
\(\eta=2.4127904527582454\times10^{-5}\), in the retained source units.
They describe the original whole left cavity at reference logarithm 1.

| Coordinate | \(\rho_\phi\) | \(p_{r,\phi}\) | \(p_{t,\phi}\) |
|---|---:|---:|---:|
| 0.276831 | \(-1.11597\times10^{-10}\) | \(9.28899\times10^{-11}\) | \(-5.79735\times10^{-11}\) |
| 0.400000 | \(-6.49723\times10^{-10}\) | \(-9.96544\times10^{-11}\) | \(-2.61437\times10^{-10}\) |
| 0.517851 | \(-9.04149\times10^{-10}\) | \(1.06405\times10^{-9}\) | \(4.28641\times10^{-10}\) |

The other fixed coupling uses the previously specified relation
\(T_\phi(\ell)=T_\phi(1)-2(\ell-1)H\). The same value of \(\ell\) applies to
every scalar population in a case. Its physical finite curvature couplings
remain an assumption of that case. A subtraction convention alone preserves
the complete semiclassical balance.

The existing six-coordinate allocations fail the expanded spatial checks.
For example, the logarithm-1 grouped allocation leaves
\(\rho-p_r=-0.38632\) in the remainder at the left limit of 0.517851 after
the calculated scalar contribution and empirical numerical envelope.
This replaces the earlier diagnostic that contained only the radial source.

## What the fixed partitions constrain

The first 84 comparisons cover seven radial arrangements, three scalar
arrangements, two global coupling cases and nominal/empirical numerical
envelopes. The radial arrangements include fixed populations, shifted
population-group boundaries, an independently controlled bridge group,
independent existing cells and an added radial wall at 0.35 or 0.4.
The scalar alternatives are the whole module and independently populated
divisions at 0.10 or 0.30. All 84 fail the combined sampled inequalities.
Each failure has an independently checked linear exclusion certificate.

A local certificate explains part of this result. At coordinate 0.517851,
let \(D=G/(8\pi)-T_{\rm Maxwell}\) and

\[
 F(T)=(\rho-p_t)+0.4029147552(\rho-p_r).
\]

An ordinary material satisfying the dominant energy condition has
\(F(T_{\rm material})\geq0\). The demanded value is
\(F(D)=-0.0157109503\). For the original radial optical length
0.2232325446, the radial tensor has \(F(T_r)=0\). In the logarithm-2 case,
each available scalar population has nonnegative \(F\) at that location;
the populated local column gives \(5.258\times10^{-10}\) per field in the
whole cavity or \(3.159\times10^{-10}\) after the division at 0.30.
Increasing these populations preserves the incompatible sign.

This certificate concerns the specified local tensor ratios and confinement.
Shortening the radial cavity changes its Casimir contribution while
preserving the anomaly coefficient

\[
 \rho_r-p_{r,r}
 =\frac{\eta c}{48\pi^2 R^2}\left(a''+a'^2\right),
 \qquad a=\log A ,
\]

where primes denote proper-distance derivatives. The useful next variable
is therefore the radial optical length on both sides of the boundary.

## Two-sided refinement and its costs

The refinement comparison subdivides old left radial cells 21 and 22 into
two, four or eight equal-optical-length cavities each. Their original
combined extent is \([0.212974,0.916173]\). The original wall at 0.517851
stays in place. Population controls either share one setting across the pair
or use one setting per original cell. All other partitions retain their
original walls.

| Radial subdivisions per old cell | Added radial walls | Whole scalar or division at 0.10 | Division at 0.30 |
|---|---:|---|---|
| 2 | 2 | Fails sampled inequalities | Fails sampled inequalities |
| 4 | 6 | Fails sampled inequalities | Passes at logarithms 1 and 2 |
| 8 | 14 | Fails sampled inequalities | Passes at logarithms 1 and 2 |

These outcomes hold for both population patterns and for the nominal and
empirical numerical comparisons: 16 of 72 refinement cases pass, including
eight cases with the numerical envelopes included. They establish sampled
bulk allocations with an optimistic ordinary-material remainder.

The six-group logarithm-2 allocation uses about 24.97 million left scalar
fields, 32,917 right scalar fields and zero population in the left scalar
suffix. Its common radial central charge across the eight refined cavities
is about 190,933 per cavity. The earlier throat group has central charge
22,194 per cavity. The quantum mechanism count remains two.

The six groups count adjustable radial controls in this comparison. Right
module cells 8 through 23 retain their previous individual populations;
those sixteen existing cavity settings remain part of the assembly's
configuration and inventory.

Radial subdivision changes several different costs. At fixed population,
fourfold shortening multiplies the local Casimir part by sixteen. The
carrier-extent proxy \(\sum_j c_j L_{{\rm proper},j}\) is invariant under
repartitioning with the same population, whereas \(\sum_j c_j\) increases.
The optimization uses proper-length-weighted radial charges and scalar
copy populations as a heterogeneous extent proxy. Material mass and total
construction cost require additional source laws.

The radial bulk energy has an independently checked volume integral:

\[
 E_{K,j}=\eta c_j\left[
 -\frac{\pi}{24L_{{\rm opt},j}}
 +\frac{1}{24\pi}\int_j A B(2a''+a'^2)\,dx
 \right].
\]

It is the signed Killing energy in the retained time normalization.

| Logarithm-2 allocation | \(\sum c_j\) | \(\sum c_jL_{{\rm proper},j}\) | Radial bulk \(E_K\) | Sum of absolute radial net wall forces |
|---|---:|---:|---:|---:|
| Previous five groups, six coordinates | \(1.885\times10^6\) | \(7.556\times10^6\) | \(-63.49\) | 17.77 |
| Four subdivisions, six groups | \(2.276\times10^6\) | \(6.823\times10^6\) | \(-108.24\) | 18.65 |
| Eight subdivisions, six groups | \(1.521\times10^6\) | \(4.970\times10^6\) | \(-108.69\) | 18.65 |

The earlier allocation fails the expanded spatial test and supplies a cost
reference only. The comparison records field extent, signed energy and
mechanical exchange as separate costs.

For the four-subdivision representative, the largest left-module net radial
wall force is 1.488. The largest force across both modules remains 14.492,
at a right-module wall. Equal populations in equal-optical-length cavities
cancel the net radial traction at the six newly inserted walls to numerical
precision. Their individual face loads remain substantial: the largest
one-face area-integrated force is 2.420, and the sum of absolute face loads
across the new walls is 14.884. Reflector stress, mass and transverse
confinement therefore remain physical demands.

The scalar calculation also retains finite force changes at the original
module ends. Those increments are tiny for these particular division
coordinates. The absolute stress, surface energy and material at the new
scalar boundary are additional uncomputed terms.

## Remaining coverage and the next construction

For the representative logarithm-2 allocation, a 1,025/4,097-point check
between the occupied scalar interiors, supplemented by radial wall limits,
finds

\[
 (\rho+p_t)_{\rm remainder}=-0.00796195
 \quad\text{at }x=0.300001 .
\]

Here the known assigned sources are Maxwell plus radial channels. The
exterior scalar state and the new angular-end material remain unsupplied.
This is a resolved remaining duty of the trial after its sampled bulk
improvement. The logarithm-1 allocation keeps a populated scalar suffix;
its absolute profile between the existing probes is a separate calculation.

The next construction should compare the neighborhood of the angular
division/end at 0.30 with its finite material and exterior state, including
overlapping scalar interiors or a populated suffix where useful. The
radial refinement supplies a controlled comparison for that work.
Confinement response, population extent and boundary exchange enter
together. A geometry revision remains available if those measured costs
justify changing the transport reference.

Microscopic field multiplicities, achievable reflection, the ordinary
material constitutive tensor, global exterior completion and time-dependent
C1 handoff remain open. Scalar copy counts and radial central charges are
continuous allocation variables in this screen. The static comparison
provides source-placement evidence for the finite construction.

## Numerical controls and reproduction

The absolute calculation uses paired cutoffs 16 and 32 at regulator masses
8, 16 and 24, with a combined shooting/interpolation/frequency control at
0.517851. Raw one-field component envelopes are \(6.23\times10^{-8}\),
\(1.62\times10^{-7}\) and \(8.80\times10^{-7}\) at the three added coordinates.
They include trace, regulator-fit and measured numerical discrepancies.

The finite scalar response uses 40 initial calculations, six finer-grid
controls and six independent shooting integrals. The finite-volume Ward
check nearest the 0.30 wall is sensitive to differentiation and resolution;
the additional original-field mode checks and shooting integrals independently
check its local stress. All measured component variations enter the
empirical allocation envelope. This envelope is a numerical sensitivity
measure. Six original-mode checks agree with the absolute shooting kernel
to a maximum component difference of \(1.10\times10^{-11}\).

Independent audits reconstruct all 156 allocation results or exclusion
certificates, thirteen radial cost layouts and the refined angular-gap
profiles. The seven C1 test files pass 61 tests, including three new tests
of refinement costs, clock normalization and one-sided force accounting.
The closing validator verifies 222 manifest hash entries.

The [data directory](data/c1_population_boundary/validation.json) contains
normalized tensors, mode artifacts, declarations of occupied intervals,
cost matrices, exclusion certificates and execution snapshots. Numerical
drivers support independent process workers; four workers are the production
setting, with single-thread BLAS.

From the repository root, set:

    export PYTHONPATH=toolkit/adm_harness_cli
    export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1

Run these scripts in order under toolkit/adm_harness_cli/scripts:

    python toolkit/adm_harness_cli/scripts/screen_c1_population_boundary.py --workers 4
    python toolkit/adm_harness_cli/scripts/control_c1_population_boundary.py --workers 4
    python toolkit/adm_harness_cli/scripts/shoot_c1_boundary_response.py --workers 4
    python toolkit/adm_harness_cli/scripts/assess_c1_population_boundary.py --workers 4
    python toolkit/adm_harness_cli/scripts/refine_c1_population_boundary.py --workers 4
    python toolkit/adm_harness_cli/scripts/audit_c1_population_boundary.py --workers 4
    python toolkit/adm_harness_cli/scripts/audit_c1_population_boundary.py --workers 4 --refinement
    python toolkit/adm_harness_cli/scripts/validate_c1_population_boundary.py

The associated tests run with:

    python -m pytest toolkit/adm_harness_cli/tests/test_c1_*.py -q

The numerical production stages require empty output directories. Reproduce
them in an isolated checkout with this milestone's generated data removed,
while retaining the parent evidence. The assessment, audit and validation
stages can be rerun against the committed numerical evidence.
