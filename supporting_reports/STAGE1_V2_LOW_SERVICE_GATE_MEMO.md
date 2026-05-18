# Stage I V2 Low-Service Gate Memo

## Purpose

This memo records a quick low-service-factor check, not a full report. The question was whether the current Stage I difficulty is mostly caused by trying to make a high-load V10 architecture, or whether the strong packet/source-separation target remains hard even at low service factor.

Hard gates checked:

```text
zero live packet-norm failures
zero top hard-channel points in the live packet
live radial-null Tkk and radial-pressure p_l fractions below the strict target band
controlled max point peak ratio
V5 survives as a cap, even if less clean
```

The strict target band is interpreted as the minimal-traversability harness pass line:

```text
live bad-channel fraction < 1e-2
```

## Runs

```text
toolkit/adm_harness_cli/runs/stage1_v2_temporal_beta_gate_check/
toolkit/adm_harness_cli/runs/stage1_v2_deep_annular_gate_check/
toolkit/adm_harness_cli/runs/stage1_v2_aggressive_annular_gate_probe/
toolkit/adm_harness_cli/runs/stage1_v5_aggressive_annular_nearpass_cap_check/
toolkit/adm_harness_cli/runs/stage1_v5_aggressive_annular_peakcontrolled_cap_check/
```

The checks used existing harness knobs only.

## Main Results

The moderate annular / temporal-beta family remains packet-safe at V2, but does not approach the strict live-fraction target:

| branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---|---:|---:|---:|---:|---:|
| moderate annular, temporal lapse, beta 0.0 | 0 | 0 | 0.072435 | 0.075390 | 5.150912 |
| moderate annular, temporal lapse, beta 0.6 | 0 | 0 | 0.073610 | 0.075393 | 4.833107 |

The deep annular branch improves both hard fractions but still misses the strict target and has elevated peaks:

| branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---|---:|---:|---:|---:|---:|
| deep annular, temporal lapse, beta 0.6 | 0 | 0 | 0.026558 | 0.023540 | 7.274291 |

The aggressive annular probe nearly crosses the strict band in radial-null and does cross it in radial pressure, but it does not keep peaks controlled:

| branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---|---:|---:|---:|---:|---:|
| aggressive near-pass | 0 | 0 | 0.012860 | 0.005288 | 11.849591 |

V5 cap check for that near-pass branch:

| V | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---:|---:|---:|---:|---:|
| 5 | 47 | 0 | 0.017154 | 0.005641 | 7.899945 |

So the near-pass V2 branch fails the V5 cap due to packet-norm failures.

The best peak-controlled branch is more architecture-like and survives V5, but it is not close to the strict target band:

| V | branch | packet failures | top hard live points | live Tkk fraction | live p_l fraction | max point peak ratio |
|---:|---|---:|---:|---:|---:|---:|
| 2 | peak-controlled aggressive | 0 | 0 | 0.027464 | 0.026317 | 4.990092 |
| 5 | peak-controlled aggressive cap | 0 | 0 | 0.032604 | 0.026352 | 3.326820 |

## Interpretation

The low-service check does not support the idea that the project is merely overengineering a high-V architecture.

Current readout:

```text
V2-V5 can be made packet-safe and peak-controlled with existing knobs.
V2 can be pushed close to the strict live-fraction band only by accepting high point peaks and losing V5 cap safety.
The strict packet/source-separation criterion still fails even at V2.
```

The remaining problem therefore looks architectural, not just a V10 load problem. Lower V helps, but the current local carve/lapse/beta controls still trade among the same three costs:

```text
live radial-null fraction
packet causal margin
point-peak control
```

## Recommendation

Do not reframe the current branch as a clean low-V minimal-traversability success. A fair statement is:

```text
The current harness can produce stable V2-V5 warning-grade architectures.
It has not produced a strict packet/source-separation pass, even at V2.
Future improvement likely needs a deeper timing/control-law change rather than more amplitude pushing on the existing local knobs.
```

Stage II should remain paused for strict source-target selection.
