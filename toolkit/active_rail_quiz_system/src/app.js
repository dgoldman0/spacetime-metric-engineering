(function () {
  const bank = Array.isArray(window.ACTIVE_RAIL_QUESTION_BANK) ? window.ACTIVE_RAIL_QUESTION_BANK : [];
  const optionalFlags = ["project_material", "project_state", "open_question", "revision_sensitive"];
  const claimLabels = {
    established_theory: "Established theory",
    established_constraint: "Established constraint",
    literature_model: "Literature model",
    active_rail_model: "Active-rail model",
    project_hypothesis: "Project hypothesis",
    open_gate: "Open gate",
    fictional_frame: "Fictional frame"
  };
  const typeLabels = {
    mc: "Multiple choice",
    multi: "Select all",
    tf: "True/false",
    drag_fill: "Drag-fill",
    sequence: "Sequencing",
    matching: "Matching"
  };

  const state = {
    current: [],
    responses: {},
    reviewed: new Set(),
    selectedToken: null
  };

  const $ = (selector) => document.querySelector(selector);

  function init() {
    $("#bankStatus").textContent = `${bank.length} sample questions loaded`;
    populateFilters();
    bindEvents();
    buildQuiz();
  }

  function populateFilters() {
    fillSelect($("#track"), ["all", ...unique(bank.map((q) => q.track))], "All tracks");
    fillSelect($("#module"), ["all", ...unique(bank.map((q) => q.module))], "All modules");
    fillSelect($("#type"), ["all", ...unique(bank.map((q) => q.type))], "All types", typeLabels);
    fillSelect($("#claimStatus"), ["all", ...unique(bank.map((q) => q.claim_status))], "All statuses", claimLabels);
  }

  function fillSelect(select, values, allLabel, labels) {
    select.innerHTML = "";
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value === "all" ? allLabel : (labels && labels[value]) || value;
      select.appendChild(option);
    });
  }

  function bindEvents() {
    $("#buildQuiz").addEventListener("click", buildQuiz);
    $("#submitQuiz").addEventListener("click", () => reviewAll());
    $("#resetAnswers").addEventListener("click", resetAnswers);
    $("#mode").addEventListener("change", buildQuiz);

    $("#quiz").addEventListener("click", (event) => {
      const token = event.target.closest("[data-token-id]");
      const blank = event.target.closest("[data-blank-id]");
      const checkOne = event.target.closest("[data-check-one]");
      const sequenceMove = event.target.closest("[data-sequence-move]");

      if (token) {
        selectToken(token);
      }
      if (blank) {
        placeSelectedToken(blank);
      }
      if (checkOne) {
        reviewOne(checkOne.dataset.checkOne);
      }
      if (sequenceMove) {
        moveSequenceItem(sequenceMove.dataset.qid, Number(sequenceMove.dataset.index), sequenceMove.dataset.sequenceMove);
      }
    });

    $("#quiz").addEventListener("dragstart", (event) => {
      const token = event.target.closest("[data-token-id]");
      if (!token) return;
      event.dataTransfer.setData("text/plain", JSON.stringify({ qid: token.dataset.qid, tokenId: token.dataset.tokenId }));
    });

    $("#quiz").addEventListener("dragover", (event) => {
      if (event.target.closest("[data-blank-id]")) {
        event.preventDefault();
      }
    });

    $("#quiz").addEventListener("drop", (event) => {
      const blank = event.target.closest("[data-blank-id]");
      if (!blank) return;
      event.preventDefault();
      try {
        const payload = JSON.parse(event.dataTransfer.getData("text/plain"));
        if (payload.qid === blank.dataset.qid) {
          placeToken(blank.dataset.qid, blank.dataset.blankId, payload.tokenId);
        }
      } catch (error) {
        return;
      }
    });

    $("#quiz").addEventListener("change", (event) => {
      const choice = event.target.closest("[data-choice-qid]");
      if (choice) {
        updateChoiceResponse(choice.dataset.choiceQid);
      }

      const select = event.target.closest("[data-match-prompt]");
      if (select) {
        const qid = select.dataset.qid;
        ensureResponse(qid);
        state.responses[qid].matches[select.dataset.matchPrompt] = select.value;
      }
    });
  }

  function buildQuiz() {
    const pool = filteredBank();
    const count = $("#count").value;
    const mode = $("#mode").value;
    const selected = shuffle(pool).slice(0, count === "all" ? pool.length : Number(count));

    state.current = mode === "boundary" ? selected.filter((q) => q.module === "Claim classification" || q.claim_status !== "established_theory") : selected;
    state.responses = {};
    state.reviewed = new Set();
    state.selectedToken = null;

    state.current.forEach((q) => {
      if (q.type === "sequence") {
        ensureResponse(q.id);
        state.responses[q.id].sequence = shuffle(q.items.map((item) => item.id));
      }
    });

    renderQuiz();
    renderEmptyReport();
  }

  function filteredBank() {
    const track = $("#track").value;
    const module = $("#module").value;
    const difficulty = $("#difficulty").value;
    const type = $("#type").value;
    const claimStatus = $("#claimStatus").value;
    const optionalMode = $("#optionalContent").value;

    return bank.filter((q) => {
      const flags = q.content_flags || [];
      const hasOptional = flags.some((flag) => optionalFlags.includes(flag));
      if (optionalMode === "stable" && hasOptional) return false;
      if (optionalMode === "flagged" && !hasOptional) return false;
      return (track === "all" || q.track === track)
        && (module === "all" || q.module === module)
        && (difficulty === "all" || q.difficulty === difficulty)
        && (type === "all" || q.type === type)
        && (claimStatus === "all" || q.claim_status === claimStatus);
    });
  }

  function renderQuiz() {
    const quiz = $("#quiz");
    $("#quizTitle").textContent = $("#mode").selectedOptions[0].textContent + " Set";
    $("#quizMeta").textContent = `${state.current.length} question${state.current.length === 1 ? "" : "s"} ready`;

    if (!state.current.length) {
      quiz.innerHTML = `<p class="muted">No questions match those filters.</p>`;
      return;
    }

    quiz.innerHTML = state.current.map((q, index) => renderQuestion(q, index)).join("");
  }

  function renderQuestion(q, index) {
    const reviewed = state.reviewed.has(q.id);
    const result = reviewed ? evaluate(q) : null;
    const classes = ["question-card"];
    if (reviewed) {
      classes.push("reviewed");
      classes.push(resultClass(result));
    }

    return `
      <article class="${classes.join(" ")}" id="card-${escapeAttr(q.id)}">
        <div class="question-head">
          <div>
            <div class="question-kicker">Question ${index + 1} / ${typeLabels[q.type] || q.type}</div>
            <h3>${escapeHtml(q.module)}</h3>
          </div>
          <div class="badges">${renderBadges(q)}</div>
        </div>
        <div class="prompt">${renderPrompt(q)}</div>
        ${renderBody(q)}
        ${$("#mode").value === "study" ? `<button type="button" class="study-check" data-check-one="${escapeAttr(q.id)}">Check this</button>` : ""}
        ${renderExplanation(q, result)}
      </article>
    `;
  }

  function renderBadges(q) {
    const flags = q.content_flags || [];
    const status = `<span class="badge ${escapeAttr(q.claim_status)}">${escapeHtml(claimLabels[q.claim_status] || q.claim_status)}</span>`;
    const difficulty = `<span class="badge">${escapeHtml(q.difficulty)}</span>`;
    const flagBadges = flags.map((flag) => `<span class="badge ${escapeAttr(flag)}">${escapeHtml(flag.replaceAll("_", " "))}</span>`);
    return [status, difficulty, ...flagBadges].join("");
  }

  function renderPrompt(q) {
    if (q.type !== "drag_fill") return escapeHtml(q.prompt);
    return escapeHtml(q.prompt).replace(/\{([^}]+)\}/g, (_match, blankId) => renderBlank(q, blankId));
  }

  function renderBody(q) {
    if (q.type === "mc" || q.type === "multi" || q.type === "tf") return renderOptions(q);
    if (q.type === "drag_fill") return renderDragFill(q);
    if (q.type === "sequence") return renderSequence(q);
    if (q.type === "matching") return renderMatching(q);
    return `<p class="muted">Unsupported question type: ${escapeHtml(q.type)}</p>`;
  }

  function renderOptions(q) {
    const inputType = q.type === "multi" ? "checkbox" : "radio";
    const response = ensureResponse(q.id).choices;
    return `
      <div class="options">
        ${q.choices.map((choice) => `
          <label class="option">
            <input type="${inputType}" name="${escapeAttr(q.id)}" value="${escapeAttr(choice.id)}" data-choice-qid="${escapeAttr(q.id)}" ${response.includes(choice.id) ? "checked" : ""}>
            <span>${escapeHtml(choice.text)}</span>
          </label>
        `).join("")}
      </div>
    `;
  }

  function renderDragFill(q) {
    return `
      <div class="token-bank" aria-label="Word bank">
        ${q.tokens.map((token) => `
          <button type="button" class="token ${token.render_kind === "math" ? "mathish" : ""}" draggable="true" data-qid="${escapeAttr(q.id)}" data-token-id="${escapeAttr(token.id)}">
            ${escapeHtml(token.text)}
          </button>
        `).join("")}
      </div>
      <p class="muted">Drag a token into a blank, or click a token and then click a blank.</p>
    `;
  }

  function renderBlank(q, blankId) {
    const response = state.responses[q.id] && state.responses[q.id].blanks && state.responses[q.id].blanks[blankId];
    const token = response ? q.tokens.find((item) => item.id === response) : null;
    const label = token ? token.text : "blank";
    return `<button type="button" class="blank ${token ? "filled" : ""} ${token && token.render_kind === "math" ? "mathish" : ""}" data-qid="${escapeAttr(q.id)}" data-blank-id="${escapeAttr(blankId)}">${escapeHtml(label)}</button>`;
  }

  function renderSequence(q) {
    return `<ol class="sequence-list" data-sequence-list="${escapeAttr(q.id)}">${renderSequenceItems(q)}</ol>`;
  }

  function renderSequenceItems(q) {
    const order = sequenceOrder(q);
    return order.map((itemId, index) => {
      const item = q.items.find((candidate) => candidate.id === itemId);
      return `
        <li class="sequence-item">
          <span class="sequence-index">${index + 1}</span>
          <span>${escapeHtml(item.text)}</span>
          <button type="button" class="mini-button" data-qid="${escapeAttr(q.id)}" data-index="${index}" data-sequence-move="up">Up</button>
          <button type="button" class="mini-button" data-qid="${escapeAttr(q.id)}" data-index="${index}" data-sequence-move="down">Down</button>
        </li>
      `;
    }).join("");
  }

  function renderMatching(q) {
    const response = ensureResponse(q.id).matches;
    return `
      <div class="matching-grid">
        ${q.prompts.map((prompt) => `
          <div class="matching-row">
            <div class="matching-prompt">${escapeHtml(prompt.text)}</div>
            <select data-qid="${escapeAttr(q.id)}" data-match-prompt="${escapeAttr(prompt.id)}">
              <option value="">Choose status</option>
              ${q.options.map((option) => `<option value="${escapeAttr(option.id)}" ${response[prompt.id] === option.id ? "selected" : ""}>${escapeHtml(option.text)}</option>`).join("")}
            </select>
          </div>
        `).join("")}
      </div>
    `;
  }

  function renderExplanation(q, result) {
    const scoreLine = result ? `<p><strong>Score:</strong> ${formatScore(result.earned)} / ${formatScore(result.possible)}</p>` : "";
    return `
      <div class="explanation">
        ${scoreLine}
        <p><strong>Answer:</strong> ${escapeHtml(q.explanation.answer)}</p>
        <p><strong>Why:</strong> ${escapeHtml(q.explanation.why)}</p>
        <p><strong>Boundary:</strong> ${escapeHtml(q.explanation.boundary)}</p>
        ${q.explanation.references && q.explanation.references.length ? `<p><strong>References:</strong> ${escapeHtml(q.explanation.references.join("; "))}</p>` : ""}
      </div>
    `;
  }

  function selectToken(token) {
    state.selectedToken = { qid: token.dataset.qid, tokenId: token.dataset.tokenId };
    document.querySelectorAll(".token.selected").forEach((item) => item.classList.remove("selected"));
    token.classList.add("selected");
  }

  function placeSelectedToken(blank) {
    if (!state.selectedToken || state.selectedToken.qid !== blank.dataset.qid) return;
    placeToken(blank.dataset.qid, blank.dataset.blankId, state.selectedToken.tokenId);
  }

  function placeToken(qid, blankId, tokenId) {
    ensureResponse(qid).blanks[blankId] = tokenId;
    const card = $(`#card-${cssEscape(qid)}`);
    const q = state.current.find((item) => item.id === qid);
    if (!card || !q) return;
    card.querySelector(".prompt").innerHTML = renderPrompt(q);
  }

  function moveSequenceItem(qid, index, direction) {
    const q = state.current.find((item) => item.id === qid);
    const order = sequenceOrder(q);
    const target = direction === "up" ? index - 1 : index + 1;
    if (target < 0 || target >= order.length) return;
    [order[index], order[target]] = [order[target], order[index]];
    state.responses[qid].sequence = order;
    const list = document.querySelector(`[data-sequence-list="${cssEscape(qid)}"]`);
    if (list) list.innerHTML = renderSequenceItems(q);
  }

  function sequenceOrder(q) {
    const response = ensureResponse(q.id);
    if (!response.sequence.length) response.sequence = q.items.map((item) => item.id);
    return response.sequence;
  }

  function ensureResponse(qid) {
    if (!state.responses[qid]) {
      state.responses[qid] = { blanks: {}, sequence: [], matches: {}, choices: [] };
    }
    return state.responses[qid];
  }

  function updateChoiceResponse(qid) {
    const response = ensureResponse(qid);
    response.choices = Array.from(document.querySelectorAll(`input[data-choice-qid="${cssEscape(qid)}"]:checked`)).map((input) => input.value);
  }

  function reviewOne(qid) {
    const q = state.current.find((item) => item.id === qid);
    if (!q) return;
    state.reviewed.add(qid);
    const card = $(`#card-${cssEscape(qid)}`);
    if (card) {
      const index = state.current.findIndex((item) => item.id === qid);
      card.outerHTML = renderQuestion(q, index);
    }
    renderReport();
  }

  function reviewAll() {
    state.current.forEach((q) => state.reviewed.add(q.id));
    renderQuiz();
    renderReport();
  }

  function resetAnswers() {
    state.responses = {};
    state.reviewed = new Set();
    state.selectedToken = null;
    state.current.forEach((q) => {
      if (q.type === "sequence") {
        ensureResponse(q.id);
        state.responses[q.id].sequence = shuffle(q.items.map((item) => item.id));
      }
    });
    renderQuiz();
    renderEmptyReport();
  }

  function evaluate(q) {
    if (q.type === "mc" || q.type === "tf" || q.type === "multi") return evaluateChoice(q);
    if (q.type === "drag_fill") return evaluateDragFill(q);
    if (q.type === "sequence") return evaluateSequence(q);
    if (q.type === "matching") return evaluateMatching(q);
    return { earned: 0, possible: 1, correct: false };
  }

  function evaluateChoice(q) {
    updateChoiceResponse(q.id);
    const selected = [...ensureResponse(q.id).choices].sort();
    const answer = [...q.answer].sort();
    const correct = arraysEqual(selected, answer);
    return { earned: correct ? 1 : 0, possible: 1, correct };
  }

  function evaluateDragFill(q) {
    const response = ensureResponse(q.id).blanks;
    let earned = 0;
    q.blanks.forEach((blank) => {
      if (blank.accepts.includes(response[blank.id])) earned += 1;
    });
    return { earned, possible: q.blanks.length, correct: earned === q.blanks.length };
  }

  function evaluateSequence(q) {
    const order = sequenceOrder(q);
    let earned = 0;
    q.answer.forEach((itemId, index) => {
      if (order[index] === itemId) earned += 1;
    });
    return { earned, possible: q.answer.length, correct: earned === q.answer.length };
  }

  function evaluateMatching(q) {
    const matches = ensureResponse(q.id).matches;
    let earned = 0;
    q.prompts.forEach((prompt) => {
      if (matches[prompt.id] === q.answer[prompt.id]) earned += 1;
    });
    return { earned, possible: q.prompts.length, correct: earned === q.prompts.length };
  }

  function renderEmptyReport() {
    $("#report").innerHTML = `<p class="muted">Answer questions to see scoring by module and claim status.</p>`;
  }

  function renderReport() {
    const reviewedQuestions = state.current.filter((q) => state.reviewed.has(q.id));
    if (!reviewedQuestions.length) {
      renderEmptyReport();
      return;
    }

    const results = reviewedQuestions.map((q) => ({ q, result: evaluate(q) }));
    const earned = sum(results.map((item) => item.result.earned));
    const possible = sum(results.map((item) => item.result.possible));
    const exact = results.filter((item) => item.result.correct).length;
    const percent = possible ? Math.round((earned / possible) * 100) : 0;

    $("#report").innerHTML = `
      <div class="report-score">
        <div class="score-tile"><span class="score-number">${percent}%</span><span>points</span></div>
        <div class="score-tile"><span class="score-number">${exact}/${reviewedQuestions.length}</span><span>exact</span></div>
      </div>
      ${renderBreakdown("By module", breakdown(results, (q) => q.module))}
      ${renderBreakdown("By claim status", breakdown(results, (q) => claimLabels[q.claim_status] || q.claim_status))}
      ${renderReviewAdvice(results)}
    `;
  }

  function renderBreakdown(title, rows) {
    return `
      <h3>${escapeHtml(title)}</h3>
      <div class="breakdown">
        ${rows.map((row) => {
          const percent = row.possible ? Math.round((row.earned / row.possible) * 100) : 0;
          return `
            <div class="breakdown-row">
              <span>${escapeHtml(row.label)}</span>
              <strong>${percent}%</strong>
              <div class="bar"><span style="width:${percent}%"></span></div>
            </div>
          `;
        }).join("")}
      </div>
    `;
  }

  function renderReviewAdvice(results) {
    const weak = results
      .filter((item) => !item.result.correct)
      .map((item) => item.q.module);
    const uniqueWeak = unique(weak).slice(0, 3);
    if (!uniqueWeak.length) {
      return `<p class="muted">No missed reviewed questions yet.</p>`;
    }
    return `<p><strong>Review next:</strong> ${escapeHtml(uniqueWeak.join(", "))}</p>`;
  }

  function breakdown(results, labeler) {
    const map = new Map();
    results.forEach(({ q, result }) => {
      const label = labeler(q);
      if (!map.has(label)) map.set(label, { label, earned: 0, possible: 0 });
      const row = map.get(label);
      row.earned += result.earned;
      row.possible += result.possible;
    });
    return Array.from(map.values()).sort((a, b) => a.label.localeCompare(b.label));
  }

  function resultClass(result) {
    if (result.correct) return "correct";
    if (result.earned > 0) return "partial";
    return "incorrect";
  }

  function unique(values) {
    return Array.from(new Set(values)).sort((a, b) => String(a).localeCompare(String(b)));
  }

  function shuffle(values) {
    const copy = [...values];
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function arraysEqual(a, b) {
    return a.length === b.length && a.every((value, index) => value === b[index]);
  }

  function sum(values) {
    return values.reduce((total, value) => total + value, 0);
  }

  function formatScore(value) {
    return Number.isInteger(value) ? String(value) : value.toFixed(1);
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function escapeAttr(value) {
    return escapeHtml(value);
  }

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === "function") return window.CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\$&");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
