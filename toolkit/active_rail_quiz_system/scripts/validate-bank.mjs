import { questionBank } from "../src/data/questionBank.js";
import { getQuestionContext } from "../src/data/taxonomy.js";

const ids = new Set();
const multiSelectShapes = new Set();
const multiSelectChoiceCounts = new Set();
const multiSelectCorrectCounts = new Map();
const allowedTypes = new Set(["mc", "multi", "tf", "drag_fill", "sequence", "matching", "claim_classification"]);
const allowedDifficulties = new Set(["core", "intermediate", "advanced"]);
const allowedContexts = new Set(["general_theory", "paper_theory", "project_application", "project_state"]);
const referenceRequiredStatuses = new Set(["established_theory", "established_constraint", "literature_model"]);
const flaggedSourceRequired = new Set(["project_material", "project_state", "open_question", "revision_sensitive"]);
const publicUrlPattern = /^https:\/\/(arxiv\.org|openstax\.org|davidtong\.org|github\.com\/dgoldman0\/spacetime-metric-engineering)\//;
const bannedSourceText = [/PROJECT_WORK_ANALYSIS/i, /Project work analysis/i];
const bannedPaperTheoryText = [/\bactive-rail\b/i, /\bservice-design\b/i, /\bservice-governor\b/i];
const publicationYearPattern = /\b(19|20)\d{2}\b/;
const minWhyWords = { core: 10, intermediate: 14, advanced: 24 };
const minBoundaryWords = { core: 8, intermediate: 10, advanced: 12 };
const bannedMetaPatterns = [
  /\bquiz\b/i,
  /\bquestion bank\b/i,
  /\bscoring policy\b/i,
  /\blabeling policy\b/i,
  /\bauthoring policy\b/i
];
const bannedExplanationMetaPatterns = [
  /\badvanced\b/i,
  /\bintermediate\b/i,
  /\bcore\b/i,
  /\bthis item\b/i,
  /\blearner\b/i,
  /\bthis is advanced\b/i,
  /\badvanced (move|point|task|transfer|reasoning|distinction)\b/i,
  /\bdifficulty label\b/i,
  /\brubric\b/i
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
  validateExplanationDepth(question);
  validateExplanationIsMaterialFacing(question);
  validateAdaptiveFeedback(question);

  if (["mc", "multi", "tf"].includes(question.type)) {
    const choices = new Set(question.choices.map((choice) => choice.id));
    question.answer.forEach((answer) => assert(choices.has(answer), `bad answer ${answer} on ${question.id}`));
    if (question.type === "multi") {
      multiSelectShapes.add(`${question.answer.length}/${question.choices.length - question.answer.length}/${question.choices.length}`);
      multiSelectChoiceCounts.add(question.choices.length);
      multiSelectCorrectCounts.set(question.answer.length, (multiSelectCorrectCounts.get(question.answer.length) || 0) + 1);
    }
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

if (multiSelectShapes.size > 0) {
  const multiSelectTotal = [...multiSelectCorrectCounts.values()].reduce((sum, count) => sum + count, 0);
  const dominantCorrectCount = Math.max(...multiSelectCorrectCounts.values());
  assert(multiSelectShapes.size >= 3, "multi-select bank is too patterned; vary correct-answer counts and choice counts");
  assert(multiSelectCorrectCounts.size >= 3, "multi-select bank needs varied correct-answer counts");
  assert(
    dominantCorrectCount / multiSelectTotal <= 0.6,
    "multi-select bank has a dominant correct-answer count; review for answer-pattern leakage"
  );
  assert([...multiSelectChoiceCounts].some((count) => count > 4), "multi-select bank needs some richer 5- or 6-choice items");
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

  const promptText = richTextToPlain(question.prompt || question.promptParts || "");
  assert(publicationYearPattern.test(promptText), `paper-theory prompt needs a publication year or equivalent citation anchor on ${question.id}`);
}

function validateExplanationDepth(question) {
  const whyWords = wordCount(question.explanation.why);
  const boundaryWords = wordCount(question.explanation.boundary);
  assert(whyWords >= minWhyWords[question.difficulty], `explanation why is too thin for ${question.difficulty} item ${question.id}`);
  assert(boundaryWords >= minBoundaryWords[question.difficulty], `explanation boundary is too thin for ${question.difficulty} item ${question.id}`);
}

function validateExplanationIsMaterialFacing(question) {
  const text = richTextToPlain(question.explanation);
  bannedExplanationMetaPatterns.forEach((pattern) => {
    assert(!pattern.test(text), `explanation contains authoring-room difficulty/rubric language on ${question.id}`);
  });
}

function validateAdaptiveFeedback(question) {
  const adaptive = question.explanation.adaptive;
  if (!adaptive) return;

  if (adaptive.choices) {
    const choices = new Set((question.choices || []).map((choice) => choice.id));
    Object.keys(adaptive.choices).forEach((choiceId) => {
      assert(choices.has(choiceId), `adaptive feedback references unknown choice ${choiceId} on ${question.id}`);
    });
  }

  if (adaptive.blanks) {
    const blanks = new Set((question.blanks || []).map((blank) => blank.id));
    const tokens = new Set((question.tokens || []).map((token) => token.id));
    Object.entries(adaptive.blanks).forEach(([blankId, feedback]) => {
      assert(blanks.has(blankId), `adaptive feedback references unknown blank ${blankId} on ${question.id}`);
      Object.keys(feedback.tokens || {}).forEach((tokenId) => {
        assert(tokens.has(tokenId), `adaptive feedback references unknown token ${tokenId} on ${question.id}`);
      });
    });
  }

  if (adaptive.sequence) {
    const items = new Set((question.items || []).map((item) => item.id));
    adaptive.sequence.forEach((relation) => {
      assert(items.has(relation.before), `adaptive feedback references unknown sequence item ${relation.before} on ${question.id}`);
      assert(items.has(relation.after), `adaptive feedback references unknown sequence item ${relation.after} on ${question.id}`);
    });
  }

  if (adaptive.matches) {
    const prompts = new Set((question.prompts || []).map((prompt) => prompt.id));
    const options = new Set((question.options || []).map((option) => option.id));
    Object.entries(adaptive.matches).forEach(([promptId, feedback]) => {
      assert(prompts.has(promptId), `adaptive feedback references unknown match prompt ${promptId} on ${question.id}`);
      Object.keys(feedback.options || {}).forEach((optionId) => {
        assert(options.has(optionId), `adaptive feedback references unknown match option ${optionId} on ${question.id}`);
      });
    });
  }

  if (adaptive.classifications) {
    const statements = new Set((question.statements || []).map((statement) => statement.id));
    const statuses = new Set(question.statuses || []);
    Object.entries(adaptive.classifications).forEach(([statementId, feedback]) => {
      assert(statements.has(statementId), `adaptive feedback references unknown classification statement ${statementId} on ${question.id}`);
      Object.keys(feedback.statuses || {}).forEach((status) => {
        assert(statuses.has(status), `adaptive feedback references unknown classification status ${status} on ${question.id}`);
      });
    });
  }
}

function wordCount(value) {
  return richTextToPlain(value).trim().split(/\s+/).filter(Boolean).length;
}

function richTextToPlain(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(richTextToPlain).join(" ");
  if (value && typeof value === "object") return Object.values(value).map(richTextToPlain).join(" ");
  return "";
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
