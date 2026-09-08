# LE Classifier Repair

The spherical ADM stress classifier now distinguishes diagonal degeneracy,
null dust, resolved Type IV, and numerically unresolved radial boundaries.
It assigns rest energy through the timelike eigenvector, including the negative
radial-enthalpy branch found in the pre-flight.

The repaired algebra uses the dimensionless margin
`(|rho+p_l|-2|j_l|)/max(|rho|,|p_l|,|j_l|)`. The `type_tolerance` argument is a
relative stress-margin tolerance, with default `1e-12`. Exactly diagonal tensors
retain Type I at every amplitude, including vacuum and radial tension. An exact
nonzero null-flux boundary has Type II. Nearby non-diagonal cases within the
tolerance receive `indeterminate_radial_boundary`, with unavailable rest-frame
quantities represented by NaN. Type II and Type IV also have unavailable material
rest-frame quantities and a false Type-I heat-frame compatibility flag.

For Type I, the stable boost expression is

\[
v=\frac{2j_l}{\rho+p_l+\operatorname{sgn}(\rho+p_l)
\sqrt{(\rho+p_l)^2-4j_l^2}}.
\]

The implementation evaluates it using scaled channels and handles zero current
directly. Rest energy and radial pressure use the sign of radial enthalpy in
the eigenvalue assignment. NEC, WEC, and DEC margins are then computed from the
Type-I rest energy and principal pressures.

The new full eigensystem certifier takes the four-by-four covariant tensor in
an orthonormal ADM frame. It checks spherical block structure and verifies
the eigen-equations against the supplied tensor. Type I requires a complete
causal eigenbasis with one timelike direction; Type II requires a repeated null
direction and a length-two Jordan chain; Type IV requires a complex pair.
Additional angular flux or shear outside the specified numerical tolerance
requires a more general classifier. The current frozen spherical geometry is
within this certifier's intended tensor class.

## Validation

All 19 pre-flight fixtures pass after repair. Their retained results are in
[classifier_fixtures.csv](data/le_classifier_repair/classifier_fixtures.csv).

The regression tests cover amplitude factors from `1e-100` to `1e100`, positive
and negative radial enthalpy, vacuum, degenerate Type I, positive null dust,
Type IV, near-null uncertainty, timelike boost invariance, causal eigenvectors,
Jordan structure, and rejection of invalid or unsupported tensors.

The full harness suite passes: **219 tests**, with four multiprocessing
deprecation warnings from existing tests. The focused classifier/endpoint suite
passes all 62 tests.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=toolkit/adm_harness_cli \
python -m pytest -q -p no:cacheprovider toolkit/adm_harness_cli/tests
```

The pre-flight snapshot and the existing endpoint artifacts retain their
original provenance. In particular, their stored rest-frame energy columns
record the earlier eigenvalue assignment. Reevaluations and the geometry-demand
boundary diagnostic use the repaired classifier. Reinterpreting the endpoint
material's admissibility requires recomputing its rest-frame-dependent checks;
the tensor identity and geometry-demand inputs are independently available.
