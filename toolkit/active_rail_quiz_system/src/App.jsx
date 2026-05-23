import { useEffect, useMemo, useState } from "react";
import { questionBank } from "./data/questionBank.js";
import { claimLabels } from "./data/taxonomy.js";
import { ActivityCard } from "./components/ActivityCard.jsx";
import { ReportPanel } from "./components/ReportPanel.jsx";
import { RichText } from "./components/RichText.jsx";
import { BoundaryClassificationActivity } from "./renderers/BoundaryClassificationActivity.jsx";
import { MatchingActivity } from "./renderers/MatchingActivity.jsx";
import { SequenceActivity } from "./renderers/SequenceActivity.jsx";
import { StandardChoiceActivity } from "./renderers/StandardChoiceActivity.jsx";
import { SymbolFillActivity } from "./renderers/SymbolFillActivity.jsx";
import { registry } from "./renderers/registry.jsx";
import { buildInitialResponse, shuffle, unique } from "./lib/session.js";

const workspaceDefs = [
  {
    id: "mixed",
    label: "Mixed Quiz",
    title: "Qualification Drill",
    deck: "A compact exam bench for ordinary questions, explanations, and module scoring.",
    types: null
  },
  {
    id: "boundary",
    label: "Boundary Board",
    title: "Claim Boundary Board",
    deck: "Sort statements by epistemic status so project vocabulary cannot masquerade as established theory.",
    types: ["claim_classification"]
  },
  {
    id: "symbols",
    label: "Symbol Lab",
    title: "Symbol And Equation Lab",
    deck: "Use rendered math tokens and symbol-role matching without typing LaTeX.",
    types: ["drag_fill", "matching"]
  },
  {
    id: "chronology",
    label: "Timeline",
    title: "Service Chronology Timeline",
    deck: "Work directly with support, carry, catch, fade, decompression, and reset order.",
    types: ["sequence"]
  },
  {
    id: "review",
    label: "Design Review",
    title: "Plant Review Dossier",
    deck: "Inspect a service case and decide what evidence is missing before qualification.",
    types: ["multi", "mc"],
    modules: ["Failure analysis", "Project-state handling"]
  }
];

const defaultFilters = {
  count: "6",
  tracks: [],
  modules: [],
  difficulties: [],
  claimStatuses: [],
  optionalContent: "stable"
};

export function App() {
  const [workspace, setWorkspace] = useState("mixed");
  const [filters, setFilters] = useState(defaultFilters);
  const [current, setCurrent] = useState(() => buildWorkspaceQuestions("mixed", defaultFilters));
  const [responses, setResponses] = useState(() => initialResponses(current));
  const [reviewed, setReviewed] = useState(new Set());

  const activeWorkspace = workspaceDefs.find((item) => item.id === workspace) || workspaceDefs[0];
  const options = useMemo(() => ({
    tracks: unique(questionBank.map((q) => q.track)),
    modules: unique(questionBank.map((q) => q.module)),
    difficulties: ["core", "intermediate", "advanced"],
    claimStatuses: unique(questionBank.map((q) => q.claimStatus))
  }), []);

  const reviewedResults = useMemo(() => {
    return current
      .filter((question) => reviewed.has(question.id))
      .map((question) => ({
        question,
        result: registry[question.type].grade(question, responses[question.id])
      }));
  }, [current, responses, reviewed]);

  useEffect(() => {
    rebuild(workspace, filters);
  }, [workspace, filters]);

  function rebuild(nextWorkspace = workspace, nextFilters = filters) {
    const next = buildWorkspaceQuestions(nextWorkspace, nextFilters);
    setCurrent(next);
    setResponses(initialResponses(next));
    setReviewed(new Set());
  }

  function updateFilter(name, value) {
    setFilters((previous) => ({ ...previous, [name]: value }));
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
          <h1>Engineering Board</h1>
        </div>
        <div className="header-status">{questionBank.length} local questions loaded</div>
      </header>

      <section className="workspace-launcher" aria-label="Activity workspaces">
        {workspaceDefs.map((item) => (
          <button
            type="button"
            key={item.id}
            className={`workspace-card ${workspace === item.id ? "active" : ""}`}
            onClick={() => setWorkspace(item.id)}
          >
            <span>{item.label}</span>
            <strong>{item.title}</strong>
            <small>{item.deck}</small>
          </button>
        ))}
      </section>

      <main className="board-layout">
        <aside className="session-panel" aria-label="Session controls">
          <h2>Session</h2>
          <p className="muted">Controls are intentionally secondary. Pick the workspace first; then narrow the content.</p>
          <div className="session-controls">
            <SelectControl label="Count" value={filters.count} onChange={(value) => updateFilter("count", value)} options={[
              ["6", "6"],
              ["10", "10"],
              ["all", "All"]
            ]} />
            <MultiFacet label="Tracks" values={filters.tracks} options={options.tracks.map((value) => [value, value])} emptyLabel="All tracks" onChange={(value) => updateFilter("tracks", value)} />
            <MultiFacet label="Modules" values={filters.modules} options={options.modules.map((value) => [value, value])} emptyLabel="All modules" onChange={(value) => updateFilter("modules", value)} />
            <MultiFacet label="Difficulty" values={filters.difficulties} options={options.difficulties.map((value) => [value, titleCase(value)])} emptyLabel="All levels" onChange={(value) => updateFilter("difficulties", value)} />
            <MultiFacet label="Claim Status" values={filters.claimStatuses} options={options.claimStatuses.map((value) => [value, claimLabels[value] || value])} emptyLabel="All statuses" onChange={(value) => updateFilter("claimStatuses", value)} />
            <SelectControl label="Optional Content" value={filters.optionalContent} onChange={(value) => updateFilter("optionalContent", value)} options={[
              ["stable", "Stable only"],
              ["include", "Include flagged"],
              ["flagged", "Flagged only"]
            ]} />
          </div>
        </aside>

        <section className={`workspace-panel ${workspace}-workspace`} aria-live="polite">
          <WorkspaceHeader
            workspace={activeWorkspace}
            count={current.length}
            onReviewAll={reviewAll}
            onReset={reset}
          />
          <WorkspaceBody
            workspace={workspace}
            questions={current}
            responses={responses}
            reviewed={reviewed}
            onResponse={updateResponse}
            onReview={reviewOne}
          />
        </section>

        <ReportPanel results={reviewedResults} totalQuestions={current.length} />
      </main>
    </div>
  );
}

function WorkspaceHeader({ workspace, count, onReviewAll, onReset }) {
  return (
    <div className="workspace-header">
      <div>
        <p className="eyebrow">{workspace.label}</p>
        <h2>{workspace.title}</h2>
        <p>{workspace.deck}</p>
      </div>
      <div className="toolbar-actions">
        <span className="question-count">{count} item{count === 1 ? "" : "s"}</span>
        <button type="button" onClick={onReviewAll}>Check Workspace</button>
        <button type="button" className="secondary-action" onClick={onReset}>Reset</button>
      </div>
    </div>
  );
}

function WorkspaceBody({ workspace, questions, responses, reviewed, onResponse, onReview }) {
  if (!questions.length) {
    return <div className="empty-workspace">No questions match this workspace and filter combination.</div>;
  }

  if (workspace === "boundary") {
    return <BoundaryWorkspace questions={questions} responses={responses} reviewed={reviewed} onResponse={onResponse} onReview={onReview} />;
  }
  if (workspace === "symbols") {
    return <SymbolWorkspace questions={questions} responses={responses} reviewed={reviewed} onResponse={onResponse} onReview={onReview} />;
  }
  if (workspace === "chronology") {
    return <ChronologyWorkspace questions={questions} responses={responses} reviewed={reviewed} onResponse={onResponse} onReview={onReview} />;
  }
  if (workspace === "review") {
    return <DesignReviewWorkspace questions={questions} responses={responses} reviewed={reviewed} onResponse={onResponse} onReview={onReview} />;
  }
  return <MixedWorkspace questions={questions} responses={responses} reviewed={reviewed} onResponse={onResponse} onReview={onReview} />;
}

function MixedWorkspace({ questions, responses, reviewed, onResponse, onReview }) {
  return (
    <div className="mixed-sheet">
      {questions.map((question, index) => (
        <ActivityCard
          key={question.id}
          question={question}
          index={index}
          response={responses[question.id]}
          reviewed={reviewed.has(question.id)}
          mode="study"
          onResponse={(nextResponse) => onResponse(question.id, nextResponse)}
          onReview={() => onReview(question.id)}
        />
      ))}
    </div>
  );
}

function BoundaryWorkspace({ questions, responses, reviewed, onResponse, onReview }) {
  return (
    <div className="boundary-board">
      {questions.map((question) => {
        const result = reviewed.has(question.id) ? registry[question.type].grade(question, responses[question.id]) : null;
        return (
          <section className="board-tool" key={question.id}>
            <div className="tool-head">
              <div>
                <h3>{question.module}</h3>
                <p>Every row is a claim. The task is classification, not trivia.</p>
              </div>
              <button type="button" onClick={() => onReview(question.id)}>Check Board</button>
            </div>
            <BoundaryClassificationActivity
              question={question}
              response={responses[question.id]}
              reviewed={reviewed.has(question.id)}
              result={result}
              onResponse={(nextResponse) => onResponse(question.id, nextResponse)}
            />
            {result && <InlineExplanation question={question} result={result} />}
          </section>
        );
      })}
    </div>
  );
}

function SymbolWorkspace({ questions, responses, reviewed, onResponse, onReview }) {
  const symbolQuestions = questions.filter((question) => question.type === "drag_fill");
  const matchQuestions = questions.filter((question) => question.type === "matching");
  return (
    <div className="symbol-lab-grid">
      <section className="lab-bench">
        <h3>Equation Bench</h3>
        <p className="muted">Rendered tokens are moved into blanks. The learner sees math, not raw LaTeX.</p>
        {symbolQuestions.map((question) => {
          const result = reviewed.has(question.id) ? registry[question.type].grade(question, responses[question.id]) : null;
          return (
            <div className="lab-exercise" key={question.id}>
              <SymbolFillActivity
                question={question}
                response={responses[question.id]}
                reviewed={reviewed.has(question.id)}
                result={result}
                onResponse={(nextResponse) => onResponse(question.id, nextResponse)}
              />
              <button type="button" onClick={() => onReview(question.id)}>Check Symbol</button>
              {result && <InlineExplanation question={question} result={result} />}
            </div>
          );
        })}
      </section>
      <section className="lab-bench secondary-bench">
        <h3>Symbol Roles</h3>
        <p className="muted">Pair rendered symbols with their operational meaning.</p>
        {matchQuestions.map((question) => {
          const result = reviewed.has(question.id) ? registry[question.type].grade(question, responses[question.id]) : null;
          return (
            <div className="lab-exercise" key={question.id}>
              <MatchingActivity
                question={question}
                response={responses[question.id]}
                reviewed={reviewed.has(question.id)}
                result={result}
                onResponse={(nextResponse) => onResponse(question.id, nextResponse)}
              />
              <button type="button" onClick={() => onReview(question.id)}>Check Matches</button>
              {result && <InlineExplanation question={question} result={result} />}
            </div>
          );
        })}
      </section>
    </div>
  );
}

function ChronologyWorkspace({ questions, responses, reviewed, onResponse, onReview }) {
  return (
    <div className="timeline-deck">
      <div className="timeline-ruler">
        <span>Support</span>
        <span>Carry</span>
        <span>Catch</span>
        <span>Fade</span>
        <span>Decompress</span>
        <span>Reset</span>
      </div>
      {questions.map((question) => {
        const result = reviewed.has(question.id) ? registry[question.type].grade(question, responses[question.id]) : null;
        return (
          <section className="timeline-tool" key={question.id}>
            <SequenceActivity
              question={question}
              response={responses[question.id]}
              reviewed={reviewed.has(question.id)}
              result={result}
              onResponse={(nextResponse) => onResponse(question.id, nextResponse)}
            />
            <button type="button" onClick={() => onReview(question.id)}>Check Timeline</button>
            {result && <InlineExplanation question={question} result={result} />}
          </section>
        );
      })}
    </div>
  );
}

function DesignReviewWorkspace({ questions, responses, reviewed, onResponse, onReview }) {
  return (
    <div className="dossier-grid">
      <section className="dossier-artifacts">
        <h3>Service Case File</h3>
        <div className="artifact-strip">
          <div><strong>Packet trace</strong><span>arrival clean</span></div>
          <div><strong>Plant report</strong><span>channels omitted</span></div>
          <div><strong>Reset status</strong><span>not evidenced</span></div>
        </div>
        <p>The review surface asks whether the evidence package is sufficient, not whether the story sounds successful.</p>
      </section>
      <section className="decision-panel">
        <h3>Review Decision</h3>
        {questions.map((question) => {
          const result = reviewed.has(question.id) ? registry[question.type].grade(question, responses[question.id]) : null;
          return (
            <div className="dossier-question" key={question.id}>
              <StandardChoiceActivity
                question={question}
                response={responses[question.id]}
                reviewed={reviewed.has(question.id)}
                result={result}
                onResponse={(nextResponse) => onResponse(question.id, nextResponse)}
              />
              <button type="button" onClick={() => onReview(question.id)}>Submit Review</button>
              {result && <InlineExplanation question={question} result={result} />}
            </div>
          );
        })}
      </section>
    </div>
  );
}

function InlineExplanation({ question, result }) {
  return (
    <div className="inline-explanation">
      <p><strong>Score:</strong> {result.earned} / {result.possible}</p>
      <p><strong>Answer:</strong> <RichText content={question.explanation.answer} /></p>
      <p><strong>Boundary:</strong> <RichText content={question.explanation.boundary} /></p>
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

function MultiFacet({ label, values, options, emptyLabel, onChange }) {
  function toggle(optionValue) {
    const next = values.includes(optionValue)
      ? values.filter((value) => value !== optionValue)
      : [...values, optionValue];
    onChange(next);
  }

  return (
    <fieldset className="multi-facet">
      <legend>{label}</legend>
      <div className="facet-summary">{values.length ? `${values.length} selected` : emptyLabel}</div>
      <div className="facet-options">
        {options.map(([optionValue, optionLabel]) => (
          <label className={`facet-chip ${values.includes(optionValue) ? "selected" : ""}`} key={optionValue}>
            <input
              type="checkbox"
              checked={values.includes(optionValue)}
              onChange={() => toggle(optionValue)}
            />
            <span>{optionLabel}</span>
          </label>
        ))}
      </div>
      {values.length > 0 && (
        <button type="button" className="facet-clear" onClick={() => onChange([])}>Clear</button>
      )}
    </fieldset>
  );
}

function buildWorkspaceQuestions(workspaceId, filters) {
  const workspace = workspaceDefs.find((item) => item.id === workspaceId) || workspaceDefs[0];
  const pool = questionBank.filter((question) => matchesWorkspace(question, workspace) && matchesFilters(question, filters));
  const count = filters.count === "all" || workspaceId !== "mixed" ? pool.length : Number(filters.count);
  return shuffle(pool).slice(0, count);
}

function matchesWorkspace(question, workspace) {
  const typeMatch = !workspace.types || workspace.types.includes(question.type);
  const moduleMatch = !workspace.modules || workspace.modules.includes(question.module);
  return typeMatch && moduleMatch;
}

function matchesFilters(question, filters) {
  const flags = question.contentFlags || [];
  const hasOptional = flags.length > 0;
  if (filters.optionalContent === "stable" && hasOptional) return false;
  if (filters.optionalContent === "flagged" && !hasOptional) return false;
  return facetIncludes(filters.tracks, question.track)
    && facetIncludes(filters.modules, question.module)
    && facetIncludes(filters.difficulties, question.difficulty)
    && facetIncludes(filters.claimStatuses, question.claimStatus);
}

function initialResponses(questions) {
  return Object.fromEntries(questions.map((question) => [question.id, buildInitialResponse(question)]));
}

function facetIncludes(values, candidate) {
  return values.length === 0 || values.includes(candidate);
}

function titleCase(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}
