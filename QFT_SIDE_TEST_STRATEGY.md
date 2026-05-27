# QET Service-Rail Experimental Test Plan

The testing setup uses a dual-track superconducting circuit-QED chip. One track is a programmable QET field rail. The other track is a protected packet corridor. The field rail supplies the correlated quantum medium, source-side measurement, feed-forward receiver operation, local energy deficit, extracted work, repayment channels, and reset burden. The packet corridor carries a quantum state past the service region and records how well the packet survives while the QET service operates nearby.

The field rail is a line of seven coupled microwave resonators, labeled (F_0) through (F_6), connected by SQUID-tunable nearest-neighbor couplers. The resonator chain is the field-like subsystem. Its Hamiltonian can be calibrated as onsite mode energies plus tunable coupling terms, giving a direct local-energy ledger from resonator occupations and inter-mode correlations. Transmon ancillas are attached at the source station and receiver station. The source ancilla performs the local measurement/injection operation. The receiver ancilla applies the feed-forward-conditioned operation. A high-Q battery resonator or work qubit is coupled to the receiver station so extracted work is recorded as a measurable energy increase.

The packet corridor is a parallel line of five storage-resonator stations, labeled (P_0) through (P_4). A clean first implementation uses a dual-rail logical packet at each station, with two storage modes per packet site. The logical packet state is encoded as
[
|\psi\rangle=c_0|10\rangle+c_1|01\rangle,
]
so the information packet can be moved while keeping a fixed excitation budget. The packet is carried from (P_0) to (P_4) by shaped tunable-coupler state transfer between packet stations. Sequential iSWAP-style transfer gives the first implementation. Adiabatic passage or counterdiabatic transfer gives smoother packet motion in later sweeps.

The field rail and packet corridor meet through a controlled handoff collar near the middle and receiver side of the chip. The handoff collar contains tunable couplers between selected packet stations and selected field-rail modes. These couplers are normally parked at high isolation and activated according to a scheduled pulse envelope. The packet-facing couplers define where the packet is allowed to feel the service environment. The receiver and battery station define where energy extraction is scored. The support modes around the receiver and handoff collar define where repayment, residual excitation, and reset cost are scored.

A single service cycle proceeds in six phases. First, the field rail is cooled and prepared in a correlated low-energy state by adiabatic ramping or variational ground-state preparation. Second, the packet state is loaded into (P_0) and carried along the packet corridor through shaped state-transfer pulses. Third, the source ancilla performs the local QET measurement on the source side of the field rail and sends the classical record to the receiver controller. Fourth, while the packet passes the handoff collar, the receiver station applies the conditioned QET operation and couples the extracted work into the battery register. Fifth, the packet-facing couplers are smoothly faded and the packet transfer completes at (P_4). Sixth, the battery, field rail, handoff collar, and support/reset modes are measured or reset according to the selected run type.

Measurement is divided into service measurement and diagnostic reconstruction. The source-side measurement is part of the physical service. Its backaction is the energy injection event that creates the feed-forward record. Diagnostic information is collected through repeated-shot reconstruction. The same service cycle is run many times. Some batches reconstruct the final packet state. Some batches reconstruct the battery energy. Some batches freeze the couplers at selected service times and reconstruct field-rail occupations and correlations. Some batches measure reset cost and residual heating. This produces a time-resolved ledger without continuous live surveillance of the packet and field rail.

The apparatus therefore carries three ledgers. The packet ledger records packet fidelity, coherence, leakage, entropy growth, and repeated-cycle survival. The QET ledger records source injection, receiver extraction, battery energy, local field-energy deficit, correlation consumption, and repayment. The reset ledger records the cost of restoring the field rail, receiver station, support modes, and battery interface to the next ready state.

The two test axes then ask different questions.

---

## Axis 1 — Service Control and Packet Health

**Question:**
Can the timing, placement, and shape of the QET service cycle protect a carried packet while energy injection, extraction, repayment, and reset occur mostly in the surrounding field rail, support collar, receiver, and reset degrees of freedom?

**Vary:**
Start with a calibrated baseline service cycle. The baseline uses the same prepared field-rail state, the same packet input state, the same packet transfer schedule, the same source measurement, the same receiver operation, the same battery coupling, and the same reset procedure. This gives a reference run for packet survival, extracted work, local field-energy deficit, support heating, and reset cost.

Vary the source operation by changing measurement basis, measurement strength, pulse duration, and source-ancilla coupling envelope. This tests how the initial energy injection and correlation consumption influence later extraction and packet disturbance. The source-side measurement remains a deliberate service operation, and its injected energy is recorded as part of the QET ledger.

Vary the feed-forward schedule by changing the delay between source measurement and receiver operation, adding controlled timing jitter, and comparing one-pulse receiver operations with staged receiver operations. This tests the timing sensitivity of extraction, local deficit formation, and packet exposure while the packet passes the handoff collar.

Vary the packet transport schedule by changing the packet velocity, dwell time near the handoff collar, transfer pulse smoothness, and packet-coupler isolation. Compare abrupt packet transfer, sequential iSWAP transfer, smooth adiabatic transfer, and counterdiabatic transfer. The packet’s carried state is scored at (P_4) against a transport-only baseline.

Vary the handoff collar by changing which packet station is weakly coupled to the field rail, how many couplers participate, how wide the active collar is, and how sharply the couplers turn on and off. Compare a narrow single-coupler collar, a two-coupler packet-edge collar, a broad multi-coupler support collar, and a receiver-side collar. This tests whether a wider or smoother handoff region moves service disturbance out of the protected packet.

Vary the extraction placement by coupling the receiver operation to a field-rail mode near the packet, a field-rail mode just beyond the packet, a terminal receiver mode, or the battery-facing interface. This distinguishes packet-adjacent extraction from endpoint-mediated extraction and measures how extraction location changes packet health and repayment placement.

Vary the release profile by comparing sudden decoupling, smooth fade, minimum-jerk fade, and multi-step release of the packet-facing couplers. The release sweep tests whether packet disturbance comes from the extraction event itself, from residual coupling after extraction, or from sharp decoupling transients.

Vary the reset process by comparing local receiver reset, distributed support reset, delayed reset, and reservoir-mediated reset. Repeated-cycle runs should use the same packet input ensemble and the same field-rail preparation target, then measure how packet health and energy accounting drift across many service cycles.

After single-parameter sweeps, run combined service families: direct collar service, broad support-collar service, endpoint-mediated service, smooth staged service, aggressive high-load service, and repeated-cycle service. These families map which combinations preserve packet health while maintaining a measurable QET extraction event.

**Measure:**
Measure packet health as its own output channel. For each packet input state, reconstruct the final packet state at (P_4). Use a standard input ensemble, such as the six cardinal qubit states on the Bloch sphere, plus selected coherent or code-state packets if the storage resonators support them. Record state fidelity, process fidelity, leakage out of the logical packet subspace, phase noise, amplitude damping, unwanted packet-field entanglement, and cycle-to-cycle degradation.

Measure packet disturbance during the service window through stroboscopic batches. Freeze the packet transfer at selected times, turn off packet-facing couplers, and reconstruct the packet state and nearby support modes. These snapshots give packet exposure maps across entry, handoff, receiver operation, release, and post-release transfer. The same snapshots should be repeated for transport-only runs, source-only runs, receiver-only runs, and full service runs.

Measure the QET energy ledger by calibrated Hamiltonian terms. Record source-side injected energy, receiver-side energy change, battery energy increase, local field-energy deficit near the receiver/handoff region, energy stored in support modes, energy stored in field-rail couplings, energy left as residual heating, and reset/repreparation cost. The local energy ledger should include onsite resonator occupations and coupling-term correlations, so the experiment can separate field-mode energy from interaction energy.

Measure tradeoff curves that matter for service control. Plot extracted work versus packet infidelity, deficit duration versus packet dephasing, source injection versus receiver extraction, support heating versus packet leakage, release smoothness versus residual excitation, and reset cost versus cycle count. The key service result is a burden-separation map: how much energy cost and disturbance lands in the packet, the handoff collar, the field rail, the receiver, the battery, and the reset reservoir.

A strong service-control pattern would show that smoother staged protocols preserve packet fidelity while retaining measurable extracted work and a closed repayment ledger. It would also show that packet-edge and endpoint-mediated operations reduce packet disturbance compared with operations that place extraction directly on the carried packet. The resulting map identifies which schedules keep the packet quiet, which schedules overload the support collar, and which schedules support repeated operation.

---

## Axis 2 — Robustness of Negative Energy Under Local Accounting

**Question:**
Does the QFT-side negative-energy event remain operationally meaningful when the local energy ledger is repartitioned among field modes, couplers, handoff collar, receiver, battery, packet corridor, support modes, and reset reservoir?

**Vary:**
Hold the physical service run fixed and vary the local-energy accounting scheme. Analyze the same reconstructed circuit state under several accepted Hamiltonian partitions. Assign each coupling term symmetrically between neighboring modes, assign it to the upstream field mode, assign it to the downstream field mode, assign it to the handoff collar, assign it to the receiver interface, and assign it to the support ledger. Compare fine-grained site-level accounting with grouped-region accounting.

Vary the region definitions. Use a minimal receiver region containing a single receiver field mode and battery interface. Use a receiver-plus-collar region containing the receiver field mode, the battery interface, and the nearest packet-facing coupler. Use a broader support region containing neighboring field modes and tunable couplers. Use a packet-excluding field ledger and a packet-inclusive collar ledger. These region choices test how the location and duration of the local deficit respond to reasonable boundary choices.

Vary the reference baseline used for the word “negative.” Compare energy relative to the uncoupled device ground state, the coupled field-rail ground state, the prepared correlated state, the ready-to-run state immediately before source measurement, the state immediately before receiver operation, and the post-reset state. This produces a baseline-sensitivity profile for local energy deficits and repayment.

Vary the diagnostic observable. For the resonator field rail, compare ledgers built from onsite occupations alone, onsite occupations plus shared coupling terms, normal-mode reconstructed energy, local quadrature-energy density, and coarse-grained finite-window energy over several neighboring modes. For packet health, keep the packet fidelity ledger separate from the field-energy ledger, then examine how much packet-field coupling contaminates local energy assignments during handoff.

Vary the time window. Compare instantaneous snapshots with finite-window averages over source operation, packet entry, handoff, receiver extraction, release, and reset. A transient local deficit may be sharper in an instantaneous map, while repayment and support burden may be clearer in finite-window accounting.

**Measure:**
Measure operational invariants first. These include source-injected energy, battery energy increase, total device energy balance, reset/repreparation cost, feed-forward dependence, causal order of operations, and correlation consumption between source and receiver regions. These quantities define the core service event because they are tied to actual operations and measured energy changes.

Measure local negative-energy maps under every accounting scheme. Track where the deficit appears, how deep it is, how long it lasts, which service phase it belongs to, which modes carry the compensating positive energy, and which reset operation restores the rail. Compare the maps under different coupling assignments, region groupings, baselines, and time windows.

Measure stability of the extraction claim separately from stability of the local deficit map. Extracted work is scored by the battery. The local deficit is scored by field-rail energy reconstruction. Repayment is scored by support, coupling, residual heating, and reset cost. This separation makes it possible to find a robust extraction-and-repayment cycle even when the visual placement of local energy shifts under different partitions.

Measure an invariance profile. The profile should report which features remain stable across reasonable ledgers: battery work, source injection, correlation consumption, timing order, reset cost, deficit phase, deficit region, and repayment region. The profile should also report which features are sensitive to accounting choices: exact deficit depth, exact deficit boundary, interaction-energy attribution, and visual localization.

A strong robustness pattern would show stable extracted work, stable source injection, stable reset cost, stable causal timing, and stable correlation consumption across local-energy partitions. The local deficit map may shift moderately as coupling energy is reassigned, while the service event remains anchored by operational observables. A stronger localization pattern would show the deficit region itself remaining tied to the same receiver/collar phase across several ledgers.

The useful output is an invariance map of QFT-side negative energy. It identifies which aspects behave like a controlled operational resource and which aspects belong to the presentation of local energy density. That map is valuable even before any gravitational interpretation is attempted, because it gives a sharper experimental account of energy extraction, local deficit formation, repayment, correlation use, and repeatability.

---

## Measurement and Control Runs

Each reported data point should come from matched batches of repeated shots. One batch performs the full service cycle and measures packet output. Another batch performs the full service cycle and measures battery energy. Other batches freeze the circuit at selected service times and reconstruct field-rail mode occupations, coupler correlations, and local energy maps. The service movie is assembled from these repeated identical runs.

The source measurement receives special treatment. It is a service operation, so its backaction is part of the physics being tested. Its energy injection, measurement basis, measurement strength, and outcome-conditioned feed-forward record are logged as service variables. Diagnostic readout is performed after the selected run phase, after couplers are parked in measurement configuration.

Matched controls should be run alongside the full service cycle. Packet transport alone gives the packet-motion baseline. Field-rail QET without packet loading gives the energy-extraction baseline. Packet transport with source measurement and disabled receiver operation gives the source-backaction baseline. Packet transport with randomized feed-forward gives the feed-forward-dependence baseline. Receiver drive without valid source record gives the receiver-control baseline. Full service with packet-facing couplers parked off gives the crosstalk baseline. Repeated-cycle service gives the reset and drift baseline.

The apparatus should record calibration data for readout crosstalk, residual packet-field coupling, battery leakage, coupler hysteresis, source-measurement infidelity, receiver-pulse error, and reset error. These calibration ledgers let packet disturbance, field-energy deficit, extracted work, and reset burden be separated in the final analysis.

---

## Outcome Patterns

| If results look like this                                                                                                  | It suggests                                                                         |
| -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Smooth staged protocols reduce packet disturbance while preserving battery work                                            | Timing choreography has physical control value                                      |
| Packet-edge or endpoint-mediated extraction preserves packet fidelity better than packet-centered extraction               | Protected-packet and extraction roles can be separated                              |
| A local field-energy deficit appears near the receiver or handoff collar while repayment appears in support/reset channels | Energy borrowing and repayment can be spatially organized                           |
| Repeated cycles work with bounded reset overhead and bounded packet degradation                                            | The protocol behaves like a repeatable service process                              |
| Higher-load protocols fail through packet leakage, support heating, or reset overhead                                      | The system has meaningful service-load limits                                       |
| Battery work, source injection, causal order, and correlation consumption stay stable across accounting schemes            | QFT negative energy has a robust operational core                                   |
| The local deficit map shifts while the operational ledger remains stable                                                   | Local energy-density visualization has convention-sensitive features                |
| The deficit region remains tied to the same receiver/collar phase across several ledgers                                   | Local negative energy has strong operational localization                           |
| Reset cost dominates repeated cycles                                                                                       | Negative energy is operationally real and costly as a service resource              |
| Support/collar ledgers absorb most repayment while packet fidelity remains high                                            | The service architecture successfully separates packet health from repayment burden |

The experimental target is a controlled map of whether quantum negative energy can be scheduled, localized, protected, repaid, and repeated, and whether those features survive changes in local energy accounting. The first axis tests whether service choreography protects a carried quantum packet. The second axis tests whether the negative-energy event is a robust operational structure under local-energy repartitioning.
