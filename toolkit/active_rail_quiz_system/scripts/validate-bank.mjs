import { questionBank } from "../src/data/questionBank.js";

const ids = new Set();
const allowedTypes = new Set(["mc", "multi", "tf", "drag_fill", "sequence", "matching", "claim_classification"]);
const allowedDifficulties = new Set(["core", "intermediate", "advanced"]);
const referenceRequiredStatuses = new Set(["established_theory", "established_constraint", "literature_model"]);
const flaggedSourceRequired = new Set(["project_material", "project_state", "open_question", "revision_sensitive"]);
const bannedMetaPatterns = [
  /\bquiz\b/i,
  /\bquestion bank\b/i,
  /\bscoring policy\b/i,
  /\blabeling policy\b/i,
  /\bauthoring policy\b/i
];

for (const question of questionBank) {
  assert(question.id, "missing id");
  assert(!ids.has(question.id), `duplicate id ${question.id}`);
  ids.add(question.id);
  assert(allowedTypes.has(question.type), `unknown type ${question.type} on ${question.id}`);
  assert(question.track, `missing track on ${question.id}`);
  assert(question.module, `missing module on ${question.id}`);
  assert(question.difficulty, `missing difficulty on ${question.id}`);
  assert(allowedDifficulties.has(question.difficulty), `bad difficulty ${question.difficulty} on ${question.id}`);
  assert(question.claimStatus, `missing claimStatus on ${question.id}`);
  assert(question.explanation?.answer, `missing explanation.answer on ${question.id}`);
  assert(question.explanation?.why, `missing explanation.why on ${question.id}`);
  assert(question.explanation?.boundary, `missing explanation.boundary on ${question.id}`);
  assertNoMetaText(question, question.id);

  if (referenceRequiredStatuses.has(question.claimStatus)) {
    assert(question.explanation.references?.length > 0, `missing references for ${question.claimStatus} item ${question.id}`);
  }

  if ((question.contentFlags || []).some((flag) => flaggedSourceRequired.has(flag))) {
    const hasSources = question.explanation.sourceLinks?.length > 0 || question.explanation.references?.length > 0;
    assert(hasSources, `missing source links for flagged item ${question.id}`);
  }

  if (["mc", "multi", "tf"].includes(question.type)) {
    const choices = new Set(question.choices.map((choice) => choice.id));
    question.answer.forEach((answer) => assert(choices.has(answer), `bad answer ${answer} on ${question.id}`));
  }

  if (question.type === "drag_fill") {
    const tokens = new Set(question.tokens.map((token) => token.id));
    question.blanks.forEach((blank) => {
      blank.accepts.forEach((answer) => assert(tokens.has(answer), `bad blank answer ${answer} on ${question.id}`));
    });
  }

  if (question.type === "sequence") {
    const items = new Set(question.items.map((item) => item.id));
    question.answer.forEach((answer) => assert(items.has(answer), `bad sequence answer ${answer} on ${question.id}`));
  }

  if (question.type === "matching") {
    const options = new Set(question.options.map((option) => option.id));
    question.prompts.forEach((prompt) => assert(options.has(question.answer[prompt.id]), `bad match answer ${prompt.id} on ${question.id}`));
  }

  if (question.type === "claim_classification") {
    const statuses = new Set(question.statuses);
    question.statements.forEach((statement) => assert(statuses.has(statement.answer), `bad status ${statement.answer} on ${question.id}`));
  }
}

console.log(`validated ${questionBank.length} questions`);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertNoMetaText(value, id, path = "question") {
  if (typeof value === "string") {
    bannedMetaPatterns.forEach((pattern) => {
      assert(!pattern.test(value), `meta curriculum text "${value}" on ${id} at ${path}`);
    });
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertNoMetaText(item, id, `${path}[${index}]`));
    return;
  }
  if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, entry]) => {
      if (key === "id" || key === "type" || key === "url" || key === "path") return;
      assertNoMetaText(entry, id, `${path}.${key}`);
    });
  }
}
