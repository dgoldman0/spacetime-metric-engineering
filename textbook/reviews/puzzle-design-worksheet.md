# Design worksheet for thought experiments, puzzles and checks

Written 26 September 2026. It replaces the yes-or-no criteria in
`2026-09-26_teaching-devices-review.md`, which passed a flawed thought
experiment ("How stiff is the sheet?", described below). Those criteria were
answered by assertion. Every line of this worksheet has to be answered by
writing something down: an answer worked in full, a number, a named step.
Nothing passes by a tick.

## Thought experiments

**W1. Concept.** The one idea the topic teaches, in one sentence.

**W2. Hook.** The intuition, misconception or tension the puzzle plays on, and
why a reader would hold it.

**W3. First answer.** What a typical reader would answer before reading the
topic.

**W4. Answer and its engine.** The correct answer, worked in full. Name the
step where the surprise enters. That step must be W1. If the surprise comes
from anything else (a scaling law, a geometric factor, an extreme choice of
parameter), the puzzle fails.

**W5. Vary test.** Change each incidental parameter (a distance, a size, a
speed, a material) by about a factor of ten and redo the answer. The lesson
must survive. If it changes with an incidental choice, the puzzle is about that
choice.

**W6. Continuity.** The question follows from the setup; every element of the
setup is used in the resolution; the resolution needs nothing the reader lacks
by the end of the topic.

**W7. Well posed.** Signs, directions and physical possibility are checked:
the setup can exist, and the effect has the sign the text claims. Every general
statement in the setup and the resolution is true as worded, with the
qualifiers it needs ("at first", "for these observers", "with space held
flat", "before its rays cross").

**W8. Not given away.** Neither the setup nor any earlier chapter already
contains the answer.

**W9. Distinct.** No other puzzle or check in the book teaches the same lesson
in the same way. A deliberate return to an earlier puzzle has to ask something
new.

**W10. Arithmetic.** Every number in the setup and the answer is recomputed.
A check script is the right tool for this, and it checks arithmetic only. A
passing script is never evidence that a puzzle teaches well.

## Who reviews

Scripts cannot judge teaching. Every thought experiment, puzzle and check
passes through three readings before the user sees it:

1. The author's worksheet, written out line by line.
2. An independent reviewer agent that fills the worksheet without seeing the
   author's verdicts, and is told to look for the calibration failures below.
3. A learner-perspective agent that reads the chapter in order as the target
   student would. It writes its answer to each thought experiment and check
   before reading on, then reports whether the topic equipped it and where it
   got stuck.

The user reads last and has the final say.

## Checks of understanding

A check answers W1 (what it tests), W3 (the likely error), W4 (the answer, and
the step that tests understanding instead of recall), W6 (answerable from the
topic just read), W7, W9 and W10, and one more:

**C1. More than recall or substitution.** The question cannot be answered by
copying a sentence or by putting numbers into a formula stated just before it,
unless the size of the result is itself the lesson.

## Calibration: the gate must reject these

**The first "How stiff is the sheet?"** The Earth slows clocks by less than a
billionth; what compact mass one metre from a clock would slow it by a
billionth? Answer: 1.3 × 10¹⁸ kg, an asteroid squeezed into a lump.

- W4 fails. The surprise ("an asteroid in a lump") enters where the mass is
  moved from 6400 km to one metre: the fall-off of gravity with distance, and
  the density that follows from it. Stiffness sets the number, but the lesson
  a reader takes away is about fall-off and compactness.
- W5 fails. At ten metres the answer is ten times larger and the image
  changes; the lesson depends on the choice of one metre.
- W6 fails. The Earth fact in the setup connects to the question only through
  the fall-off scaling.

**The first rewrite, made on 26 September.** Fill a one-metre room with
material so that clocks at its centre tick faster than clocks at its walls by
a billionth; what pressure or energy density? W7 fails: positive energy
density at the centre makes the clocks there tick *slower*, as clocks at the
centre of the Earth do. Faster clocks at the centre need tension, which is
Chapter 3's discovery.
