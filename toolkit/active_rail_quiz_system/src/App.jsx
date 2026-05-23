import { useMemo, useState } from "react";
import { questionBank } from "./data/questionBank.js";
import { claimLabels } from "./data/taxonomy.js";
import { ActivityCard } from "./components/ActivityCard.jsx";
import { ReportPanel } from "./components/ReportPanel.jsx";
import { RichText } from "./components/RichText.jsx";
import { SourceList } from "./components/SourceList.jsx";
import { BoundaryClassificationActivity } from "./renderers/BoundaryClassificationActivity.jsx";
import { MatchingActivity } from "./renderers/MatchingActivity.jsx";
import { SequenceActivity } from "./renderers/SequenceActivity.jsx";
import { StandardChoiceActivity } from "./renderers/StandardChoiceActivity.jsx";
import { SymbolFillActivity } from "./renderers/SymbolFillActivity.jsx";
import { registry } from "./renderers/registry.jsx";
import { buildInitialResponse, shuffle, unique } from "./lib/session.js";

export const workspaceDefs = [
  {
    id: "mixed",
    label: "Mixed Quiz",
    title: "Qualification Drill",
    deck: "Certification readiness across foundations, constraints, architecture, and review.",
    types: null,
    tone: "amber"
  },
  {
    id: "boundary",
    label: "Boundary Board",
    title: "Claim Boundary Board",
    deck: "Epistemic status, claim boundaries, and curriculum governance.",
    types: ["claim_classification"],
    tone: "violet"
  },
  {
    id: "symbols",
    label: "Symbol Lab",
    title: "Symbol and Equation Lab",
    deck: "Notation, source ledgers, and symbol-role interpretation.",
    types: ["drag_fill", "matching"],
    tone: "blue"
  },
  {
    id: "chronology",
    label: "Timeline",
    title: "Service Chronology Timeline",
    deck: "Support, carry, catch, fade, decompression, and reset order.",
    types: ["sequence"],
    tone: "green"
  },
  {
    id: "review",
    label: "Design Review",
    title: "Plant Review Dossier",
    deck: "Evidence packages, missing channels, qualification gates, and review burden.",
    types: ["multi", "mc"],
    modules: ["Failure analysis", "Project-state handling"],
    tone: "red"
  }
];

export const defaultFilters = {
  count: "6",
  tracks: [],
  modules: [],
  difficulties: [],
  claimStatuses: [],
  optionalContent: "stable"
};

export function App({ initialWorkspace = "mixed", initialFilters = defaultFilters } = {}) {
  const [workspace, setWorkspace] = useState(initialWorkspace);
  const [filters, setFilters] = useState(initialFilters);
  const [current, setCurrent] = useState(() => buildWorkspaceQuestions(initialWorkspace, initialFilters));
  const [responses, setResponses] = useState(() => initialResponses(current));
  const [reviewed, setReviewed] = useState(new Set());

  const activeWorkspace = workspaceDefs.find((item) => item.id === workspace) || workspaceDefs[0];
  const options = useMemo(() => ({
    tracks: unique(questionBank.map((q) => q.track)),
    modules: unique(questionBank.map((q) => q.module)),
    difficulties: ["core", "intermediate", "advanced"],
    claimStatuses: unique(questionBank.map((q) => q.claimStatus))
  }), []);
  const workspaceCounts = useMemo(() => {
    return Object.fromEntries(
      workspaceDefs.map((item) => [
        item.id,
        questionBank.filter((question) => matchesWorkspace(question, item)).length
      ])
    );
  }, []);

  const reviewedResults = useMemo(() => {
    return current
      .filter((question) => reviewed.has(question.id))
      .map((question) => ({
        question,
        result: registry[question.type].grade(question, responses[question.id])
      }));
  }, [current, responses, reviewed]);

  function rebuild(nextWorkspace = workspace, nextFilters = filters) {
    const next = buildWorkspaceQuestions(nextWorkspace, nextFilters);
    setCurrent(next);
    setResponses(initialResponses(next));
    setReviewed(new Set());
  }

  function changeWorkspace(nextWorkspace) {
    setWorkspace(nextWorkspace);
    rebuild(nextWorkspace, filters);
  }

  function updateFilter(name, value) {
    const nextFilters = { ...filters, [name]: value };
    setFilters(nextFilters);
    rebuild(workspace, nextFilters);
  }

  function reset() {
    setResponses(initialResponses(current));
    setReviewed(new Set());
  }

  function clearFilters() {
    setFilters(defaultFilters);
    rebuild(workspace, defaultFilters);
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
          <h1>Training Board</h1>
        </div>
        <div className="header-status">
          <span>{questionBank.length} local questions</span>
          <span>{workspaceCounts[workspace] || 0} in lane</span>
        </div>
      </header>

      <main className="training-layout">
        <nav className="workspace-rail" aria-label="Activity workspaces">
          <div className="rail-heading">
            <span>Workspaces</span>
          </div>
          {workspaceDefs.map((item) => (
            <button
              type="button"
              key={item.id}
              className={`workspace-tab ${workspace === item.id ? "active" : ""}`}
              data-tone={item.tone}
              onClick={() => changeWorkspace(item.id)}
            >
              <span className="workspace-tab-label">{item.label}</span>
              <strong>{item.title}</strong>
              <small>{item.deck}</small>
              <span className="workspace-count">{workspaceCounts[item.id] || 0} ready</span>
            </button>
          ))}
        </nav>

        <section className={`workspace-panel ${workspace}-workspace`} data-tone={activeWorkspace.tone} aria-live="polite">
          <WorkspaceHeader
            workspace={activeWorkspace}
            count={current.length}
            onReviewAll={reviewAll}
            onReset={reset}
          />
          <WorkspaceBody
            workspace={workspace}
            workspaceDef={activeWorkspace}
            availableCount={workspaceCounts[workspace] || 0}
            questions={current}
            responses={responses}
            reviewed={reviewed}
            onResponse={updateResponse}
            onReview={reviewOne}
            onClearFilters={clearFilters}
          />
        </section>

        <aside className="side-stack">
          <section className="session-panel" aria-label="Session controls">
            <div className="panel-title-row">
              <h2>Scope</h2>
              <button type="button" className="text-action" onClick={clearFilters}>Default</button>
            </div>
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
          </section>

          <ReportPanel results={reviewedResults} totalQuestions={current.length} />
        </aside>
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
        <button type="button" onClick={onReviewAll} disabled={count === 0}>Check Workspace</button>
        <button type="button" className="secondary-action" onClick={onReset}>Reset</button>
      </div>
    </div>
  );
}

function WorkspaceBody({ workspace, workspaceDef, availableCount, questions, responses, reviewed, onResponse, onReview, onClearFilters }) {
  if (!questions.length) {
    return <EmptyWorkspace workspace={workspaceDef} availableCount={availableCount} onClearFilters={onClearFilters} />;
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

function EmptyWorkspace({ workspace, availableCount, onClearFilters }) {
  const seeded = availableCount > 0;
  return (
    <div className="empty-workspace">
      <div>
        <p className="eyebrow">{seeded ? "Filtered out" : "Curriculum gap"}</p>
        <h3>{seeded ? "No matching items in this scope" : "This workspace is waiting for seed questions"}</h3>
        <p>
          {seeded
            ? "This lane has questions in the local bank, but the current scope excludes them."
            : `${workspace.title} is defined in the interface, but the bank does not contain matching activities yet.`}
        </p>
      </div>
      <button type="button" onClick={onClearFilters}>Reset Scope</button>
    </div>
  );
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
        <p className="muted">Rendered tokens and demanded-source notation.</p>
        {!symbolQuestions.length && <LaneEmpty label="No symbol-fill questions in this scope." />}
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
        <p className="muted">Symbol meanings and operational roles.</p>
        {!matchQuestions.length && <LaneEmpty label="No matching questions in this scope." />}
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

function LaneEmpty({ label }) {
  return <div className="lane-empty">{label}</div>;
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
      <p><strong>Why:</strong> <RichText content={question.explanation.why} /></p>
      <p><strong>Boundary:</strong> <RichText content={question.explanation.boundary} /></p>
      {question.explanation.openGate && (
        <p><strong>Open gate:</strong> <RichText content={question.explanation.openGate} /></p>
      )}
      <SourceList references={question.explanation.references} sourceLinks={question.explanation.sourceLinks} />
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
