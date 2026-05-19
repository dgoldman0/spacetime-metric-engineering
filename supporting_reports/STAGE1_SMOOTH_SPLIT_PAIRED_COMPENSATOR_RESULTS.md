# Stage I Smooth Split Paired-Compensator Results

## Purpose

The latest smooth split candidate lowered the V5 live radial-null and radial-pressure burden, but it consistently pushed cost into live `j_l` and `pOmega` during `catch_rematch / packet_in_support`. The channel-cause ledger identified those points as radial-metric dominated, which suggested that the radial split might need a paired metric partner rather than another carve-only refinement.

This screen tested that idea directly by adding a packet-local angular-capacity partner. The new partner applies a local `gamma_omega` factor on the smooth-split edge footprint, so it is much narrower than the earlier broad throat-capacity screen.

## Harness Addition

The harness now exposes a local smooth-split angular partner:

```text
standing_support_packet_smooth_split_angular_log_gain
```

When nonzero, the factor is applied as:

```text
gamma_omega *= exp(angular_log_gain * smooth_split_angular_window)
```

where `smooth_split_angular_window` follows the guarded smooth-split edge footprint. The point ledger records:

```text
standing_support_packet_smooth_split_angular_window
standing_support_packet_smooth_split_angular_factor
standing_support_packet_smooth_split_delta_gamma_omega
standing_support_packet_smooth_split_angular_window_slope_abs
```

This preserves the existing smooth split behavior when the angular gain is zero.

## Runs

Focused V5 sign and trim screens were run at `41 x 61`:

```text
toolkit/adm_harness_cli/runs/stage1_v5_smooth_split_angular_partner_screen_41x61/
toolkit/adm_harness_cli/runs/stage1_v5_smooth_split_angular_partner_fine_41x61/
```

The screen compared `split_ref`, the current smooth additive candidate, and angular gains:

```text
-0.20, -0.10, -0.05, -0.025, +0.025, +0.05, +0.10, +0.20
```

The grid is intentionally a direction-finding screen, not a final gate. Absolute numbers should be read within this run only.

## Main Results

| case | angular gain | live Tkk | live p_l | live j_l | live pOmega | Tkk peak | pOmega peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `split_ref` | 0 | 10.1885 | 0.4088 | 0.0669 | 1.9415 | 0.9726 | 0.2167 |
| `smooth_additive_edge004_null_m007` | 0 | 9.7451 | 0.3971 | 0.0682 | 1.9572 | 0.9579 | 0.2337 |
| `ang_p0025` | +0.025 | 8.9185 | 0.3931 | 0.0706 | 1.9667 | 0.9768 | 0.2342 |
| `ang_p005` | +0.05 | 8.6311 | 0.3891 | 0.0736 | 1.9763 | 0.9984 | 0.2347 |
| `ang_p010` | +0.10 | 8.4168 | 0.3819 | 0.0811 | 1.9957 | 1.0427 | 0.2357 |
| `ang_p020` | +0.20 | 8.8641 | 0.3715 | 0.0983 | 2.0353 | 1.2316 | 0.2376 |
| `ang_m0025` | -0.025 | 11.4470 | 0.4012 | 0.0663 | 1.9477 | 1.1473 | 0.2332 |
| `ang_m005` | -0.05 | 13.3598 | 0.4054 | 0.0649 | 1.9384 | 1.7285 | 0.2327 |
| `ang_m010` | -0.10 | 18.7245 | 0.4143 | 0.0640 | 1.9199 | 2.9624 | 0.2318 |
| `ang_m020` | -0.20 | 30.7503 | 0.4317 | 0.0654 | 1.8839 | 5.6432 | 0.2298 |

The `+0.20` case also introduced a small live packet-comoving density burden:

```text
rho_packet_live_burden = 0.00017077
```

## Interpretation

The angular partner is a real steering knob, but this same-footprint implementation is not a successful compensator.

Positive angular gain improves the already-improving channels:

```text
live Tkk and live p_l drop further
```

but it worsens exactly the channels it was meant to control:

```text
live j_l and live pOmega rise monotonically
```

Negative angular gain does the mirror image:

```text
live j_l and live pOmega improve
```

but radial-null burden and point peaks grow rapidly. Even the small `-0.025` trim pushes live Tkk from `9.7451` to `11.4470`, erasing the smooth split's radial gain.

That is not random whack-a-mole. The signs are coherent: the local `gamma_omega` factor can move cost between the radial-null side and the current/angular side. The problem is that the same edge footprint couples the channels too tightly. It does not provide an independent cancellation direction.

## Implications

The paired-compensator idea remains conceptually plausible, but not in this simple same-footprint angular-capacity form.

The screen says:

1. The live `j_l / pOmega` penalty is not a bookkeeping artifact. It responds strongly to angular-sector changes.
2. A broad or same-footprint angular factor is too blunt. It either amplifies the live current/angular penalty or gives away the radial-null improvement.
3. The next viable paired law would need extra structure, not just another scalar gain. It likely needs a derivative-balanced radial/angular profile where the angular partner is offset, delayed, or moment-constrained relative to the radial split.
4. If such a profile is attempted, it should be screened with hard guardrails first: no positive packet norm, no live `j_l/pOmega` increase over `split_ref`, and no large `Tkk` point-peak growth.

## Current Design Read

The smooth split branch has made real progress over the piecewise split family, but the local angular-capacity partner did not convert that progress into a clean Stage I closure. The architecture is not exhausted yet, because the response is structured and algebraically interpretable. However, the simple paired-compensator screen narrows the next search: the missing ingredient is probably not "add local angular capacity," but a more constrained derivative-balanced support law that controls how radial and angular metric derivatives trade through the catch/rematch packet edge.

