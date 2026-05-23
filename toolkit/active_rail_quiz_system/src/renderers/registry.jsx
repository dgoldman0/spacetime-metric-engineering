import { BoundaryClassificationActivity } from "./BoundaryClassificationActivity.jsx";
import { MatchingActivity } from "./MatchingActivity.jsx";
import { SequenceActivity } from "./SequenceActivity.jsx";
import { StandardChoiceActivity } from "./StandardChoiceActivity.jsx";
import { SymbolFillActivity } from "./SymbolFillActivity.jsx";
import {
  gradeBoundaryClassification,
  gradeChoice,
  gradeDragFill,
  gradeMatching,
  gradeSequence
} from "../lib/grading.js";

export const registry = {
  mc: {
    Component: StandardChoiceActivity,
    grade: gradeChoice
  },
  multi: {
    Component: StandardChoiceActivity,
    grade: gradeChoice
  },
  tf: {
    Component: StandardChoiceActivity,
    grade: gradeChoice
  },
  drag_fill: {
    Component: SymbolFillActivity,
    grade: gradeDragFill
  },
  sequence: {
    Component: SequenceActivity,
    grade: gradeSequence
  },
  matching: {
    Component: MatchingActivity,
    grade: gradeMatching
  },
  claim_classification: {
    Component: BoundaryClassificationActivity,
    grade: gradeBoundaryClassification
  }
};
