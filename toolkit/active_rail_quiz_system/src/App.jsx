import { useMemo, useState } from "react";
import { questionBank } from "./data/questionBank.js";
import { claimLabels, optionalFlags, typeLabels } from "./data/taxonomy.js";
import { ActivityCard } from "./components/ActivityCard.jsx";
import { ReportPanel } from "./components/ReportPanel.jsx";
import { registry } from "./renderers/registry.jsx";
import { buildInitialResponse, shuffle, unique } from "./lib/session.js";

const defaultFilters = {
  mode: "study",
  count: "6",
  track: "all",
  module: "all",
  difficulty: "all",
  type: "all",
  claimStatus: "all",
  optionalContent: "stable"
};

export function App() {
  const [filters, setFilters] = useState(defaultFilters);
  const [current, setCurrent] = useState(() => buildQuestionSet(defaultFilters));
  const [responses, setResponses] = useState(() => initialResponses(current));
  const [reviewed, setReviewed] = useState(new Set());

  const options = useMemo(() => ({
    tracks: ["all", ...unique(questionBank.map((q) => q.track))],
    modules: ["all", ...unique(questionBank.map((q) => q.module))],
    types: ["all", ...unique(questionBank.map((q) => q.type))],
    claimStatuses: ["all", ...unique(questionBank.map((q) => q.claimStatus))]
  }), []);

  const reviewedResults = useMemo(() => {
    return current
      .filter((question) => reviewed.has(question.id))
      .map((question) => ({
        question,
        result: registry[question.type].grade(question, responses[question.id])
      }));
  }, [current, responses, reviewed]);

  function updateFilter(name, value) {
    setFilters((previous) => ({ ...previous, [name]: value }));
  }

  function rebuild() {
    const next = buildQuestionSet(filters);
    setCurrent(next);
    setResponses(initialResponses(next));
    setReviewed(new Set());
  }

  function reset() {
    setResponses(initialResponses(current));
    setReviewed(new Set());
  }

  function updateResponse(questionId, nextResponse) {
    setResponses((previous) => ({
      ...previous,
      [questionId]: typeof nextResponse === "function" ? nextResponse(previous[questionId]) : nextResponse
    }));
  }

  function reviewOne(questionId) {
    setReviewed((previous) => new Set([...previous, questionId]));
  }

  function reviewAll() {
    setReviewed(new Set(current.map((question) => question.id)));
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Active-Rail Service Engineering</p>
          <h1>Quiz Console</h1>
        </div>
        <div className="header-status">{questionBank.length} local questions loaded</div>
      </header>

      <section className="control-panel" aria-label="Quiz controls">
        <SelectControl label="Mode" value={filters.mode} onChange={(value) => updateFilter("mode", value)} options={[
          ["study", "Study"],
          ["quiz", "Quiz"],
          ["boundary", "Boundary"]
        ]} />
        <SelectControl label="Count" value={filters.count} onChange={(value) => updateFilter("count", value)} options={[
          ["6", "6"],
          ["10", "10"],
          ["all", "All"]
        ]} />
        <SelectControl label="Track" value={filters.track} onChange={(value) => updateFilter("track", value)} options={options.tracks.map((value) => [value, value === "all" ? "All tracks" : value])} />
        <SelectControl label="Module" value={filters.module} onChange={(value) => updateFilter("module", value)} options={options.modules.map((value) => [value, value === "all" ? "All modules" : value])} />
        <SelectControl label="Difficulty" value={filters.difficulty} onChange={(value) => updateFilter("difficulty", value)} options={[
          ["all", "All"],
          ["core", "Core"],
          ["intermediate", "Intermediate"],
          ["advanced", "Advanced"]
        ]} />
        <SelectControl label="Activity" value={filters.type} onChange={(value) => updateFilter("type", value)} options={options.types.map((value) => [value, value === "all" ? "All activities" : typeLabels[value] || value])} />
        <SelectControl label="Claim Status" value={filters.claimStatus} onChange={(value) => updateFilter("claimStatus", value)} options={options.claimStatuses.map((value) => [value, value === "all" ? "All statuses" : claimLabels[value] || value])} />
        <SelectControl label="Optional Content" value={filters.optionalContent} onChange={(value) => updateFilter("optionalContent", value)} options={[
          ["stable", "Stable only"],
          ["include", "Include flagged"],
          ["flagged", "Flagged only"]
        ]} />
        <button type="button" className="primary-action" onClick={rebuild}>Build Quiz</button>
      </section>

      <main className="workspace">
        <section className="quiz-panel" aria-live="polite">
          <div className="toolbar">
            <div>
              <h2>{modeTitle(filters.mode)}</h2>
              <p>{current.length} question{current.length === 1 ? "" : "s"} ready</p>
            </div>
            <div className="toolbar-actions">
              <button type="button" onClick={reviewAll}>Check Answers</button>
              <button type="button" className="secondary-action" onClick={reset}>Reset</button>
            </div>
          </div>

          <div className="activity-stack">
            {current.length === 0 ? (
              <p className="muted">No questions match those filters.</p>
            ) : current.map((question, index) => (
              <ActivityCard
                key={question.id}
                question={question}
                index={index}
                response={responses[question.id]}
                reviewed={reviewed.has(question.id)}
                mode={filters.mode}
                onResponse={(nextResponse) => updateResponse(question.id, nextResponse)}
                onReview={() => reviewOne(question.id)}
              />
            ))}
          </div>
        </section>

        <ReportPanel results={reviewedResults} totalQuestions={current.length} />
      </main>
    </div>
  );
}

function SelectControl({ label, value, onChange, options }) {
  return (
    <label>
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map(([optionValue, optionLabel]) => (
          <option key={optionValue} value={optionValue}>{optionLabel}</option>
        ))}
      </select>
    </label>
  );
}

function buildQuestionSet(filters) {
  const pool = questionBank.filter((question) => matchesFilters(question, filters));
  const count = filters.count === "all" ? pool.length : Number(filters.count);
  const modePool = filters.mode === "boundary"
    ? pool.filter((question) => question.type === "claim_classification" || question.claimStatus !== "established_theory")
    : pool;
  return shuffle(modePool).slice(0, count);
}

function matchesFilters(question, filters) {
  const flags = question.contentFlags || [];
  const hasOptional = flags.some((flag) => optionalFlags.includes(flag));
  if (filters.optionalContent === "stable" && hasOptional) return false;
  if (filters.optionalContent === "flagged" && !hasOptional) return false;
  return (filters.track === "all" || question.track === filters.track)
    && (filters.module === "all" || question.module === filters.module)
    && (filters.difficulty === "all" || question.difficulty === filters.difficulty)
    && (filters.type === "all" || question.type === filters.type)
    && (filters.claimStatus === "all" || question.claimStatus === filters.claimStatus);
}

function initialResponses(questions) {
  return Object.fromEntries(questions.map((question) => [question.id, buildInitialResponse(question)]));
}

function modeTitle(mode) {
  if (mode === "boundary") return "Boundary Set";
  if (mode === "quiz") return "Quiz Set";
  return "Study Set";
}
