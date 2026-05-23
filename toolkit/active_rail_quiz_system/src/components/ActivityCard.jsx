import { claimLabels, typeLabels } from "../data/taxonomy.js";
import { RichText } from "./RichText.jsx";
import { registry } from "../renderers/registry.jsx";

export function ActivityCard({ question, index, response, reviewed, mode, onResponse, onReview }) {
  const entry = registry[question.type];
  const Renderer = entry.Component;
  const result = reviewed ? entry.grade(question, response) : null;
  const resultClass = result ? (result.correct ? "correct" : result.earned > 0 ? "partial" : "incorrect") : "";

  return (
    <article className={`question-card ${reviewed ? "reviewed" : ""} ${resultClass}`}>
      <div className="question-head">
        <div>
          <div className="question-kicker">Question {index + 1} / {typeLabels[question.type] || question.type}</div>
          <h3>{question.module}</h3>
        </div>
        <div className="badges">
          <span className={`badge ${question.claimStatus}`}>{claimLabels[question.claimStatus] || question.claimStatus}</span>
          <span className="badge">{question.difficulty}</span>
          {(question.contentFlags || []).map((flag) => (
            <span key={flag} className={`badge ${flag}`}>{flag.replaceAll("_", " ")}</span>
          ))}
        </div>
      </div>

      <Renderer question={question} response={response} reviewed={reviewed} result={result} onResponse={onResponse} />

      {mode === "study" && (
        <button type="button" className="study-check" onClick={onReview}>Check this</button>
      )}

      {reviewed && (
        <div className="explanation">
          <p><strong>Score:</strong> {formatScore(result.earned)} / {formatScore(result.possible)}</p>
          <p><strong>Answer:</strong> <RichText content={question.explanation.answer} /></p>
          <p><strong>Why:</strong> <RichText content={question.explanation.why} /></p>
          <p><strong>Boundary:</strong> <RichText content={question.explanation.boundary} /></p>
          {question.explanation.references?.length > 0 && (
            <p><strong>References:</strong> {question.explanation.references.join("; ")}</p>
          )}
        </div>
      )}
    </article>
  );
}

function formatScore(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}
