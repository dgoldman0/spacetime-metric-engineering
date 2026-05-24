# Constraint Card 003: Support-Shell Metric Actuator Layer

Status: component-level physical construction hypothesis.

## Controlling Sources

- Internal: V5 support-shell final freeze, continuous support-shell 4D source
  sweep, coupled timing feasibility, shape robustness reports.
- External analogs:
  [`caloz_deck_leger_spacetime_metamaterials_1905.00560.pdf`](../sources/caloz_deck_leger_spacetime_metamaterials_1905.00560.pdf),
  [`cui_coding_digital_programmable_metamaterials_1407.8442.pdf`](../sources/cui_coding_digital_programmable_metamaterials_1407.8442.pdf),
  [`estakhri_nonreciprocal_metasurface_space_time_phase_modulation_1905.10316.pdf`](../sources/estakhri_nonreciprocal_metasurface_space_time_phase_modulation_1905.10316.pdf),
  [`zang_nonreciprocal_wavefront_time_modulated_gradient_metasurfaces_2019.pdf`](../sources/zang_nonreciprocal_wavefront_time_modulated_gradient_metasurfaces_2019.pdf),
  [`pop_a_active_acoustic_metamaterials_realtime_1505.00453.pdf`](../sources/pop_a_active_acoustic_metamaterials_realtime_1505.00453.pdf),
  [`wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf`](../sources/wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf).

## Role

The support-shell actuator layer is the annular infrastructure band that routes
service demand away from the live packet. In metric terms it acts through
carrying-flow `beta`, clock-lapse `alpha`, rail-stretch `gamma_ll`, and
throat-capacity `gamma_OmegaOmega`.

## Physical Construction Hypothesis

The actuator layer is a programmable annular metamaterial. Its local cells
change effective index, impedance, boundary condition, elastic stiffness, or
acoustic response under a scheduled service waveform. Space-time metamaterial
literature supplies the central engineering idea: a moving material
perturbation can create synthetic motion, frequency conversion, nonreciprocal
response, and traveling phase fronts without moving a macroscopic wall.

The near-term hardware analogs split by scale:

- Microwave/THz: PIN-diode, varactor, or FPGA-controlled digital metasurface
  cells.
- Optical: electro-optic, semiconductor, nonlinear, or pump-driven index cells.
- Superconducting microwave: SQUID-tuned transmission lines and effective
  boundary modulation.
- Acoustic/mechanical: active acoustic cells, piezoelectric shunts, and
  elastic waveguide modules.

## Candidate Physical Stack

- Flow-front band: space-time-modulated cells generating the support-contained
  carrying-flow analog for `beta`.
- Lapse cushion band: delay, impedance, or phase-storage cells that protect
  timing margin for `alpha`.
- Stretch band: group-index, effective path-length, or elastic-stiffness
  modulation for `gamma_ll`.
- Throat-capacity band: angular/ring capacity cells for transverse support.
- Power and clock bus: service-coordinate waveform distribution with local
  phase locking and interlocks.
- Segment telemetry: phase, temperature, stored energy, shunt state, leakage,
  local current, and cone-margin proxy.

## Mathematical Constraints Carried Over

- Reduced support-shell routing puts incremental `Delta j_l` into
  catch/rematch support infrastructure with tiny packet exposure.
- Raised-cosine annular bearing is the preferred matched-strength comparator.
- Clock-lapse is the strongest default partner for aggregate burden reduction.
- Rail-stretch is useful as a peak-shaping comparator.
- Same-window throat-capacity remains a comparator until an intrinsic-window
  actuator earns promotion.
- High-amplitude or high-service cases consume packet margin and set actuator
  range requirements.

## Design Implications

The actuator shell is a multi-physics programmable skin. The design burden is
cell range, bandwidth, dispersion, loss, heat load, cross-coupling, and
service-time synchronization. The current mathematical evidence favors coupled
actuation: flow, lapse, stretch, and capacity are scheduled as a coordinated
waveform with separated channel roles and shared timing.

## Open Questions

1. Which cell technology can co-schedule `beta`, `alpha`, and `gamma_ll`
   while keeping radial-null and current burden inside the margin ledger?
2. What smoothing length keeps annular segment boundaries from producing point
   peaks under grid refinement?
3. Should throat-capacity use a physically separate angular ring band?
4. What service-aware actuator scaling law moves from `V=5` toward other
   service ratings?
