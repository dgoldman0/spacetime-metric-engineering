import { questionBank } from "../src/data/questionBank.js";

const ids = new Set();
const allowedTypes = new Set(["mc", "multi", "tf", "drag_fill", "sequence", "matching", "claim_classification"]);

for (const question of questionBank) {
  assert(question.id, "missing id");
  assert(!ids.has(question.id), `duplicate id ${question.id}`);
  ids.add(question.id);
  assert(allowedTypes.has(question.type), `unknown type ${question.type} on ${question.id}`);
  assert(question.track, `missing track on ${question.id}`);
  assert(question.module, `missing module on ${question.id}`);
  assert(question.claimStatus, `missing claimStatus on ${question.id}`);

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
