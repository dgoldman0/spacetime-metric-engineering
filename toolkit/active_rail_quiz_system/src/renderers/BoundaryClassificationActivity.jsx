import { claimLabels } from "../data/taxonomy.js";
import { RichText } from "../components/RichText.jsx";

export function BoundaryClassificationActivity({ question, response, reviewed, result, onResponse }) {
  const classifications = response?.classifications || {};

  function choose(statementId, status) {
    onResponse({ ...response, classifications: { ...classifications, [statementId]: status } });
  }

  return (
    <div className="boundary-surface">
      <div className="prompt"><RichText content={question.prompt} /></div>
      <div className="boundary-grid">
        {question.statements.map((statement) => {
          const selected = classifications[statement.id];
          const correct = reviewed && result.details?.[statement.id]?.correct;
          const incorrect = reviewed && selected && !correct;
          return (
            <section className={`boundary-row ${correct ? "correct-row" : ""} ${incorrect ? "incorrect-row" : ""}`} key={statement.id}>
              <div className="boundary-statement"><RichText content={statement.content} /></div>
              <div className="boundary-options" role="group" aria-label="Claim status choices">
                {question.statuses.map((status) => (
                  <button
                    type="button"
                    key={status}
                    className={`status-choice ${selected === status ? "selected" : ""} ${status}`}
                    onClick={() => choose(statement.id, status)}
                  >
                    {claimLabels[status] || status}
                  </button>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
