# Constraint Card 006: Regulated Heat/Current Medium and Support Reservoir

Status: first detailed physical-source target card.

Current evidence scope: sealed beta075 `V=5` operating point, as summarized in
the current disclosure and the May 22-23 Stage II source-family reports. This is
not a matter-action construction, fabrication plan, or coupled Einstein-matter
solution. It is the first detailed component brief for the source family that
the current evidence points toward.

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

## Role

This component is the lead physical-source target for the beta075
endpoint/support plant. It is intended to carry the frozen endpoint radial
heat/current block, the non-live angular response, and the localized
endpoint/support exchange current without moving hard source burden into the
live packet corridor.

It is not a scalar-only source and not an ordinary closed Type-I anisotropic
fluid. The current lead story is a regulated anisotropic heat/current endpoint
medium entrained to a radial director and coupled to a localized support
reservoir.

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
  stress divergence, not by hiding exchange inside the endpoint medium.

The natural formal container is an open-system effective action or
constitutive field-equation skeleton, with the support reservoir represented as
a derivative storage/stress operator rather than a row-by-row numerical fit.

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

- Active only on endpoint/support masks, especially support-edge and
  reset-decompression endpoint/junction regions.
- Excluded from active live packet support.
- Source response is phase-local, currently entry/catch support-edge focused.
- Release is service-coordinate scheduled, with bounded common timing jitter.
- The limiter guard is retained for over-budget rapidity concentration, but is
  inactive for the observed-amplitude sealed `V=5` package.

## Acceptance Constraints

- Regulator rows remain non-live.
- Post-regulator radial block remains Type-I; no post-regulator Type-IV rows.
- Heat/current boost remains subluminal.
- `h_reg = 1 - v_q^2` remains positive.
- Reduced principal-symbol rows keep real finite in-cone characteristic speeds
  and complete eigenbases.
- Total endpoint/support closure stays below active, allowed, local, outside,
  live, support-tail, and angular-exchange gates.
- Support exchange is explicit in `P/F`, localized, and not angular exchange.
- Fixed-background energy estimate keeps positive symmetrizer, symmetric
  principal block, in-cone flux, and bounded lower-order work.
- Finite-domain radial ANEC is not yet claimed; closure residual and live
  handoff trim remain source-completion targets.

## Current Margin Bookmarks

These values are evidence bookmarks from the current reports, not final design
tolerances.

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
   edge without becoming a hidden high-coupling denominator?
2. Can the support reservoir be written as an elastic, aether-like, or
   field-storage operator with explicit `P/F` exchange?
3. Can the phase-local source scaling be smoothed so the `0.092617` sharp
   scale becomes a controlled constitutive response?
4. Can the transport and Type-I margins be widened without changing the sealed
   carrier geometry?
5. Can the closure residual identified by the finite-domain ANEC diagnostic be
   assigned to this component as source completion?
6. How should the same construction become explicitly service-aware, so `V`
   enters the medium/support closure instead of leaving `V=5` as a single
   operating-point calibration?

## Next Artifacts

- Denominator budget table for `h_reg`, Type-I margin, cone margin, support
  closure headroom, and local `P/F` exchange headroom.
- Variable glossary for the endpoint medium and support reservoir.
- First toy constitutive equation set for `psi`, `s^mu`, `Phi_support`, and
  `Pi_support`.
- Denominator-drift ladder under support-edge constitutive refinements.
- Source-completion sketch aimed at the finite-domain radial ANEC residual.
