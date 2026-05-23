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

  if (failures.length) {
    console.error(failures.join("\n"));
    process.exitCode = 1;
  } else {
    console.log(`rendered ${workspaceDefs.length} workspaces`);
  }
} finally {
  await server.close();
}
