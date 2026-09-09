# Archived geometry controls under the longitudinal source gate

Date: 2026-09-09

## Bounded comparison

This investigation applies the newer integrated opening requirement to the
geometry alternatives recovered by the
[historical cross-reference](GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md).
The current repaired beta075 background is the common reference. Archived
parameter changes are transferred individually onto it, retaining the other
component controls. This tests their effect in the current construction;
the original Stage I and Stage II ledgers remain the evidence for their
historical embodiments.

The [candidate specification](../toolkit/adm_harness_cli/specs/archived_geometry_opening.json)
contains thirteen cases: the reference; support radii 1.90 and 2.05; angular
widths 1.80 and 2.20; radial core gains 0.04 and 0.06; the previous and broader
catch rings; the ring-only comparison with the later skirt removed; and three
receiver/beta controls. The latter verify the difference between a control's
service role and its activity on the selected static phase.

The phase is 0.745, matching the retained quantum-construction geometry.
The metric has the existing C2 receiver, origin, and shell repairs. The test
uses that metric directly through its tabulated lapse, radial scale, and
areal radius. The saved condensate exterior and material solution remain
specific to their original background. The present necessary gate instead
grants every remaining component an arbitrary aggregate tensor whose radial
null projection is nonnegative.

## Source and service conditions

The source is the same ideal longitudinal conformal channel law used in the
[coupled reorientation](COUPLED_REORIENTATION_INVESTIGATION.md), with constant
total central charge along each tested interval. Gravitational normalization
and central charge are held fixed across candidates. The eleven strengths
are one central-charge unit and the ten coefficients corresponding to
`k/R0_reference² = 1e-6, 1e-5, 1e-4, .001, .01, .03, .1, .3, .6, .9`.
Each candidate's own `k/R0²` is also recorded.

Intervals are `[-3,3]`, `[-5,5]`, and `[-7,7]` in the existing radial
coordinate. The shorter intervals deliberately grant a shorter optical path.
Any channel spanning a tested interval has at least its optical length;
setting the exterior return to zero therefore gives optimistic supply.
Clock variations receive independent pointwise boxes of 0%, 10%, and 50%,
with the interval's endpoint jets retained. Their upper bound grants the
largest numerator and shortest optical length separately. The clock boxes
are exclusion tests whose service admissibility remains open.

The scalar service check preserves the selected live start, restored arrival,
V5 schedule, and packet radius. It samples 65 times and 41 packet offsets,
recomputes the packet norm with the repaired metric, and records the two
centerline transport proxies. A non-timelike sample rejects a transfer at this
level. A clean scalar screen leaves the established full carrier, source,
quiet-packet, and component-exchange requirements for any promoted candidate.

## Independent form of the opening identity

For `dl = B dx`, `a = log A`, and
`W = exp[-(R²-R0²)/(2k)]`, the required integrated opening is

\[
D=\int W\frac{R R''}{k}\,dl+[Wa']
 =\int W\left(\frac{R^2}{k^2}-\frac1k\right)(R')^2\,dl
  +\left[W\left(a'+\frac{RR'}k\right)\right].
\]

Primes denote proper derivatives and brackets retain both endpoints. The
available Casimir contribution is

\[
S=\frac{4\pi^2}{L_{\rm opt}^2}\int\frac{W}{A^2}\,dl,
\qquad S-D=\frac{4\pi}{k}\int W R^2 H_{\rm rem}\,dl.
\]

For the tested coefficients below the minimum radius squared, the bulk term
in the first-derivative form is nonnegative. It also avoids cancellation
between positive and negative radius second derivatives. The calculation
compares this expression with the original curvature form and with a direct
Einstein-minus-quantum null integral.

Composite Gaussian quadrature integrates in the native coordinate with the
proper measure B. It includes a focused throat mesh for the smallest quantum
coefficient. The registered comparison uses 8,193 and 16,385 metric samples,
and eight- versus sixteen-node Gaussian quadrature. A relative discrepancy
above 0.001 stops the corresponding calculation for refinement. Reported
exclusions retain a margin larger than the measured sampling difference.

The static tensor summary separately records negative energy, negative radial
null stress, and absolute angular pressure with proper-volume weighting.
These quantities describe demanded stress on each candidate. They retain
the distinction between source allocation and supplied material/quantum stress.

## Resource and continuation limits

The computation uses four processes, single-thread numerical libraries, a
900-second calculation allowance, and a 20 MB output allowance. Metric samples
and scalar tables provide the retained evidence. A complete spacetime ledger
and an absolute quantum mode sum become relevant only after a candidate
survives the necessary source gate and its applicable service checks.

The comparison first asks whether the archived controls materially improve
the fixed-strength opening ratio or remove an existing exclusion. If the
small-coefficient route remains excluded even with the generous clock box,
and the retained alternatives provide only incremental changes, this round
ends at that barrier. Larger coefficients remain explicitly recorded so that
the result distinguishes geometry relief from added quantum-source strength.
