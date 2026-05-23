# Stage II Beta075 Full 1+1 Constitutive Proof Obligation

## Status

Status: `constitutive_1p1_observed_class_proof_obligation_pass`.

The observed-amplitude `1+1` constitutive source-coupled system now has a
proof-obligation certificate at the fixed-background, discrete-PDE level. This
is a different kind of rung from a stress sweep. It states the admissible class
and checks the pieces an academic reader would expect to see before taking the
model seriously as a physical proposal:

- bounded phase-local source law;
- service-coordinate scheduled release;
- bounded common timing jitter;
- positive split-step radial/service transport;
- no state/source amplification;
- local rapidity-budget invariance;
- live and packet-live exclusion;
- limiter inactivity for the observed class.

The certificate passes all eight obligations over the observed class.

## Test Object

The certified class uses the sealed beta075 package:

- dense `rematch_w6_t1p5` closure
- covariant endpoint medium and `24x14` support closure
- cap-0.95 phase-local support-source law
- service-aligned source release
- bounded rapidity transport variable
- active non-live support-source domain

The proof class contains `51` observed-amplitude cases:

- outward/forward, inward/forward, and outward/backward transport;
- common service-timing offsets from `-8` through `+8`;
- no budget limiter in the certified evolution.

The machine output is structured only:

`toolkit/adm_harness_cli/runs/stage2_beta075_constitutive_1p1_proof_obligation/`

## Result

Decision summary:

- proof status: `constitutive_1p1_observed_class_proof_obligation_pass`
- obligations: `8`
- failed obligations: `0`
- scenario count: `51`
- tested jitter radius: `8`
- max observed budget fraction: `0.742835`
- worst scenario: `proof_observed_inward_forward_offset_p0`
- worst row: `194`
- max state/source ratio: `0.985750`

Obligation summary:

| obligation | result | measured value | bound |
| --- | --- | ---: | --- |
| live and packet-live exclusion | pass | `0` | `0` |
| phase-local bounded source law | pass | `0.092617` min scale | `0 <= scale <= 1`, scaled slices only in entry/catch support-edge scope |
| source nonnegativity | pass | `0` negative rows | `0` |
| bounded common jitter schedule | pass | radius `8` | radius `8` |
| positive transport semigroup | pass | max CFL `0.4` | CFL in `[0, 1]` |
| transport L1 non-amplification | pass | `0.985750` | `<= 1` |
| observed budget invariance | pass | `0.742835` | `1.0` |
| limiter inactivity implied | pass | `0.742835` | `0.95` |

The transport certificate is simple and important. The radial steps use CFL
`0.4`, and the service steps use CFL `0.2`. In each direction the upwind map
has nonnegative convex coefficients, maps nonnegative state to nonnegative
state, and is L1 non-increasing for nonnegative state with boundary outflow.

The source law remains bounded and phase-local:

- `entry_precatch / support_edge`: `17` slices, `2` scaled, min scale
  `0.092617`
- `catch_rematch / support_edge`: `29` slices, `2` scaled, min scale
  `0.192932`
- no scaled slices outside the intended entry/catch support-edge scope

The common timing-offset class does not worsen the budget maximum. The worst
case remains the exact aligned inward/forward row `194`; radius `8` reaches
the known edge-clipping source fraction `0.842260`, but the budget fraction
stays at `0.742835`.

## Interpretation

This is the first rung that reads like a proof scaffold rather than a numerical
exploration. It does not merely say that selected runs passed. It identifies an
admissible observed-amplitude class and verifies the structural reasons the
class stays inside the local physical bounds:

1. the source is nonnegative and bounded;
2. the only source scaling is phase-local;
3. the service schedule prevents arbitrary all-domain impulse collapse;
4. bounded common jitter stays in the same budget class;
5. the transport map is positive and non-amplifying;
6. local rapidity budgets remain invariant with margin;
7. the limiter is not part of the observed proof.

That is the academic-facing value of this rung. It turns the previous
source-coupled evolution result into a checkable discrete theorem statement on
the sealed fixed background.

The claim is still bounded. This is a fixed-background discrete proof
obligation, not a continuum theorem, not a final matter action, and not a
coupled Einstein-matter proof. The right reading is: under the stated observed
source law, service schedule, timing jitter class, and split-step transport
operator, the beta075 source-coupled `1+1` model preserves the local rapidity
budget and causal transport margins on the sealed dense background.

## Academic Implications

This improves the viability story in a specific way. The system is no longer
only a thought experiment plus a collection of passing harnesses. It now has a
candidate physical evolution class with explicit assumptions and invariant
checks.

An external technical reader can now ask sharper questions:

- Are the source law and schedule physically derivable from an action or
  effective open-system constitutive model?
- Does the discrete proof class survive time-step and mesh refinement?
- Does the fixed-background exchange current lift cleanly into a conservation
  statement for the endpoint/support medium?
- Can the proof be stated independent of this particular code implementation?

Those are the right next questions. They are broader and more academic than
same-level support-edge tuning.

## Next Rung

Move to discretization and continuum robustness for the proof class.

The next useful certificate should keep the observed-amplitude proof class
fixed and vary the numerical representation:

1. service-step refinement, for example `48`, `72`, and `96` steps;
2. tail-window sensitivity;
3. CFL sensitivity inside the positive-transport regime;
4. stability of the max budget fraction, worst row, source-law scales, and
   state/source ratio;
5. a short theorem-map connecting each numerical artifact to the corresponding
   physical assumption.

The point is not to discover a scarier amplitude. The point is to show the
observed physical claim is not a single-grid artifact and can be presented as a
stable fixed-background PDE class.
