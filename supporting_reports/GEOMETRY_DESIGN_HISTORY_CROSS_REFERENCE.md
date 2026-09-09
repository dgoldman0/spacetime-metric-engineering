# Geometry design history and current source tests

Date: 2026-09-09

## Finding

The archive already contains the service constraints, a component-level map of
metric controls, and substantial radius, lapse, transition, and timing
comparisons. These results narrow the geometry question raised by the
[coupled reorientation](COUPLED_REORIENTATION_INVESTIGATION.md). The remaining
task is to connect relevant archived alternatives to the newer absolute-source
and integrated-opening criteria. The previous recommendation to select the
operational constraints before proceeding repeated work already established
in the design record.

This review cross-checks the technical disclosure, milestone reports, selected
saved run summaries, candidate specifications, and the current scalar field
builder. It adds a historical cross-reference; the existing numerical results
retain their original backgrounds, grids, and source assumptions.

## Established geometry comparisons

| Design freedom | Archived evidence and result | Relevance to the current question |
| --- | --- | --- |
| Support radius | The [topology/support screen](STAGE1_TOPOLOGY_SUPPORT_SCALING.md) compared `Rth/ROmega = 1.75, 1.90, 2.05`. Increasing the radius to 2.05 lowered the radial-null point peak from 1.039 to 0.751 while increasing live angular burden from 1.245 to 1.651. All sampled cases were packet-safe on that grid. | Radius freedom and its angular cost were directly measured. |
| Radius with separated source roles | The [promoted-pair composite screen](STAGE2_COMPOSITE_SOURCE_ANSATZ_PROMOTED_PAIR.md) compared `compact7_wide4_edge160` with `wide4_radius205`. The assigned radial-support burden rose from 382.25 to 544.88, about 43%, for the broader candidate. Its live angular-to-density ratio also increased. The compact candidate was preferred. | The larger-radius option already received a multicomponent comparison. These are demanded-source assignment metrics, distinct from material energy or absolute quantum supply. |
| Radial support-edge width and clock compensation | [Pressure softening](RADIAL_PRESSURE_SOFTENING_FINDINGS.md), the [high-resolution compensator study](COMPENSATOR_HIGHRES_REPORT.md), and the [older freeze](FREEZE_REPORT.md) established pressure relief from widening, loss of packet causal margin, and its partial recovery through a lapse cushion. The old compensated branch selected `w_th = 0.569`, `eta_N = 2`. | These choices have a measured history. Their old V10 safety boundary belongs to that branch; the current beta075 operating reference is V5. |
| Local radial shape | The [radial geometry refinement](STAGE1_RADIAL_SUPPORT_GEOMETRY_REFINEMENT.md) varied annular radius and width around a positive core stretch. Its selected catch ring used radius/width multipliers 2.4/2.4; a broader ring traded pressure/current relief against angular and radial-null performance. | Nonuniform radial shaping is already implemented and partially inherited by the current construction background. |
| Shell shape, width, strength, and clock coupling | The [shell-shape robustness study](V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md) includes 48 matched-strength shape cases, 40 radial-width cases, and 120 strength-ladder cases. The raised-cosine annulus and a narrow radial neighborhood were preferred in that overlay family. The [coupled timing study](V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md) selected a clock-lapse partner and a narrow timing neighborhood. | Shell shape and clock coupling have existing comparators and quantified tradeoffs. The September manifest uses a smooth-box shell, so the old shape winner has a separate lineage. |
| Lapse footprint relative to material carve | The [decoupled carve/lapse study](STAGE1_DECOUPLED_CARVE_LAPSE_COMPENSATOR_SWEEP.md) independently varied lapse amplitude, radius, and width, with V5 back-checks of the selected earlier V10 family. Wider lapse shoulders eventually lost packet safety. | The clock footprint was already treated as an independent physical control, subject to causal and source-placement costs. |

The radius history is especially relevant: the archive tested the proposed
direction, found a real reduction in one local peak, and then measured a larger
assigned infrastructure burden in the broader geometry. Consequently the old
results support a comparison with an identified alternative, with both gains
and costs carried forward.

## Established transition and service choices

The [endpoint-thickness closeout](STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md)
tested edge widths 7.2, 9, and 11, catch/edge broadening, reduced edge strength,
and a current-guard blend. Increasing edge width to 11 changed the selected
endpoint-null deficit from 0.990430395 to 0.990415489. The reset-cap deficit
remained approximately 0.568414. Temporal broadening introduced a live packet
failure. The report closed simple endpoint smearing as the next direction.

In contrast, the [reset-release ladder](STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md)
found a useful coordinated change. Widening beta release from 0.25 to 0.75
reduced the reset selected-null deficit by about 24%, while transferring about
29% more selected-null burden to the support-edge shoulder. The subsequent
[receiver symmetry comparison](STAGE2_BETA_MEMORY_RECEIVER_ANGULAR_SYMMETRY_MEMO.md)
identified negative-l angular response as the favorable placement: it reduced
the endpoint deficit while keeping support-edge current and angular burden
close to baseline. This led to the
[negative-l receiver promotion](STAGE2_NEGATIVE_L_RECEIVER_PROMOTION.md).

The [collar generator screen](STAGE2_BETA_COLLAR_GENERATOR_SCREEN.md) selected
`rematch_w6_t1p5` and retained `rematch_w8_t2p0` as the wider comparator. It
explicitly directed the work toward a small local bracket. The
[local bracket](STAGE2_BETA075_COLLAR_LOCAL_BRACKET_CHECKPOINT.md) mapped the
packet, angular, and endpoint tradeoffs around that selection. Its initially
pending `w6_t1p75` case was later recorded as source-ledger-clean in the
[structured endpoint report](STAGE2_BETA075_STRUCTURED_ENDPOINT_SOURCE_MODEL.md);
that report also records its incomplete companion package. The
[repaired-lead promotion audit](STAGE2_BETA075_REPAIRED_LEAD_PROMOTION_AUDIT.md)
supplies packet, finite-bundle, and affine-null companions for `w6_t1p5`.

The service contract is already stated in the
[technical disclosure](../active_rail_technical_disclosure.tex), the
[entry gate](STAGE2_ENTRY_SERVICE_GATE_MEMO.md), and the
[service-time ledger](STAGE2_SERVICE_TIME_ADVANTAGE_LEDGER.md):

- A live packet corridor lies inside the support infrastructure, with negative
  packet norm and quiet service-induced packet energy increments.
- Setup, catch, release, restored arrival, and reset have explicit accounting
  windows. The selected live start is -1.40; preparation remains counted.
- Carrier tests track reachability, escape, ray ordering, recovery, and a
  positive finite-bundle width floor.
- Service comparison keeps departure/arrival conventions and the exterior
  reference explicit. The three saved collar cases retain prepared duration
  3.045 and identical transport-proxy ratings because their centerline
  transport inputs are unchanged.
- The current service-rating reference is V5. The
  [beta075 rating ladder](STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md)
  records separate V2.5 closure and V10 packet-safety failures.

These are scoped design and diagnostic constraints. Exact radius, lapse, and
profile coefficients are calibrated embodiment choices; the archive supplies
comparisons around several of them. The service-time ratings use the recorded
transport proxies, with the strict source-grid centerline control equal to
one. They supply reference comparisons for a modified metric.

## Which controls reach the newer static tests

The [scalar builder](../toolkit/adm_harness_cli/adm_harness/source_ledger.py)
already separates lapse, carrying flow, radial metric, and angular metric.
Using x for its radial coordinate, the static construction reads

\[
A(x)=\alpha(x),\qquad B(x)=\sqrt{\gamma_{ll}(x)},\qquad
R(x)=\sqrt{\gamma_\Omega(x)},\qquad dl=B(x)\,dx.
\]

| Existing control | Effect relevant to the static construction |
| --- | --- |
| Packet beta-rematch gain, radial width, temporal width, or floor | Changes beta with the other parameters held fixed. The fixed-phase zero-shift background retains the same A, B, and R. These collar controls remain relevant to active handoff and carrier behavior. |
| Packet-local radial core, ring, or skirt | Changes B where its schedule is active, and therefore changes R as a function of proper distance and the optical path. |
| Throat radius, angular jacket, or angular receiver | Changes R(x); shared support windows can also change A and B. |
| Lapse cushion or shell clock partner | Changes A and the relative clock profile along the optical path. |
| Support carve, support-edge width, or release choreography | Couples several fields or their schedules. The selected phase and active receiver memory determine which changes reach the static profile. |

The September
[construction manifest](data/le_coupled_reset_source/manifest.json) retains
the +0.05 radial core, +0.12 annular ring at 2.4/2.4, +0.05 outer skirt, and
the w6/t1.5 beta-rematch collar. It therefore already incorporates substantial
historical shaping. The
[regularity repair](LE_BOUNDED_METRIC_REPAIR.md) adds the receiver, origin,
and shell-window treatment required by the boundary diagnostics. Its current
implementation covers the frozen smooth-box/Gaussian shell; another shell
profile needs corresponding regularity coverage before curvature comparison.

The recent longitudinal gate holds R(l) fixed while allowing clock variation.
Its exclusion therefore applies to that radius profile and quantum law.
Conversely, the May geometry comparisons measured demanded-source placement,
packet behavior, and scoped effective source fits. The absolute quantum stress,
counted holding forces, and newer integrated opening condition supply
additional criteria for those alternatives.

## Revised continuation boundary

A useful continuation starts with the existing compact/radius-broadened pair
and the established radial/angular controls, checking which remain active on
the construction phase. It carries the selected component separation and
service comparisons into a common regularized background. The cheap opening
and optical-return conditions can then screen the alternatives before an
absolute quantum recalculation or a joint field solve. An archived passing
service result remains tied to its original background; transferring a control
to beta075 creates a candidate requiring its own relevant checks.

This is a targeted application of new source criteria to known geometry
choices. The archive already supplies the control map, service conditions,
several closed directions, and a reason for preferring the compact reference.
Whether a retained alternative materially improves the newer supply-to-demand
ratio remains open.

## Archive availability checked

Local saved summaries are present for the topology/support screen, the 81 by
109 radial comparison, the 48-case matched shell-shape comparison, the
120-case shell strength ladder, and the two promoted beta-collar cases.
The [promoted-pair specification](../toolkit/adm_harness_cli/specs/stage2_promoted_candidates.json)
is also present. The historical component/composite run directories referenced
under `runs/stage2_external` are unavailable at those local paths; their
committed reports preserve the comparisons cited here. This review generated
no new physics ledgers or quantum outputs.
