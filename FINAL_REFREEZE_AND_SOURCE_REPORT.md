# Active Rail Refreeze and Source-Proxy Track Record

## Executive status

The current refreeze is **R1.75 shaped catch radial-soft lapse-cushion v1**, a tuned reduced-model active-rail candidate for **V = 10** service. It should be described as a successful reduced-geometry/source-proxy candidate, not as a demonstrated physical matter construction. It combines a small passenger packet corridor, a wider quarantined support shell, a locked-lead minimum-jerk catch/rematch, a radially softened support edge, and a lapse cushion that preserves packet causal safety.

The main design claim is now coherent: the active rail is a **source-placement architecture**. It does not remove exotic/high-risk source demand; it organizes where the demand lands. The passenger-facing goal is to keep dangerous or intense channels away from the live packet, while infrastructure bears the broad standing support, radial support, angular jacket, and timed catch/rematch correction.

## Refrozen candidate

```text
Design name: R1.75 shaped catch radial-soft lapse-cushion v1
Validation role: tuned V = 10 reduced-model freeze candidate
Packet radius: Rpass = 0.35
Support/quarantine radius: Rth = 1.75
Angular jacket radius: ROmega = 1.75
Radial support width: w_th = 0.569
Packet transition width: w_pass = 0.06
Angular jacket width: wOmega = 1.4
Angular jacket amplitude: aOmega = 0.20
Lapse cushion strength: eta_N = 2.00
Support catch: minimum jerk, x = -0.05, w = 0.32
Packet rematch: minimum jerk, x = 0.00, w = 0.32
Support decompression: minimum jerk
Validated V values: 2, 5, 10
Upper-headroom result: V just above 10 fails in the tested tuned branch
```

The correct label is **tuned V = 10 branch**. It is not a broad high-V family. The V-sweep showed that the design works below and at V = 10, but the safety cliff is very close above V = 10 in the current uniform radial-softening plus lapse-cushion architecture.

## Service sequence

The service should be understood as a staged infrastructure process:

```text
cold substrate
-> warm/ready support plant
-> live packet entry
-> locked-lead catch/rematch
-> support-contained carried shift handoff
-> packet normalization/release
-> slow decompression/reset outside passenger exposure
```

The live passenger accounting ends before reset/decompression. Reset is infrastructure work, not passenger exposure. This distinction mattered because earlier stage-level accounting could over-read reset/decompression as live packet burden. The point-level lifecycle work showed that the remaining bad channels were not mainly reset artifacts; they localized in entry/catch/rematch.

## Component list

| Component | Role |
|---|---|
| Cold substrate / support skeleton | Non-passenger infrastructure that carries support topology/geometry before live service. |
| Warm/ready rail plant | Prepared standing support with shift capacity, angular jacket, and lapse cushion. |
| Small passenger packet corridor | Keeps the passenger worldtube small inside a wider infrastructure shell. |
| Locked-lead shaped catch | Support-side catch starts slightly early; packet rematch follows closely. |
| Packet rematch | Returns the live packet toward ordinary local rail/throat geometry. |
| Support-contained carried shift | Shift/carrying field remains inside prepared infrastructure. |
| Radial-soft support edge | Reduces live radial pressure and contributes to Tkk reduction. |
| Lapse cushion | Restores causal safety margin consumed by radial softening. |
| Outer angular/effective jacket | Carries angular support mainly as infrastructure burden. |
| Modal catch-edge source absorber | Source-side transient guard for packet-edge Tkk during catch/rematch. |
| Decompression/reset | Minimum-jerk infrastructure reset after passenger exposure ends. |

## What the design learned

### 1. Catch/rematch is a real handoff layer

The best working intuition is that catch/rematch absorbs a **packet-carried shift layer** and returns the packet to ordinary local rail/throat geometry. It is not exactly a free warp shell being caught in empty space, because the support infrastructure is already present. The useful picture is an infrastructure-mediated handoff: the packet has been carried by a shift-like service layer, and the rail must absorb that carried shift without letting the passenger worldtube go causal-positive or slam into the support edge.

### 2. Support-side catch may lead, but packet rematch cannot lag freely

The bifurcation study showed a crucial rule. A support-side catch that begins slightly early is beneficial, but a freely lagging packet rematch produces safety failures. The mature version is therefore a **locked-lead catch**: infrastructure begins the catch first, but packet rematch stays close behind. This became one of the central service rules.

### 3. Tkk and p_l are not the same problem

The live negative radial-null channel Tkk responded to catch timing and shape. The radial pressure channel p_l responded to radial support-edge widening. This separation is one of the most important design lessons in the session.

```text
Tkk exposure -> shaped locked-lead catch/rematch
p_l exposure -> radial support-edge widening
packet safety -> lapse cushion
```

### 4. Uniform radial softening works, but it has a cliff

Increasing `w_th` reduces live p_l and Tkk burden, but high-resolution checks showed a sharp packet-safety cliff. Low-resolution results initially made values near `w_th = 0.569` look safe without compensation; high-resolution validation overturned that. Adding a lapse cushion restored safety at `w_th = 0.569`, but the branch remains thin: `w_th = 0.570` and above fail in the tested configuration.

### 5. The lapse cushion is a compensator, not the p_l cure

The lapse cushion does not directly solve radial pressure. It buys enough causal margin for stronger radial support-edge widening, which then reduces p_l. This is a clean separation of roles.

### 6. The catch-edge shock absorber belongs source-side

A geometry-side localized lapse guard was a partial success: it reduced integrated live catch Tkk slightly without breaking packet safety, but it also created new curvature peaks when pushed. That made the source-side interpretation cleaner. The remaining Tkk residual wants a **localized catch-edge transient source component**, not another global metric modification.

### 7. A modal catch-edge absorber is enough for the reduced source proxy

A single compact source absorber was not enough. A modal catch-edge source absorber cut live catch/rematch Tkk underfit below 5%, which is good enough for a reduced source-proxy finish-line claim for passenger-facing Tkk. This does not prove a physical material source; it shows that the residual is structured and can be assigned to a plausible service component.

## Knob ledger

| Knob | Primary channel | Lesson |
|---|---|---|
| Catch timing/profile | negative radial-null Tkk | Minimum-jerk locked-lead catch reduces live Tkk. |
| Radial support width `w_th` | radial pressure p_l and Tkk | Widening helps, but consumes packet safety margin. |
| Lapse cushion `eta_N` | packet causal safety | Buys margin for radial softening. |
| Packet transition width `w_pass` | packet/support coupling | Helps Tkk slightly; did not solve p_l. |
| Support radius `Rth` | quarantine separation | R1.75 is the best compromise found; R2.0 improves quarantine at higher infrastructure cost. |
| Angular jacket placement/width/amplitude | angular pressure | Live pOmega is tiny; global proxy basis remains crude. |
| Modal catch-edge absorber | catch/rematch Tkk residual | Several localized modes outperform one lump. |
| V | service stress | Current branch is V=10 tuned, safe below, fails just above in tested setup. |

## Quantitative milestone summary

These figures are the working design-scale results from the session reports:

| Stage | Key result |
|---|---|
| Point-level lifecycle | R1.75 still had live radial-null and radial-pressure exposure; reset/decompression was not the main explanation. |
| Shaped catch | Minimum-jerk locked-lead catch reduced live Tkk to roughly 84% of shaped baseline without packet-norm failure in the early refined check. |
| Radial softening | Radial support-edge widening reduced p_l; high-resolution validation showed only a narrower safe window. |
| Lapse compensator | `w_th = 0.569`, `eta_N = 2.00` was safe at high resolution and gave live p_l about 80.2% of shaped baseline and live Tkk about 73.6%. |
| Robustness | Candidate survives high-resolution V=10 recheck; it is a thin ridge, not a broad plateau. |
| V-sweep | Safe at V=2, V=5, V=10; unsafe above V=10 in tested branch. |
| Tkk residual fit | Targeted edge basis reduced live catch underfit; modal absorber brought it below 5%. |

## Source-side interpretation

The demanded source ledger should now be decomposed into the following proxy roles:

```text
standing support shell
+ radial-soft support edge
+ broad angular/effective jacket
+ lapse-cushion support sector
+ support-contained carried-shift sector
+ modal catch-edge transient absorber
+ decompression/reset control
+ residual packet-local correction
```

The strongest source-proxy result is for p_l and passenger-facing Tkk. p_l fits the radial support-edge story. The remaining live catch/rematch Tkk residual fits a localized modal absorber at the packet edge. Negative density in the live packet is not the urgent issue in this ledger. Angular pressure is mostly infrastructure/standing support from the passenger-exposure perspective, though its global proxy fit should be improved later.

## Refreeze statement

This design can be refrozen as a **successful V = 10 reduced-model source-shaped active-rail candidate**.

A precise claim:

> The R1.75 shaped catch radial-soft lapse-cushion candidate achieves packet-safe V=10 service in the reduced active-rail model by separating the service burden into a locked-lead catch/rematch, radially softened support edge, lapse safety cushion, and source-side modal catch-edge absorber. The remaining dangerous source demand is structured and mostly infrastructure/source-component localized rather than a global unexplained packet failure.

A precise non-claim:

> This is not yet a physical matter construction, a semiclassical stress tensor result, or a proof that the demanded source can be realized without trans-Planckian or otherwise pathological fields.

## Remaining gates after this refreeze

The next work should be staged rather than exploratory:

1. **Off-axis/null exposure check**: radial-only checks are not enough. Test whether off-axis null congruences discover worse live packet exposure.
2. **Convergence validation**: run the final candidate at multiple grid densities with checkpointing and compare live Tkk, live p_l, packet norm, and top residual locations.
3. **Compact modal control law**: replace independent fitted absorber modes with a smaller source-control ansatz.
4. **Source realism pass**: estimate whether scalar/effective jacket, support shell, lapse cushion, and modal catch absorber can be assigned to plausible source families.
5. **Trans-Planckian-risk localization**: determine whether high-risk amplitudes remain in infrastructure rather than the passenger packet.
6. **V-headroom branch**: only if needed, design a nonuniform or V-aware radial support edge. Do not keep pushing uniform `w_th`.

## Included archive inventory

This bundle includes all zip archives found from the session under `included_bundles/`. See:

- `included_bundles_manifest.csv`
- `included_bundles_manifest.json`

The most important included bundles are the lifecycle ledger, point-level ledger, bifurcation/shaped-catch studies, radial-softening studies, high-resolution compensator work, robustness work, V-sweep, freeze report, source decomposition, Tkk catch residual, shock absorber probe, and modal source absorber.
