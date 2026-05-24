# Constraint Card 006: Regulated Heat/Current Medium and Support Reservoir

Status: detailed physical-source target card with engineering anchors.

Current evidence scope: sealed beta075 `V=5` operating point, as summarized in
the current disclosure and the May 22-23 Stage II source-family reports. This
card is the lead component brief for the source family that the current
evidence points toward.

## Controlling Reports

- [`README.md`](../../README.md): current claim boundary and service-rating scope.
- [`active_rail_technical_disclosure.tex`](../../active_rail_technical_disclosure.tex): current disclosure text.
- [`STAGE2_BETA075_SOURCE_LAW_DEFINITION_PACKAGE.md`](../../supporting_reports/STAGE2_BETA075_SOURCE_LAW_DEFINITION_PACKAGE.md): source-law definition.
- [`STAGE2_BETA075_SOURCE_FAMILY_EQUATION_PACKAGE.md`](../../supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_EQUATION_PACKAGE.md): formal fixed-background equation skeleton.
- [`STAGE2_BETA075_COVARIANT_ENDPOINT_MEDIUM_AUDIT.md`](../../supporting_reports/STAGE2_BETA075_COVARIANT_ENDPOINT_MEDIUM_AUDIT.md): covariant endpoint-medium tensor identity.
- [`STAGE2_BETA075_SOURCE_FAMILY_ENERGY_CERTIFICATE.md`](../../supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_ENERGY_CERTIFICATE.md): fixed-background energy-estimate certificate.
- [`STAGE2_BETA075_BV_ANALOGUE_SOURCE_PATHOLOGY_MAP.md`](../../supporting_reports/STAGE2_BETA075_BV_ANALOGUE_SOURCE_PATHOLOGY_MAP.md): denominator and boundedness map.
- [`STAGE2_BETA075_FINITE_DOMAIN_RADIAL_ANEC_DIAGNOSTIC.md`](../../supporting_reports/STAGE2_BETA075_FINITE_DOMAIN_RADIAL_ANEC_DIAGNOSTIC.md): finite-domain radial ANEC caveat.

Older context: the May 16 ADM writeup and May 17-20 support-shell/component
reports are provenance for how the source roles were discovered. The May 22-23
beta075 source-family reports control this card.

## Engineering Sources

- [`denicol_heat_flow_transient_relativistic_fluid_1207.6811.pdf`](../sources/denicol_heat_flow_transient_relativistic_fluid_1207.6811.pdf):
  causal heat-flow variables and relaxation dynamics.
- [`sha_printable_freeform_thermal_metamaterials_s41467-021-27543-7.pdf`](../sources/sha_printable_freeform_thermal_metamaterials_s41467-021-27543-7.pdf):
  printable thermal metamaterials for shaped heat-flux routing.
- [`ma_transient_thermal_cloak_1305.2871.pdf`](../sources/ma_transient_thermal_cloak_1305.2871.pdf):
  transient heat-flow control through anisotropic diffusivity.
- [`schittny_transient_heat_flux_shielding_1305.3197.pdf`](../sources/schittny_transient_heat_flux_shielding_1305.3197.pdf):
  transient heat-flux shielding around protected regions.
- [`duran_thermal_instability_superconducting_fault_current_limiters_cond-mat0312190.pdf`](../sources/duran_thermal_instability_superconducting_fault_current_limiters_cond-mat0312190.pdf)
  and
  [`noe_high_temp_superconducting_fault_current_microlimiters_0901.2299.pdf`](../sources/noe_high_temp_superconducting_fault_current_microlimiters_0901.2299.pdf):
  current-limiting hardware with coupled electromagnetic and thermal behavior.
- [`eling_jacobson_mattingly_einstein_aether_gr-qc0410001.pdf`](../sources/eling_jacobson_mattingly_einstein_aether_gr-qc0410001.pdf):
  director-field analogy.
- [`natario_rigid_elastic_solids_relativity_1912.08221.pdf`](../sources/natario_rigid_elastic_solids_relativity_1912.08221.pdf):
  causal elastic support intuition.

## Role

This component is the lead physical-source target for the beta075
endpoint/support plant. It carries the frozen endpoint radial heat/current
block, the non-live angular response, and the localized endpoint/support
exchange current while the live packet corridor remains a protected guide.

The current lead story is a regulated anisotropic heat/current endpoint medium
entrained to a radial director and coupled to a localized support reservoir.

## Physical Construction Hypothesis

Model the endpoint/support plant as an open, regulated, anisotropic medium:

- a radial director `s^mu` defines the preferred support direction;
- a heat/current state `psi` bounds the radial heat-flux ratio by
  `v_q = tanh(psi)`;
- a small non-live regulator supplies the enthalpy cushion in the radial
  `rho + p_l` pair;
- an internal angular response supplies the non-live `p_Omega` closure;
- a localized support reservoir supplies explicit power and radial-force
  exchange through `P` and `F`;
- total conservation is restored by pairing endpoint divergence with support
  stress divergence.

The natural formal container is an open-system effective action or
constitutive field-equation skeleton, with the support reservoir represented as
a derivative storage/stress operator.

## Physical Plant Guess

The engineering picture is a station-adjacent manifold with three coupled
physical layers.

1. Heat/current regulator: anisotropic thermal and current-routing cells shape
   radial heat flux, cap local rapidity, and move heat into dump paths. Thermal
   metamaterial experiments supply the closest construction analog: layered or
   printed material distributions that steer transient heat flow around
   protected regions.
2. Limiter and enthalpy cushion: superconducting or solid-state limiter
   elements absorb current spikes, convert over-budget current into a measured
   thermal/electromagnetic state, and provide the finite `rho + p_l` cushion.
   Fault-current limiter literature is a direct hardware analogy for a medium
   whose impedance changes under overload while recovery remains measurable.
3. Support reservoir: elastic, magnetic, or field-storage elements carry the
   explicit `P/F` exchange with the support substrate and endpoint reset plant.
   This layer is the physical home for derivative storage, radial force, and
   reset-domain stress handoff.

## Candidate Physical Stack

- Director manifold: radial rails, fibers, field lines, or anisotropic cells
  that define `s^mu`.
- Thermal metamaterial manifold: printed or layered anisotropic conduction
  paths for radial heat-flux shaping.
- Current limiter layer: superconducting microbridge, high-temperature
  superconducting tape, or solid-state limiter stage with local recovery
  telemetry.
- Regulator store: finite heat/current/stress storage that supplies the
  enthalpy cushion.
- Angular response jacket: circumferential storage/stress channel coupled to
  endpoint angular closure.
- Reservoir exchange port: explicit `P/F` connection to substrate anchors,
  collar load, and reset plant.
- Diagnostic fibers: temperature, strain, current, flux, limiter state, and
  rapidity proxy.

## Required Degrees of Freedom

- Endpoint density and stresses: `rho`, `p_l`, `p_Omega`.
- Radial heat/current channel: `j_l`.
- Bounded heat-current rapidity: `psi`.
- Radial director / support orientation: `s^mu` or equivalent `n_l`.
- Regulator / enthalpy cushion: a controlled contribution to `rho + p_l`.
- Support reservoir state: `Phi_support`, `Pi_support`.
- Exchange channels: `J_support^nu = P u^nu + F s^nu + J_perp^nu`.
- Phase-local source response: `kappa_phase B_service R_psi`.
- Service-coordinate timing law for source release.

## Placement And Timing

- Active on endpoint/support masks, especially support-edge and
  reset-decompression endpoint/junction regions.
- Excluded from active live packet support.
- Source response is phase-local, currently entry/catch support-edge focused.
- Release is service-coordinate scheduled, with bounded common timing jitter.
- The limiter guard is retained for over-budget rapidity concentration; the
  observed-amplitude sealed `V=5` package keeps it inactive.

## Acceptance Constraints

- Regulator rows remain non-live.
- Post-regulator radial block remains Type-I.
- Heat/current boost remains subluminal.
- `h_reg = 1 - v_q^2` remains positive.
- Reduced principal-symbol rows keep real finite in-cone characteristic speeds
  and complete eigenbases.
- Total endpoint/support closure stays below active, allowed, local, outside,
  live, support-tail, and angular-exchange gates.
- Support exchange is explicit in `P/F`, localized, and angular response is
  accounted separately.
- Fixed-background energy estimate keeps positive symmetrizer, symmetric
  principal block, in-cone flux, and bounded lower-order work.
- Finite-domain radial ANEC is a source-completion target; closure residual
  and live handoff trim remain assigned quantities.

## Current Margin Bookmarks

These values are evidence bookmarks from the current reports and are treated
as design-margin targets for later component work.

| Quantity | Current read |
| --- | ---: |
| Dense max boost speed | `0.987443` |
| Dense tight transport margin | `7.983e-05` |
| Dense tight Type-I margin | `4.036e-09` |
| Minimum source-profile scale | `0.092617` |
| Dense local support closure | `0.544567 / 0.55` |
| Dense support closure headroom | `0.005433` |
| Local power channel `P` watch | `0.609031` |
| Local radial-force channel `F` watch | `0.475062` |
| Energy work constant | `2.049051 / 2.5` |
| Finite-domain ANEC status | geometric total negative; closure-residual dominated |

## Design Questions

1. What physical variable supplies the local enthalpy cushion at the support
   edge while keeping denominator headroom measurable?
2. Can the support reservoir be written as an elastic, aether-like, or
   field-storage operator with explicit `P/F` exchange?
3. Can the phase-local source scaling be smoothed so the `0.092617` sharp
   scale becomes a controlled constitutive response?
4. Can transport and Type-I margins be widened within the sealed carrier
   geometry?
5. Can the closure residual identified by the finite-domain ANEC diagnostic be
   assigned to this component as source completion?
6. How should the same construction become explicitly service-aware, with `V`
   entering the medium/support closure as an explicit input beyond the current
   `V=5` operating-point calibration?

## Next Artifacts

- Denominator budget table for `h_reg`, Type-I margin, cone margin, support
  closure headroom, and local `P/F` exchange headroom.
- Variable glossary for the endpoint medium and support reservoir.
- First toy constitutive equation set for `psi`, `s^mu`, `Phi_support`, and
  `Pi_support`.
- Denominator-drift ladder under support-edge constitutive refinements.
- Source-completion sketch aimed at the finite-domain radial ANEC residual.
