I used your uploaded draft as the base and kept the two original axes. I also aligned the hardware roles with the active-rail disclosure’s separation of prepared support, live packet, handoff, source placement, and reset roles, plus its service-cycle structure.   

# QET Service-Rail Experimental Test Plan

## Experimental Spine

The experiment uses a superconducting circuit-QED device to test two operational questions. The first question is how service parameters influence the health of a protected quantum packet. The second question is whether QFT-side negative energy behaves like a robust operational structure, or whether its apparent location and meaning depend strongly on the local energy partition used to describe the system.

The apparatus is a programmable QET service system. A coupled microwave-resonator rail supplies the correlated quantum medium used for QET. A separate protected packet memory carries the quantum state whose health is scored. A handoff collar controls how strongly the packet memory is exposed to the service rail. A receiver station performs the feed-forward-conditioned QET operation. A battery mode records extracted work. Nearby support and reset modes record repayment, residual excitation, and reset cost.

The packet system has two operating modes. The primary mode is an anchored packet test: the packet is prepared in a high-Q storage resonator near the handoff collar, held through a service window, and then tomographically scored. This mode cleanly tests how service parameters affect packet health. The extension mode is a carried packet test: the packet is moved through a short corridor of storage resonators while the service rail operates near the handoff region. This mode adds a closer transport analogue after the anchored-packet energy ledger is calibrated.

This structure keeps the original experimental center intact. The service rail supplies QET extraction, local deficit formation, repayment, and reset. The packet memory supplies a protected subsystem whose health can be measured under different service schedules. The same physical runs can then be reanalyzed under different local energy partitions to test robustness of the negative-energy interpretation.

---

## Apparatus Design

The field rail is a line of coupled microwave resonators, labeled (F_0) through (F_6). Neighboring resonators are connected by SQUID-tunable couplers so the effective rail Hamiltonian can be calibrated as onsite resonator energies plus controlled coupling terms. The rail is the field-like subsystem. It is prepared in a correlated low-energy state and supplies the QET resource.

A source transmon ancilla couples to the source side of the rail, near (F_0) or (F_1). This ancilla performs the source-side measurement. Its measurement backaction is part of the service: it injects energy, consumes correlations, and produces the classical feed-forward record used by the receiver.

A receiver transmon ancilla couples to the receiver side of the rail, near (F_5) or (F_6). It applies the feed-forward-conditioned operation. A battery mode, implemented as a high-Q resonator or work qubit, couples to the receiver station. Battery energy is the clean operational readout for extracted work.

The protected packet system is a high-Q storage-resonator memory placed near the receiver/handoff region. In the anchored-packet mode, the packet state is loaded into this memory, held through the service window, and reconstructed after the service. In the carried-packet extension, the packet memory becomes one station in a short packet corridor (P_0) through (P_4), and the packet is moved by shaped tunable-coupler state-transfer pulses.

The clean first packet encoding is a dual-rail logical qubit, using two storage modes:
[
|\psi\rangle=c_0|10\rangle+c_1|01\rangle.
]
This keeps the packet within a fixed excitation sector and makes leakage, dephasing, and amplitude loss easier to diagnose. Other packet states can be added later: coherent-state packets, cat-code packets, or small bosonic code states.

The handoff collar is the controlled interface between packet and rail. It consists of one or more tunable couplers between the protected packet memory and selected receiver-side rail modes. These couplers are normally parked at high isolation. During service, they are activated through shaped envelopes: narrow collar pulses, broader support-collar pulses, smooth fades, minimum-jerk fades, and staged multi-coupler handoffs.

Support and reset modes are placed around the receiver and handoff collar. These modes collect residual excitation, repayment burden, and reset cost. They also let the experiment distinguish packet damage from support heating and reset overhead.

The device therefore has five functional regions: source station, field rail, handoff collar, protected packet memory, and receiver/battery/reset station. Each region has a corresponding energy ledger.

---

## Service Cycle

A single anchored-packet service cycle proceeds as follows.

First, the field rail is cooled and prepared in a correlated low-energy state. Preparation can use adiabatic ramping, variational ground-state preparation, or calibrated pulse preparation. The prepared rail state is verified in separate calibration batches.

Second, the packet state is loaded into the protected packet memory. The handoff couplers are parked at high isolation while the packet is prepared.

Third, the source ancilla performs the local QET measurement on the source side of the rail. The source outcome is recorded and routed to the receiver controller. The energy injected by this measurement is recorded as part of the service ledger.

Fourth, the handoff collar opens according to the selected service schedule. The receiver station applies the feed-forward-conditioned operation. The receiver operation extracts work into the battery mode and creates the local field-energy deficit associated with the QET event.

Fifth, the handoff collar closes through the selected release profile. The packet remains in the protected memory during the service window. The receiver, rail, battery, support, and reset modes are then measured or reset according to the selected run type.

Sixth, the packet memory is tomographically reconstructed. The output packet state is compared against the input state and against matched no-service baselines.

The carried-packet extension uses the same sequence, with one additional layer: the packet is transferred from (P_0) to (P_4) through shaped coupler pulses, and the service window is timed so the packet passes the handoff collar during the receiver operation. This extension is run after the anchored-packet protocol has established the baseline energy ledger and packet-health response.

---

## Measurement Strategy

Measurement is divided into service measurement and diagnostic reconstruction.

The source-side measurement is a service operation. It creates the classical record used for feed-forward and supplies the controlled energy injection. Its backaction is part of the physics being tested.

Diagnostic reconstruction is performed through repeated-shot batches. The same service cycle is run many times. One batch reconstructs the final packet state. Another batch measures battery energy. Other batches freeze the circuit at selected service times, park the couplers, and reconstruct field-rail occupations, coupling correlations, and local energy maps. Additional batches measure reset cost and residual heating.

This produces a time-resolved service ledger from repeated identical runs. It avoids continuous live monitoring of the packet and rail during the service window, while still reconstructing packet health, extracted work, local deficit formation, repayment, and reset.

The packet ledger records fidelity, coherence, leakage, entropy proxies, packet-field entanglement, and repeated-cycle survival. The QET ledger records source injection, receiver extraction, battery energy, local field-energy deficit, correlation consumption, and compensating positive energy. The reset ledger records the cost of returning the rail, receiver, support modes, and battery interface to the next ready state.

---

## Axis 1 — Service Control and Packet Health

**Question:**
How do service parameters influence the health of a protected packet while QET extraction, deficit formation, repayment, and reset occur in the surrounding rail, handoff collar, receiver, support, and battery degrees of freedom?

**Vary:**
Start with a calibrated anchored-packet baseline. The baseline uses the same prepared field-rail state, the same packet input state, the same source measurement, the same receiver operation, the same handoff-collar pulse, the same battery coupling, and the same reset procedure. This baseline gives reference values for packet survival, extracted work, local field-energy deficit, support heating, and reset cost.

Vary the source operation by changing measurement basis, measurement strength, pulse duration, and source-ancilla coupling envelope. This maps how energy injection and correlation consumption affect later extraction and packet disturbance.

Vary the feed-forward schedule by changing receiver delay, timing jitter, and receiver-pulse structure. Compare one-pulse receiver operations with staged receiver operations. This maps the timing sensitivity of extraction, local deficit formation, and packet exposure.

Vary the handoff collar by changing its coupling strength, active width, pulse shape, participating couplers, and duration. Compare a narrow single-coupler collar, a two-coupler packet-edge collar, a broad support collar, and a receiver-side collar. This maps how much service burden reaches the packet versus the support region.

Vary extraction placement by coupling the receiver operation to a rail mode near the packet, a rail mode just beyond the packet, a terminal receiver mode, or the battery-facing interface. This maps how extraction location affects packet health, local deficit formation, and repayment placement.

Vary the release profile by comparing sharp decoupling, smooth fade, minimum-jerk fade, and multi-step release of the packet-facing couplers. This maps whether packet disturbance is dominated by receiver action, collar exposure, or release transients.

Vary reset by comparing local receiver reset, distributed support reset, delayed reset, and reservoir-mediated reset. Repeated-cycle runs should use the same packet input ensemble and the same rail-preparation target, then measure packet-health drift and energy-ledger drift across many cycles.

After anchored-packet sweeps, run selected carried-packet sweeps. Use transport-only calibration first, then add source-only, receiver-only, and full-service runs. In the carried-packet mode, vary packet speed, dwell time near the handoff collar, packet-transfer pulse smoothness, and collar timing relative to packet arrival.

**Measure:**
Measure packet health as its own output channel. For each packet input state, reconstruct the final packet state. Use a standard process-tomography ensemble, such as the six cardinal qubit states on the Bloch sphere. Record state fidelity, process fidelity, leakage out of the logical packet subspace, dephasing, amplitude damping, packet-field entanglement, and cycle-to-cycle degradation.

Measure packet disturbance during the service window using stroboscopic batches. Freeze the service at selected times, park the couplers, and reconstruct the packet memory and nearby support modes. These snapshots produce packet-exposure maps across source measurement, handoff opening, receiver operation, release, and reset.

Measure the QET energy ledger by calibrated Hamiltonian terms. Record source-side injected energy, receiver-side energy change, battery energy increase, local field-energy deficit near the receiver/handoff region, energy stored in support modes, energy stored in coupling terms, residual heating, and reset/repreparation cost.

Measure tradeoff curves that answer the service-control question. Plot extracted work versus packet infidelity, deficit depth versus packet dephasing, deficit duration versus packet leakage, source injection versus receiver extraction, support heating versus packet damage, release smoothness versus residual excitation, and reset cost versus cycle count.

The main output is a service-parameter map. It shows which schedules keep the packet quiet, which schedules move repayment into support/reset channels, which schedules overload the handoff collar, and which schedules support repeated operation.

---

## Axis 2 — Robustness of Negative Energy Under Local Accounting

**Question:**
Does the QFT-side negative-energy event remain operationally meaningful when the local energy ledger is repartitioned among field modes, couplers, handoff collar, receiver, battery, packet memory, support modes, and reset reservoir?

**Vary:**
Hold the physical service run fixed and vary the energy accounting. Analyze the same reconstructed circuit state under several Hamiltonian partitions.

Assign each coupling term symmetrically between neighboring modes. Then assign the same coupling term to the upstream field mode, downstream field mode, handoff collar, receiver interface, support ledger, or packet-facing boundary. Compare fine-grained site-level accounting with grouped-region accounting.

Vary region definitions. Use a minimal receiver region containing one receiver-side field mode and the battery interface. Use a receiver-plus-collar region containing the receiver field mode, battery interface, and nearest packet-facing coupler. Use a broader support region containing neighboring field modes and tunable couplers. Use a packet-excluding field ledger and a packet-inclusive collar ledger.

Vary the reference baseline used for “negative.” Compare energy relative to the uncoupled device ground state, the coupled field-rail ground state, the prepared correlated state, the ready-to-run state before source measurement, the state before receiver operation, and the post-reset state.

Vary the diagnostic observable. Compare ledgers built from onsite occupations alone, onsite occupations plus shared coupling terms, normal-mode reconstructed energy, local quadrature-energy density, and coarse-grained finite-window energy over neighboring modes.

Vary the time window. Compare instantaneous snapshots with finite-window averages over source operation, handoff opening, receiver extraction, release, and reset. This separates sharp local deficits from the broader repayment cycle.

**Measure:**
Measure operational invariants first. These include source-injected energy, battery energy increase, total device energy balance, reset/repreparation cost, feed-forward dependence, timing order, and correlation consumption between source and receiver regions. These are tied to physical operations and measured energy changes.

Then measure local negative-energy maps under every accounting scheme. Track where the deficit appears, how deep it is, how long it lasts, which service phase it belongs to, which modes carry compensating positive energy, and which reset operation restores the rail.

Measure stability of the extraction claim separately from stability of the local deficit map. Extracted work is scored by the battery. The local deficit is scored by field-rail energy reconstruction. Repayment is scored by support excitation, coupling energy, residual heating, and reset cost.

Measure an invariance profile. The profile reports which features remain stable across ledgers: battery work, source injection, correlation consumption, timing order, reset cost, deficit phase, deficit region, and repayment region. It also reports which features are ledger-sensitive: exact deficit depth, exact deficit boundary, interaction-energy attribution, and visual localization.

The main output is a robustness map. It shows which aspects of QFT-side negative energy behave as stable operational features of the protocol and which aspects depend on local energy presentation.

---

## Measurement and Control Runs

Each data point should come from matched repeated-shot batches.

Packet-only runs prepare the packet, hold or transport it through the same timing window, and reconstruct the output packet state. These runs establish packet baseline error.

Rail-only QET runs prepare the field rail, perform source measurement and receiver feed-forward, and measure battery energy and rail energy maps. These runs establish QET extraction and repayment without packet exposure.

Source-only packet runs prepare the packet and rail, perform the source measurement, and disable the receiver operation. These runs isolate source-measurement crosstalk and source backaction.

Receiver-only packet runs apply receiver pulses without a valid source record. These runs isolate receiver-drive disturbance and battery-interface crosstalk.

Randomized-feed-forward runs preserve the same pulse schedule while scrambling the source-to-receiver correlation. These runs test whether extraction depends on the QET feed-forward record.

Collar-off full-service runs run the rail QET protocol while packet-facing couplers stay parked. These runs measure field-to-packet crosstalk outside scheduled exposure.

Full-service anchored-packet runs expose the packet through the selected handoff collar while QET extraction occurs. These runs answer the primary packet-health question.

Full-service carried-packet runs move the packet through (P_0) to (P_4) while the QET service window opens near the handoff collar. These runs test the transport extension after anchored-packet calibration.

Repeated-cycle runs execute multiple service cycles with the same preparation target. These runs measure reset burden, accumulated heating, packet degradation, and drift in the energy ledger.

The apparatus should record calibration data for readout crosstalk, residual packet-field coupling, battery leakage, coupler hysteresis, source-measurement infidelity, receiver-pulse error, packet-transfer error, and reset error. These calibration ledgers support clean separation between packet disturbance, field-energy deficit, extracted work, repayment, and reset burden.

---

## Theory-testing outcome table

| Axis                                        | Result pattern                                                                                                                                                                             | Answer to the central question                                     | Interpretation                                                                                                                                      |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Axis 1: service parameters vs packet health | At fixed or comparable extracted work, smoother handoff, staged receiver operation, wider support collar, or gentler release produces higher packet fidelity and lower leakage/decoherence | **Yes, service parameters control packet health**                  | Packet health depends on choreography, placement, timing, and support routing, not only on whether QET occurred                                     |
| Axis 1                                      | Packet health changes predictably with handoff width, release smoothness, receiver placement, reset timing, or service load                                                                | **Yes, service parameters define an operating envelope**           | The experiment yields a service map: safe schedules, damaging schedules, high-load boundaries, and repeatable-cycle regions                         |
| Axis 1                                      | At matched integrated coupling exposure and matched extracted work, packet health is nearly unchanged across timing, placement, handoff, release, and reset schedules                      | **No strong choreography effect**                                  | Packet health is governed mainly by total exposure/interaction strength; service shaping adds little protective structure                           |
| Axis 1                                      | Packet protection improves only by reducing extraction, deficit depth, or battery work proportionally                                                                                      | **Mostly no, with tradeoff**                                       | The apparatus shows a protection/extraction Pareto curve rather than an independent packet-protection mechanism                                     |
| Axis 1                                      | Packet health worsens specifically when repayment/reset is concentrated near the packet, and improves when repayment/reset is distributed into support modes                               | **Yes, repayment placement matters**                               | Packet health is affected by where the compensating energy burden is routed                                                                         |
| Axis 1                                      | Packet health is insensitive to reset placement once the live handoff ends                                                                                                                 | **Reset placement has weak packet-health relevance**               | Reset burden matters energetically but has little effect on the protected packet in that regime                                                     |
| Axis 2: robustness of QFT negative energy   | Battery work, source injection, feed-forward dependence, reset cost, correlation consumption, and the local deficit phase remain stable across reasonable local-energy partitions          | **Yes, QFT negative energy has a robust operational core**         | The event survives repartitioning as an extraction/deficit/repayment structure                                                                      |
| Axis 2                                      | The local deficit remains attached to the same receiver/collar region across partitions, baselines, and finite time windows                                                                | **Yes, local negative energy is robustly localized in this setup** | The negative-energy event behaves like a stable local operational feature                                                                           |
| Axis 2                                      | Battery work and repayment remain stable, while the exact deficit boundary/depth shifts with coupling-energy assignment                                                                    | **Mixed result**                                                   | QET extraction is robust; the local negative-energy map has convention-sensitive details                                                            |
| Axis 2                                      | Battery work is feed-forward dependent, but the negative-energy region moves or disappears under reasonable partitions                                                                     | **Operational extraction yes; stable local negativity weak**       | QFT-side energy extraction is real, while “negative energy here” behaves like a partition-sensitive description in this setup                       |
| Axis 2                                      | Total energy accounting closes, but no local deficit remains stable across partitions, baselines, or time windows                                                                          | **No robust local negative-energy structure**                      | The experiment supports total energy accounting and repayment, while local negativity behaves like ledger-dependent bookkeeping in this realization |
| Axis 2                                      | A local deficit appears in one preferred ledger but disappears under equally reasonable ledgers                                                                                            | **No strong robustness**                                           | The negative-energy claim depends on a chosen local accounting convention                                                                           |
| Axis 2                                      | Deficit timing, location, extracted work, and repayment pattern all remain stable across partitions                                                                                        | **Strong positive result**                                         | QFT negative energy behaves like a controlled operational resource in this hardware analogue                                                        |
| Axis 2                                      | Different partitions produce incompatible stories about where extraction, deficit, and repayment occur, while hard battery/source/reset observables remain stable                          | **Strong negative result for local negativity**                    | The physical energy cycle is real; the local negative-energy story lacks invariant structure                                                        |

## Apparatus-validity gates

| Validity gate                                                                     | Meaning                                                                |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Rail-only QET produces feed-forward-dependent battery work                        | The QET service is operating                                           |
| Randomized feed-forward removes or strongly reduces battery work                  | The battery signal is correlation-mediated                             |
| Packet-only runs preserve packet fidelity above threshold                         | The packet memory/corridor is usable                                   |
| Collar-off full-service runs show low packet disturbance                          | Stray crosstalk is controlled                                          |
| Source-only and receiver-only controls stay below full-service disturbance levels | Packet damage is tied to the scheduled service, not raw control pulses |
| Energy reconstruction closes within calibration tolerance                         | The energy ledger is trustworthy                                       |
| Repeated-shot snapshots agree with endpoint observables                           | The reconstructed energy movie is reliable                             |

