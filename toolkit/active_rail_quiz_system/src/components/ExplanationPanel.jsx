import { claimLabels } from "../data/taxonomy.js";
import { RichText } from "./RichText.jsx";
import { SourceList } from "./SourceList.jsx";

export function ExplanationPanel({ question, response, result, inline = false }) {
  return (
    <div className={inline ? "inline-explanation" : "explanation"}>
      <p><strong>Score:</strong> {formatScore(result.earned)} / {formatScore(result.possible)}</p>
      <AdaptiveFeedback question={question} response={response} />
      <p><strong>Answer:</strong> <RichText content={question.explanation.answer} /></p>
      <p><strong>Why:</strong> <RichText content={question.explanation.why} /></p>
      <p><strong>Boundary:</strong> <RichText content={question.explanation.boundary} /></p>
      {question.explanation.misconceptions && (
        <p><strong>Watch for:</strong> <RichText content={question.explanation.misconceptions} /></p>
      )}
      {question.explanation.openGate && (
        <p><strong>Open gate:</strong> <RichText content={question.explanation.openGate} /></p>
      )}
      <SourceList references={question.explanation.references} sourceLinks={question.explanation.sourceLinks} />
    </div>
  );
}

function AdaptiveFeedback({ question, response }) {
  const adaptive = question.explanation.adaptive;
  if (!adaptive) return null;

  const items = getAdaptiveItems(question, response, adaptive);
  if (items.length === 0) return null;

  return (
    <section className="adaptive-feedback" aria-label="Answer-specific feedback">
      <h4>Answer Feedback</h4>
      <div className="adaptive-feedback-list">
        {items.map((item) => (
          <article className={`adaptive-feedback-item ${item.status}`} key={item.key}>
            <div className="adaptive-feedback-label">{item.label}</div>
            <RichText content={item.content} />
          </article>
        ))}
      </div>
    </section>
  );
}

function getAdaptiveItems(question, response, adaptive) {
  if (["mc", "multi", "tf"].includes(question.type)) return getChoiceFeedback(question, response, adaptive);
  if (question.type === "drag_fill") return getBlankFeedback(question, response, adaptive);
  if (question.type === "sequence") return getSequenceFeedback(question, response, adaptive);
  if (question.type === "matching") return getMatchingFeedback(question, response, adaptive);
  if (question.type === "claim_classification") return getClassificationFeedback(question, response, adaptive);
  return [];
}

function getChoiceFeedback(question, response, adaptive) {
  const selected = new Set(response?.choices || []);
  const answers = new Set(question.answer);
  const items = [];

  question.choices.forEach((choice) => {
    const feedback = adaptive.choices?.[choice.id];
    if (!feedback) return;

    const isSelected = selected.has(choice.id);
    const isAnswer = answers.has(choice.id);
    if (isSelected && isAnswer) {
      items.push(makeItem(choice.id, "selected-correct", "Selected and supported", feedback.supported || feedback.correct || feedback));
    } else if (isSelected) {
      items.push(makeItem(choice.id, "selected-unsupported", "Selected but unsupported", feedback.unsupported || feedback.incorrect || feedback));
    } else if (isAnswer) {
      items.push(makeItem(choice.id, "missed-supported", "Supported but not selected", feedback.missed || feedback.supported || feedback.correct || feedback));
    }
  });

  return items;
}

function getBlankFeedback(question, response, adaptive) {
  const blanks = response?.blanks || {};

  return question.blanks.flatMap((blank) => {
    const feedback = adaptive.blanks?.[blank.id];
    if (!feedback) return [];

    const selectedToken = blanks[blank.id];
    if (!selectedToken) {
      return [makeItem(blank.id, "missing", "Blank not filled", feedback.missing || "The blank needs a role-specific token before it can be graded.")];
    }

    if (blank.accepts.includes(selectedToken)) {
      return [makeItem(blank.id, "selected-correct", "Placed token is supported", feedback.correct || feedback.tokens?.[selectedToken])];
    }

    return [makeItem(blank.id, "selected-unsupported", "Placed token has the wrong role", feedback.tokens?.[selectedToken] || feedback.incorrect)];
  }).filter((item) => item.content);
}

function getSequenceFeedback(question, response, adaptive) {
  const order = response?.order || question.items.map((item) => item.id);

  return (adaptive.sequence || []).map((relation) => {
    const beforeIndex = order.indexOf(relation.before);
    const afterIndex = order.indexOf(relation.after);
    const satisfied = beforeIndex >= 0 && afterIndex >= 0 && beforeIndex < afterIndex;
    return makeItem(
      relation.id || `${relation.before}-${relation.after}`,
      satisfied ? "selected-correct" : "selected-unsupported",
      satisfied ? "Order relation preserved" : "Order relation needs attention",
      satisfied ? relation.satisfied || relation.content : relation.unsatisfied || relation.content
    );
  }).filter((item) => item.content);
}

function getMatchingFeedback(question, response, adaptive) {
  const matches = response?.matches || {};

  return question.prompts.map((prompt) => {
    const feedback = adaptive.matches?.[prompt.id];
    if (!feedback) return null;

    const selected = matches[prompt.id];
    const answer = question.answer[prompt.id];
    if (!selected) return makeItem(prompt.id, "missing", "Match not selected", feedback.missing || feedback.correct);
    if (selected === answer) return makeItem(prompt.id, "selected-correct", "Match supported", feedback.correct || feedback.options?.[selected]);
    return makeItem(prompt.id, "selected-unsupported", "Match has a different role", feedback.options?.[selected] || feedback.incorrect);
  }).filter((item) => item?.content);
}

function getClassificationFeedback(question, response, adaptive) {
  const classifications = response?.classifications || {};

  return question.statements.map((statement) => {
    const feedback = adaptive.classifications?.[statement.id];
    if (!feedback) return null;

    const selected = classifications[statement.id];
    const answer = statement.answer;
    if (!selected) return makeItem(statement.id, "missing", "Status not selected", feedback.missing || feedback.correct);
    if (selected === answer) return makeItem(statement.id, "selected-correct", `Classified as ${claimLabels[answer] || answer}`, feedback.correct || feedback.statuses?.[selected]);
    return makeItem(statement.id, "selected-unsupported", `Selected ${claimLabels[selected] || selected}`, feedback.statuses?.[selected] || feedback.incorrect);
  }).filter((item) => item?.content);
}

function makeItem(key, status, label, content) {
  return { key, status, label, content };
}

function formatScore(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}
