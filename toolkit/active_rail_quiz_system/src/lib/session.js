export function buildInitialResponse(question) {
  if (question.type === "sequence") {
    return { order: shuffle(question.items.map((item) => item.id)) };
  }
  if (question.type === "drag_fill") {
    return { blanks: {} };
  }
  if (question.type === "matching") {
    return { matches: {} };
  }
  if (question.type === "claim_classification") {
    return { classifications: {} };
  }
  return { choices: [] };
}

export function shuffle(values) {
  const copy = [...values];
  for (let index = copy.length - 1; index > 0; index -= 1) {
    const other = Math.floor(Math.random() * (index + 1));
    [copy[index], copy[other]] = [copy[other], copy[index]];
  }
  return copy;
}

export function unique(values) {
  return Array.from(new Set(values)).sort((a, b) => String(a).localeCompare(String(b)));
}
