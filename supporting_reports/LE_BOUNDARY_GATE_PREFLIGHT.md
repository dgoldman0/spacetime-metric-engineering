# LE Boundary Gate Pre-flight

Date: 2026-09-08.

The frozen beta075 V5 geometry and endpoint tensor are available and reproducible.
The complete material-stack gate requires a corrected classifier, an explicit
support stress tensor, and an exterior definition consistent with the standing
geometry. The pre-flight establishes these requirements through the stored
baseline and dense artifacts, analytic classifier fixtures, and fresh metric
evaluations. Its result concerns readiness for the boundary gate; the physical
boundary verdict remains open.

## Frozen inputs and numerical identity

The reference is `rematch_w6_t1p5`, with the 1.10 regulated endpoint medium and
the 24-by-14 support-stroke reference. The two source surfaces use identical
`SourceParams` over `s=[-1.5,15]`, `l=[-6,6]`. Fourteen selected artifact hashes
match their manifests, and the current source-ledger module matches both source
manifests. Six metric points per surface were regenerated from those parameters.

| Check | Baseline | Dense |
| --- | ---: | ---: |
| Sampling grid | 189 × 121 | 377 × 241 |
| Full source points | 22,869 | 90,857 |
| Maximum sampled regeneration error in an ADM source channel | 3.34e-13 | 1.01e-12 |
| Maximum endpoint tensor projection error | 1.14e-16 | 1.21e-16 |
| Points covered by the intermediate S0/J/R decomposition | 7,832 | 30,881 |
| Maximum reconstruction error on that subset | 1.04e-16 | 1.04e-16 |
| Endpoint medium points | 7,188 | 28,359 |
| Retained support-exchange points, including derivative halos | 7,667 | 29,317 |

The full source channels are finite, the ADM lapse and spatial metric factors
are positive, and the spacetime keys are unique. These checks establish usable
input tensors for a geometry-demand boundary diagnostic.

Both stored grids use `h_s=h_l=0.0025` for curvature differentiation. Consequently,
the pair supplies sampling-resolution evidence. A curvature-convergence study
also needs an explicit derivative-step ladder. The stored support coefficient
files differ between the two meshes; a frozen-profile test must pin a continuous
source representation and its coefficients while changing evaluation resolution.

## Classifier validation

The pre-flight checks seven analytic tensor families: vacuum, ordinary diagonal
matter, radial tension, isotropic degeneracy, negative radial enthalpy, null
dust, and flux-dominated Type IV. Nonzero families are evaluated at amplitudes
`1e-8`, `1`, and `1e8`, giving 19 fixtures. Each fixture checks algebraic type,
rest-frame output, and the heat-frame compatibility flag. The expected types
come from the explicit canonical tensors; a separate mixed-tensor eigensystem
records eigenvalue residuals, causal norms, and eigenbasis rank.

The legacy endpoint classifier fails 15 fixtures. Ten fixtures have an incorrect
type label, and seven have incorrect rest-frame output; these sets overlap.

| Example | Expected result | Current output |
| --- | --- | --- |
| Vacuum | Degenerate Type I, with a complete eigenbasis | Type II label |
| rho=1, p_l=-1, j_l=0 | Diagonal Type I | Type II label |
| Small-amplitude ordinary diagonal matter | Type I at every amplitude | Type II at amplitude 1e-8 |
| rho=1, p_l=-2, j_l=0 | Rest energy 1, radial pressure -2 | Rest energy 2, radial pressure -1 |
| Positive null dust | Type II, with a null flow direction | Type II label accompanied by a Type-I heat-frame flag and finite rest-frame values |
| Small-amplitude flux-dominated tensor | Type IV | Type II at amplitude 1e-8 |

The implementation compares the squared radial discriminant against a fixed
absolute `1e-12` tolerance and assigns the entire near-zero band to Type II.
Its rest-energy branch always uses the positive square root. For a resolved
Type-I radial block, the timelike eigenvalue instead gives

\[
\rho_{\rm rest}
=\frac{\rho-p_l+\operatorname{sgn}(\rho+p_l)
\sqrt{(\rho+p_l)^2-4j_l^2}}{2}.
\]

The negative-enthalpy branch affects the existing endpoint artifacts. The stored
rest energy disagrees with this branch on 6,810 baseline rows and 26,929 dense
rows. All endpoint rows pass the pre-flight's resolved positive-discriminant
screen. The largest rest-energy discrepancy is about 0.03179. At the worst row
on each surface, the corrected value agrees independently with the mixed
tensor's timelike eigenvector. The underlying covariant tensor still passes its
projection identity. Rest-frame-dependent admissibility quantities therefore
require reevaluation with the corrected eigenvalue assignment.

For example, at the dense point `s=3.8098404255`, `l=0.2`, the stored rest energy
is `+0.0030240884`; the timelike eigenvector gives `-0.0287654042`. Its metric norm
before normalization is approximately `-0.999876`, providing a clear causal
identification of the energy eigenvalue.

The four existing focused tests pass. Their coverage includes ordinary Type I,
ordinary Type IV, and the previous endpoint/support identities. The added fixture
table provides the boundary cases required for the classifier repair. The
pre-flight preserves the legacy implementation and the frozen artifacts as the
objects being examined.

## Tensor assembly and source accounting

The intermediate `S0_constant_flux_string_cloud`, `J_endpoint_junction_layer`,
and `core_body_residual_leakage` rows reconstruct their declared radial-source
subset to about 1e-16. That subset covers approximately 34% of the full sampling
grid. The remaining 15,037 baseline and 59,976 dense points all carry source
channels exceeding 1e-12 in magnitude. Their tensor is available from the full
geometry ledger and needs an explicit role in the complete sum.

The component-assignment table records channel burdens. Its source columns
repeat the full local demanded tensor for each assigned channel, with up to four
rows per spacetime point. The repeated tensors agree with the geometry ledger to
3.39e-21. Summing those rows as independent component stresses would multiply the
same source. Independent tensors for the remaining named source roles require
an explicit partition rule.

The frozen endpoint fit and regulated medium are also distinct from the original
geometric J target. Using the existing volume weights and the sum of absolute
rho, p_l, j_l, and p_Omega channel errors gives:

| Replacement comparison | Baseline | Dense |
| --- | ---: | ---: |
| Frozen endpoint fit error / original J target norm | 48.10% | 46.44% |
| Completed endpoint medium error / original J target norm | 49.62% | 47.98% |
| Completed endpoint replacement error / full geometric source norm | 2.99% | 2.87% |

These are ADM-frame channel L1 diagnostics using the stored grid weights. The
denominator is stated separately for each comparison. The covariant tensor
identity tests reconstruction of the fitted medium; this replacement comparison
tests its difference from the original demanded J. A complete tensor sum needs
to retain that difference or account for it explicitly through the source model.

The 1.10 regulator is already included in the endpoint medium. In the rho,
p_l, and j_l channels, medium minus frozen fit equals the stored regulator
increment to about 1.01e-16. It is therefore counted once when assembling the
medium contribution.

The support-stroke path supplies `fit_P`, `fit_F`, and their exchange four-vector.
Its `Tuu` columns reproduce the endpoint tensor on active rows to 3.39e-21 and
are zero on inactive rows. They are inherited endpoint fields. The audited path
provides the equation

\[
\nabla_\mu T_{\rm support}^{\mu\nu}=J_{\rm support}^{\nu}
\]

and a fitted exchange current, while a separately evaluated support stress tensor
remains to be specified. The divergence condition allows addition of any
divergence-free tensor, so it leaves the support tensor's algebraic type
underdetermined. This is the principal source-specification requirement for
the proposed material-stack gate.

## Exterior and control definition

At `s=15`, `l=±6`, both source ledgers contain approximately

\[
(\rho,p_l,j_l,p_\Omega)
=(-7.98575\times10^{-5},-7.98575\times10^{-5},0,
  7.98575\times10^{-5}).
\]

The angular metric satisfies `gamma_omega-l^2=3.0625=Rth^2`. The residual
geometry approaches the ultrastatic throat form

\[
ds^2=-d\sigma^2+dl^2+(l^2+a^2)d\Omega^2,
\qquad a=R_{\rm th},
\]

whose orthonormal source channels are

\[
\rho=p_l=-\frac{a^2}{8\pi(l^2+a^2)^2},\qquad
j_l=0,\qquad
p_\Omega=\frac{a^2}{8\pi(l^2+a^2)^2}.
\]

This analytic expression agrees with the stored outer samples within 8.02e-11.
Thus the standing geometry carries a decaying source beyond the actuator windows.
The mandatory outer test should follow that asymptotic source, or use an
explicitly specified vacuum-matched exterior. A region label such as
`far_exterior` supplies a bookkeeping location; the stress tensor supplies the
vacuum criterion.

The existing `matched_hold` setting is an active release-choreography parameter.
The older `v5_service_flow_off.yaml` uses the reduced sample-V5 data path. A
matched control for this gate needs a declared rule on the current frozen metric,
such as a frozen-time spatial geometry with zero shift, followed by a fresh
Einstein-tensor evaluation. The rule must identify which temporal derivatives
are removed and preserve the selected spatial taper profiles.

## Gate readiness and next implementation

The geometry-demand boundary calculation has reproducible inputs. Its next
implementation step is a scale-aware mixed-tensor classifier with causal
eigenspace checks, followed by the active/control derivative-refinement and
asymptotic-tail studies. This calculation can identify a demanded-source
obstruction before a material reconstruction is completed.

The full material-stack gate additionally requires a pointwise support tensor,
an explicit partition of the remaining source roles, and accounting for the
endpoint replacement residual. A required balancing tensor can be computed as
the difference between the geometric demand and the declared contributions;
that tensor is a realization target whose exchange and constitutive properties
can then be compared with the existing support-reservoir model.

The acceptance rule also needs to state the source family's permitted
energy-condition deficits and distinguish regular degenerate Type I from a
defective null eigenspace. The current pre-flight supplies no physical PASS or
FAIL for the completed boundary gate.

## Reproduction and evidence

Run from the repository root:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 \
python toolkit/adm_harness_cli/scripts/run_le_boundary_preflight.py --jobs 4
```

The two independent surfaces run in separate worker processes; `--jobs 1`
provides the serial path. Serial and parallel runs produce identical numerical
measurements and byte-identical CSV tables. The script writes numerical evidence only. The output
tables occupy less than 30 KiB. Full ledgers, source parameters, fit coefficients,
and the legacy classifier remain unchanged.

- [Pre-flight measurements and provenance](data/le_boundary_preflight/preflight.json)
- [Classifier fixtures](data/le_boundary_preflight/classifier_fixtures.csv)
- [Artifact hashes](data/le_boundary_preflight/artifact_hashes.csv)
- [Metric regeneration samples](data/le_boundary_preflight/metric_regeneration.csv)
- [Exterior samples](data/le_boundary_preflight/exterior_samples.csv)
- [Reproduction script](../toolkit/adm_harness_cli/scripts/run_le_boundary_preflight.py)

The principal implementation references are
`endpoint_j_source_class_screen.py`, `intermediate_source_model.py`,
`component_source_ledger.py`, `endpoint_medium_covariant_audit.py`,
`endpoint_support_stroke_exchange.py`, `endpoint_support_total_closure.py`, and
`source_ledger.py` under `toolkit/adm_harness_cli/adm_harness/`.
