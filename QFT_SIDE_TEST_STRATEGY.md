The testing setup would use a superconducting transmon circuit arranged as a short programmable QET service rail. A practical first target is a seven-site line: two source-side transmons, two support/coupler transmons, one protected packet transmon, one packet-edge handoff transmon, and one endpoint/battery transmon. Neighboring sites are connected through tunable couplers so the experiment can prepare a correlated low-energy rail state, shape the coupling path, isolate the protected packet, and move the extraction operation between the packet edge and the endpoint. Each transmon has local microwave control, dispersive readout, and calibrated single-site energy tomography; selected couplers are measured or reconstructed so the interaction-energy ledger can be tracked along with site energies.

The run begins by cooling and calibrating the device, then preparing the seven-site rail in a correlated low-energy state using adiabatic preparation or variational ground-state preparation. The source-side transmons receive the initial local operation and measurement. Their measurement record is sent through classical feed-forward to drive a conditioned operation on the packet-edge handoff transmon or endpoint/battery transmon. The protected packet transmon is monitored as a quiet subsystem: its state fidelity, excitation probability, coherence, entropy proxy, and leakage into neighboring couplers are scored across the live service window. The extraction/battery transmon records work extraction, while the support/coupler sites absorb and reveal the repayment burden.

The service cycle has six concrete phases: prepare the correlated rail state; activate the source-side measurement/injection operation; apply the feed-forward-conditioned handoff pulse; extract into the endpoint/battery site; fade the packet-facing coupling through a smooth release pulse; reset the support and endpoint sites for the next cycle. The apparatus should support repeated runs with the same prepared packet state, allowing one-shot extraction, staged extraction, endpoint-mediated extraction, and repeated-cycle service to be compared on the same hardware. The two test axes then ask different questions.

---

## Axis 1 — Service control and packet health

**Question:**
Can the timing, placement, and shape of the QET service cycle protect a packet-like subsystem while energy injection, extraction, repayment, and reset occur mostly in surrounding support degrees of freedom?

**Vary:**
Start with a calibrated baseline protocol: same prepared state, same protected packet subsystem, same source operation, same feed-forward channel, same extraction/battery register, and same reset procedure. Establish the baseline as the reference service cycle, then build controlled families around it.

Vary the **source operation** by changing pulse strength, duration, measurement basis, and smoothing profile. Vary the **feed-forward schedule** by changing delay, timing jitter, and whether the target operation is applied as one pulse or a staged sequence. Vary the **handoff geometry** by moving the extraction operation among a packet-edge coupler, a nearby support site, a terminal endpoint, and an explicit battery-facing register. Vary the **packet coupling** by changing the packet-to-support coupling strength, packet-edge coupling width, and number of intermediate coupler sites. Vary the **release profile** by comparing sudden decoupling, smooth fade, minimum-jerk fade, and multi-step release. Vary the **reset process** by comparing local reset, distributed reset, delayed reset, and reset through an auxiliary reservoir.

After single-parameter sweeps, run combined service families: direct packet-adjacent extraction, support-mediated extraction, endpoint-mediated extraction, smooth staged service, aggressive high-load service, and repeated-cycle service. These families should map how packet health depends on choreography, support capacity, extraction placement, and reset timing.

**Measure:**
Measure packet health as its own output channel. Record packet-state fidelity, excitation leakage, entropy growth, coherence loss, disturbance of selected packet observables, packet-support entanglement growth, and cycle-to-cycle degradation. Score these during the live packet window and again after reset to capture both immediate disturbance and accumulated damage.

Measure the energy ledger by functional role. Record source-side injected energy, extracted work into the battery, local negative-energy depth and duration near the handoff/endpoint, energy stored in support sites, energy stored in coupling terms, energy left as support heating, reset/repreparation cost, and residual drift after each cycle. Build tradeoff curves showing extractable work versus packet disturbance, deficit duration versus reset cost, support heating versus packet leakage, and cycle count versus accumulated degradation.

The strongest service-control pattern would show that staged, support-mediated protocols preserve packet health while maintaining a measurable extraction event and a closed repayment ledger. The useful output is a map of which service schedules keep the packet quiet, where the repayment burden goes, and which control choices make the cycle repeatable.

---

## Axis 2 — Robustness of negative energy under local accounting

**Question:**
Does the QFT-side negative-energy event remain operationally meaningful when the local energy ledger is repartitioned, or does the claim “negative energy appears here” depend strongly on how the system is divided?

**Vary:**
Hold the physical circuit run fixed and analyze it under multiple local-energy ledgers. Assign interaction energy symmetrically between neighboring sites, assign it to the packet side, assign it to the support side, assign it to the handoff/coupler region, and assign it to the endpoint/battery interface. Compare fine-grained site-level accounting with grouped-region accounting: packet, packet edge, handoff, support, endpoint, battery, and reset reservoir.

Vary the baseline used for “negative.” Compare energy relative to the uncoupled ground state, the prepared correlated state, the ready-to-run state, the pre-extraction state, and the post-reset state. Vary the local observable used as the energy-density diagnostic when more than one reasonable definition exists. Compare ledgers that treat coupling energy as shared, mediator-owned, boundary-owned, or region-owned. Compare instantaneous maps with time-windowed maps, since a transient deficit and its repayment may be clearer across a finite service interval.

**Measure:**
Measure operational invariants first. Record source-injected energy, extracted work into the battery, total energy conservation, reset/repreparation cost, causal order of operations, feed-forward dependence, correlation consumption, and total cycle balance. These quantities define the stable operational core of the protocol.

Then measure local negative-energy maps under each ledger. Track where the deficit appears, how deep it is, how long it lasts, which phase of the protocol it belongs to, where repayment appears, and how the map changes under coarse-graining. Compare the visual/local deficit map against the hard operational ledger. A strong robustness pattern would show stable extracted work, stable repayment cost, stable causal timing, and stable correlation consumption across accounting schemes, with only moderate changes in the displayed local placement of the deficit.

The useful output is an invariance profile. It should show which parts of QFT negative energy behave like a controlled operational resource and which parts are tied to local bookkeeping choices. That profile gives a sharper account of what the circuit actually demonstrates: extractable work, local deficit formation, repayment structure, correlation use, and repeatability.

---

| If results look like this                                                                                   | It suggests                                                            |
| ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Smooth staged protocols reduce packet disturbance                                                           | Timing choreography matters physically                                 |
| Packet-edge or endpoint extraction preserves the packet better than direct packet-centered extraction       | Protected-packet and extraction roles can be separated                 |
| A local deficit appears near the handoff/endpoint while repayment appears in support/reset channels         | Energy borrowing and repayment can be spatially organized              |
| Repeated cycles work with bounded reset overhead                                                            | The protocol behaves like a repeatable service process                 |
| Higher-load protocols fail through packet leakage or support heating                                        | The system has meaningful service-load limits                          |
| Extracted work, reset cost, causal order, and correlation consumption stay stable across accounting schemes | QFT negative energy has a robust operational core                      |
| The local deficit map shifts while the operational ledger remains stable                                    | Local energy-density visualization is partly convention-sensitive      |
| The deficit location, timing, and repayment profile remain stable under several ledgers                     | Local negative energy has strong operational localization              |
| Reset cost dominates repeated cycles                                                                        | Negative energy is operationally real and costly as a service resource |

The experimental target is a controlled map of whether quantum negative energy can be **scheduled, localized, protected, repaid, and repeated**, and whether those features survive changes in local energy accounting.
