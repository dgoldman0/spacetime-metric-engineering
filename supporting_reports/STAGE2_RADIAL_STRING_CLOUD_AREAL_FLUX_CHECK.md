# Stage II Radial String-Cloud Areal-Flux Check

## Summary

This is a focused follow-up to the source-family target pass. The previous
report closed the effective-sector target split and the A/B/I radial-shell
decomposition. This check asks a narrower next question:

```text
Does the A/B/I radial scaffold look like a conserved radial string cloud,
or only like a generic anisotropic tension fit?
```

The answer is encouraging. Joining the A/B/I scaffold back to the metric
`gamma_omega` field shows that the main non-live radial scaffold is very close
to a constant areal-flux profile:

```text
mu ~= Phi / gamma_omega
rho ~= mu
p_l ~= -mu
j_l ~= 0
pOmega ~= 0
```

The breakdown is concentrated in reset/support-edge and reset/core cap rows, not
in the main core-throat scaffold.

## Artifacts

Input closure:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_entry_sector_closure_component_source_151x225_refined_roles/
```

Updated radial-shell diagnostic output:

```text
toolkit/adm_harness_cli/runs/radial_shell_viability_entry_closure_151x225/
```

Tooling updated for this check:

```text
toolkit/adm_harness_cli/adm_harness/radial_shell_viability.py
toolkit/adm_harness_cli/scripts/run_radial_shell_viability.py
```

The diagnostic now joins the component-source rows back to the source ledger
geometry columns and records:

```text
gamma_omega
best_string_density = max((rho - p_l) / 2, 0)
areal_string_flux_proxy = best_string_density * gamma_omega
constant-flux residuals against mu = Phi / gamma_omega
```

This is still a demanded-source diagnostic. It is not a matter model, not a
conservation proof, and not a stress-energy construction.

## Main Numbers

Global A/B/I areal-flux fit:

```text
areal string flux proxy mean      = 0.039772
weighted relative mean deviation  = 0.0904%
constant-flux rho residual L1     = 0.360731
constant-flux p_l residual L1     = 0.355848
constant-flux pair residual       = 0.716579
pair residual / integral |rho|+|p_l| = 0.4634%
```

This is stronger than the earlier pointwise scaffold result. The A/B/I sector
is not merely close to `p_l = -rho`; its main body also follows the
area-dilution law expected of a conserved radial string cloud.

## Location Structure

Location-level areal-flux deviations:

| stage / region | scaffold | selected-null deficit | flux rel. MAD |
| --- | ---: | ---: | ---: |
| `entry_precatch / core_throat` | `29.024593` | `0.002287` | `0.0017%` |
| `catch_rematch / core_throat` | `24.141591` | `0.003009` | `0.0041%` |
| `catch_rematch / support_edge` | `9.631658` | `0.148939` | `0.0680%` |
| `entry_precatch / support_edge` | `4.843128` | `0.096216` | `0.1948%` |
| `reset_decompression / core_throat` | `0.326970` | `0.176146` | `2.9474%` |
| `reset_decompression / support_edge` | `0.079312` | `0.391122` | `7.4307%` |

The dominant scaffold body is therefore extremely clean:

```text
entry_precatch/core_throat and catch_rematch/core_throat
carry most scaffold and have flux deviations below 0.005%.
```

The cap rows are the problem:

```text
reset_decompression/support_edge and reset_decompression/core_throat
carry little scaffold but a large share of the selected-null deficit.
```

That means the first source-family risk is not the body of the radial string
cloud. It is how to terminate, anchor, or cap that cloud without creating
unacceptable current, transverse pressure, live burden, or new SNEC pressure.

## Model Implication

The first serious source-family model should now be more specific than
"radial string dust" or "tension lattice":

```text
Primary body:
  constant-areal-flux radial string cloud
  mu = Phi / gamma_omega

First trim:
  reset/support-edge and reset/core cap residual
  coupled to D/H current relaxation and G angular capacity
```

The scaffold target is:

```text
rho =  Phi / gamma_omega
p_l = -Phi / gamma_omega
j_l =  0
pOmega = 0
```

The cap target is:

```text
non-live only
localized in reset/support-edge and reset/core rows
allowed to couple to D/H current relaxation
allowed to hand off small transverse-pressure burden to G
not allowed to leak into live C/E/F
```

## Alternative Models

The areal-flux result changes the model ranking:

| candidate | status | reason |
| --- | --- | --- |
| constant-flux radial string cloud | primary | matches `p_l ~= -rho`, low current, low transverse pressure, and `rho * gamma_omega ~= constant` |
| anchored string cap / tension-lattice endpoint trim | required trim | needed where reset/support-edge rows break free string-cloud behavior |
| scalar field | reject as primary | wrong anisotropy and already failed whole-plant scalar screens |
| pure radial Maxwell field | reject as primary | tends to bring transverse stresses not present in the A/B/I body |
| perfect fluid | reject | cannot represent the radial anisotropy |
| angular jacket G | separate secondary model | needed for transverse-pressure capacity, not the radial body |
| D/H vector/current relaxation | coupled cap model | small quantity burden but important for conservation |

## Next Check

The next concrete check should be a source-family replacement target for the
A/B/I body:

```text
1. Fit Phi for mu = Phi / gamma_omega on A/B/I point targets.
2. Build residual ledgers:
   rho - mu
   p_l + mu
   j_l
   pOmega
   selected-null deficit
3. Split residuals into body residual versus reset/support cap residual.
4. Assign the cap residual to D/H plus G candidate roles, not live C/E/F.
5. Re-run closure and hard-affine SNEC on the replaced scaffold-plus-cap target.
```

Decision criterion:

```text
If the constant-flux scaffold absorbs the A/B/I body and the cap residual
stays small, non-live, localized, and SNEC-clean, then the first source-family
model is worth promoting.

If the cap residual requires large transverse stress, live contamination,
or uncontrolled current divergence, then the design remains quantity-gated by
the radial support sector.
```
