# Stage II Endpoint Theory Memo

This is a short theory note, not a full report. It records the current
Barcelo/Visser concern before the next endpoint tests are chosen.

## The Concern

The local source diagnostics now protect the live packet corridor and keep the
broad hard-affine SNEC gate clean, but they place the hard residual burden in a
non-live endpoint/junction layer. That pattern raises a specific concern: the
endpoint may be the "somewhere" where the exotic or trans-Planckian cost is
being localized.

The relevant lesson from `0003025v2` is not only that traversable wormholes need
NEC/ANEC violation. Barcelo and Visser show that non-minimally coupled scalar
fields can support traversable wormhole branches, but those branches require the
scalar field to reach trans-Planckian values somewhere in the geometry, or force
an extreme behavior in the effective gravitational coupling. In other words,
the geometry can appear supported by a formally acceptable source theory while
the hard price is hidden in an amplitude, coupling denominator, sign change, or
thin region.

## Current Algebra Screen

The endpoint/junction sector has a real exotic-support signature:

```text
J selected null deficit:       1.010455
J pure rho + p_l NEC deficit:  0.423023
J plus-branch deficit:         0.543527
J minus-branch deficit:        0.692236
J abs current:                 0.381351
J abs pOmega:                  3.961789
```

The support-edge endpoint is the more throat-like part:

```text
support-edge selected deficit:              0.443187
support-edge pure rho + p_l deficit:        0.315000
support-edge both-branches-negative share:  85.5%
```

The reset/decompression cap is different:

```text
reset selected deficit:             0.567268
reset pure rho + p_l deficit:       0.108023
reset one-branch-negative share:    75.6%
reset both-branches-negative share:  2.7%
```

So the support-edge endpoint looks more like a radial NEC throat-support
problem, while the reset cap looks more like a current/branch-selected endpoint
relaxation problem.

## Geometry Read

The simple geometry-side algebra is less damning than the stress algebra:

```text
selected-deficit share at local areal-radius minima: 0.07%
selected-deficit share near zero dR/dl:              2.7%
selected-deficit share with d2R/dl2 > 0:             98.6%
```

That says the endpoint load lies in a flaring support/junction region, but not
mostly at a clean local areal-radius throat by this simple screen. The current
evidence therefore supports "throat-like source demand" more strongly than
"literal transient traversable wormhole throat."

## Current Read

The Barcelo/Visser-style concern is live and well targeted. The endpoint has the
right algebraic smell: co-located radial NEC deficit, angular capacity, and
current relaxation. But this is not yet a proof that the endpoint hits the same
wall. We have not shown a trans-Planckian scalar amplitude, an effective Newton
constant sign flip, a singular thin shell, or resolution-growing stress.

The next test should not be another broad architecture gate. It should ask
whether `J_endpoint_junction_layer` remains finite and distributable:

```text
1. Endpoint scale/thickness ladder.
2. Endpoint stress-concentration and resolution-growth check.
3. Conservation or effective-coupling diagnostic for the junction layer.
4. Endpoint-local SNEC/ANEC-style accumulation screen.
```

If the endpoint load relaxes under finite-width distribution while staying
non-live and SNEC-clean, the architecture survives this concern. If the load
only works by sharpening, becoming singular, or demanding an extreme coupling,
then the endpoint is likely the hidden "somewhere" of the traversability cost.
