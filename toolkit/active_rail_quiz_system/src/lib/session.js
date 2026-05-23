export function buildInitialResponse(question) {
  if (question.type === "mc" || question.type === "multi" || question.type === "tf") {
    return {
      choices: [],
      choiceOrder: shuffle(question.choices.map((choice) => choice.id))
    };
  }
  if (question.type === "sequence") {
    return {
      order: shuffleAwayFromAnswer(
        question.items.map((item) => item.id),
        question.answer
      )
    };
  }
  if (question.type === "drag_fill") {
    return {
      blanks: {},
      tokenOrder: shuffle(question.tokens.map((token) => token.id))
    };
  }
  if (question.type === "matching") {
    return {
      matches: {},
      promptOrder: shuffle(question.prompts.map((prompt) => prompt.id)),
      optionOrder: shuffle(question.options.map((option) => option.id))
    };
  }
  if (question.type === "claim_classification") {
    return {
      classifications: {},
      statementOrder: shuffle(question.statements.map((statement) => statement.id))
    };
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

export function orderByIds(records, orderedIds = []) {
  const byId = new Map(records.map((record) => [record.id, record]));
  const ordered = orderedIds.map((id) => byId.get(id)).filter(Boolean);
  const seen = new Set(ordered.map((record) => record.id));
  const missing = records.filter((record) => !seen.has(record.id));
  return [...ordered, ...missing];
}

function shuffleAwayFromAnswer(values, answer) {
  if (values.length < 2) return [...values];

  for (let attempt = 0; attempt < 8; attempt += 1) {
    const candidate = shuffle(values);
    if (!arraysEqual(candidate, answer)) return candidate;
  }

  return [...answer].reverse();
}

function arraysEqual(a, b) {
  return a.length === b.length && a.every((value, index) => value === b[index]);
}
