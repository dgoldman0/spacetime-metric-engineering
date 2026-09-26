# Independent review of Chapter 2's teaching devices

Report of an independent reviewer agent, 26 September 2026. It is kept here
verbatim as provenance. The reviewer worked from
`reviews/puzzle-design-worksheet.md` and the chapter texts as they stood after
commit be00945 plus the uncommitted Chapter 1 stiffness redesign. It did not
see the author's earlier verdicts. Its scratch scripts and logs are in the
session scratchpad under `review_ch2/`. Line numbers refer to
`chapters/ch02-spacetime-geometry.tex` at that time. The author's
reconciliation is recorded separately.

---

## Review of Chapter 2 teaching devices

I made no changes to the repository. My scripts and logs are in the `review_ch2/` scratchpad folder:
- `numbers.py`, `orbit_paradox.py`, `curvature.py` (sympy), `thrown_ball.py`, `proposals_check.py`, each with a `*_run*.log`;
- `figs/` holds the rendered figures.

`orbit_paradox_run1.log` is a failed first run: my file name `numbers.py` shadowed Python's `numbers` module. I kept it and reran with `python3 -P` as `run2`.

I did not read any review notes. I only grepped `textbook/checks/*.py` to see which numbers existing scripts cover (for W10). They cover most numbers, but nothing covers the rebuilt sliding grid.

**Scorecard**
- **PASS (5):** Check 2.2, Check 2.3, The thrown ball, The windowless capsule, Check 2.5.
- **MARGINAL (4):** Betelgeuse, The twins, Light climbing a tower, Problem 2.11.
- **FAIL (4):** Check 2.1, A sliding grid, Check 2.4, The fish and the waterfall.

---

### 1. "Has Betelgeuse exploded?" (thought experiment): MARGINAL
- **W1:** The interval sorts pairs of events for every observer, and light cones decide what can influence what. For spacelike pairs the time order is not shared.
- **W2:** Belief in a universal "now".
- **W3:** "It has happened, we just can't see it for 550 years. No influence either way."
- **W4:**
  - Δt = 0 and Δx = 550 ly give Δs² = +302,500 ly², which is spacelike. There is no influence either way, and the light arrives in 550 years.
  - Those two sub-answers are what the reader already believes.
  - The only surprise is that "has it happened yet?" depends on the observer. At v = 0.5 toward the star, t′ = −317.5 yr; walking at 1 m/s gives 58 s; the Earth's orbital motion gives ±20 days.
  - The surprise enters at the relativity of simultaneity. The topic never shows it: it has no Lorentz transformation, which appears only inside Problem 2.2, and the resolution defers to that problem.
- **W5:** Passes. At 55 or 5500 ly, and at v = 0.05 (27.5 yr), the lesson is unchanged.
- **W6:** FAIL. The key claim needs a tool the reader lacks.
- **W7:** Passes. The signs are right. There is no exact common rest frame, which is acceptable for a "suppose".
- **W8:** FAIL. Ch1 lines 592–595 state the answer: observers disagree on order "whenever the events are too far apart for light to connect them".
- **W9:** Passes. It overlaps Check 2.1 somewhat, and Problem 2.2 continues it deliberately.
- **W10:** Numbers recomputed.
- **Fix:** Put a ship in the setup: it passes you toward the star at 0.5, and its crew dates the explosion 318 yr before passing. Ask how far away the crew says it was, and whether they could have seen it and warned you.
  - W3: "length-contracted, 476 ly".
  - W4: invariance gives Δx′ = √(550² + 317.5²) = 635 ly. The star was then 476 + 0.5 × 317.5 = 635 ly away, and its light is still 317.5 yr from the crew. The surprise enters at invariance of the interval (W1).
  - W5: at v = 0.05 the numbers are 27.5 yr, 550.7 ly against a contracted 549.3; at D = 55 ly they are 31.75 yr and 63.5 ly.
  - W6: needs only eq:interval. W8: Ch1 never says this. W10: in `proposals_check_run1.log`.
  - If the resolution keeps the claim about order, move the Lorentz transformation and the one-line sign-flip argument into the topic.

### 2. "The twins" (thought experiment): MARGINAL
- **W1:** Proper time is worldline length, and the straight worldline is the longest.
- **W2:** The mutual slowing looks symmetric.
- **W3:** For this audience: "the traveller, because she accelerated". The verdict is folklore; the misconception is that acceleration does the ageing.
- **W4:** 8.48 ly at 0.8 takes 10.6 yr; the traveller records 0.6 × 10.6 = 6.36 yr; the gap is 4.24 yr. The surprise enters at "the bent worldline is shorter", which is W1.
- **W5:** Passes. With D × 10 the gap is 42.4 yr; at v = 0.08 it is 0.34 yr.
- **W6:** Marginal. "Resolved at the corner, where the traveller's sense of 'now' jumps forward" rests on simultaneity, which the chapter never develops. The jump is 1.91 → 8.69 Earth years.
- **W7:** Passes, with an idealised turnaround. Line 187 "seen" is wrong: on the way home each twin sees the other's clock run three times fast.
- **W8:** Passes. **W9:** Passes.
- **W10:** Passes. The figure's ticks are consistent.
- **Fix:**
  - Resolve the symmetry with a tick count the reader can check on the diagram. Yearly signals arrive at 1/3 rate going out and 3× coming back, so the traveller receives 1.06 + 9.54 = 10.6 Earth years.
  - Aim the question at the real misconception: "The turnaround takes one day. With the same turnaround, a star ten times farther: does the gap change?" It becomes 42.4 yr, so the corner does not do the ageing.

### 3. Check 2.1 (classify): FAIL
- **Working:**
  - **W1:** classifying an interval.
  - **W3:** a sign slip, or "B is later, so A can affect it".
  - **W4:** AB = −9 + 16 = +7, spacelike, no; AC = −25 + 16 = −9, timelike, yes. Both correct.
- **C1:** FAIL. It is substitution into eq:interval plus recall of the three definitions in the paragraph just above.
- **W9:** FAIL. Problem 2.1 is the same drill (−4 + 2.25 = −1.75).
- **W6, W7, W10:** pass.
- **Fix:** "C happens 5 s after A at B's place. A probe goes from A to C: how fast, and what does its clock read? Can any probe attend both A and B? For an observer who calls A and B simultaneous, how far apart are they?"
  - The answers are 0.8; 3 s; no; √7 = 2.65 ls. The Lorentz checks at v = 0.8 (Δt′ = 3, Δx′ = 0) and v = 0.75 (Δt′ = 0, Δx′ = 2.646) confirm them.
  - The step that tests understanding is using the invariant to get a clock's time or a distance.

### 4. Check 2.2 (zigzag): PASS
- **W1:** No lower bound on proper time; the straight path is longest.
- **W3:** Euclidean intuition.
- **W4:** dτ = √(1−v²)dt → 0. At v = 0.99 the clock records 1.41 of the 10 yr. The understanding step is that the shortening is unbounded.
- **C1:** Passes.
- **W7:** Minor. Light out and back has τ = 0, so the answer should say the infimum is reached only by light, which carries no clock.
- **W6, W9, W10:** pass.

### 5. "A sliding grid" (thought experiment): FAIL
- **W1:** The metric works in any coordinates. Coordinate features, even a direction no light takes in the labels, can belong to the labels alone.
- **W2:** "1.5 squares per unit time looks superluminal."
- **W3:** "No, it's a moving pattern", and "no, lines at 2c outrun light." Both are correct, so there is no surprise.
- **W4:** FAIL.
  - With x = X + v₀t, light has dx/dt = v₀ ± 1: 1.5 and −0.5, or 3 and 1 at v₀ = 2. That is Galilean addition of a pattern's speed.
  - eq:flow-metric only relabels these numbers. No step introduces a surprise, and the metric is not the engine.
- **W5:** FAIL for the hook. It needs squares one light-unit across; with 10-light-unit squares, light covers 0.15 squares per unit time.
- **W6:** Marginal. "Surveyors paint grids on solid ground" is unused.
- **W7:** Passes on sign: a fixed-x clock has ds² = +3dt² at v₀ = 2. The units are unstated (lines 209–210).
- **W8:** FAIL. The setup answers itself (lines 207–209: "only a pattern ... can slide at any speed at all"). Ch1's "race with a light beam" and "message to the front" answer the second question.
- **W9:** FAIL. The v₀ = 2 part is the lesson of Ch1's message to the front and of the fish two topics later. The fixed-x computation repeats Check 2.3.
- **W10:** Numbers correct, but no existing check script covers them.
- **Extra risk:** line 312, "Keep this in mind for the river".
  - At v₀ = 2 the label x is a time function everywhere (g^xx = 1 − v₀² = −3, verified), exactly like r inside a black hole, yet there is no horizon.
  - The chapter never says what makes the black-hole horizon physical: r is fixed by sphere areas, and static observers can exist outside it.
  - The link invites "horizons are label effects".
- **Replacement, "A current faster than light":** "Ch1's radio command stalled where space streamed backward at 2c. Now let space stream at 2c uniformly everywhere. Two probes drift with it 1 light-second apart, and the downstream one radios upstream. Does the message arrive?"
  - W3: "never".
  - W4: probes move at dx/dt = 2 and the message at v₀ − 1 = 1, so they meet at t = 1, the flat-space time.
  - The surprise enters at the relabelling x′ = x − v₀t from Example ex:flow: the uniform stream is flat, and both probes sit at fixed x′. Ch1's stall needs a stream that changes from 2c to 0, which no relabelling removes.
  - W5: t = 1 at v₀ = 20; t = 10 at separation 10; t = 1 at v₀ = 0.2.
  - W6 and W7 pass. W8: Ch1 suggests the opposite. W9: distinct from the fish. W10: verified.
  - The resolution should end by saying that a horizon needs the flow to cross c next to slower flow, where observers can hold position.

### 6. Check 2.3 (grid clock): PASS
- **W3:** "10 yr, since the clock sits at fixed x."
- **W4:** dx = 0 gives dτ = 0.8dt, so 8 yr, equal to SR dilation at 0.6. The understanding step is that fixed x is not rest.
- **C1:** Passes by exception, because the equality is the lesson.
- **W9:** Minor. The sliding-grid resolution repeats this computation.
- **W10:** Passes.

### 7. "Light climbing a tower" (thought experiment): MARGINAL
This is the soundest of the seven.
- **W1:** In a static field, clocks at different heights tick at different rates, and the redshift is that difference.
- **W2:** Energy conservation (the free-lift argument) collides with crest conservation (a steady beam).
- **W3:** "The light slows", "the wavelength stretches", or "crests get lost".
- **W4:**
  - The geometry is static, so crests are equally spaced in t at both ends. Each clock converts at its own rate, (1+Φ)Δt, so the top clock counts a longer time between crests.
  - The shift is gh/c² = 2.47e-15 over 22.6 m. The stone argument gives the same fraction independently.
  - The surprise enters at "the ends disagree about what a second is", which is W1.
- **W5:** Passes. h × 10 gives 2.5e-14; h ÷ 10 gives 2.5e-16; the frequency is irrelevant.
- **W6:** Passes. Every element is used.
- **W7:** Signs are right. The step "less energy, so lower frequency" (lines 320–322) needs E = hf, which is unstated.
- **W8:** Partial fail.
  - Ch1 lines 45–47 already state that higher clocks run fast.
  - Ch1 Problem 1.1 is a clock on a 100 m tower gaining gh/c².
  - A Ch1 reader can therefore answer at once.
- **W9:** Passes.
- **W10:** Passes: 74 ft = 22.56 m; 3.6e-17 (the "four parts in 10¹⁷" is the measured 4.1 ± 1.6).
- **Also:** lines 441–442, "Energy conservation alone" overclaims. The argument also uses the weight of energy, E = hf and the static geometry.
- **Fix:** State "a photon's energy is h times its frequency". Then ask: "Ch1 says the top clock runs fast by gh/c². Is the detected frequency lower by gh/c², or by 2gh/c², the lost energy plus the fast clock?"
  - This targets a real double-counting error.
  - The answer is gh/c²: one effect seen two ways.
  - Pound–Rebka's ratio of 1.05 ± 0.10 excludes the factor 2 at 9.5σ.
  - Replace "alone" with "together with the weight of energy".

### 8. Check 2.4 (Everest): FAIL
- **W4:** 9.8 × 8850 / 9e16 = 9.64e-13; × 2.52e9 s = 2.43 ms. Correct. The rotation correction (0.27%) and the 1/r correction (0.14%) are negligible.
- **C1:** FAIL. It is substitution into ΔΦ = gh/c² from line 370, and the "tiny size" lesson is already in Ch1.
- **W9:** FAIL. It is the same computation as Ch1 Problem 1.1 ("Two clocks").
- **W7:** Line 430, "Neither travels. When they meet", contradicts itself.
- **Fix, a clock at the Earth's centre:** "It feels no pull, like a far-away clock. Same rate? Compare with the surface."
  - The rate follows Φ, not g. Φ keeps falling all the way down because g points inward everywhere inside.
  - For a uniform Earth, Φ_c = −1.5GM/(Rc²) = −1.04e-9. The centre clock is slowest: 3.5e-10 behind the surface (11 ms per year). A two-layer Earth gives 1.74 times the surface depth.
  - W3: "no pull, no slowing". C1 passes. W6: lines 358–360 support it.

### 9. "The fish and the waterfall" (thought experiment): FAIL
- **W3:** "Where the flow equals the fish's 1 m/s." This is correct.
- **W4:** r = rs follows by the substitution the setup itself dictates ("replace the fish by a flash of light"), so there is no surprise.
- **W5, W6, W7:** pass.
- **W8:** FAIL. Ch1 lines 615–622 say the signal "stalls" where the stream "reaches the speed of light", that "the same thing happens to light trying to leave a black hole", and that "this place is a horizon".
- **W9:** FAIL. It is the third telling of the same lesson, and the resolution points back to Ch1 without asking anything new.
- **Replacement, "Standing still in the river":** "A probe hangs at 2rs, and its clock runs at 71% of the far-away rate (√(1−½) = 0.707). A probe falling from far away passes it at 71% of c. Moving clocks run slow. Which probe is moving? Is the match of the two 71s a coincidence?"
  - W3: "gravity for one, motion for the other; coincidence".
  - W4: eq:river with dr = 0 gives dτ/dT = √(1−rs/r) = √(1−v²) with v = √(rs/r). T is kept both by falling clocks and by far-away clocks. The hanging probe moves upstream through the local space at v, and its gravitational slowing is that motion's time dilation.
  - The surprise enters at the river concept. It is a deliberate, new return to Check 2.3.
  - W5: at 20rs, 0.224 and 0.975; at 1.01rs, 0.995 and 0.0995. For the Earth, 11.2 km/s gives √(1−v²/c²) = √(1−2GM/Rc²) exactly, the 60 μs a day of Ch1.
  - W7: hanging at 2rs of a 10 M☉ hole needs 5.4e11 m/s². W10: verified.
  - Keep the fish as a sentence of intuition in the prose.

### 10. "The thrown ball" (thought experiment): PASS
- **W1:** Free fall is geodesic, with the greatest proper time.
- **W3:** Primed by the twins: "the ball travelled and came back, so it records less."
- **W4:**
  - The gain is ∫(gh − v²/2)dt/c² = v₀³/(3gc²) (sympy). The height term is 2v₀³/(3g) and the speed term v₀³/(3g), a 2:1 ratio for any throw.
  - For 2 s: v₀ = 9.8 m/s and the gain is 3.56e-16 s.
  - All 2000 random endpoint-fixed perturbations (up to 50 m) record less. In a uniform field the maximum is global.
  - The surprise enters at the geodesic principle, the twins' lesson with the roles reversed.
- **W5:** Passes. T = 20 s gives 3.56e-13; T = 0.2 s gives 3.6e-19; g × 10 gives 3.6e-14. The sign and the 2:1 ratio never change.
- **W9:** The framing recycles Ch1's "satellite's clock", but it asks something new.
- **W10:** Passes.

### 11. "The windowless capsule" (thought experiment): PASS, with two W7 wording fixes
- **W3:** "No, by the equivalence principle."
- **W4:** At 400 km, 2GM/r³ = 2.6e-6 s⁻². Balls 10 m apart drift 4.6 cm in 60 s, or 6.9 cm in a capsule that keeps one face to Earth. The surprise enters at geodesic deviation, which is W1.
- **W5:** Passes. At 1 m, 0.46 cm; with r × 10, 19 cm per hour.
- **W7:**
  - "Any experiment" (line 613) admits a magnetometer, since the Earth's field is about 30 μT at 400 km. Restrict to objects released inside.
  - "Side by side drift together" (line 706) fails for a pair along the track in an Earth-pointing capsule (Clohessy–Wiltshire); only a pair across the orbit plane converges.
- **W10:** Passes. The figure's arrows are correct.

### 12. Check 2.5 (tidal volume): PASS
- **W3:** "Grows, since the stretch of 2 beats a squeeze of 1."
- **W4:** V̈/V = ΣL̈ᵢ/Lᵢ = 2 − 1 − 1 = 0. That the rate is a sum is not stated in the topic, so C1 passes.
- **W7:** The sign of −∇²Φ matches R^i₀ⱼ₀ = ∂ᵢ∂ⱼΦ (checked symbolically).

### 13. Problem 2.11, "The orbit paradox" (problem): MARGINAL
- **Claims that hold:**
  - T = 5568 s (92.8 min); GM/(2rc²) = 3.27e-10; the difference over one orbit is 1.82 μs.
  - The third worldline is a straight up-and-down fall launched at 8.05 km/s (escape speed is 10.8 km/s). It reaches r = 15,140 km and returns after exactly T.
  - It records 1.18 μs more than hovering and 3.0 μs more than orbiting.
- **The problem:** "Why does this not contradict the key idea?" has no correct answer available from the chapter.
  - The key idea at lines 544–549 says a geodesic beats "any nearby worldline". That is false for a full orbit: tilted orbits re-cross it at T/2 = 2784 s, a conjugate point.
  - Bulging the orbit out of its plane by ε·sin(πt/T), with the same endpoints, gains 3π²ε²/(4Tc²). For ε = 10 km that is 1.48 ps more, verified numerically.
- **Also:** hovering for one orbit needs Δv of 48 km/s. A 420 km tower is the cleaner idealisation.
- **Fix:** Restate the key idea as "stationary; over any short enough stretch, greater than every nearby worldline". Add a step to the problem asking the reader to show that tilted orbits re-meet after half an orbit.

---

## Errors in the surrounding text
- **L279–282:** "where it varies from place to place the geometry is genuinely curved" is false. Sympy gives zero Riemann tensor for a rigidly rotating flow (shift ω×r) and for flow along x at speed √(2ax).
- **L544–549, L596–597, L724–725:** the maximum-proper-time claim is overstated.
  - The key idea is only true over short enough stretches.
  - Lines 596–597 and the summary (724–725) state a global version.
  - Problem 2.11 refutes both: a non-geodesic records more, and three free-fall worldlines join the same two events.
- **L187–189:** "seen" should be "measured". The "sense of now" resolution relies on simultaneity, which the chapter never develops.
- **L110–114:** the order claim is deferred to a problem and is already stated in Ch1 (lines 592–595).
- **L320–322:** E = hf is used but not stated.
- **L441–442:** "Energy conservation alone" overclaims.
- **L209–210:** the grid square size is unstated.
- **L312:** the river analogy suggests horizons are label effects.
- **L430:** "Neither travels" contradicts "when they meet".
- **L613 and L706:** capsule wording, as described in item 11.
- **L164–165:** e^−22.75 is 1.3e-10, one in 7.6 billion rather than "ten billion".
- **L748–750:** the zigzag answer needs the null infimum.
- **L814–817:** the rocket hover requires Δv of 48 km/s.
- **L506 (low confidence):** Michell's paper was a letter to Cavendish that was read at the Society, so "Michell read a paper" may be inaccurate.
- **L618–620 (minor):** the logic runs backwards. Local flatness is a theorem for any metric; the equivalence principle is why gravity is modelled as one.

## Most serious problems, ranked
1. **The core free-fall key idea is wrong as stated.** Its global restatements repeat the error, and the chapter's own orbit paradox is a verified counterexample, so that problem's conceptual question cannot be answered correctly from the chapter.
2. **"A sliding grid" fails** W3, W4, W5, W8 and W9. Its link to the river, combined with the false curvature claim at lines 279–282, sets up a misreading of horizons and of flow-based designs.
3. **"The fish and the waterfall" fails.** Ch1's "A message to the front" gives the answer word for word, including "horizon", and the fish offers no surprise.
4. **Checks 2.1 and 2.4 are substitution drills** that duplicate Problem 2.1 and Ch1 Problem 1.1. Check 2.4 also contradicts itself.
5. **Relativity of simultaneity is used but never taught** (Betelgeuse, twins). The tower puzzle is given away by Ch1 and overclaims "energy conservation alone".
