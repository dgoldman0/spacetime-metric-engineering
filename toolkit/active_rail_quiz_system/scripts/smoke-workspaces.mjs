import React from "react";
import { renderToString } from "react-dom/server";
import { createServer } from "vite";

const server = await createServer({
  appType: "custom",
  logLevel: "silent",
  server: { middlewareMode: true }
});

try {
  const { App, workspaceDefs } = await server.ssrLoadModule("/src/App.jsx");
  const { questionBank } = await server.ssrLoadModule("/src/data/questionBank.js");
  const { buildInitialResponse } = await server.ssrLoadModule("/src/lib/session.js");
  const failures = [];

  for (const workspace of workspaceDefs) {
    try {
      const html = renderToString(React.createElement(App, { initialWorkspace: workspace.id }));
      if (!html.includes(workspace.title)) {
        failures.push(`${workspace.id}: title did not render`);
      }
      if (html.includes("This workspace is waiting for seed questions")) {
        failures.push(`${workspace.id}: rendered curriculum-gap state`);
      }
    } catch (error) {
      failures.push(`${workspace.id}: ${error.message}`);
    }
  }

  for (const question of questionBank) {
    const response = buildInitialResponse(question);
    const presentationFailures = validatePresentationOrder(question, response);
    failures.push(...presentationFailures.map((message) => `${question.id}: ${message}`));
  }

  if (failures.length) {
    console.error(failures.join("\n"));
    process.exitCode = 1;
  } else {
    console.log(`rendered ${workspaceDefs.length} workspaces`);
  }
} finally {
  await server.close();
}

function validatePresentationOrder(question, response) {
  const failures = [];

  if (question.type === "mc" || question.type === "multi" || question.type === "tf") {
    assertSameIds(failures, "choiceOrder", response.choiceOrder, question.choices.map((choice) => choice.id));
  }
  if (question.type === "drag_fill") {
    assertSameIds(failures, "tokenOrder", response.tokenOrder, question.tokens.map((token) => token.id));
  }
  if (question.type === "matching") {
    assertSameIds(failures, "promptOrder", response.promptOrder, question.prompts.map((prompt) => prompt.id));
    assertSameIds(failures, "optionOrder", response.optionOrder, question.options.map((option) => option.id));
  }
  if (question.type === "claim_classification") {
    assertSameIds(failures, "statementOrder", response.statementOrder, question.statements.map((statement) => statement.id));
  }
  if (question.type === "sequence") {
    assertSameIds(failures, "order", response.order, question.items.map((item) => item.id));
    if (question.answer.length > 1 && arraysEqual(response.order, question.answer)) {
      failures.push("sequence starts in answer order");
    }
  }

  return failures;
}

function assertSameIds(failures, label, actual = [], expected = []) {
  const actualSorted = [...actual].sort();
  const expectedSorted = [...expected].sort();
  if (!arraysEqual(actualSorted, expectedSorted)) {
    failures.push(`${label} is not a permutation of bank IDs`);
  }
}

function arraysEqual(a, b) {
  return a.length === b.length && a.every((value, index) => value === b[index]);
}
