# Stage II Beta075 Constitutive 1+1 Discretization Robustness

## Status

Status: `discretization_robustness_pass_with_smooth_variation`.

The observed beta075 `1+1` constitutive source-coupled proof class now has a
discretization-robustness certificate. This rung keeps the physical claim
fixed and varies the numerical representation:

- service-step refinement;
- tail-window extension;
- CFL sensitivity inside the positive-transport regime.

All six variants pass the full observed proof-obligation table. The result
supports the read that the observed proof class is not a single-grid artifact.

## Test Object

The robustness certificate reuses the same observed proof class:

- dense `rematch_w6_t1p5` closure
- covariant endpoint medium and `24x14` support closure
- cap-0.95 phase-local support-source law
- service-coordinate scheduled source release
- bounded common timing jitter
- positive split-step radial/service transport
- active non-live support-source domain

The machine output is structured only:

`toolkit/adm_harness_cli/runs/stage2_beta075_constitutive_1p1_discretization_robustness/`

## Variants

| variant | role | steps | tail | jitter radius | radial CFL | service CFL |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `baseline_48_tail48_cfl040_020` | baseline | `48` | `48` | `8` | `0.40` | `0.20` |
| `service_refine_72_tail72_cfl040_020` | service refinement | `72` | `72` | `12` | `0.40` | `0.20` |
| `service_refine_96_tail96_cfl040_020` | service refinement | `96` | `96` | `16` | `0.40` | `0.20` |
| `tail_extend_48_tail96_cfl040_020` | tail sensitivity | `48` | `96` | `8` | `0.40` | `0.20` |
| `cfl_low_48_tail48_cfl025_010` | CFL sensitivity | `48` | `48` | `8` | `0.25` | `0.10` |
| `cfl_high_48_tail48_cfl055_030` | CFL sensitivity | `48` | `48` | `8` | `0.55` | `0.30` |

The refined runs scale the common jitter radius with service resolution. The
tail extension doubles the post-source tail without changing the source
window. The CFL variants stay inside the positive-transport coefficient
regime.

## Result

Decision summary:

- status: `discretization_robustness_pass_with_smooth_variation`
- variant count: `6`
- max budget fraction: `0.892161`
- min budget fraction: `0.731883`
- baseline budget fraction: `0.742835`
- relative drift from baseline: `0.201022`
- drift watch: `False`
- max state/source ratio: `0.991094`
- min source-profile scale: `0.092617`

Every variant passes all eight proof obligations:

- live and packet-live exclusion;
- bounded phase-local source law;
- source nonnegativity;
- service schedule with bounded common jitter;
- positive transport semigroup;
- transport L1 non-amplification;
- observed budget invariance;
- implied limiter inactivity.

Variant maxima:

| variant | max budget fraction | worst row | worst phase | max state/source |
| --- | ---: | ---: | --- | ---: |
| baseline `48` | `0.742835` | `194` | `entry_precatch / support_edge` | `0.985750` |
| service `72` | `0.731883` | `194` | `entry_precatch / support_edge` | `0.987713` |
| service `96` | `0.774729` | `194` | `entry_precatch / support_edge` | `0.989231` |
| tail `96` | `0.742835` | `194` | `entry_precatch / support_edge` | `0.985750` |
| low CFL | `0.892161` | `2489` | `release_shift_fade / support_edge` | `0.991094` |
| high CFL | `0.732031` | `195` | `entry_precatch / support_edge` | `0.980406` |

The source law is invariant across variants: `4` scaled slices, minimum scale
`0.092617`, and no scaled slices outside the expected entry/catch support-edge
scope.

## Interpretation

The cleanest read is that service-step refinement and tail extension do not
expose a hidden instability. The `72`-step run is slightly lower than baseline,
the `96`-step run is slightly higher, and both remain comfortably below the
local budget gate. Doubling the tail from `48` to `96` leaves the baseline
maximum unchanged, so delayed post-source concentration is not appearing in
this class.

The low-CFL case is the most informative variation. Reducing radial and service
CFL reduces numerical transport/outflow, so more rapidity burden remains near
the support-edge release row. That shifts the worst row from the familiar
inward/forward entry-precatch row `194` to release-shift-fade row `2489`, and
raises the max budget fraction to `0.892161`. This is still below the local
budget gate and below the configured `0.95` limiter cap, so it is a robustness
tightening, not a failure.

The high-CFL case moves in the opposite direction and remains clean. That gives
a useful monotonic narrative: the proof class is sensitive to transport
strength in the expected way, not in a chaotic or mechanism-changing way.

## Academic Implications

This rung makes the fixed-background viability story more credible. The
observed proof class no longer rests on one service resolution, one tail
window, or one CFL choice. Across the tested numerical representations, the
same physical source law remains bounded and phase-local, the same proof
obligations pass, no limiter is needed, and no live support appears.

The result is still not a continuum theorem. It is a discretization-robust
certificate for the observed fixed-background PDE class. That is exactly the
right bridge to the next academic question: whether the source law belongs to a
recognizable physical source family.

## Next Rung

Move to the source-law definition package.

That package should define the observed beta075 constitutive source law as a
physical candidate rather than only as a successful effective-PDE rule. It
should include:

1. state variables and constitutive relations;
2. phase-local source scaling and service-schedule assumptions;
3. support/exchange terms and regulator/rapidity bounds;
4. reduced hyperbolicity/principal-symbol evidence;
5. comparison against anisotropic heat-current media, director/aether-like
   media, elastic/support reservoirs, and open-system effective actions.

The artificial large-amplitude rows should stay in margin context. The active
question is now whether known or minimally conservative source families can
realize the observed law.
