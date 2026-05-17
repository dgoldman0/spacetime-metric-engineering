# Active Rail Reduced-Geometry Freeze Report

## Freeze candidate

**Design:** R1.75 shaped catch radial-soft lapse-cushion v1  
**Case key:** `V10_tuned_w0569_eta200`  
**Role:** tuned V=10 reduced-geometry freeze candidate for the active-rail source-analysis track.

This is a prescribed-geometry diagnostic candidate. The source ledger is computed as demanded source, `T_munu = G_munu[g] / 8π`, and should not be read as a solved matter model or renormalized stress tensor.

## Candidate definition

```text
V = 10
Rpass = 0.35
Rth = 1.75
w_th = 0.569
w_pass = 0.06
eta_N = 2.00
ROmega = 1.75
wOmega = 1.4
aOmega = 0.20

support-side catch:
  x_catch = -0.05
  w_catch = 0.32
  profile = minimum jerk

packet rematch:
  x_catch = 0.00
  w_catch = 0.32
  profile = minimum jerk
```

## Design lessons frozen into this branch

The branch now has a coherent knob separation:

```text
Tkk exposure       -> shaped locked-lead catch/rematch timing
p_l exposure       -> radial support-edge widening
packet safety      -> lapse cushion
speed headroom     -> still limited by a sharp V-dependent cliff
```

The most important catch/rematch lesson is that the support-side catch can lead slightly, but the packet rematch cannot lag freely. The viable branch uses a locked lead: infrastructure begins the catch a little early, while packet rematch follows close behind.

The most important radial-pressure lesson is that `p_l` responds to support-edge widening. High-resolution validation narrowed the safe window: raw widening above roughly `w_th = 0.52` became unsafe without a compensator, and the lapse cushion made the `w_th = 0.569` branch safe at V=10.

## High-resolution V=10 source-channel ledger

| channel | total burden | live packet burden | live packet fraction | point peak | live packet peak |
|---|---:|---:|---:|---:|---:|
| neg_Tkk_radial | 317.303 | 72.3794 | 22.81% | 0.142686 | 0.142686 |
| abs_p_l | 51.1238 | 13.8318 | 27.06% | 0.0115534 | 0.00953056 |
| abs_pOmega | 2.88471 | 0.00721474 | 0.25% | 0.0835714 | 0.000116242 |
| abs_j_l | 0.261114 | 0.0021128 | 0.81% | 0.0090502 | 0.000123627 |
| neg_rho_euler | 0.344305 | 0 | 0.00% | 0.0123701 | 0 |

Safety at V=10:

```text
live packet points: 260
max live packet norm: -198.9
positive live packet-norm points: 0
```

## V-sweep conclusion

The tuned branch survives V=2, V=5, and V=10. It fails quickly above V=10 in the current uniform radial-softening architecture. The fast threshold scan placed the cliff very close to the design point, around V≈10.005–10.01.

This means the branch is freezeable as a tuned V=10 reduced-geometry candidate. It is not yet a broad high-V family.

## Next phase

The geometry tuning phase has done enough to justify a source-decomposition phase. The next test is whether the demanded source ledger can be assigned to plausible roles:

```text
cold substrate / support shell
broad angular or scalar-effective jacket
lapse-cushion support sector
transient catch/rematch correction
packet-local residual
reset/decompression infrastructure
```

The key success condition is not perfect fitting. The key question is whether the dangerous/high-risk demand lands in infrastructure while packet-local residual remains small and interpretable.
