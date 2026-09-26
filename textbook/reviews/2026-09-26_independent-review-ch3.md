# Independent review of Chapter 3's teaching devices

Report of an independent reviewer agent, 26 September 2026. It is kept here
verbatim as provenance. The reviewer worked from
`reviews/puzzle-design-worksheet.md` and the chapter texts as they stood after
commit be00945 plus the uncommitted edits of the stiffness redesign. It did
not see the author's earlier verdicts. Its scratch scripts and logs are in the
session scratchpad under `review_ch3/`. Line numbers refer to
`chapters/ch03-matter-and-geometry.tex` at that time unless marked as
Chapter 1. The author's reconciliation is recorded separately.

---

# Chapter 3 teaching-device review

**Method.** I read the worksheet, all of Chapters 1–3 and the Chapter 3 figure sources. I did not read the review notes or the author's check script (`checks/rev2_teaching_devices.py`). I used read-only `git diff` and `git show` to see what changed today.
- Every curvature and stress-energy claim was checked in sympy: 45 checks, all passing, plus extra cases.
- Every number was recomputed.
- Scratch files are kept in the `review_ch3/` scratchpad folder: `gr_tools.py`, `verify_curvature.py`, `verify_numbers.py`, `verify_extra.py` and `verify_replacement.py`, each with a `*_run1.log`. I ran `verify_numbers.py` twice, so its log was rewritten once with identical, deterministic output.
- Nothing in the repository was touched.

**Verdicts at a glance**

| Item | Verdict |
|---|---|
| Brick in passing | PASS |
| Flying through empty space | PASS |
| Between the Earth and the Moon | **FAIL** |
| Box of hot gas | MARGINAL |
| Room where time runs fast | MARGINAL |
| River with a fast lane | MARGINAL |
| Check 3.1 | PASS |
| Check 3.2 | FAIL |
| Check 3.3 | MARGINAL |
| Check 3.4 | FAIL |
| Check 3.5 | FAIL |
| Check 3.6 | PASS |

---

## Thought experiments

### 1. "A brick in passing" (thought experiment) — PASS
- **W1:** Energy density is the tt component of a two-index tensor. A boost therefore multiplies it by γ twice: once for the energy of each atom, once for the atoms per unit volume. ρ_w = T_μν w^μ w^ν.
- **W2/W3:** Energy carries one factor of γ, and so does charge density. Readers answer "the same factor, 5/3".
- **W4:** ρ_w = ρ0(u·w)² = γ²ρ0 = 25/9 ρ0 ≈ 2.78 ρ0. The surprise enters at the second γ, the "per unit volume" index (contraction packs the atoms). That is W1.
- **W5:** At v = 0.08, γ = 1.0032 and γ² = 1.0064. At v = 0.99, γ = 7.09 and γ² = 50.3. Any material behaves the same. The lesson survives.
- **W6:** Every element is used (the table is only scenery).
- **W7:** Correct.
- **W8:** Nothing earlier gives γ².
- **W9:** Distinct: the rod example adds stress and the laser check adds flux.
- **W10:** γ = 5/3 and γ² = 25/9 confirmed in sympy.
- **Note:** "the same factor, or a different one?" signals the intended answer. Asking "By what factor?" removes that hint.

### 2. "Flying through empty space" (thought experiment) — PASS
- **W1:** Vacuum energy has T_μν = −ρ_vac g_μν, a tension equal to its energy density, so every observer measures the same ρ_vac.
- **W2/W3:** The setup primes the brick's rule, so the first answer is "yes, 25/9 times more".
- **W4:** ρ_w = −ρ_vac g_μν w^μ w^ν = ρ_vac. Equivalently, γ²(ρ − v²τ) with τ = ρ gives ρ. The surprise enters at "tension equals energy density", which is W1.
- **W5:** Holds at any speed (sympy: γ²(1 − v²) = 1).
- **W6:** The dark-energy clause is scene-setting; it is used in the next topic.
- **W7 and W8:** Correct.
- **W9:** Minor overlap: Problem "Vacuum energy" (L678–680) repeats the first half of the revisited box.
- **W10:** Verified.
- **Suggestion:** A reader who answers "no" because relativity has no preferred frame never meets the mechanism. Ask instead what the vacuum's stress must be for every observer to agree.

### 3. "Between the Earth and the Moon" (thought experiment, written today) — FAIL
- **W1:** Einstein's equation fixes only the Ricci part of the curvature. In vacuum R_μν = 0, while tides that change only shape survive.
- **W2/W3 fail:** The question's own second sentence ("If it does, what steers the Moon… raises the tides?") hands the reader the answer. So does Laplace's equation, which every physics student knows: zero source does not mean zero field. The first answer is already the correct one, "No".
- **W4 fails:** No surprise enters anywhere. The new content (Ricci fixed, the rest free) answers a "how" question that the box never asks.
- **W5:** Passes trivially.
- **W6 fails:** The Moon clause is resolved by "its slope steers the Moon" (L337).
  - The slope is the part of gravity that is *not* curvature. The equivalence principle removes it, and α = 1 + gx has zero Riemann tensor (sympy). The chapter teaches exactly this two topics later with the rocket.
  - One of the two pieces of evidence the setup offers against flatness is therefore not curvature. A version consistent with general relativity would say that the Earth and Moon both fall freely yet circle each other, which is curvature again.
- **W8 fails:** The answer is given away by the setup, by Chapter 2's windowless capsule ("The relative acceleration is curvature", in orbit), and by Chapter 2's `chk:tidal-volume` answer ("In empty space, tides change the shape… not its volume… vanishes wherever there is no matter"). The topic body even cites that check (L316).
- **W9 fails:** It is a near-duplicate of `chk:tidal-volume` and the capsule.
- **W10:** It contains no numbers.

**Replacement: "A drop and a lake."**
- **Thought box:** A grape-sized water drop floats in a space station. A tiny ball of test particles, able to pass through water unhindered, is released at rest at the drop's centre. A second ball is released a few metres deep in a lake on Earth, where gravity pulls about 3.5×10⁹ times harder than at the drop's surface. Which ball begins to shrink faster?
- **Revisited box:** Neither. eq:ball depends only on ρ and the pressures where the ball is, so both balls have V̈/V = −4πGρ = −8.39×10⁻⁷ s⁻². Free fall removes the Earth's pull. The Earth's tides remain, and they only reshape the balls.

Worksheet for the replacement:
- **W1:** Einstein's equation fixes, at each place, only how a falling ball begins to change volume, and fixes it through the local energy density and stresses. Curvature from matter elsewhere changes only shape.
- **W2:** Readers equate strength of gravity with the pull.
- **W3:** "The lake's ball shrinks enormously faster", or "the drop's ball does not shrink at all".
- **W4:** The rates are equal. The step is evaluating eq:ball at each ball (the same ρ; pressure correction about 10⁻¹⁵), which is W1. Newtonian tidal components per unit length:
  - drop: +2.28, −1.56, −1.56 (×10⁻⁶ s⁻²), summing to −8.39×10⁻⁷;
  - lake: +2.24, −1.54, −1.54 (×10⁻⁶ s⁻²), summing to −8.39×10⁻⁷.
- **W5:** Drop radius ×10, lake depth ×10 and station 10× farther from Earth all leave the rates unchanged. Water replaced by rock (×3 density) multiplies both by 3, so they stay equal.
- **W6:** Every element is used: drop and lake give the local ρ, the station gives Earth's tides, the Earth's pull is removed by free fall, and passing through water lets the ball sit inside matter.
- **W7:** Signs and trace-free vacuum tides check out. The test particles are an idealization.
- **W8:** Chapter 2 treats only vacuum and defers matter to Chapter 3.
- **W9:** New. Retarget `chk:water` (see Check 3.3).
- **W10:** Verified in `verify_replacement.py`.

### 4. "A box of hot gas" (thought experiment) — MARGINAL
- **W1:** Pressure and tension both source gravity (ρ + 3p). In a body held by its own material stresses, they cancel in total.
- **W2/W3:** Given the premise, the first answer is "yes, heavier by 3pV/c²".
- **W4:** The answer is no. The engine is the walls' tension, which counts negatively (W1), and equilibrium makes the cancellation exact: ∫T^xx dV = ∫dx (net force across the plane x = const) = 0. This is sound.
- **W5:** Pressure, size or material ×10 still cancels.
- **W6 fails partly:** The opening star (L347) is never resolved.
- **W7 fails partly:** "For any object that holds itself together in equilibrium, the two cancel exactly" (L394–395) is false for bodies held together by gravity.
  - Hydrostatic equilibrium gives ∫3p dV = −W. Sympy confirms this for a uniform star: both sides equal 16π²Gρ²R⁵/15.
  - That is about 3×10⁻⁶ Mc² for the Sun and about 0.1 Mc² for a neutron star, with no tension anywhere to cancel it.
  - von Laue needs negligible self-gravity (`prob:von-laue` says "in flat spacetime"; the revisited box drops that condition). The summary repeats the error (L629–630).
- **W8:** Correct. However, fig:gas-box's caption states the answer and floats `[tb]`; check it cannot land beside the thought box.
- **W9 and W10:** Correct.

**Fixes:**
1. Replace the first sentence with "Einstein's equation counts pressure as a source of gravity alongside energy."
2. Revisited box: "For any object held together by the strength of its materials, with its own gravity negligible…"
3. Summary: "in a body held together by material stresses rather than its own gravity…"
4. Optionally add a problem on the star virial.

### 5. "A room where time runs fast" (thought experiment, rewritten today) — MARGINAL
- **W1:** The demand depends on α'', the curvature of the clock-rate profile, not its slope. A straight-line α is flat spacetime. With space held flat, a bump demands zero energy density and stress across the gradient, with tension at the peak.
- **W2:** Chapter 1 equated a clock-rate difference with a strain costing neutron-star stresses, yet the rocket gets its difference for free.
- **W3:** For the first question, "the engine pays for it". For the second, "negative energy at the centre", by Newtonian intuition.
- **W4:** α = 1 + gx has zero Riemann tensor. For any α(x,y,z) with flat space, G_tt = 0 (sympy). G_yy = G_zz = α''/α, and ρ + p_y = α''/(8πα) < 0 at the peak. The surprise enters at G_tt = 0 and at the dependence on α'', both W1.
- **W5:** At L = 10 m the stress is 4.8×10³¹ Pa, same lesson. ε ×10 scales the stress ×10. Turning the bump into a dip moves the tension to the flanks, and the null-energy (NEC) violation persists.
- **W6 fails partly:** "Stress along the two directions parallel to the walls" (L517–519) is the result for a slab, where α varies along one axis only.
  - A room whose centre is fastest relative to all its walls has G_ij = (δ_ij∇²α − ∂_i∂_jα)/α.
  - For a cosine box, this gives equal tension in all three directions at the centre: G_ii = −2π²ε/(L²(1+ε)), twice the slab's −π²ε/(L²(1+ε)). Sympy confirms both.
- **W7 fails partly:** The first question's premise ("the room does not [get it for free]") is false for a spinning room.
  - Wall clocks move, so the centre ticks fastest in flat spacetime (the rotating metric has zero Riemann tensor).
  - For 10⁻⁹ at r = 0.5 m, v = 13.4 km/s and the steel hoop stress is about 1.4×10¹² Pa. That is a materials problem roughly 21 orders of magnitude below 5×10³³ Pa, with no exotic matter involved. This is Einstein's rotating disk, which sharp readers know.
  - The last sentence (L525–526) drops "with space held flat". With curved space allowed, vacuum energy that respects the NEC gives a lapse peak (static de Sitter, G = −3H²g, sympy). A static lapse maximum still requires ρ + Σp < 0 there (D²α = 4πα(ρ + Σp), sympy), but that violates the strong energy condition, not the null one given as the reason.
- **W8:** Mostly correct. Chapter 1 (L205–206) announces "a surprise in the kind of stress", a partial hint.
- **W9:** A deliberate return to "How stiff is the sheet?" that asks something new.
- **W10:** 10⁻⁹·c⁴/(8πG) = 4.8×10³³ Pa checks out. However, L494 calls this "the exact demand". A 10⁻⁹ bump confined within a 1 m room has |α''| = 8×10⁻⁹ to 3.2×10⁻⁸ m⁻² (parabola to Gaussian with σ = L/4), so the peak tension is 3.9×10³⁴ to 1.5×10³⁵ Pa.

**Fixes:**
1. Thought box: "…while a room that holds still, neither accelerating nor spinning, does not?" and "…fill the space between two facing walls for clocks midway between them to tick fastest…". Alternatively keep "room" and state the 3D result in the revisited box.
2. Revisited box: "With space held flat, a simple bump…"
3. L494: "matches in order of magnitude; a bump confined within a 1-m room needs ~4×10³⁴ Pa at its peak."
4. Add "clocks at rest in a region that holds still" to Chapter 1's stiffness rule (L144–147).

### 6. "A river with a fast lane" (thought experiment) — MARGINAL
- **W1:** A shearing flow of space demands a negative energy density from the observers riding it, ρ = −(β')²/32π, in either direction.
- **W2/W3 fail:** The positive-or-negative guess is telegraphed. Chapter 1 (L373–375 and fig:warp b) says warp walls need negative energy, and Chapter 2 (L273–276, L280–282) says warp drives are exactly this metric with a varying speed. Primed readers answer "negative".
- **W4 is weak:** The engine is the square in eq:shear-density, but the text only asserts it ("a good exercise for computer algebra", L553–554). The reader never sees why the sign is negative. The formula itself is verified: riding observers see −(β')²/32π, and they are geodesic. For a general β(x,y,z), ρ = −[(∂_yβ)² + (∂_zβ)²]/32π and ∂_xβ drops out, which also confirms the Alcubierre link.
- **W5:** Width ×10 or speed ×10 changes the magnitude only; the sign never changes.
- **W6 and W7:** Correct.
- **W8 fails partly**, for the reasons under W2/W3.
- **W9:** Distinct.
- **W10:** 1.20×10⁴² J/m³ checks out. The mass density is 1.34×10²⁵ kg/m³ (the text says about 1×10²⁵).

**Fixes:**
1. Ask instead: "if the fast lane costs something, does reversing it (slowest in the middle) reverse the sign, the way a clock-rate bump's tensions and pressures balance?" Answer: no. ∫ρ dy = −(1/32π)∫(β')² dy < 0 for every channel, whereas ∫α'' dx = 0 for a clock-rate profile.
2. Show the engine: with flat slices and unit lapse, 16πρ = K² − K_ijK^ij, where K_xy = β'/2 and K = 0. Or say plainly that Chapter 4 derives it.
3. Fix Chapter 1's fig:warp (b) caption (see errors below).

---

## Checks of understanding

### Check 3.1 (laser) — PASS
- **W1:** ρ_w for a tensor with flux components, and the sign of lowered indices.
- **W3:** Keeping T_tx = +u gives 9u when chasing, which is backwards; reusing γ² gives 25u/9 both ways.
- **W4:** ρ_w = γ²u(1−v)² = u(1−v)/(1+v), so u/9 when chasing and 9u head-on. The step that tests understanding is the sign of the cross term, which the Doppler picture confirms.
- **W6, W7, W9:** Correct.
- **W10:** Confirmed in sympy.
- **C1:** Passes: the asymmetric result is the lesson.

### Check 3.2 (ρ + p) — FAIL
- **W1:** Reading p from each catalogue entry.
- **W3:** Getting the sign of the vacuum pressure wrong.
- **W4:** Dust ρ, radiation 4ρ/3, fluid above ρ, vacuum 0. There is no understanding step; L184–185 literally states that the vacuum's tension equals its energy density.
- **W6, W7, W10:** Correct.
- **W9 fails:** The vacuum puzzle and the magnetic box both make the same point.
- **C1 fails:** It is recall plus addition.
- **Fix:** "Show that an observer moving at v through a perfect fluid measures ρ_w = ρ + γ²v²(ρ+p) (sympy-verified). At 0.8, compare dust, radiation and vacuum. What does a fast observer see if ρ + p < 0?"
  - Answers: dust 25/9 ρ ≈ 2.78ρ, radiation 91/27 ρ ≈ 3.37ρ, vacuum ρ at every speed, and ρ_w → −∞ as v → 1 when ρ + p < 0.
  - This tests the algebra and the meaning of ρ + p (the quantity the NEC constrains). C1 passes.

### Check 3.3 (water) — MARGINAL
- **W1:** Converting to geometric units and relating curvature to a length.
- **W3:** Dropping the factor c².
- **W4:** 7.43×10⁻²⁵ m⁻², and 1/√(8πρ) = 2.3×10¹¹ m ≈ 1.5 AU.
- **W6, W7, W10:** Correct.
- **W9 fails partly:** "Spacetime is stiff" re-teaches Chapter 1: its thought experiment, the stiffness rule, Problem 2 and the Earth example.
- **C1:** Passes only because the size is the lesson, and that lesson is Chapter 1's.
- **Fix:** Also ask how large a water ball must be to trap its own light: √(3/(8πρ)) = 4.0×10¹¹ m ≈ 2.7 AU. Alternatively change the material if the drop-and-lake puzzle is adopted.

### Check 3.4 (tension that stops shrinking) — FAIL
- **W4:** ρ + 3p = 0 gives p = −ρ/3. That is one step from eq:active-mass; L364–366 already says "enough [tension] reverses its sign" and gives the vacuum value −2ρ.
- **W9:** Overlaps that text.
- **C1 fails:** The w = −1/3 threshold could make the size a lesson, but the answer never draws it out.
- **Fix:** "A rod has energy density ρ and tension τ along its length only. What τ keeps a ball inside it from shrinking? How close does steel come?"
  - The answer requires eq:ball with anisotropic stress: ρ − τ = 0, so τ = ρ. The trap answer is τ = ρ/3.
  - Steel reaches τ/ρ ≈ 1.4×10⁻¹².
  - A magnetic flux tube has τ = ρ but adds sideways pressure (ρ + Σp = B²), so it still attracts; a straight cosmic string does not.

### Check 3.5 (lapse dip) — FAIL
- **W4:** α'' = (1 − 2x²)e^(−x²), so there is pressure for |x| < 1/√2 and tension beyond. That is the caption's pattern (L501–503) with its sign flipped.
- **W9 fails:** It duplicates the caption, the revisited box (L519–521) and Problem "A rippled clock rate" (L700–702).
- **C1 fails.**
- **Fix:** "Can any α(x), flat space, constant far away on both sides, avoid tension altogether?"
  - Answer: no. ∫α'' dx = α'(∞) − α'(−∞) = 0, so α'' < 0 somewhere, and there ρ + p_y < 0.
  - Also ∫α p_y dx = 0: tension and pressure balance in total, echoing the gas box.
  - Both integrals are verified for the bump. C1 passes.

### Check 3.6 (shear width) — PASS
- **W4:** ρ = −β0²/(32πw²). Doubling w divides ρ by 4 and halves the total per unit area, −β0²/(32πw).
- **W3:** "A thinner layer has less volume, so the total stays the same."
- **W7:** Correct. The corners of the profile put β'' surface layers into G_tt and G_tx, but the riding observers' ρ contains no β'' (sympy), so the question is well posed.
- **C1:** Passes; the scaling is the lesson.

---

## Physics and wording errors in the surrounding text

**Chapter 3**
- **L394–395 and L629–630:** Stresses said to cancel for "any object that holds itself together". This is false for self-gravitating bodies (see the gas box above).
- **L347:** The star premise is never resolved.
- **L337:** "its slope steers the Moon" uses the part of gravity that is not curvature, and conflicts with L474–477 and `prob:rindler`.
- **L517–519:** A result that holds for a slab is stated for a room.
- **L409–419:** The spinning-room loophole.
- **L525–526:** "A simple bump… demands matter that no ordinary material can provide" needs "with space held flat".
- **L602–604 and summary L632–633:**
  - "Shaping the rate of clocks demands stress without energy" needs "with space held flat". The Earth shapes clock rates using positive energy, per L480–487.
  - "Shearing… demands negative energy density" needs "for the observers riding it". The observer-independent fact is ρ + p_z = −(β')²/16π < 0 (sympy).
- **L489–494:** "now from the exact demand" overstates an order-of-magnitude estimate; a confined bump needs 4×10³⁴ to 1.5×10³⁵ Pa at its peak.
- **L522:** "The tension at the peak is worse than it looks" tells the reader how to react.
- **L308–310:** Clock rates are listed as predictions beyond Newton. At first order they follow from the equivalence principle and the Newtonian g_tt, not from the constant 8π. The bending of light does test the field equation.
- **L280:** "begins to change at the rate V̈/V": V̈/V is the initial volume acceleration (V̇ = 0 at the start).
- **L45–47:** "a number every observer agrees on", placed right after saying that energy depends on the observer, invites confusion.
- **L432–433 vs L553–554:** "simple enough to follow by hand" conflicts with the shear example's reliance on computer algebra.
- **L544 vs Chapter 2 L255:** The sign convention silently flips from (dx − v0 dt) to (dx + β dt).
- **L570–572:** The mass density is −1.3×10²⁵ kg/m³, not −1×10²⁵. "Nuclear matter, the densest material in nature" is also wrong: neutron-star cores reach about 5 times nuclear density, roughly 10¹⁸ kg/m³.
- **L586–589:** Relies on Chapter 1's fig:warp (b); see the Chapter 1 item below.
- **L626–627:** "change only the ball's shape" needs "at first".
- **L208:** Calls γ²(ρ − v²τ) a "factor"; it is an expression.
- **L313–323 (with L316):** The body gives away the Earth–Moon answer.

**Chapter 1, relevant to Chapter 3's items**
- **L360–361:** fig:warp (b) is captioned "observers at rest outside the bubble", and the source comment says "at rest in the grid". The plotted formula is the riding observers' density.
  - Observers at rest in the grid measure −[(1+3β²)β'² + 4ββ'']/(32π(1−β²)) (sympy). This differs from the plotted density and is positive at the centre of the fast lane.
  - `prob:shear-check` asks students to compare these two families of observers, so they will find the mismatch.
- **L144–147:** The stiffness rule's clock-rate example needs "clocks at rest in a region that holds still".
- **L205–206:** "works out exactly … surprise … in its size": Chapter 3 reaches the same size by the same estimate.

---

## Most serious problems, ranked
1. **A false general statement in a revisited box and the summary** (L394–395, L629–630). It says pressures and tensions cancel in any self-held body, but for a star ∫3p dV = |W|, about 0.1 Mc² for a neutron star. The box's own opening star is left contradicted.
2. **"Between the Earth and the Moon" fails the gate.**
   - Its answer is in its own second sentence and in Chapter 2, which the topic body cites.
   - It duplicates `chk:tidal-volume`.
   - Its Moon clause answers a curvature question with the part of gravity that is not curvature.
   - Replace it with "A drop and a lake" (worked above).
3. **"A room where time runs fast", as rewritten today, is not well posed.**
   - A spinning room gets fast clocks at its centre for free in flat spacetime.
   - The resolution states a slab result for a 3D room, which actually needs equal tension in all three directions at its centre.
   - The final claim drops the flat-space condition.
   - L494 calls an order-of-magnitude figure exact.
4. **Three of the six checks fail C1.**
   - Check 3.2 is recall; Check 3.4 is one step of algebra; Check 3.5 is a sign flip of a pattern printed just above, and it duplicates the caption, the revisited box and a problem.
   - Check 3.3 re-teaches Chapter 1's stiffness.
5. **"A river with a fast lane" is telegraphed by Chapters 1 and 2.**
   - The chapter's central negative-energy result appears with no visible derivation.
   - The Chapter 1 figure it cites names the wrong observers.
