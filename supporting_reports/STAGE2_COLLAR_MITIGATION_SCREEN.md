# Stage II Collar Mitigation Screen

Date: 2026-05-21

## Purpose

This report records the first narrow mitigation/redesign screen after the dense
congruence caustic audit. The target is the finite minus-branch
carrier-focus collar: the live branch-band handoff layer that produces adverse
caustic-like compression with later escape.

This is a prescribed-metric perturbation screen. It is not a regenerated
demanded-source ledger, a conservation closure, or a matter model. The first
phase identified which metric channel is worth promoting; the follow-up
artifacted geometry phase writes compact metric point ledgers for candidate
beta-collar geometries so the finite-bundle observations are reproducible from
files.

## Diagnostic

New postprocessor:

```text
toolkit/adm_harness_cli/scripts/run_collar_mitigation_screen.py
```

The screen reads the existing point ledger and trace-expansion table, selects
the same strongest minus-branch branch-band centers used by the dense
congruence audit, builds the collar core from live both-shrinking rows, and
applies narrow windowed field edits in memory. Each candidate is then rerun
through the dense congruence observation:

```text
dense rays per run: 136
centers: 8
rays per center: 17
bundle half-width: 2 l-grid steps
collar window: live both-shrinking core, Gaussian-dilated by 4 s-grid and
               4 l-grid steps
observations: bundle width, packet norm, radial escape, sustained focusing
```

Screened variants:

```text
beta_l_smooth: local l-smoothing of beta inside the collar
areal_l_smooth: local l-smoothing of gamma_omega inside the collar
gamma_ll_l_smooth: local l-smoothing of gamma_ll inside the collar
packet_beta_relax: local beta relaxation toward packet-comoving beta
beta_areal_l_smooth: beta_l_smooth plus areal_l_smooth
```

## Runs

Full s15 screen:

```text
toolkit/adm_harness_cli/runs/collar_mitigation_beta075_p003_mid_s15/
```

Beta-channel ladder sanity check:

```text
toolkit/adm_harness_cli/runs/collar_mitigation_beta075_p003_mid_s9_beta/
toolkit/adm_harness_cli/runs/collar_mitigation_beta075_p003_mid_s12_beta/
```

Artifacted beta-collar geometry screens:

```text
toolkit/adm_harness_cli/runs/beta_collar_geometry_beta075_p003_mid_s15/
toolkit/adm_harness_cli/runs/beta_collar_geometry_beta075_p003_mid_s15_pass8_wide6/
```

## Main Result

The first mitigation signal points to the beta channel, not pure areal-radius
smoothing and not radial-metric smoothing.

At `s15`, all candidates preserved dense-ray radial escape and packet
timelikeness:

```text
dense radial escapes: 136/136 for every candidate
positive live packet-norm samples: 0 for every candidate
sustained-to-end both-shrinking dense rays: 0 for every candidate
```

The width-relief result at `s15` is:

| candidate | min all-both l-width ratio | gain vs baseline | min all-both areal-width ratio | gain vs baseline | note |
| --- | ---: | ---: | ---: | ---: | --- |
| baseline | 0.009603 | - | 0.000696 | - | adverse collar compression |
| `beta_l_smooth_s0p30` | 0.015835 | 1.649x | 0.001147 | 1.649x | clean beta-channel relief |
| `beta_l_smooth_s0p45` | 0.018649 | 1.942x | 0.001351 | 1.942x | strongest clean beta-only relief |
| `packet_beta_relax_s0p30` | 0.012363 | 1.287x | 0.000895 | 1.287x | weaker but directionally useful |
| `packet_beta_relax_s0p45` | 0.014028 | 1.461x | 0.001016 | 1.461x | useful but weaker than smoothing |
| `areal_l_smooth_s0p45` | 0.009494 | 0.989x | 0.000704 | 1.013x | no finite-width relief |
| `gamma_ll_l_smooth_s0p45` | 0.003403 | 0.354x | 0.000246 | 0.354x | worsens compression |

The beta-channel signal is stable across the future-domain ladder:

| rung | baseline min l-width | best beta-channel candidate | candidate min l-width | gain | caustic-like bundles | dense escapes | positive live packet norm |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `s9` | 0.008337 | `beta_l_smooth_s0p45` | 0.016398 | 1.967x | 6/8 vs 7/8 baseline | 136/136 | 0 |
| `s12` | 0.008195 | `beta_areal_l_smooth_s0p45` | 0.016546 | 2.019x | 7/8 vs 8/8 baseline | 136/136 | 0 |
| `s15` | 0.009603 | `beta_areal_l_smooth_s0p45` | 0.018649 | 1.942x | 8/8 vs 8/8 baseline | 136/136 | 0 |

At `s15`, beta+areal is not materially better in l-width than beta-only, though
it gives a small extra areal-width gain. Areal smoothing alone does not relieve
the finite-bundle compressor. Gamma_ll smoothing makes the compressor worse.

The artifacted geometry follow-up confirms the same direction and shows that a
broader/passier beta-collar softening can reduce the number of bundles crossing
the current caustic-like threshold:

| screen | candidate | dense escapes | positive live packet norm | caustic-like bundles | min all-both l-width | l-width gain | min all-both areal-width | areal-width gain |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| local 4x4/pass3 | baseline | 136/136 | 0 | 8/8 | 0.009603 | - | 0.000696 | - |
| local 4x4/pass3 | `beta_l_smooth_s1p0` | 136/136 | 0 | 8/8 | 0.036718 | 3.823x | 0.005133 | 7.379x |
| wide 6x6/pass8 | `beta_l_smooth_s0p75` | 136/136 | 0 | 6/8 | 0.080422 | 8.374x | 0.017395 | 25.009x |
| wide 6x6/pass8 | `beta_l_smooth_s1p0` | 136/136 | 0 | 4/8 | 0.127830 | 13.311x | 0.045665 | 65.651x |
| wide 6x6/pass8 | `beta_areal_l_smooth_s1p0` | 136/136 | 0 | 4/8 | 0.127830 | 13.311x | 0.045833 | 65.892x |

The saved candidate metric ledgers live under each run's
`candidate_metric_ledgers/` directory. They are observation artifacts only:
their metric columns are suitable for trace/dense-bundle follow-up, but their
source tensor columns are intentionally absent rather than treated as a
regenerated matter/source result.

## Interpretation

This is the first encouraging redesign signal after the dense caustic-like
compression result. The collar is not behaving like a pure areal-radius
geometry problem. The strongest low-cost relief comes from softening l-variation
in beta inside the live collar. That points to branch/null-speed shear in the
carrier rematch layer as the immediate engineering target.

The current read is:

```text
effect: adverse caustic-like compression with later escape
candidate cause: finite minus-branch carrier-focus collar
first mitigation signal: collar-local beta smoothing / beta relaxation
failed simple lever: gamma_ll smoothing
weak lever: gamma_omega smoothing alone
observed constraints preserved: packet timelikeness and radial escape
```

This does not yet certify viability, because the best artifacted candidates
still leave `4/8` caustic-like bundles under the current threshold at `s15`.
But the search is now pointed: the obstruction is not invariant under beta
collar softening. The redesign problem is no longer undirected geometry
surgery; it is to implement a tensor-consistent beta-collar softening/rematch
knob in the generator, then regenerate ledgers and rerun dense congruence,
packet safety, radial escape, source accounting, and SNEC companion checks.

## Decision

Proceed to a true tensor-consistent geometry/source beta-collar mitigation. The
first promoted knob should be a branch-band/local beta smoothing or relaxation
partner, shaped around the finite minus-branch carrier-focus collar, with
bundle-width preservation as a first-class gate alongside packet timelikeness
and radial escape.
