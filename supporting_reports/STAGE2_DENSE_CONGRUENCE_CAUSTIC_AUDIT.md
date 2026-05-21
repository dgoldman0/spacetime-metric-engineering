# Stage II Dense Congruence Caustic Audit

Date: 2026-05-21

## Purpose

This report records the dense follow-up to the trace-integrated expansion audit.
The previous rung showed that scheduled minus-branch branch-band traces enter
the pointwise both-null-focusing patch, recover, and still escape. The open
question was whether a denser bundle around those strongest recovered traces
keeps finite width, or whether nearby rays compress in a caustic-like way while
the center trace still looks favorable.

This is still a prescribed-metric probe diagnostic. It is not a caustic theorem,
matter evolution, or dynamical Einstein evolution.

## Diagnostic

New postprocessor:

```text
toolkit/adm_harness_cli/scripts/run_dense_congruence_caustic_audit.py
```

The diagnostic reads a point ledger and the prior trace-expansion trace table,
selects the strongest recovered minus-branch branch-band centers, and expands
each center into a dense fixed-time radial bundle:

```text
top centers: 8
rays per bundle: 17
bundle half-width: 2 l-grid steps
offset spacing: 0.25 l-grid steps
theta_eps: 1e-6
trace_step_scale: 0.5
```

This keeps the same nominal width as the earlier five-ray congruence bundle, but
samples it much more densely. For each bundle the audit records common-prefix
coordinate width, areal-radius width, adjacent-ray gaps, ordering crossings,
both-shrinking recovery, sustained both-shrinking, and integrated focusing.

The caustic-like proxy is triggered when common-prefix bundle width falls below
10% of its initial width, adjacent separation falls below 5% of its initial
gap, or ray ordering crosses.

## Runs

The audit was run on the beta075 `p003_mid` scheduled ADM ladder:

```text
toolkit/adm_harness_cli/runs/dense_congruence_caustic_beta075_p003_mid_s9/
toolkit/adm_harness_cli/runs/dense_congruence_caustic_beta075_p003_mid_s12/
toolkit/adm_harness_cli/runs/dense_congruence_caustic_beta075_p003_mid_s15/
```

## Main Result

Formal result name:

```text
adverse caustic-like compression with later escape
```

The dense congruence rung is adverse for caustic-like compression, but not for
single-ray escape or sustained-to-end trapped behavior.

Across `s9`, `s12`, and `s15`, every dense ray still reaches the lower radial
boundary, every ray that enters the both-shrinking patch recovers before exit,
and no ray remains both-shrinking to the final sampled point. However, the
bundles compress severely inside the live both-shrinking region:

| rung | result | dense rays | radial escapes | sustained to end | caustic-like bundles | min l-width ratio while all rays both-shrinking | min areal-width ratio while all rays both-shrinking |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `s9` | adverse caustic-like compression with later escape | 136 | 136 | 0 | 7/8 | 0.008337 | 0.000668 |
| `s12` | adverse caustic-like compression with later escape | 136 | 136 | 0 | 8/8 | 0.008195 | 0.000657 |
| `s15` | adverse caustic-like compression with later escape | 136 | 136 | 0 | 8/8 | 0.009603 | 0.000696 |

The strongest `s15` center remains the same branch-band/congruence neighborhood
identified by the trace audit:

```text
source family: congruence_branch_band
branch: minus
center: s = -1.236702, l = -1.1
prior integrated trapped-like strength: 0.307438
dense rays: 17
radial escapes: 17
recovered rays: 17
sustained-to-end rays: 0
min common l-width ratio: 0.069827
min common areal-width ratio: 0.004272
max integrated trapped-like strength over dense rays: 0.396579
```

The most compressed `s15` bundle is centered at:

```text
source family: congruence_branch_band
center: s = -1.236702, l = -0.8
min common l-width ratio: 0.009192
min common areal-width ratio: 0.000670
min adjacent l-gap ratio: 0.006102
ordering crossings: 0
```

Inside the all-rays-both-shrinking live patch, the same bundle reaches:

```text
s = -0.051862
l-width ratio = 0.009603
areal-width ratio = 0.000696
adjacent l-gap ratio = 0.006386
both-shrinking fraction = 1.0
inside live fraction = 1.0
```

## Interpretation

The dense-bundle rung upgrades the branch-band warning from transient pointwise
focusing to adverse caustic-like compression with later escape. The result does
not show sustained trapping, because the rays recover expansion and reach the
radial boundary. It does show that the current live entry/rematch geometry
drives neighboring branch-band rays into a hard interior compression event.

This changes the causal read of the expansion story. The previous trace audit
was favorable at the single-trace level: branch-band minus traces recovered and
escaped. The dense congruence audit says that is not enough. Nearby rays remain
ordered and eventually escape, but the bundle becomes extremely narrow in the
live both-null-focusing patch before recovery.

So the correct current status is:

```text
pointwise expansion proxy: adverse in live branch-band rows
scheduled single traces: recover and escape
dense congruence width: adverse caustic-like compression with later escape
sustained trapped-like state to exit: not observed
ray ordering crossings: not observed
```

This is not a proof of trapped-surface formation. It is a serious adverse
congruence-width warning: the architecture can preserve endpoint escape while
still driving near-caustic compression inside the protected live carrier band.
The candidate mechanism is a finite minus-branch carrier-focus collar: a
localized handoff layer that may be performing real optical matching work, but
whose present tuning produces caustic-like bundle collapse before recovery.

## Decision

The dense rung fails the proposed promotion criterion. The next useful rung is
not a broader `s18` future-domain extension. The next work item should target
the finite minus-branch carrier-focus collar directly: soften or redistribute
the collar without losing branch handoff, packet timelikeness, or radial escape.
