export function gradeChoice(question, response) {
  const selected = [...(response?.choices || [])].sort();
  const answer = [...question.answer].sort();
  const correct = arraysEqual(selected, answer);
  if (question.type === "multi" && question.scoring === "subtract_incorrect") {
    const answerSet = new Set(answer);
    const correctSelections = selected.filter((id) => answerSet.has(id)).length;
    const incorrectSelections = selected.filter((id) => !answerSet.has(id)).length;
    const earned = Math.max(0, correctSelections - incorrectSelections);
    return { earned, possible: answer.length, correct: earned === answer.length };
  }
  return { earned: correct ? 1 : 0, possible: 1, correct };
}

export function gradeDragFill(question, response) {
  const blanks = response?.blanks || {};
  let earned = 0;
  question.blanks.forEach((blank) => {
    if (blank.accepts.includes(blanks[blank.id])) earned += 1;
  });
  return { earned, possible: question.blanks.length, correct: earned === question.blanks.length };
}

export function gradeSequence(question, response) {
  const order = response?.order || [];
  let earned = 0;
  question.answer.forEach((itemId, index) => {
    if (order[index] === itemId) earned += 1;
  });
  return { earned, possible: question.answer.length, correct: earned === question.answer.length };
}

export function gradeMatching(question, response) {
  const matches = response?.matches || {};
  let earned = 0;
  question.prompts.forEach((prompt) => {
    if (matches[prompt.id] === question.answer[prompt.id]) earned += 1;
  });
  return { earned, possible: question.prompts.length, correct: earned === question.prompts.length };
}

export function gradeBoundaryClassification(question, response) {
  const classifications = response?.classifications || {};
  let earned = 0;
  const details = {};
  question.statements.forEach((statement) => {
    const correct = classifications[statement.id] === statement.answer;
    if (correct) earned += 1;
    details[statement.id] = { correct, selected: classifications[statement.id], answer: statement.answer };
  });
  return {
    earned,
    possible: question.statements.length,
    correct: earned === question.statements.length,
    details
  };
}

function arraysEqual(a, b) {
  return a.length === b.length && a.every((value, index) => value === b[index]);
}
