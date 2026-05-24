import { claimLabels, contextLabels, getQuestionContext } from "../data/taxonomy.js";

export function ReportPanel({ results, totalQuestions, sessionSummary }) {
  if (!results.length) {
    return (
      <aside className="report-panel" aria-label="Quiz report">
        <h2>Report</h2>
        {sessionSummary && <SessionSummary summary={sessionSummary} />}
        <p className="muted">Answer questions to see scoring by module, claim status, and activity surface.</p>
      </aside>
    );
  }

  const earned = sum(results.map((item) => item.result.earned));
  const possible = sum(results.map((item) => item.result.possible));
  const exact = results.filter((item) => item.result.correct).length;
  const percent = possible ? Math.round((earned / possible) * 100) : 0;
  const missedModules = unique(results.filter((item) => !item.result.correct).map((item) => item.question.module)).slice(0, 3);

  return (
    <aside className="report-panel" aria-label="Quiz report">
      <h2>Report</h2>
      {sessionSummary && <SessionSummary summary={sessionSummary} />}
      <div className="report-score">
        <div className="score-tile"><span className="score-number">{percent}%</span><span>points</span></div>
        <div className="score-tile"><span className="score-number">{exact}/{results.length}</span><span>exact</span></div>
      </div>
      <p className="muted">Reviewed {results.length} of {totalQuestions} questions.</p>
      <Breakdown title="By module" rows={breakdown(results, (q) => q.module)} />
      <Breakdown title="By claim status" rows={breakdown(results, (q) => claimLabels[q.claimStatus] || q.claimStatus)} />
      <Breakdown title="By context" rows={breakdown(results, (q) => contextLabels[getQuestionContext(q)] || getQuestionContext(q))} />
      <Breakdown title="By activity" rows={breakdown(results, (q) => q.type)} />
      {missedModules.length ? (
        <p><strong>Review next:</strong> {missedModules.join(", ")}</p>
      ) : (
        <p className="muted">No missed reviewed questions yet.</p>
      )}
    </aside>
  );
}

function SessionSummary({ summary }) {
  return (
    <div className="session-summary">
      <div><span>Elapsed</span><strong>{formatTime(summary.elapsed)}</strong></div>
      <div><span>Remaining</span><strong>{formatTime(summary.timeLeft)}</strong></div>
      <div><span>Answered</span><strong>{summary.answered}/{summary.answered + summary.skipped + summary.unanswered}</strong></div>
      {summary.skipped > 0 && <p className="muted">Skipped {summary.skipped} item{summary.skipped === 1 ? "" : "s"}.</p>}
      {summary.ended && <p className="muted">Timed session ended.</p>}
    </div>
  );
}

function Breakdown({ title, rows }) {
  return (
    <>
      <h3>{title}</h3>
      <div className="breakdown">
        {rows.map((row) => {
          const percent = row.possible ? Math.round((row.earned / row.possible) * 100) : 0;
          return (
            <div className="breakdown-row" key={row.label}>
              <span>{row.label}</span>
              <strong>{percent}%</strong>
              <div className="bar"><span style={{ width: `${percent}%` }} /></div>
            </div>
          );
        })}
      </div>
    </>
  );
}

function breakdown(results, labeler) {
  const rows = new Map();
  results.forEach(({ question, result }) => {
    const label = labeler(question);
    if (!rows.has(label)) rows.set(label, { label, earned: 0, possible: 0 });
    const row = rows.get(label);
    row.earned += result.earned;
    row.possible += result.possible;
  });
  return Array.from(rows.values()).sort((a, b) => a.label.localeCompare(b.label));
}

function sum(values) {
  return values.reduce((total, value) => total + value, 0);
}

function unique(values) {
  return Array.from(new Set(values)).sort((a, b) => a.localeCompare(b));
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${minutes}:${String(remainder).padStart(2, "0")}`;
}
