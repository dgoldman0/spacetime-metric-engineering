# Independent review of Chapter 1's teaching devices

Report of an independent reviewer agent, 26 September 2026. It is kept here
verbatim as provenance. The reviewer worked from
`reviews/puzzle-design-worksheet.md` and the chapter texts as they stood after
commit be00945 plus the uncommitted redesign of "How stiff is the sheet?"
(the stress-per-strain version comparing spacetime with steel and rubber). It
did not see the author's earlier verdicts. Its scratch scripts, logs and page
renders are in the session scratchpad under `review_ch1/`. Line numbers refer
to `chapters/ch01-what-is-spacetime-engineering.tex` at that time. The
author's reconciliation is recorded separately.

---

# Chapter 1 teaching devices: adversarial review

I reviewed the current working-tree `textbook/chapters/ch01-what-is-spacetime-engineering.tex` (16:10) and the rebuilt `main.pdf` (16:13), which matches it. I read no review notes. Nothing in the repository was edited. I used `git diff` read-only to see the redesign. I grepped `textbook/checks/*.py` only for the redesign's numbers, for W10.

Scratch files, all kept, are in the `review_ch1/` scratchpad folder:
- `check_ch1_numbers.py/.log` recomputes every number.
- `check_ch1_physics.py/.log` holds the sympy Einstein tensors (lapse bump; Alcubierre observers) and the numerical ring-lens integrals.
- `layout-09..17.png` and `main_p1-30.txt` are the page layout.
- `vandenbroeck1999.txt` and `olum1998.txt` are source checks.

## Verdicts

| Item | Verdict |
|---|---|
| Thought experiment: The satellite's clock | PASS |
| Thought experiment: How stiff is the sheet? | **FAIL** |
| Thought experiment: Can relativity say no? | PASS (only if Check 1.2 is replaced) |
| Thought experiment: The race with a light beam | PASS (wording notes) |
| Thought experiment: A concave lens made of gravity | MARGINAL |
| Thought experiment: A stack of Casimir plates | MARGINAL |
| Thought experiment: A message to the front | MARGINAL |
| Check 1.1 (Sun, neutron star) | PASS |
| Check 1.2 (which questions) | **FAIL** |
| Check 1.3 (warp aging) | MARGINAL |
| Check 1.4 (Casimir force) | MARGINAL |
| Check 1.5 (Krasnikov control) | MARGINAL |

---

## Thought experiments

### How stiff is the sheet? (redesigned): FAIL (W7 and W8 fail; W5 and W6 fail in part)

- **W1.** c⁴/G sets how hard spacetime is to bend. A bump of ε across L needs about ε·c⁴/(8πGL²), which is 4.8e42 Pa per unit strain at L = 1 m.
- **W2.** The rubber-sheet picture suggests spacetime is soft. This is weak for upper-level students, who already know gravity is weak.
- **W3.** "Stiffer than steel." The binary is announced three times before the box:
  - the chapter-opening bullet "why spacetime is so stiff" (l.13);
  - the section heading "Spacetime is stiff" (l.95);
  - the box title.

  The reader has no basis for guessing the number.
- **W4.** 1e-9 × 4.815e42 = 4.8e33 Pa (30 MeV/fm³). Divided by the 200 Pa steel needs, that is 2.4e31. The surprise enters at the value of c⁴/(8πG), which is W1, so W4 passes. The "worked answer", though, is a one-line substitution into eq. (1.3), printed two paragraphs earlier.
- **W5 (fails in part).**
  - Across L = 0.1, 1 and 10 m the stress is 4.8e35, 4.8e33 and 4.8e31 Pa, which is 2.4e33, 2.4e31 and 2.4e29 times steel. The qualitative lesson survives.
  - The neutron-star image does not survive at 0.1 m: about 3000 MeV/fm³ is beyond the centre of any neutron star.
  - More seriously, c⁴/(8πGL²) belongs to the scale, not to a medium. It equals steel's modulus at L ≈ 0.5 light-years and soft rubber's at ≈164 light-years.
  - The answer's "the comparison does not depend on the size of the strain" points at an invariance that does not matter and hides the 1/L² dependence that does.
- **W6 (fails in part).** The room and its clocks, the concrete element of the question, are never used in the Chapter 1 resolution; they are deferred to Chapter 3. Rubber appears only as "far stiffer than either".
- **W7 (fails).**
  - "Strain spacetime by one part in a billion across a metre", and "a rate … different from clocks at its walls", both admit a clock rate that changes steadily from wall to wall. That profile demands nothing: it is Chapter 3's own rocket (α = 1 + gx). Yet the answer states generally that "a strain of one part in a billion across a metre takes about 5e33 Pa".
  - Apply the rule (l.144–152) and the summary (l.673–676) as worded to any room on Earth. The floor-to-ceiling difference is 1.1e-16 per metre, and the rule puts about 2e27 Pa of stress in the air. The true curvature there is 1.7e-23 m⁻², seven orders of magnitude below the rule's ε/L² = 1.5e-16.
  - Only a bump (centre faster, or slower, than everywhere on the walls) must be paid for inside the room, because a potential with no matter inside has no maximum or minimum.
  - Even for a bump the rule runs low. A parabolic bump in a room 1 m wide needs 3.9e34 Pa (8×), and 9.6e33 Pa if the walls are 1 m from the centre (2×). A slow-centre uniform ball of radius 0.5 m needs ρc² = 2.3e35 J/m³ (48×).
- **W8 (fails).** The heading, the bullet and the title give the answer away. In the current build the answer box (top of p.5) faces the question (p.4).
- **W9 passes.** Chapter 3's "A room where time runs fast" is a deliberate return. But the promise "Chapter 3 works out exactly what the room would need, and finds a surprise … as well as in its size" does not hold. Chapter 3 (l.489–494) reuses α″ ~ ε/L², gets the same 5e33 Pa and calls it "exact".
- **W10 passes.**
  - 200 Pa = 1/507 atm.
  - "A hundred thousand times less" implies a rubber modulus of 2 MPa (soft latex; handbook rubbers at 1–100 MPa would give 2e3–2e5).
  - 4.815e42 Pa; 4.8e33 Pa (inside the GW170817 pressure range at twice nuclear density); 2.4e31.
  - `checks/rev3_redesigns.py` covers these numbers. It does not test the steady-strain or scale caveats.

**Replacement, worked through the worksheet ("How stiff is the sheet?", new):**

> *Popular pictures show gravity as a heavy ball denting a stretched rubber sheet. Try making a dent yourself. Fill a sphere one metre across with osmium, the densest metal known: twelve tonnes of it. Put one of today's best atomic clocks in a small hollow at its centre and another at its surface; such clocks tell apart rates that differ by one part in 10¹⁸. Will they see the dent the metal makes in time?*

- **W1.** c²/G = 1.35e27 kg/m fixes the dent, (M/r)/(c²/G). Nothing of human size dents time measurably.
- **W2.** Rubber sheet, plus the famous precision of clocks.
- **W3.** "Yes, just."
- **W4.**
  - M = 22,590 × (4/3)π(0.5)³ = 1.18e4 kg, so M/r = 2.4e4 kg/m.
  - Divided by c²/G, that gives 1.8e-23 at the surface relative to far away. The centre-to-surface difference is half of that, 8.8e-24, some 1e5 below what the clocks can see.
  - The surprise enters at the division by c²/G (eq. 1.4), which is W1.
  - Optional coda: a part-in-a-billion dent needs about 7e17 kg in the sphere, around 1e18 kg/m³, the density of a neutron star's core.
- **W5.**
  - Radius 0.05 m or 5 m gives 8.8e-26 or 8.8e-22, still 1e3 short at 5 m.
  - Water gives 3.9e-25.
  - Clocks at 1e-17 or 1e-19 still see nothing.
  - Detection needs a radius of about 170 m.
- **W6.** Every element is used, and eq. 1.4 is in the topic.
- **W7.** Dense matter slows the centre clock, as at the Earth's centre. The setup is real.
- **W8.** Not decidable from the word "stiff", because 1e-18 is extreme. Still retitle the heading and bullet, for example "How hard is it to bend spacetime?".
- **W9.** Distinct from Example 1.1, Check 1.1 and Chapter 3's water check. It is also distinct from the rejected first version: there is no distance fall-off, and it asks about detection, not about the mass needed at 1 m.
- **W10.** Section J of the log.

**Minimal repair, if the steel framing is kept:**
- Make the question a bump: "faster than clocks anywhere on its walls".
- Restate the rule and the summary as "a bump of height ε across a region of size L", paid for by matter inside the region.
- Drop "rubber or steel?", for example in favour of "Could any material hold it?".
- Replace "does not depend on the size of the strain" with the 1/L² dependence.
- Fix "as well as in its size".
- Retitle the heading and bullet, and keep the answer box off the question's spread.

### The satellite's clock: PASS

- **W1.** Motion slows a clock and height speeds it up. At navigation precision both matter, and which one wins depends on the orbit.
- **W2.** Special relativity's "moving clocks run slow" is the familiar effect.
- **W3.** "Behind", or GPS lore "ahead". For the station, "same as GPS".
- **W4.**
  - GPS: +45.72 − 7.21 = +38.50 µs/day. The surprise enters where the height term (5.29e-10) beats the speed term (8.35e-11), which is W1.
  - Station (420 km, 7.66 km/s): +3.72 − 28.21 = −24.49 µs/day. The flip comes from v² = GM/r; the net crosses zero at r = 1.5R (altitude 3,186 km).
- **W5.**
  - A factor of ten in either altitude flips its answer: 2,019 km gives −8.4 µs/day, and 4,200 km gives +5.8 µs/day.
  - This is acceptable because the two-orbit contrast is the lesson, and the lesson survives.
  - Speed ×10 on its own (not an orbit) gives −674 µs/day.
- **W6 passes.** "By radio" is incidental.
- **W7 passes.**
- **W8 passes.** The figure is on the next page, and the adjacent column is ordinary topic text.
- **W9 passes.** Chapter 2's "thrown ball" reuses the same height-versus-speed competition, but asks a new, geodesic question.
- **W10 passes.** 20,189 km; 3.87 km/s; 11.4 km in 38 µs; 4.457e-10 without rotation, versus the factory 4.465e-10; 7.66 km/s against "almost 8" (loose); −24.5 µs/day.

### Can relativity say no?: PASS

- **W1.** Read backwards, Einstein's equation gives every geometry a demand.
- **W2.** "Relativity forbids faster-than-light travel."
- **W3.** "Yes, it forbids this."
- **W4.** G_μν exists for every metric, and T = G/8π is automatically conserved (Bianchi). The surprise enters at "every geometry has a demand", which is W1.
- **W5 passes.** Afternoon, year or century; galaxy or room.
- **W6 passes.**
- **W7.** Last line: "allowed exactly if nature can supply its demand" drops the "put in place" and causality conditions; "only if" would be accurate.
- **W8.** Mild cue in "on its own".
- **W9 fails, but only through Check 1.2(b).**
- **W10.** No numbers.

### The race with a light beam: PASS

- **W1.** The ship always stays inside its local light cone. The designs shorten the route or tilt the cones.
- **W2.** "Nothing can overtake light" against science-fiction shortcuts.
- **W3.** "A wormhole", or "impossible".
- **W4.** The figure's numbers check out:
  - Wormhole: home at 0.60 of the light time.
  - Warp at 3c: home at 2/3; the cone slopes are 14.0° and 26.6°, and the ship's path is 18.4°.
  - Krasnikov: the ship reaches the star at 1.25, after the pulse at 1.00. The return is timelike (ds² = −0.01) and arrives home at 0.45.
  - The surprise enters at "stays inside the local cone", which is W1.
- **W5 passes.**
- **W6 passes.**
- **W7 (minor wording).**
  - "What the designs change is the course" (l.415) is true of the wormhole only.
  - "Tilted toward the star" holds for the outbound leg only.
  - In design (c) the ship reaches the star after the pulse, yet is home, in Earth's frame, before it even reached the star. That striking fact is unmentioned, and the setup's "reaches the star, turns round, and is home…" reads as if the star comes first.
- **W8 passes.**
- **W9 passes.**
- **W10 passes.**

### A concave lens made of gravity: MARGINAL (W7 details and W8 fail)

- **W1.** Matter that satisfies the null energy condition always focuses light; a throat must defocus it.
- **W2.** Glass diverges light by its shape, and a ring pulls light toward its rim.
- **W3.** "Yes, use a dense ring."
- **W4.**
  - For a ring I integrated the transverse kick along each ray. Inside the ring, face-on and at a 40° tilt, it is below 1e-5. Outside it is −2/b, as for a point mass.
  - A shell's walls focus the light that crosses them.
  - Tides alone change a bundle's area by the factor 1 − (4GMD/c²b²)², always less than 1.
  - The surprise enters at "focusing is set by ρ + p where the light passes", which is W1.
- **W5 passes.**
- **W6 passes.**
- **W7 fails in two details.**
  - (i) Lines 515–517 give the reason "just as there is no gravitational pull inside a hollow shell". The conclusion is right but the reason is wrong: inside a ring, in its plane, the pull is 0.17, 0.49 and 2.7 GM/a² at 0.3, 0.6 and 0.9a, pointing toward the ring. The pulls cancel only when integrated along the ray: the flat shell theorem applied to projected mass.
  - (ii) Line 520–521 says "Spreading a bundle that has been shrinking takes matter that violates the NEC". Line 488–490 says "once it has started to shrink it keeps shrinking", and line 456–458 says "never spreads it". All three are false beyond a focus: the Sun's own rays cross at about 550 AU and then spread. Add "before its rays cross at a focus".
- **W8 fails.** Lines 334–343 already state the answer ("Ordinary matter always makes a bundle of light converge… A throat has to act as a diverging lens… exotic"). The answer box also faces the question (p.8/9).
- **W9 passes.**
- **W10 passes.** 8.51e-6 rad; 1.754″; 8.18e13 m = 547 AU; 13.8 × Pluto.

**Fix:**
- Move the diverging-lens and exotic-matter sentences out of l.334–343 to after the puzzle.
- Rewrite the ring's reason.
- Add the focus qualifier in all three places.

### A stack of Casimir plates: MARGINAL (W4 and W6 fail as written)

- **W1.** Negative energy is real, but the quantum inequalities (QIs) limit it: the more negative, the smaller or briefer.
- **W2.** More plates should mean more negative energy.
- **W3.** "It works with enough plates."
- **W4.**
  - The numbers: u(1 µm) = −4.33e-4 J/m³; aluminium's ρc² = 2.43e20 J/m³ (5.6e23 times larger, and at least 5.6e21 even for 10 nm plates); the throat needs τ − ρ = 4.8e42–9.6e42 J/m³ at b₀ = 1 m.
  - As written, the surprise enters at the plates' rest energy. That is apparatus bookkeeping, not the topic's concept; the QIs get one closing sentence.
- **W5.** At a 0.1 µm gap, "more than twenty orders" becomes 19.7 orders, but the lesson survives.
- **W6 fails in part.** The resolution rests on facts the topic never gives: the plates' rest energy and the stack's net positivity.
- **W7 (minor).** "The stack as a whole has plenty of positive energy" uses net energy as the test. What counts is ρ + p along the rays:
  - Between the plates T = |u| diag(−1, 1, 1, −3).
  - Rays crossing the stack see the plates dominate by about 23 orders.
  - Rays running along a gap see ρ + p = 0.
- **W8.** The answer box is on the same page as the question (p.10).
- **W9 passes.**
- **W10 passes.**

**Fix: rewrite the answer around the quantum inequalities.**

> *Stacking adds gaps, never deeper ones. Each 1 µm gap holds −4e-4 J/m³, and a 1 m throat needs 5e42 J/m³, 46 orders more. Because u ∝ 1/d⁴, that would take plates 3.1e-18 m apart, 270 times smaller than a proton. That is the quantum-inequality pattern. The plates' own 2e20 J/m³ also outweighs each gap by about 23 orders.*

This passes the worksheet:
- **W4.** The surprise now enters at the 1/d⁴ law, which is the quantum-inequality concept.
- **W5.** A throat ten times larger gives d ≈ 1e-17 m, still below a proton.
- **W6.** Uses eq. 1.5, the QIs and eq. 1.3.
- **W10.** Section F of the log.

### A message to the front: MARGINAL (W8 fails, W6 is minor)

- **W1.** Control: a horizon in the front wall cuts the crew off.
- **W2.** The wall is at rest relative to you and 100 m away.
- **W3.** "Yes, in 0.33 µs."
- **W4.** In the bubble's frame, space in the wall flows backward at v(1 − f). Forward light stalls where f = 1 − 1/v, which is 0.5 at v = 2, mid-wall (r ≈ R). The surprise enters at "light moves at c relative to local space", which is W1.
- **W5 passes.** v = 1.2 gives f = 0.17 (r ≈ 1.2R); v = 20 gives f = 0.95 (r ≈ 0.63R); the distance to the wall does not matter.
- **W6 (minor).** The 100 m is never addressed; the answer lacks "however close the wall".
- **W7 passes.**
- **W8 fails.** Lines 386–389 give the answer and promise the reason. The answer box also faces the question (p.10/11).
- **W9 passes.** Chapter 2's fish-and-waterfall puzzle is a deliberate return.
- **W10 passes.**

**Fix:** reword l.386–389 as "Krasnikov pointed out a problem with building and steering warp drives, taken up at the end of this chapter", and add "however close the wall is".

---

## Checks

### Check 1.1 (Sun, neutron star): PASS

- **W1.** Apply (M/r)/(c²/G) and judge whether the weak-field approximation holds.
- **W3.** Likely error: treating 0.17 as small.
- **W4.** Sun: 2.1e-6. Neutron star: 0.172. The linear estimate gives a rate of 0.828; the exact rate is 0.81 (a slowing of 0.19). The step that tests understanding is judging 0.17 against "where the effect is small".
- **W6 passes.** **W7 passes.** **W9 passes.**
- **C1.** It is substitution, but the size of the result is the lesson, so the exception applies.
- **W10 passes.**
- Suggestion: replace the Sun, which repeats Example 1.1, with a white dwarf (1.3e-4), so the progression of sizes carries the lesson.

### Check 1.2 (which questions): FAIL (C1, W9, W7)

- **C1 fails.** Every answer can be copied from l.220–235 and 245–248. The key even reuses their phrasing.
- **W9 fails.** Part (b) is "Can relativity say no?" again, in the same topic and in the same way.
- **W7.** The key hands (c) to Einstein's equation alone. Finding the geometry of given matter also needs boundary conditions ("what arrives from far away", Chapter 3 l.322–323) and the matter's own equations.

**Replacement check:**

> *Team A writes a geometry that carries a ship to a star in a week and computes its demand. Team B takes a moving shell of ordinary steel and solves Einstein's equation for its geometry. What is each team sure of, and what must each still find out?*

- **Answer.** Team A is sure the geometry does the job, and gets the demand by differentiation; it must find out whether the matter exists. Team B is sure the matter exists; it faces nonlinear PDEs (solvable by hand only with symmetry, and needing boundary conditions), and its geometry may do nothing useful.
- **W3.** "Team A's design is allowed, so it is buildable."
- **W4.** The understanding step is pairing each direction's guarantee with its open question; no sentence in the text states that pairing.
- **W6.** Answerable from l.220–251 and 263–267.
- **W9.** Distinct from the thought experiment.
- **C1 passes.**

### Check 1.3 (warp aging): MARGINAL (C1 fails)

- γ(0.99) = 7.09.
- The answer is l.44–45 plus l.351–352 and 368–370, juxtaposed.

**Replacement check:**

> *A round trip to a star 10 light-years away, once in a bubble at 5c and once coasting at 0.99c. How much does each crew age, and how long does each wait at home?*

- **Answer.** Warp: 4.0 years for both crew and home. Coasting: home waits 20.2 years, the crew ages 2.85 years.
- **W3.** Applying time dilation to the bubble's speed.
- **W4.** The understanding step is deciding which motion counts.
- **C1 passes.**
- **W10.** Section I of the log.

### Check 1.4 (Casimir force): MARGINAL (C1)

- The direction of the force is already stated at l.534–535 ("attract each other"). The rest is one differentiation.
- The key is correct: 1.300 mPa at 1 µm.
- **Fix:** change "attract each other" to "exert a force on each other", and add the misconception prompt: "The energy between the plates is negative. Does that make them repel?" Optional: the pressure equals 1 atm at 10.6 nm.

### Check 1.5 (Krasnikov control): MARGINAL (C1)

- The question supplies the answer ("less than the speed of light, modifying spacetime along the way"), and l.606 supplies "laid out in advance".

**Replacement check:**

> *Robot ships leave at 0.9c for a star 10 light-years away, programmed to shape a bubble's wall as it passes. Can the crew now steer? How soon can the first bubble reach the star?*

- **Answer.** No, the robots follow a fixed schedule. The bubble cannot outrun its preparers, so the first trip arrives no earlier than 11.1 years, later than light. Only later trips gain.
- **C1 passes.** **W7 passes.** **W9.** Distinct from "A message to the front".

---

## Physics and wording errors in the surrounding text

1. **l.138–140.** "Its inverse is c⁴/G". The displayed constant is 8πG/c⁴, whose inverse is c⁴/(8πG) = 4.8e42 N, off by a factor of 8π.
2. **l.144–152 and summary l.673–676.** As worded, the rule is false for a strain that changes steadily (seven orders of magnitude out in any room on Earth). It contradicts Chapter 3's rocket and its "Between the Earth and the Moon". Restrict the rule to bumps.
3. **l.47–48.** "At everyday speeds and heights … a few parts in 10¹⁰". Everyday values are at most about 1e-12 (airliner speed 3.5e-13; 11 km altitude 1.2e-12). A few parts in 10¹⁰ is the satellites' size.
4. **l.360–362 (warp caption b).** The plotted density is the one measured by observers carried with the flow of space. Observers at rest relative to the stars measure something else, positive in parts of the wall. At v = 1 they measure +0.24 in the inner wall against −0.029 for the flow-carried observers, and +0.11 at the front and back where the flow-carried value is 0. So "negative everywhere it is not zero" is false as captioned. It should read "observers carried along by the flow of space".
5. **l.334–343 and l.386–389.** These pre-answer the concave-lens and message puzzles.
6. **l.456–458, 488–490, 520–521.** The focal-point qualifier is missing. **l.515–517:** the ring's reason implies there is no pull inside a ring.
7. **l.198–207.** "Finds a surprise … as well as in its size": Chapter 3 finds the same size, and calls an order-of-magnitude α″ "exact" (Chapter 3 l.489–494). The exact value for a 1 m room is 3.9e34 Pa.
8. **l.368–370.** "Age no more … than": they age exactly as much. **l.373–375:** a throat needs negative energy density only for some observers, as l.339–341 says. **l.89:** "almost 8 km/s" is 7.66 km/s.
9. **l.411–415.** "Change the course" applies to the wormhole only; see also the Krasnikov ordering noted under the race.
10. **Layout.** In the current build, four answer boxes are in view of their questions:
    - How stiff: p.4/5, facing pages.
    - Concave lens: p.8/9, facing pages.
    - Casimir: same page, p.10.
    - Message to the front: p.10/11, facing pages.

Checked and correct: Van Den Broeck's "a few solar masses" and "about ten Planck lengths" (1.4e-34 m); Pfenning–Ford's 6.2e62 v kg (about 1e10 times the visible universe); the chapter's NEC wording for Olum's result (his proof uses the null condition R_ab K^a K^b ≥ 0).

## Most serious problems, ranked

1. **"How stiff is the sheet?" fails.**
   - Its rule and answer, as worded, charge 5e33 Pa for any strain across a metre, including the free steady case. That contradicts Chapter 3.
   - The rubber-or-steel binary is given away by the heading, the chapter bullet and the box title.
   - The steel comparison is tied to the metre scale as 1/L², but is presented as a material property.
2. **Answers given away before three puzzles** (concave lens, message to the front, stiffness), plus four answer boxes in view of their questions in print.
3. **Recall checks.** Check 1.2 fails outright and duplicates "Can relativity say no?". Checks 1.3 and 1.5 can be answered by copying sentences, and 1.4's direction is stated in the text.
4. **Factual slips.** c⁴/G called the inverse of 8πG/c⁴ (off by 8π); the warp caption's observers, which make its sign claim false; the "everyday … 10⁻¹⁰" magnitude.
5. **Imprecise resolutions.** The focusing statements lack the focal-point qualifier (the Sun's own 550 AU focus is a counterexample), the ring argument rests on a false analogy, and the Casimir answer's engine lies outside the topic's concept.
