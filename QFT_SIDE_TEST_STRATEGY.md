The testing setup would treat the QET circuit as a **programmable quantum service rail** rather than a one-shot Alice/Bob demonstration. A chain or small lattice of coupled qubits/oscillators is prepared in a correlated low-energy state. One region acts as the **support/source side**, one region acts as the **packet/target side**, and intermediate degrees of freedom act as the rail. The protocol injects energy and information at the source side, applies feed-forward control through the rail schedule, extracts energy or produces a local deficit at the target side, and then measures the full ledger: local site energies, coupling energies, entropy/noise, reset cost, correlation consumption, and packet disturbance.

The two test axes then ask different questions.

---

## Axis 1 — Service choreography

**Question:**
Can packet health be protected while energy burden and repayment are displaced into prepared support/rail degrees of freedom?

**Vary:**
Timing, coupling profile, feed-forward schedule, extraction strength, support capacity, reset cadence, staged versus abrupt extraction, packet isolation.

**Measure:**
Packet disturbance, extractable work, deficit depth and duration, rail heating, support burden, repayment localization, reset cost, repeatability.

This axis treats the circuit as a control laboratory. The goal is to determine whether smoother or more structured service schedules meaningfully shape where burden accumulates and whether the packet region can remain comparatively protected while the support side absorbs most of the repayment overhead.

---

## Axis 2 — Operational robustness of QFT negative energy

**Question:**
Does QFT-side “negative energy” remain operationally meaningful under changes in local accounting, or does it shift substantially depending on how the system is partitioned?

**Vary:**
Hamiltonian decomposition, interaction-energy assignment, boundary conventions, site grouping, local observable choice.

**Measure:**
Deficit location, extractable work, repayment pattern, causal timing, entropy cost, correlation consumption, invariance across decompositions.

This axis asks whether the negative-energy event behaves like a robust operational structure or whether it is heavily convention-sensitive. If the same deficit/extraction behavior survives reasonable changes in local accounting, then the effect has stronger physical character. If the effect moves, weakens, or disappears under different partitions, then the local negative-energy interpretation becomes more fragile.

---

| If results look like this                                                                                | It suggests                                                                                    |
| -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Smooth or staged schedules improve packet health                                                         | Rail choreography meaningfully shapes burden distribution                                      |
| Negative-energy deficit localizes at the target while repayment localizes in support/rail/reset channels | Energy borrowing and repayment can be spatially and temporally organized                       |
| Repeated cycles remain possible with bounded reset overhead                                              | The protocol behaves like a repeatable service process rather than a one-shot extraction trick |
| Extractable work and repayment cost remain stable across reasonable decompositions                       | QFT negative energy has robust operational content                                             |
| Deficit timing and causal ordering remain stable across partitions                                       | The negative-energy event tracks physical protocol structure rather than arbitrary bookkeeping |
| Deficit location or extraction behavior shifts strongly under accounting changes                         | Local negativity is highly partition-sensitive                                                 |
| Positive repayment leaks substantially into the packet region                                            | Packet protection and repayment isolation are in tension                                       |
| Reset/repreparation dominates every cycle                                                                | Negative energy exists operationally, but is weak as a repeatable resource                     |
| Rail scheduling changes little beyond ordinary QET behavior                                              | The active-rail analogy adds limited additional structure                                      |

The clean claim would remain modest: this setup would not decide whether GR and QFT mean the same thing by “negative energy.” It would test whether quantum negative energy can be **scheduled, localized, protected, repaid, and repeated**, and whether those features survive changes in local accounting. That is already meaningful on the QFT side.
