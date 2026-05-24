# Constraint Card 003: Support-Shell Metric Actuator Layer

Status: component-level physical-design hypothesis.

## Controlling Sources

- Internal: V5 support-shell final freeze, continuous support-shell 4D source
  sweep, coupled timing feasibility, shape robustness reports.
- External analogs:
  [`leonhardt_philbin_transformation_optics_0805.4778.pdf`](../sources/leonhardt_philbin_transformation_optics_0805.4778.pdf),
  [`smolyaninov_metamaterial_alcubierre_1009.5663.pdf`](../sources/smolyaninov_metamaterial_alcubierre_1009.5663.pdf),
  [`wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf`](../sources/wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf),
  [`philbin_fiber_optical_event_horizon_0711.4796.pdf`](../sources/philbin_fiber_optical_event_horizon_0711.4796.pdf).

## Role

The support-shell actuator layer is the annular infrastructure band that routes
service-induced demand away from the live packet. In metric terms it acts
through carrying-flow `beta`, clock-lapse `alpha`, rail-stretch `gamma_ll`,
and throat-capacity `gamma_OmegaOmega`.

## Actual Physical Construction Hypothesis

The physical analog is a programmable annular field shell. It is closer to a
phased metamaterial/circuit array than to a rocket motor. Each annular segment
changes effective propagation, impedance, or boundary conditions in a scheduled
window. The closest existing hardware families are:

- transformation-optics metamaterial shells with spatially patterned effective
  permittivity/permeability;
- nonlinear optical fibers, where a moving pulse creates an effective horizon
  for probe waves;
- superconducting transmission lines with SQUID-tuned boundary conditions,
  where the effective electrical length changes rapidly;
- tunable microwave/metasurface rings where phase, delay, impedance, and
  coupling can be programmed per segment.

For a lab analog, the support shell should be a ring or line of tunable cells:

- "carrying-flow" channel: moving index/phase front or traveling-wave pump;
- "clock-lapse" channel: local delay/impedance modulation that protects timing
  margin;
- "rail-stretch" channel: effective path-length or group-index modulation;
- "throat-capacity" channel: transverse-mode/ring-capacity modulation.

For a speculative rail-scale design, these would become nested actuator bands:
one band for longitudinal support-contained flow, one for timing/lapse cushion,
one for radial capacity, and one for angular/throat capacity. They would be
driven by a service scheduler, not by continuous full-power forcing.

## Hardware Sketch

- Annular cell array with independently tunable impedance/index/stress state.
- Traveling service pulse generator to create the support-contained flow front.
- Delay/lapse cushion layer, likely a separate actuator rather than a passive
  material.
- Radial-capacity layer for peak smoothing and gradient matching.
- Diagnostics per segment: phase, energy, temperature, stored stress, timing.

## Mathematical Constraints Carried Over

- Reduced support-shell routing must put incremental `Delta j_l` into
  catch/rematch support infrastructure with tiny packet exposure.
- Raised-cosine annular bearing is the preferred matched-strength comparator.
- Clock-lapse is the strongest default partner for aggregate burden reduction.
- Rail-stretch is useful as a peak-shaping comparator.
- Same-window throat-capacity is neutral by default and should remain a
  comparator unless a later intrinsic-window design earns promotion.
- High-amplitude or high-service cases consume packet margin, so actuator
  strength is not unlimited.

## Design Implications

Single-channel actuation is the trap. The reports say the shell must co-shape
load, timing, radial capacity, and angular capacity. The hardware lesson from
metamaterial and superconducting-circuit analogs is that changing effective
geometry means managing dispersion, bandwidth, losses, and parameter range.
Smolyaninov-style metamaterial warp analogs are useful here mostly because they
show how quickly material-parameter limits become the real engineering wall.

## Open Questions

1. What physical actuation mechanism can couple `beta`, `alpha`, and
   `gamma_ll` without overproducing radial-null or current burden?
2. Can annular actuator modules be made smooth enough to avoid point-peak
   growth under refinement?
3. Should throat-capacity be a separate physical layer rather than same-window
   support-shell actuation?
4. What service-aware scaling law should retune this layer away from `V=5`?
