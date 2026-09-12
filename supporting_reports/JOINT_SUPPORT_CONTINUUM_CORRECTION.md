# Joint support continuum audit correction

The material-frame force audit requires the temporal electric-field term
`-v H_t/(N R^4)`. The archived audit omitted this contribution when projecting
the normal-frame electric stress into the moving material frame. The joint
solver's force target already retained it through the endpoint divergence.
Consequently, the correction updates the independent residual assessment
while preserving the previously solved stress schedules and their end loads.

For a radial field with remaining flux energy `H-S(x)`, the complete projection is

```
P_field = H_t/(N R^4),
F_field = -(H_x-S_x)/(ell R^4) - v P_field.
```

The second term follows directly from `F_rest=Gamma(F_normal-v P_normal)`.
A new manufactured test uses a time-dependent electric field on an expanding
metric with nonzero material velocity. Its independently differentiated
normal-frame tensor reproduces both corrected projections.

| Candidate | Corrected weighted force residual | Power residual | Cell force residual |
| --- | ---: | ---: | ---: |
| General material, 32 cells / stride 8 | 11.893% | 1.825% | 1.066% |
| General material, 64 cells / stride 4 | 9.831% | 0.518% | 0.908% |
| Separate-member composite, 32 cells / stride 8 | 8.181% | 1.848% | 0.951% |

Each weighted ratio compares the absolute residual with the summed absolute
component terms under proper material spacetime weighting. The cell ratio
uses the integrated radial equation. These quantities describe interpolation
error and unresolved force balance; the raw linear-program residual describes
a different, discrete equation system.

For the separate-member composite, the allocation reconstruction reduces the
corrected force ratio to 4.497%. Its maximum local dominant-energy violation
remains `3.75104e-4`, so it still requires an admissible material completion.
The largest raw force residual remains `0.0241887`.

The earlier [stress-schedule report](JOINT_SUPPORT_STRESS_SCHEDULE.md), audit,
and figure preserve the original results. The force residual values above
supersede their corresponding diagnostics. Source remainders, support
inventories, and mechanical end-work figures retain their original values.

The corrected producer is
`toolkit/adm_harness_cli/scripts/audit_joint_support_corrected.py`.
[Recomputed evidence](data/joint_support_audit_corrected) includes five cases,
264 verified upstream hashes, residual arrays, and end histories. Seventeen
focused audit and pressure-field tests pass. The next calculation resolves
the actual continuum mismatch and tests a coupled constitutive response.
