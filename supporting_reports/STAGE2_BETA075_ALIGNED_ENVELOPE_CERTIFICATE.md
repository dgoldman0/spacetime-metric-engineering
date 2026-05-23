# Stage II Beta075 Aligned-Envelope Certificate

## Status

Status: `aligned_envelope_pass_convex_kernel_bound`.

The service-aligned timing result now has a stronger proof-style certificate.
The previous sweep showed that a list of selected pulse widths behaved well.
This rung asks a broader question: once source release is ordered by service
coordinate, can the whole class of common nonnegative temporal kernels be
bounded without testing each kernel one by one?

For the fixed-background split-step transport model used here, the answer is
yes. The one-step service-aligned basis response bounds any common nonnegative
temporal kernel over the same service-ordered source bins by linearity and
positivity of the transport operator.

## Test Object

The certificate keeps the same sealed beta075 source and geometry package:

- dense `rematch_w6_t1p5` closure
- covariant endpoint medium and `24x14` support closure
- cap-0.95 support-source coupling law
- bounded rapidity transport variable
- active non-live support-source domain

The admissible timing class is now:

1. partition source rows by service coordinate into the service-ordered bins;
2. release those bins in the appropriate service direction;
3. allow any common nonnegative temporal kernel over that ordered release;
4. require the kernel weights to sum to one.

This is narrower than arbitrary row-independent impulse timing, but broader
than the finite pulse-width sweep. It captures the active-rail idea that the
whole service has one schedule law rather than every support row choosing an
independent adversarial release time.

## Result

Decision summary:

- status: `aligned_envelope_pass_convex_kernel_bound`
- scenario count: `3`
- live support exclusion: `True`
- max convex-kernel bound budget fraction: `0.742835`
- worst scenario: `observed_action_inward_forward`
- worst row: `194`
- max state/source ratio: `0.985750`

Per-direction basis bounds:

- outward/forward: `0.690041`
- inward/forward: `0.742835`
- outward/backward: `0.727448`

The certificate includes a 48-step tail after the source release window. The
tail does not increase the bound, so the worst rows are driven during the
service-ordered release itself rather than by delayed post-service
concentration.

The largest service-bin source fractions are also finite:

- forward service: max bin fraction `0.157857`
- backward service: max bin fraction `0.167668`

## Interpretation

This closes the timing gap at the level it was meant to close.

The arbitrary impulse adversary failed because it allowed all observed source
burden to arrive at once, independent of service order. The service-aligned
sweep then showed that selected physically meaningful schedules pass. This
certificate bridges those two reads: it shows that the pass is not an accident
of a few hand-picked pulse widths. Any common nonnegative temporal kernel over
the service-ordered bins is bounded by the one-step aligned basis response.

That matters because it turns "scheduled service seems fine" into a usable
proof obligation. The source-time law no longer needs a specially tuned pulse
shape. It needs service-order alignment and a common nonnegative temporal
kernel.

The worst remaining rows are still support-edge rows, as expected, but they are
watch rows inside the aligned timing class, not failing rows. The tightest
budget fraction stays below `0.75`, leaving meaningful headroom relative to the
local rapidity budget.

## Implications

The sealed beta075 package now has a coherent fixed-background timing story:

- arbitrary all-domain impulse timing is too broad and fails;
- service-coordinate-aligned finite pulse schedules pass;
- the convex-kernel envelope over the service-ordered bins also passes.

The next question is no longer whether scheduling matters. It does. The next
question is how much schedule imperfection the proof can tolerate.

## Next Rung

The next useful rung is bounded service-timing jitter.

The aligned-envelope certificate assumes exact service-coordinate ordering and
a common temporal kernel. A practical proof should now ask how much bounded
phase error can be tolerated without breaking local rapidity budgets:

1. allow small integer timing offsets around the service bin;
2. keep the offsets bounded and service-local rather than globally arbitrary;
3. certify the worst allowed jitter envelope against the same rapidity budgets;
4. preserve live exclusion, state non-amplification, and cone/transport margin.

This remains action-level fixed-background PDE work. It should not reopen
geometry, support-edge source shaping, or artificial high-amplitude tuning
unless bounded jitter fails in a way that points to a real physical mechanism.
