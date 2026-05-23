# Stage II Beta075 First-Order 3+1 Coupling Entry

## Status

Status: `first_order_3p1_entry_watch_pass`.

This is the entry slice of the 3+1/backreaction program. It is not a return to
same-level fixed-background tuning. The diagnostic asks whether the sealed
beta075 endpoint-plus-support source package can be handed to the Einstein
side at first order without immediately creating a Bianchi-accounting or
constraint-propagation obstruction.

The hard answer is clean: zero hard failures across sealed baseline V5, sealed
dense V5, and lower-service dense V2. The watches are the expected inherited
margin constants: near-luminal but still subluminal boost, the reset-sector
local P/F closure constant, and the energy theorem constant.

This report is manually written from structured outputs. The harness writes
CSV/JSON evidence only and does not generate report prose.

## Machine Output

Structured output:

`toolkit/adm_harness_cli/runs/stage2_beta075_first_order_3p1_coupling/`

Rows:

- run manifest: `3`
- surface summary: `3`
- surface stability: `3`
- classification gates: `9`
- top constraint drivers: `240`
- decision rows: `1`

## Decision

```text
first_order_3p1_status: first_order_3p1_entry_watch_pass
hard_first_order_3p1_pass: true
failed_gate_count: 0
watch_count: 3
surface_count: 3
```

Worst rows:

```text
worst local P/F closure surface: sealed_dense_v5
worst local P/F ratio:           0.544566954 / 0.55
worst active driver surface:     lower_service_dense_v2
worst active driver ratio:       0.452211702 / 0.55
max live driver fraction:        0.003553401 / 0.005
max outside driver fraction:     0.001036596 / 0.006
max boost velocity:              0.987443281
```

## What Was Tested

At first order, a coupled Einstein-side calculation cares whether the source
has a controlled conservation footprint. The diagnostic treats the residual

```text
nabla_mu (T_endpoint^{mu nu} + T_support^{mu nu})
```

as the perturbative Bianchi / constraint driver. It then checks that this
driver remains bounded in the active source sector, localized to allowed
endpoint/support masks, absent from angular exchange, and free of live support
leakage. It also carries the formal equation package and the energy-constant
audit as inherited gates.

That is the right bridge question between fixed-background source-family
proofs and a full 3+1 backreaction run. The fixed-background math can be
consistent on its own and still be unusable for dynamical gravity if
`nabla_mu T^{mu nu}` creates an uncontrolled constraint driver. This rung
looked directly for that failure mode.

## Gate Summary

| gate | status | value |
| --- | --- | ---: |
| formal source-family equations | pass | formal package hard pass |
| covariant endpoint tensor identity | watch | boost `0.987443281 / 0.98` watch |
| total endpoint/support Bianchi closure | pass | `0.452211702 / 0.55` |
| local constraint-driver P/F closure | watch | `0.544566954 / 0.55` |
| off-mask/live localization | pass | outside `0.001036596`, live `0.003553401` |
| angular constraint-driver absence | pass | `0.0` |
| energy constant buffer requirement | watch | utilization `0.819620378` |
| adjacent dense surface stability | pass | active-driver delta `0.000823226` |
| available surface scope | pass | `3` surfaces |

The three watches are not new. They are the same tight but bounded constants
we already knew were part of the sealed package.

## Surface Read

| surface | active driver / endpoint | driver / source abs | local P/F closure | live fraction | outside fraction |
| --- | ---: | ---: | ---: | ---: | ---: |
| sealed baseline V5 | `0.244987` | `0.036938` | `0.302640` | `0.003553` | `0.001037` |
| sealed dense V5 | `0.451388` | `0.074019` | `0.544567` | `0.003199` | `0.000871` |
| lower-service dense V2 | `0.452212` | `0.075168` | `0.544567` | `0.003228` | `0.000691` |

The dense V2 surface does not amplify the driver in a meaningful way. Its
active driver ratio is only `0.000823` above sealed dense V5, while the local
P/F ratio is slightly lower in the last digits. This is the same recurrence
pattern seen in the energy-constant audit: the tight number repeats as a
stable limiting constant, not as a growing instability.

## Constraint-Driver Location

The largest driver rows are in
`reset_decompression_endpoint_junction / reset_decompression / support_edge`,
with a smaller core-throat presence. That is exactly where the formal source
family already carries its support-reservoir margin debt. The top rows do not
move into packet-live support, do not require angular exchange, and do not
spread into an unrelated off-mask sector.

That location matters. A failure here would have been allowed to point back to
the support-reservoir or source law. A pass here means the same watch can be
carried upward as 3+1 margin debt rather than reopened as a local retuning
project.

## Interpretation

This is the cleanest answer we could reasonably ask from the entry rung. The
sealed beta075 source family can be handed to first-order 3+1 accounting
without an immediate Bianchi or constraint-propagation obstruction. The
source package is not yet a full coupled Einstein-matter solution, but it now
has the consistency evidence needed to justify running the larger 3+1
backreaction tests.

The uncomfortable part remains the same: dense reset-sector margins are thin.
The important part is that those margins do not become a new conservation
failure when interpreted as first-order gravitational source data.

## Claim Boundary

Included:

- first-order 3+1/backreaction entry diagnostic;
- Bianchi / constraint-driver proxy for total endpoint-plus-support source;
- cross-surface check on baseline V5, dense V5, and dense V2;
- inherited formal-equation and energy-constant gates.

Excluded:

- full dynamical metric evolution;
- off-axis 3+1 solve;
- final coupled Einstein-matter theorem;
- new source-law or support-reservoir retuning.

## Current Read

The next rigorous gate is the broader 3+1/backreaction run: allow metric
response probes and off-axis structure while monitoring constraint growth,
source conservation, cone preservation, and whether the reset-sector constants
remain bounded under geometric feedback.

This first-order handoff says we have earned that jump. It does not say the
full 3+1 problem is solved.
