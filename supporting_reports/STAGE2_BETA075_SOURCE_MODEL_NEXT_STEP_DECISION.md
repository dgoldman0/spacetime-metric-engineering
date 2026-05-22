# Stage II Beta075 Source Model Next-Step Decision

Date: 2026-05-22

## Decision

Clean up the endpoint source model before running a harder source-model test.

The current generic smooth endpoint-family fit has already answered the
near-term question it was built to answer. It shows that finite, non-live
envelopes can make the endpoint-J conservation proxy benign, but it also shows
that independent smooth component fits are too blunt: they over-carry
support-edge selected-null, current, and angular burden, with support-edge
`p_omega` remaining the clearest effective-coupling bottleneck.

Running a more rigorous test directly on that generic fit would mostly test a
model we already know is physically understructured. The useful next step is to
replace the generic support-edge fit with a cleaner structured model, then test
that model harder.

## Required Model Cleanup

Keep the reset-cap plant broad and finite. It is not the current blocker.

Replace the support-edge smooth interpolation with a structured endpoint source
model:

```text
1. Coupled stress-vector modes, so rho/p_l/j_l/p_omega move together rather
   than as four unrelated interpolants.
2. A targeted edge-tail counterterm aligned to the conservation residual rows.
3. Direct penalties for excess selected-null, current, and angular burden.
4. Hard zero-live-leakage gate.
5. Coefficient/effective-coupling proxy reporting.
```

## Test After Cleanup

Once the structured support-edge model exists, run:

```text
endpoint_j_conservation on the fitted family
family-fit burden and coefficient summaries
local-bracket comparison around rematch_w6_t1p5
dense-resolution scaling check for effective volume, residuals, and coefficients
```

Interpretation rule:

```text
If the structured model reduces support-edge overburden without coefficient
sharpening or live leakage, proceed to dense confirmation.

If it only works through large angular coefficients, singularly localized
counterterms, or live contamination, treat support-edge endpoint J as the main
remaining physical-source feasibility blocker.
```
