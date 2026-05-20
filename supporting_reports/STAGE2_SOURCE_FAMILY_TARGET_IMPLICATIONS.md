# Stage II Source-Family Target Pass

## Summary

The dense entry-gated source-sector closure has now been converted into a
source-family target pass. This pass does not solve a matter model. It defines
what an explicit source family would have to reproduce, separates regular-like
support from radial-tension burden, and decomposes the dominant A/B/I sector
against an ideal radial string/tension scaffold.

Main result:

```text
The raw role burden is dominated by A/B/I radial infrastructure.
The A/B/I algebra is close to NEC-saturating radial tension.
The residual selected-null deficit is small in the scaffold proxy,
non-live, and concentrated in reset/support-edge current-sensitive rows.
```

So the first serious source-family model should not be a scalar and should not
try to fit the whole support plant at once. It should start with a radial
string-dust or tension-lattice scaffold for A/B/I, plus a small conserved
over-tension/current trim.

## Artifacts

Dense closure report:

```text
supporting_reports/STAGE2_ENTRY_SECTOR_CLOSURE_DENSE.md
```

Source-family target tables:

```text
toolkit/adm_harness_cli/runs/source_family_targets_entry_closure_151x225/
```

A/B/I radial-shell viability tables:

```text
toolkit/adm_harness_cli/runs/radial_shell_viability_entry_closure_151x225/
```

New tooling:

```text
toolkit/adm_harness_cli/adm_harness/source_family_targets.py
toolkit/adm_harness_cli/scripts/run_source_family_targets.py
toolkit/adm_harness_cli/adm_harness/radial_shell_viability.py
toolkit/adm_harness_cli/scripts/run_radial_shell_viability.py
```

Caveat: these are demanded-source postprocessing diagnostics. They are not a
conservation proof, a quantum RSET calculation, or a physical source solve.

## Quantity Split

The current source-family target split is:

| target family | sector/components | burden | share |
| --- | --- | ---: | ---: |
| anisotropic radial-tension shell | A/B/I | `538.872629` | `94.03%` |
| live handoff boundary trim | C/E/F | `16.511753` | `2.88%` |
| angular capacity jacket | G | `8.625375` | `1.50%` |
| non-current closure residual | unassigned non-current residual | `8.461464` | `1.48%` |
| current control | D/H | `0.647478` | `0.11%` |

This answers the first support question directly. In role accounting, this is
not mostly regular support with a small exotic correction. The design is
overwhelmingly carried by the A/B/I radial infrastructure family.

Regular-like infrastructure is small by comparison. The G angular jacket is only
about `1.50%` of the target burden, and D/H current control is only about
`0.11%`. H matters because it is conservation-sensitive current relaxation, not
because it is a large quantity burden.

## A/B/I Stress Target

The A/B/I sector fit is close to a radial-tension equation of state:

```text
p_l / rho      = -0.999288
j_l / rho      = -0.000485
pOmega / rho   =  0.001078
live fraction  =  0.000000
```

This is the key distinction. A/B/I is large, but it is not asking for a generic
perfect fluid or a scalar-like pressure pattern. It is asking for something much
closer to radial string dust or a radial tension lattice:

```text
positive energy density
radial tension nearly equal to energy density
nearly zero radial current
nearly zero transverse pressure
zero live-packet burden
```

If exact `p_l = -rho` radial tension is treated as an admissible
NEC-saturating scaffold, then the irreducibly exotic part may be the small
over-tension/null-deficit trim, not the entire A/B/I amplitude. If any large
radial tension scaffold is classified as exotic engineering burden, then the
design remains exotic-support dominated. The current pass sharpens that
distinction but does not settle the physical interpretation.

## Radial-Shell Decomposition

The A/B/I demanded-channel burden is:

| component | role | burden |
| --- | --- | ---: |
| A | infrastructure radial-null support | `461.479029` |
| B | core radial-pressure balance | `61.146812` |
| I | support-edge radial-pressure balance | `16.246787` |
| total | radial infrastructure | `538.872629` |

Point-level decomposition against an ideal radial string/tension scaffold gives:

```text
integral |rho|                = 77.228369
integral |p_l|                = 77.393600
string-like scaffold          = 76.987679
selected-null deficit         =  1.030155
radial over-tension           =  0.405401
radial under-tension          =  0.216798
negative energy density       =  0.023892
absolute current              =  0.393488
absolute transverse pressure  =  4.167522
```

Normalized residuals:

```text
selected-null deficit / string scaffold       = 1.338%
selected-null deficit / A/B/I channel burden  = 0.191%
live scaffold fraction                        = 0.000%
live deficit fraction                         = 0.000%
```

This is a material improvement in the viability question. The raw A/B/I role
burden is large, but the string-like scaffold proxy says the local algebra is
near NEC saturation, with a much smaller selected-null deficit.

This does not erase the radial-null channel burden. The harness channel burden
is the demanded-source burden under the actual geometry and weighting, not just
the local unit-frame `rho + p_l +/- 2j` residual. The useful implication is more
specific: the first source model should test whether the large scaffold can be
regularized as radial tension, while keeping the small residual trim controlled.

## Deficit Localization

The selected-null deficit is not spread like the main radial-channel burden. Its
largest location groups are:

| stage / region | selected-null deficit | fraction |
| --- | ---: | ---: |
| `reset_decompression / support_edge` | `0.391122` | `37.97%` |
| `reset_decompression / core_throat` | `0.176146` | `17.10%` |
| `catch_rematch / support_edge` | `0.148939` | `14.46%` |
| `post_release_buffer / support_edge` | `0.109035` | `10.58%` |
| `entry_precatch / support_edge` | `0.096216` | `9.34%` |

This shifts the immediate blocker. The question is not simply "is the radial
support too large?" The sharper question is whether the residual trim can be
made conserved and non-live in reset/support-edge and reset/core rows, where it
mixes naturally with the D/H current-relaxation story.

## Interpretation

The current design is not yet physically viable. But the quantity gate is now
better posed.

The pessimistic reading would be:

```text
The design needs about 94% exotic radial support, so physical viability is
dominated by a large exotic source burden.
```

The more precise reading supported by this pass is:

```text
The design needs a large non-live radial-tension scaffold. In the unit-frame
proxy, that scaffold is close to NEC saturation, and the selected-null deficit
trim is about 1.34% of the scaffold. The hard part is now explicit realization
and conservation, especially current-coupled reset/support-edge localization.
```

That is a better position than the raw role split alone, but it is not a proof.
The next pass must choose and test an explicit source family.

## First Serious Model Choice

Recommended first model:

```text
A/B/I radial string-dust or radial tension-lattice scaffold
  plus
small conserved over-tension/current trim
  plus, later
separate angular jacket G and packet-bound live handoff trim C/E/F
```

The scaffold target is an anisotropic stress of the form:

```text
rho > 0
p_l ~= -rho
j_l ~= 0
pOmega ~= 0
```

The trim target is:

```text
small selected-null deficit
non-live only
localized mostly in reset/support-edge and reset/core rows
coupled to D/H current relaxation rather than hidden inside the live handoff
```

Why this is the right first model:

| candidate | status | reason |
| --- | --- | --- |
| radial string-dust / tension lattice | first | directly matches `p_l ~= -rho`, low current, low transverse pressure |
| scalar field | reject as first model | prior scalar screens failed the whole-plant audition and the target is too anisotropic |
| pure radial Maxwell field | reject as first model | tends to bring large transverse stress, unlike the A/B/I target |
| perfect fluid | reject | cannot represent the required anisotropy |
| angular jacket G | second | real but only `1.50%`; should not be forced into the radial shell |
| D/H vector/current relaxation | coupled trim | small burden, but important for conservation |

## Next Work

The next artifact should be an explicit A/B/I radial scaffold check:

```text
1. Fit a radial string/tension scaffold amplitude to the A/B/I point targets.
2. Compute residuals in rho, p_l, j_l, pOmega, and selected-null deficit.
3. Test whether the residual trim is small, non-live, and localized.
4. Couple the residual current/over-tension trim to D/H instead of live C/E/F.
5. Re-run sector closure and hard-affine SNEC on the replaced source-family target.
```

Decision criterion:

```text
If the scaffold absorbs the A/B/I body and leaves only a small conserved
non-live trim, continue to G and D/H source-family checks.

If the scaffold cannot be conserved without large extra transverse pressure,
live contamination, or new SNEC pressure, then the design remains quantity-gated
by exotic radial support.
```
