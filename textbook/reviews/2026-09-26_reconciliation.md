# Reconciliation of the independent reviews of Chapters 1–3

26 September 2026. The three reviewer reports are kept beside this record
(`2026-09-26_independent-review-ch1.md`, `-ch2.md`, `-ch3.md`). This record
gives my decision on each finding and the reason for it. "Adopt" means the
reviewer's fix is used as proposed. "Adapt" means the finding is accepted and
the fix changed. "Reject" means the finding is judged wrong or not worth the
change. Every claim I adopt was checked against the text. The physics claims
that go into the book were also checked in sympy
(`scratchpad/reconcile/verify_claims.py` and `checks/rev3_redesigns.py`). The
teaching judgments rest on the reviewers' working and on my reading, not on
scripts.

The reviews confirm the user's two objections. The first written criteria had
passed puzzles that fail on reflection. Script checks, which all passed, said
nothing about whether a puzzle teaches its topic. Of the 36 thought
experiments and checks, 10 failed, 13 were marginal and 13 passed (one
problem, the orbit paradox, was also marginal), and the reviews found physics errors in the surrounding
text that no script had caught.

## Chapter 1

| Finding | Decision | Reason and change |
|---|---|---|
| "How stiff is the sheet?" (stress-per-strain version) fails. Its rule charges a steady clock-rate gradient, which is free (the rocket; any room on Earth). The binary is given away by the heading. The stiffness c⁴/(8πGL²) is a property of the scale, not of a medium. | Adopt the replacement, with changes | New puzzle: a one-metre ball of osmium with one of today's best clocks against it. Will the clock see the dent? The answer is about 2 × 10⁻²³ against the clock's 10⁻¹⁸: the surprise enters at c²/G. The clock sits against the ball and is compared with one across the laboratory, so eq. (clock-slowing) answers it directly, without the interior potential. The stiffness rule is restated as "a radius of curvature L needs energy densities or stresses of order c⁴/(8πGL²)", which contains no strain. The heading becomes "How hard is it to bend spacetime?" and the opening bullet matches. |
| "Its inverse is c⁴/G" (off by 8π) | Adopt | Reworded: the constant is 8πG/c⁴; its size is set by c⁴/G. |
| "Everyday … a few parts in 10¹⁰" | Adopt | Everyday effects are about 10⁻¹² or less; satellites reach a few parts in 10¹⁰. |
| Warp figure (b) names the wrong observers | Adopt | Caption: observers carried along by the flow of space. |
| Concave lens: answer given away in the wormhole subsection; the ring's reason is wrong; the focal-point qualifier is missing | Adopt | The diverging-lens and exotic-matter statements move into the lens topic, after the puzzle. The ring's reason becomes cancellation along the ray. "Before its rays cross" is added in three places. |
| Casimir stack: the engine is apparatus bookkeeping | Adopt | The resolution now runs on the 1/d⁴ law and the quantum inequalities: a 1 m throat needs gaps of 3 × 10⁻¹⁸ m. The plates' rest energy is kept as a second point. |
| Message to the front: answer given away in the Krasnikov subsection | Adapt | The Krasnikov subsection now only announces the problem, so nothing before the puzzle answers it. Inside its own topic, the control paragraph explains the mechanism (a flow of space, light moving at c relative to local space) before it states Krasnikov's conclusion, and the resolution adds "however close the wall is". |
| Race with a light beam: "change the course" is true of the wormhole only; the Krasnikov ordering goes unmentioned | Adopt | The resolution now says what each design changes, and notes that the Krasnikov ship reaches the star after the pulse yet is home before the pulse arrives there. |
| Check 1.1: use a white dwarf for a progression | Adopt | The Sun, a white dwarf and a neutron star. |
| Check 1.2 fails (recall, duplicate) | Adopt | Replaced by Team A and Team B. |
| Check 1.3: recall | Adopt | Replaced by the round trip at 5c versus 0.99c. |
| Check 1.4: direction given in the text | Adopt | "Attract" becomes "exert a force on each other"; the check asks whether negative energy means repulsion. |
| Check 1.5: answer supplied by the question | Adopt | Replaced by the robot ships. |
| Travellers "age no more"; the throat's observers; "almost 8 km/s" | Adopt | "Age exactly as much"; the observers named; 7.7 km/s. |
| Answer boxes in view of their questions in print | Refer to the user | Short topics put the thought experiment and its answer on the same spread. The fix changes a design the user chose, so it is put to the user. |

## Chapter 2

| Finding | Decision | Reason and change |
|---|---|---|
| Free-fall key idea false over a full orbit (conjugate points); global restatements | Adopt | Key idea: stationary, and more than every nearby worldline over any short enough stretch. The summary is corrected. The thrown ball keeps its global claim, which holds in the nearly uniform field. |
| "A sliding grid" fails (the setup answers itself; no surprise; duplicates) | Adopt the replacement | "A current faster than light": a uniform stream at 2c is flat, so the message arrives in one second. The resolution states what a horizon needs. |
| "The fish and the waterfall" fails (answered in Chapter 1) | Adopt the replacement | "Standing still in the river": the hanging clock's slowing is its motion upstream through flowing space. The fish stays as intuition in the prose. |
| Betelgeuse: simultaneity is untaught and pre-stated | Adopt the ship version | The crew dates the explosion 318 years before passing. Invariance gives 635 light-years, and the light is still on its way. A sentence on the order of spacelike events is added to the topic text. |
| Twins: aim at the real misconception | Adopt | The one-day turnaround is kept and the star made ten times farther: the gap grows to 42.4 years. The resolution counts signals, 1.06 + 9.54 = 10.6 years, and drops the "sense of now" claim. |
| Tower: given away by Chapter 1; E = hf unstated; "alone" overclaims | Adopt | Now asks whether the redshift is gh/c² or 2gh/c² (double counting). Pound–Rebka rules out the factor 2. |
| Check 2.1: drill, duplicate of Problem 2.1 | Adopt | Replaced by the probe from A to C, and the distance for an observer who calls A and B simultaneous. |
| Check 2.2: null infimum | Adopt | Added. |
| Check 2.4: substitution, duplicate, self-contradiction | Adopt | Replaced by the clock at the Earth's centre. |
| Capsule: "any experiment" admits a magnetometer; side-by-side convergence depends on orientation | Adopt | "With loose objects inside"; the resolution uses the vertical pair. |
| Orbit paradox: unanswerable from the chapter; the hovering idealisation | Adopt | A tower replaces the rockets. The problem asks the reader to show that tilted orbits meet again after half an orbit. |
| "Where the flow varies, the geometry is curved" | Adopt | Verified false (the rotating flow is flat). Reworded. |
| Muon "ten billion"; Michell wording; equivalence-principle logic; "seen" | Adopt | Eight billion; "in a paper read to"; local flatness is a mathematical fact and the equivalence principle is the physical one; "measured". |

## Chapter 3

| Finding | Decision | Reason and change |
|---|---|---|
| Gas box: "any object that holds itself together" is false for self-gravitating bodies; the star premise is unresolved | Adopt | The claim is qualified to bodies held by the strength of their materials, with their own gravity negligible, in the resolution and the summary. The first sentence of the thought experiment is changed. A problem on a star's pressure is added. |
| "Between the Earth and the Moon" fails (answer in the setup and in Chapter 2; "slope steers the Moon" is not curvature) | Adopt the replacement | "A drop and a lake": both balls shrink at −4πGρ, because Einstein's equation is local. |
| Room: the spinning-room loophole; slab result stated for a room; flat-space qualifier dropped; "exact" overclaims | Adopt | "Midway between two facing walls, held still, neither accelerating nor spinning". "With space held flat" is added. The price paragraph gives 4 × 10³⁴ Pa for a bump confined within a metre. The Chapter 1 callback is removed, since Chapter 1's puzzle changed. |
| Fast lane: telegraphed; the engine is not shown | Adopt | Now asks whether the demand balances the way the lapse bump's does (it does not: ρ ∝ −(β′)²). The constraint rule is stated in words as a preview of Chapter 4. The null-energy violation for every observer is added (verified). The sign convention is made to match Chapter 2. |
| Checks 3.2, 3.4 and 3.5 fail; 3.3 re-teaches stiffness | Adopt | 3.2 becomes a fluid seen by a moving observer; 3.3 the water ball that traps its own light; 3.4 the rod whose tension stops a ball from shrinking; 3.5 whether any clock-rate bump can avoid tension. |
| Mass density −1.3 × 10²⁵; "densest material"; "factor"; "at first"; V̈/V wording; conflicting "by hand" claims; "a number every observer agrees on"; "worse than it looks"; clock rates as a test of the field equation | Adopt | All corrected. |
