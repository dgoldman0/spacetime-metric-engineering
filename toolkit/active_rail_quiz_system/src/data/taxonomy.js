export const optionalFlags = ["project_material", "project_state", "open_question", "revision_sensitive"];

export const claimLabels = {
  established_theory: "Established theory",
  established_constraint: "Established constraint",
  literature_model: "Published literature",
  active_rail_model: "Active-rail model",
  project_hypothesis: "Project hypothesis",
  open_gate: "Open gate",
  fictional_frame: "Fictional frame"
};

export const contextLabels = {
  general_theory: "General theory",
  paper_theory: "Paper theory",
  project_application: "Project application",
  project_state: "Project state"
};

export const typeLabels = {
  mc: "Multiple choice",
  multi: "Select all",
  tf: "True/false",
  drag_fill: "Symbol fill",
  sequence: "Chronology",
  matching: "Matching",
  claim_classification: "Claim classification"
};

export function getQuestionContext(question) {
  if (question.context) return question.context;

  const flags = question.contentFlags || [];
  if (flags.includes("project_state") || question.claimStatus === "project_hypothesis") {
    return "project_state";
  }

  if (question.claimStatus === "active_rail_model" || question.track === "Active-rail architecture" || question.track === "Design review and synthesis") {
    return "project_application";
  }

  if (
    question.claimStatus === "literature_model"
    || question.track === "Published warp and wormhole context"
    || question.id.startsWith("constraints.qi")
    || question.id.startsWith("constraints.snec")
  ) {
    return "paper_theory";
  }

  return "general_theory";
}
