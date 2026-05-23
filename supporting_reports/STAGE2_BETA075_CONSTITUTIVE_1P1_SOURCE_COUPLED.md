# Stage II Beta075 Full 1+1 Constitutive Source-Coupled Evolution

## Status

Status: `constitutive_1p1_observed_clean_with_margin_watches`.

This rung puts the sealed beta075 package through the integrated fixed-
background `1+1` source-coupled evolution that the previous timing certificates
were preparing for. The source is no longer treated as an isolated package
sweep or as a pure timing proof object. The cap-0.95 phase-local constitutive
source law is released on the service-aligned schedule and evolved under both
radial and service split-step bounded-rapidity transport.

The observed-amplitude system passes. The large-amplitude engineering-margin
case fails without the limiter and passes with the limiter, so it remains a
watch rather than a seal driver.

## Test Object

The test uses the sealed beta075 package:

- dense `rematch_w6_t1p5` closure
- covariant endpoint medium and `24x14` support closure
- cap-0.95 phase-local support-source law
- service-aligned source release
- bounded rapidity transport variable
- active non-live support-source domain

The machine output is structured only:

`toolkit/adm_harness_cli/runs/stage2_beta075_constitutive_1p1_source_coupled/`

The scenario set separates the hard observed driver from engineering-margin
watches:

- observed outward/forward, inward/forward, and outward/backward without a
  limiter;
- the same observed cases with the limiter present as an inactivity guard;
- large `5e-4` outward/forward without a limiter as a margin watch;
- large `5e-4` outward/forward with the limiter as an engineering guard.

## Result

Decision summary:

- status: `constitutive_1p1_observed_clean_with_margin_watches`
- observed unlimited pass: `True`
- observed limiter inactive: `True`
- live support exclusion: `True`
- state amplification clean: `True`
- source law bounded: `True`
- source law phase-local: `True`
- scaled slices: `4`
- scaled outside expected scope: `0`
- minimum source-profile scale: `0.092617`
- max observed unlimited budget fraction: `0.742835`
- max state/source ratio: `0.985750`

Observed scenario maxima:

- outward/forward: `0.690041`, led by row `2489`
  (`release_shift_fade / support_edge`, `s=1.0890957446808511, l=2.1`)
- inward/forward: `0.742835`, led by row `194`
  (`entry_precatch / support_edge`, `s=-1.2367021276595744, l=-2.1`)
- outward/backward: `0.727448`, led by row `2489`

The observed limiter guard is clean in all three directions: zero limiter
active steps, zero clipped rows, and zero over-budget rows.

The source-law audit remains phase-local. The only scaled slices are in the
intended `support_edge_endpoint_junction / support_edge` entry/catch phases:

- `entry_precatch`: `17` slices, `2` scaled, min scale `0.092617`
- `catch_rematch`: `29` slices, `2` scaled, min scale `0.192932`

The large `5e-4` outward/forward unlimited watch fails with max budget fraction
`3.450203` over `118` rows, led by row `2489` in
`release_shift_fade / support_edge`. The large limited guard passes at the
configured `0.95` cap, with `81` clipped rows over `10` limiter-active steps.

## Interpretation

This is the cleanest integrated read so far for the observed beta075 package.
The constitutive source law, source timing, radial transport, service transport,
local rapidity budgets, cone/transport margins, and live-exclusion gates are no
longer being checked in separate little compartments. They are coupled in the
same fixed-background `1+1` evolution, and the observed system remains inside
budget without limiter help.

The result also says the previous support-edge attention has done its job at
this claim level. Row `194` and row `2489` remain the leading watch rows, but
they are watch rows inside a passing observed evolution. There is no evidence
here for reopening geometry, collar fitting, source-edge normalization, or
V-interpolation.

The uncomfortable part is the high-amplitude margin. The artificial `5e-4`
case is not just slightly over budget in the full source-coupled `1+1` run; it
reaches `3.450203` without the limiter. The limiter can catch it, but that is
an engineering guard, not an action-level physical source proof. The observed
seal should therefore be described as an observed-amplitude, scheduled,
phase-local constitutive source-coupled pass with margin watches, not as a
large-amplitude theorem.

The thin margins are also still real. The observed run passes, but the leading
rows sit at small positive transport/cone margins. That is exactly why the next
step should be a proof obligation rather than more same-level tuning.

## Implications

The sealed beta075 package has now cleared the full fixed-background `1+1`
observed-amplitude source-coupled rung:

- the cap-0.95 source law stays bounded and phase-local;
- service-aligned timing remains protective;
- observed unlimited transport passes in the tested directions;
- observed limiter guards are inactive;
- live and packet-live rows remain excluded;
- state/source amplification remains absent.

This supports moving upward. The right next work is not another support-edge
repair pass. It is a fuller action-level proof obligation for the scheduled
constitutive source-coupled PDE class.

## Next Rung

Promote the next rung to an action-level fixed-background proof obligation for
the full `1+1` constitutive source-coupled model.

That proof should formalize the admissible source law and timing class:

1. phase-local cap-0.95 constitutive source scaling;
2. service-coordinate scheduled release, with bounded common timing jitter as a
   robustness class;
3. positivity and non-amplification of the radial/service split-step transport;
4. invariant local rapidity-budget bounds for observed amplitude;
5. live and packet-live exclusion;
6. a clear statement that large `5e-4` stresses are engineering-margin watches,
   not the observed-amplitude seal driver.

Only if that proof obligation fails in a specific place should the project
return to a component-level repair.
