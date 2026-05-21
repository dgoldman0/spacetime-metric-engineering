# Stage II Trace-Integrated Expansion Audit

Date: 2026-05-21

## Purpose

This report records the higher-tier follow-up to the pointwise null-expansion
proxy. The pointwise proxy found a stable both-branch areal-shrinking warning in
live entry/branch-band rows. The question here is whether scheduled ADM probes
remain in that both-shrinking state, or pass through it and recover before radial
escape.

This is still a prescribed-metric probe diagnostic. It is not a full
trapped-surface theorem, matter evolution, or dynamical Einstein evolution.

## Diagnostic

New postprocessor:

```text
toolkit/adm_harness_cli/scripts/run_trace_expansion_audit.py
```

The diagnostic takes a point ledger and a scheduled ADM seed table, retraces the
same probe families through the prescribed metric, samples the pointwise
expansion proxy along the path, and records:

```text
whether the trace enters a both-shrinking patch;
whether it recovers before exit;
whether both-shrinking persists to the final sampled point;
integrated trapped-like strength;
longest consecutive both-shrinking run;
branch-expansion negative integral.
```

## Runs

The audit was run on the beta075 `p003_mid` scheduled ADM ladder:

```text
toolkit/adm_harness_cli/runs/trace_expansion_beta075_p003_mid_s9/
toolkit/adm_harness_cli/runs/trace_expansion_beta075_p003_mid_s12/
toolkit/adm_harness_cli/runs/trace_expansion_beta075_p003_mid_s15/
```

The `s9` run used the original scheduled ADM pilot seeds. The `s12` and `s15`
runs used their confidence-run scheduled ADM seed tables. All runs used:

```text
theta_eps = 1e-6
trace_step_scale = 0.5
```

## Main Result

The pointwise warning is real but transient in the scheduled branch-band probe
audit. Across `s9`, `s12`, and `s15`, branch-band radial, off-axis, and
congruence traces enter both-shrinking patches, recover from them, and still
escape radially. No branch-band trace remains both-shrinking to the final sampled
point.

The `s15` branch-band summary is:

| probe family | branch | traces | enter both-shrinking | recover | sustained to end | max integrated trapped-like strength | max longest run |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `radial_null_branch_band` | plus | 24 | 14 | 14 | 0 | 0.021587 | 4 |
| `radial_null_branch_band` | minus | 24 | 18 | 18 | 0 | 0.254517 | 30 |
| `offaxis_null_branch_band` | offaxis_plus | 24 | 15 | 15 | 0 | 0.022871 | 5 |
| `offaxis_null_branch_band` | offaxis_minus | 24 | 18 | 18 | 0 | 0.206616 | 28 |
| `congruence_branch_band` | plus | 25 | 11 | 11 | 0 | 0.058073 | 8 |
| `congruence_branch_band` | minus | 25 | 20 | 20 | 0 | 0.307438 | 28 |

The strongest `s15` integrated focusing traces are minus-branch branch-band or
congruence probes. The largest is:

```text
probe family: congruence_branch_band
branch: minus
seed: s = -1.236702, l = -1.1
outcome: l_lower_boundary
both-shrinking samples: 28
longest both-shrinking run: 28
integrated trapped-like strength: 0.307438
recovered before exit: true
sustained to end: false
```

## Ladder Stability

The trace-integrated decision is stable across the same future-domain ladder:

| rung | decision | max branch-band/congruence integrated strength | sustained branch-band traces |
| --- | --- | ---: | ---: |
| `s9` | `favorable_transient_branch_band_focusing` | 0.307366 | 0 |
| `s12` | `favorable_transient_branch_band_focusing` | 0.307410 | 0 |
| `s15` | `favorable_transient_branch_band_focusing` | 0.307438 | 0 |

This makes the result more reassuring than the pointwise proxy alone. The
pointwise both-shrinking patch is not a late-domain artifact, but the scheduled
branch-band probes do not remain trapped-like inside it.

## Red-Tag Channel

The reset-tail result remains separated from the live focusing result:

```text
s15 red_tag_reset_tail:
  traces: 41
  both-shrinking entries: 0
  sustained to end: 0
  outcomes: l_lower_boundary 30, s_upper_boundary 11
```

The unresolved wake-tail traces therefore remain a future-domain closure issue,
not the source of the live entry/branch-band both-shrinking expansion warning.

## Interpretation

The current causal picture has sharpened:

```text
local pointwise expansion proxy: adverse in live entry/branch-band rows
trace-integrated scheduled probes: favorable transient focusing
radial/off-axis/congruence escape: favorable
reset wake-tail expansion proxy: clean
```

This supports the interpretation that the promoted beta075 `p003_mid` service
program contains a local carrier-compression/focusing patch in the live entry
band, but the tested scheduled probes pass through the patch and recover before
radial escape.

This does not prove trapped-surface freedom. It does lower the immediate concern
that the pointwise both-shrinking rows are already functioning as a sustained
trapped-surface proxy under the sampled scheduled probe families.

## Decision

The next diagnostic should not be `s18` unless a clean wake-tail closure sentence
is specifically required. The expansion/focusing question is now more important
than simple future-domain extension.

Recommended next rung:

```text
bundle-level congruence width / caustic audit around the strongest
minus-branch branch-band seeds, using denser offsets than the existing
five-ray congruence bundle.
```

Promotion criterion:

```text
The dense bundle passes through the focusing patch without caustic-like collapse,
recovers expansion after the entry band, and exits radially with bounded width
and bounded integrated focusing.
```

Failure criterion:

```text
The dense bundle develops caustic-like collapse, non-recovering negative
expansion, or a sustained trapped-like state even though single traces still
reach radial boundaries.
```
