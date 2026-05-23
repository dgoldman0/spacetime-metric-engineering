import { questionBank } from "../src/data/questionBank.js";
import { getQuestionContext } from "../src/data/taxonomy.js";

const ids = new Set();
const allowedTypes = new Set(["mc", "multi", "tf", "drag_fill", "sequence", "matching", "claim_classification"]);
const allowedDifficulties = new Set(["core", "intermediate", "advanced"]);
const allowedContexts = new Set(["general_theory", "paper_theory", "project_application", "project_state"]);
const referenceRequiredStatuses = new Set(["established_theory", "established_constraint", "literature_model"]);
const flaggedSourceRequired = new Set(["project_material", "project_state", "open_question", "revision_sensitive"]);
const publicUrlPattern = /^https:\/\/(arxiv\.org|github\.com\/dgoldman0\/spacetime-metric-engineering)\//;
const bannedSourceText = [/PROJECT_WORK_ANALYSIS/i, /Project work analysis/i];
const bannedPaperTheoryText = [/\bactive-rail\b/i, /\bservice-design\b/i, /\bservice-governor\b/i];
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
  assert(allowedContexts.has(getQuestionContext(question)), `bad question context on ${question.id}`);
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

  validateSources(question);
  validateContext(question);

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

function validateSources(question) {
  const sources = [...(question.explanation.references || []), ...(question.explanation.sourceLinks || [])];
  sources.forEach((source, index) => {
    assert(!source.path, `local path is not learner-facing source material on ${question.id} source ${index}`);
    bannedSourceText.forEach((pattern) => {
      assert(!pattern.test(JSON.stringify(source)), `banned meta-analysis source on ${question.id}`);
    });
    if (source.url) {
      assert(publicUrlPattern.test(source.url), `source URL is not on an allowed public host for ${question.id}: ${source.url}`);
    }
    if (source.kind === "project_doc") {
      assert(source.url, `project source must use a verified public URL on ${question.id}`);
      assert(source.url.startsWith("https://github.com/dgoldman0/spacetime-metric-engineering/blob/main/"), `project source must use public repository URL on ${question.id}`);
    }
  });
}

function validateContext(question) {
  if (getQuestionContext(question) !== "paper_theory") return;
  const searchable = JSON.stringify({
    prompt: question.prompt,
    promptParts: question.promptParts,
    choices: question.choices,
    items: question.items,
    prompts: question.prompts,
    statements: question.statements,
    explanation: question.explanation
  });

  bannedPaperTheoryText.forEach((pattern) => {
    assert(!pattern.test(searchable), `paper-theory item has project-specific framing on ${question.id}`);
  });
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
