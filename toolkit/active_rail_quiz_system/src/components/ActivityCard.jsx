import { claimLabels, contextLabels, getQuestionContext, typeLabels } from "../data/taxonomy.js";
import { ExplanationPanel } from "./ExplanationPanel.jsx";
import { registry } from "../renderers/registry.jsx";

export function ActivityCard({ question, index, response, reviewed, lockedResult, mode, showExplanation = true, onResponse, onReview }) {
  const entry = registry[question.type];
  const Renderer = entry.Component;
  const result = reviewed ? lockedResult ?? entry.grade(question, response) : null;
  const resultClass = result ? (result.correct ? "correct" : result.earned > 0 ? "partial" : "incorrect") : "";
  const context = getQuestionContext(question);

  return (
    <article className={`question-card ${reviewed ? "reviewed" : ""} ${resultClass}`}>
      <div className="question-head">
        <div>
          <div className="question-kicker">Question {index + 1} / {typeLabels[question.type] || question.type}</div>
          <h3>{question.module}</h3>
        </div>
        <div className="badges">
          <span className={`badge context-${context}`}>{contextLabels[context] || context}</span>
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

      {reviewed && showExplanation && <ExplanationPanel question={question} response={response} result={result} />}
    </article>
  );
}
