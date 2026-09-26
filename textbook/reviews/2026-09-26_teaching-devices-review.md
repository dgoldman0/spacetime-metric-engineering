# Review of the teaching devices in Chapters 1–3

> **Superseded, 26 September 2026.** The verdicts in this record came from
> yes-or-no criteria that I answered by assertion. They passed a flawed thought
> experiment ("How stiff is the sheet?"). Independent reviews then failed 10
> and marked marginal 13 of the 36 thought experiments and checks
> (`2026-09-26_independent-review-ch1.md`, `-ch2.md`, `-ch3.md`; decisions in
> `2026-09-26_reconciliation.md`). The "Verification" section below describes
> script checks of arithmetic. They say nothing about whether the puzzles
> teach. The record is kept unchanged below as provenance.


26 September 2026, after the two-column draft was committed (ef9ae1f).

The user reviewed the two-column draft and asked for every puzzle, thought
experiment and progress check to be held to a high standard, with weak ones
removed and the devices spread evenly through the book. Summaries, thought
experiments and progress checks stay: they break up the reading and keep the
book a textbook. This record gives the criteria used, the verdict on each
instance, and what changed.

## Criteria

A thought experiment has to meet all of these:

1. It sets up a concrete situation the reader can picture.
2. It poses a real question: a tempting wrong answer, two competing effects,
   or an apparent paradox.
3. The topic supplies what the reader needs to settle it, and no earlier
   chapter has already given the answer away.
4. Its resolution carries the topic's central idea.
5. It is physically well posed, and every number in it is checked.
6. It differs from the other puzzles in the book.

A check of understanding has to meet all of these:

1. The reader can answer it in a few minutes from the topic just read.
2. It tests use or understanding (a new case, a sign, a limit, a scaling),
   never the recall of one sentence and never a bare substitution.
3. It differs from the end-of-chapter problems.
4. Its answer at the end of the chapter explains as well as states.

Distribution: every topic opens with a thought experiment except the closing
synthesis topic of a chapter; each chapter carries five or six checks, each
placed right after the material it tests, at most one per topic; a topic that
develops a technique carries a worked example or a check.

## Thought experiments

| Chapter | Topic | Thought experiment | Verdict | Action |
|---|---|---|---|---|
| 1 | Clocks that disagree | The satellite's clock | Strong: two competing effects, and the winner depends on altitude. | Kept. |
| 1 | Spacetime is stiff | How stiff is the sheet? | Adequate estimation puzzle, but it never asked the reader to commit to a guess. | Kept; now asks "Would a loaded truck do? A mountain?" before the estimate. |
| 1 | Reading the equation backwards | Can relativity say no? | Good: the common belief that relativity forbids faster-than-light travel is the tempting wrong answer. | Kept. |
| 1 | Three ways to beat a light beam | The race with a light beam | Strong. | Kept. |
| 1 | Matter that bends light the wrong way | A concave lens made of gravity | Strong. | Kept. |
| 1 | Negative energy in the laboratory | A stack of Casimir plates | Strong. | Kept. |
| 1 | Cause, effect and control | A message to the front | Strong. | Kept. |
| 2 | What every observer agrees on | Has Betelgeuse exploded? | Strong. | Kept. |
| 2 | The time a clock keeps | The twins | Strong; "each twin sees the other's clock running slow" was imprecise, since what a twin literally sees includes the Doppler shift. | Kept; now "measures". |
| 2 | The metric | A grid on a conveyor belt | Useful setup, physically ill posed: its second question needs a belt sliding at twice the speed of light. | Rebuilt as "A sliding grid" of projected lines, a pattern of light that can slide at any speed. |
| 2 | Clocks in a gravitational field | Twins on a mountain | Weak: a substitution into gh/c², and Chapter 1 had already told the reader that higher clocks run fast. | Replaced by "Light climbing a tower": energy conservation plus a steady wave force clocks at different heights to tick at different rates. The Everest calculation became Check 2.4. The topic gained a paragraph on the gravitational redshift, with the Pound–Rebka measurement. |
| 2 | Space as a flowing river | The fish and the waterfall | Strong. | Kept. |
| 2 | Falling is straight | The thrown ball | Strong. | Kept. The key idea now says a geodesic beats every *nearby* worldline, and a new starred problem (the orbit paradox) shows why the qualifier matters. |
| 2 | Tides | The windowless capsule | Strong. | Kept. |
| 3 | Energy depends on who measures it | A brick in passing | Strong: γ² where γ is expected. | Kept. |
| 3 | Pressure, tension and the vacuum | Flying through empty space | Strong. | Kept. |
| 3 | Einstein's equation | Fixing the constant | Weak: a derivation step phrased as a question, with no situation to picture. | Replaced by "Between the Earth and the Moon": does zero stress-energy mean flat spacetime? The topic gained the Baez–Bunn statement of Einstein's equation (a falling ball shrinks at the rate −4π(ρ + p_x + p_y + p_z)) and a paragraph on empty space (R_μν = 0 while the Riemann tensor survives). The history of fixing the constant moved into the discussion of Example 3.2. |
| 3 | Pressure gravitates | A box of hot gas | Strong. | Kept; the topic now derives ρ + 3p from the ball statement. |
| 3 | Reading the equation backwards | A room where time runs fast | Good. | Kept. |
| 3 | When space flows unevenly | A conveyor belt with a fast lane | Good; the name repeated the conveyor-belt image. | Kept as "A river with a fast lane". |

## Checks of understanding

| Check | Question | Verdict | Action |
|---|---|---|---|
| 1.1 | Clock slowing at the Sun and a neutron star | Good: tests where the weak-field formula fails. | Kept. |
| 1.2 | Why demand can be computed but geometry is hard to find | Recall of one sentence. | Replaced: which questions Einstein's equation answers on its own. |
| 1.3 | Alcubierre travellers versus a ship at 0.99c | New. | Tests moving through space versus space moving. |
| 1.4 | Factor by which Casimir energy grows from 1 µm to 10 nm | Bare substitution. | Replaced: from the energy per area, which way the Casimir force points and how it scales (π²ħc/240d⁴, 1.3 mPa at 1 µm). |
| 1.5 | Why a Krasnikov builder is not cut off | New. | Tests the control argument. |
| 2.1 | Classify two intervals | Good. | Kept. |
| 2.2 | A zigzag worldline with as little proper time as you like | New. | Tests the key idea from the other side: there is no least proper time. |
| 2.3 | A clock riding a grid point of flowing coordinates | New. | Shows the metric reproducing special-relativistic time dilation. |
| 2.4 | Twins on Everest | Moved from the replaced thought experiment. | A quick use of gh/c² (2.4 ms). |
| 2.5 | Does tidal stretching change a falling ball's volume? | New. | Sets up the empty-space puzzle of Chapter 3. |
| 3.1 | A laser beam seen by a moving observer | New. | Tests index lowering, including the sign of T_tx; answer u(1 − v)/(1 + v). |
| 3.2 | ρ + p for four kinds of matter | Good. | Kept. |
| 3.3 | Water in geometric units | New. | Practises the unit conversion; curvature length about 2 × 10¹¹ m. |
| 3.4 | The stress that stops a ball from shrinking | New. | p = −ρ/3, the threshold that vacuum energy passes. |
| 3.5 | Clocks slowest in the middle | Good. | Kept. |
| 3.6 | Doubling the width of a layer of shear | New. | The first design trade-off: thin shear layers cost more. |

Answers are now keyed by label, so their numbers follow the checks
automatically.

## Other changes

- Chapter 1 gained Example 1.2, "The Sun as a lens" (1.75 seconds of arc at
  the limb, a focal line starting about 550 AU out), which gives the
  converging-lens baseline of the thought experiment in numbers.
- The Chapter 1 key idea on the null energy condition now says "under very
  general conditions", matching the qualified claim in the text.
- The caption of the river figure named the wrong colours; it now matches the
  drawing (flow in blue, outgoing light in orange).
- New sources: Pound and Rebka (1960), Baez and Bunn (2005), and Dyson,
  Eddington and Davidson (1920), each checked against its Crossref record
  (`bib/crossref-metadata/`).

## Distribution before and after

| Device | Ch. 1 | Ch. 2 | Ch. 3 |
|---|---|---|---|
| Thought experiments | 7 → 7 | 7 → 7 | 6 → 6 |
| Checks of understanding | 3 → 5 | 1 → 5 | 2 → 6 |
| Worked examples | 1 → 2 | 5 → 5 | 4 → 4 |
| Key ideas | 1 | 2 | 1 |
| Sidebars | 1 | 2 | 2 |

## Verification

`checks/rev2_teaching_devices.py` recomputes every new number and verifies
the new claims: 57 checks, all passing. They include the tidal trace in empty
space, the Baez–Bunn identity R_tt = 4π(ρ + Σp), the shear demand from the
metric, and a numerical test of the orbit paradox. In that test the orbiting
astronaut records 1.8 µs less per orbit than the hovering one, and a straight
up-and-down free fall records 1.2 µs more than hovering. The first run,
kept as `rev2_teaching_devices_run1.log`, failed on one check because sympy
could not simplify γ(1 − v) = √((1 − v)/(1 + v)) without knowing |v| < 1; the
check now uses the rapidity. The Pound–Rebka baseline (74 feet, 22.6 m) and
result (1.05 ± 0.10 of the prediction) were confirmed from the text of the
paper. The earlier check scripts still pass unchanged.

## Layout

The book builds at 40 pages with no undefined references or overfull lines.
No box breaks across a page turn. Example 3.3 was made unbreakable, because
the added material had pushed it across the turn from page 27 to page 28; this
leaves a gap at the foot of page 27. Two figure placements are left for the
figure rules still under discussion: Chapter 1's two full-width figures stack
on page 8, a page turn after the text that cites them, and the gap on page 27
will move once the planned Einstein-topic figure is added.
