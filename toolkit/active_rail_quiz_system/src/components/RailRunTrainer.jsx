import { useEffect, useMemo, useState } from "react";

const stages = [
  {
    id: "support",
    label: "Support",
    command: "Establish Support",
    description: "Bring the corridor support envelope into service."
  },
  {
    id: "carry",
    label: "Carry",
    command: "Carry Packet",
    description: "Move the packet through the active service interval."
  },
  {
    id: "catch",
    label: "Catch",
    command: "Catch And Rematch",
    description: "Match the endpoint before release fade begins."
  },
  {
    id: "fade",
    label: "Fade",
    command: "Fade Carrier",
    description: "Withdraw the active carrier without dropping support."
  },
  {
    id: "decompress",
    label: "Decompress",
    command: "Decompress Line",
    description: "Unload support and source channels in controlled order."
  },
  {
    id: "reset",
    label: "Reset",
    command: "Reset Rail",
    description: "Clear residue and secure the line for reuse."
  }
];

const profiles = [
  {
    id: "inspection",
    label: "Inspection Crawl",
    summary: "Low-load packet with wide catch window.",
    badge: "Training",
    pace: 7,
    initial: {
      support: 78,
      ledger: 72,
      endpoint: 76,
      drift: 18,
      residue: 18,
      stability: 76
    }
  },
  {
    id: "standard",
    label: "Standard Packet",
    summary: "Nominal service request with ordinary review burden.",
    badge: "Nominal",
    pace: 8,
    initial: {
      support: 70,
      ledger: 66,
      endpoint: 68,
      drift: 24,
      residue: 24,
      stability: 70
    }
  },
  {
    id: "tight",
    label: "Tight-Window Handoff",
    summary: "Endpoint timing is touchy; catch discipline matters.",
    badge: "Timing",
    pace: 9,
    initial: {
      support: 66,
      ledger: 62,
      endpoint: 52,
      drift: 44,
      residue: 26,
      stability: 66
    }
  },
  {
    id: "heavy",
    label: "Heavy Packet",
    summary: "Higher source burden and faster support depletion.",
    badge: "Load",
    pace: 8,
    initial: {
      support: 54,
      ledger: 48,
      endpoint: 62,
      drift: 28,
      residue: 30,
      stability: 58
    }
  },
  {
    id: "reuse",
    label: "Post-Reset Reuse",
    summary: "Line has leftover residue from a previous pass.",
    badge: "Reuse",
    pace: 8,
    initial: {
      support: 64,
      ledger: 58,
      endpoint: 62,
      drift: 30,
      residue: 56,
      stability: 62
    }
  }
];

const meterDefs = [
  {
    id: "support",
    label: "Support Envelope",
    lowBad: true,
    caution: 58,
    red: 32,
    description: "Corridor support margin available to carry the packet."
  },
  {
    id: "ledger",
    label: "Source Ledger",
    lowBad: true,
    caution: 58,
    red: 28,
    description: "Closure of demanded source roles before active service."
  },
  {
    id: "endpoint",
    label: "Endpoint Sync",
    lowBad: true,
    caution: 58,
    red: 30,
    description: "Catch/rematch confidence at the receiving endpoint."
  },
  {
    id: "drift",
    label: "Timing Drift",
    lowBad: false,
    caution: 46,
    red: 74,
    description: "Accumulated service-window drift."
  },
  {
    id: "residue",
    label: "Reset Residue",
    lowBad: false,
    caution: 48,
    red: 78,
    description: "Residual load that can contaminate reuse."
  },
  {
    id: "stability",
    label: "Stability Posture",
    lowBad: true,
    caution: 56,
    red: 28,
    description: "Qualitative perturbation and backreaction posture."
  }
];

const actionDefs = [
  {
    id: "precharge",
    label: "Precharge Support",
    detail: "Build support envelope before or between service phases.",
    apply(metrics) {
      return {
        ...metrics,
        support: clamp(metrics.support + 18),
        stability: clamp(metrics.stability + 4),
        drift: clamp(metrics.drift + 3)
      };
    }
  },
  {
    id: "ledger",
    label: "Close Source Ledger",
    detail: "Reconcile source roles before active demand rises.",
    apply(metrics) {
      return {
        ...metrics,
        ledger: clamp(metrics.ledger + 22),
        stability: clamp(metrics.stability + 2)
      };
    }
  },
  {
    id: "sync",
    label: "Run Endpoint Sync",
    detail: "Tighten catch/rematch timing and endpoint confidence.",
    apply(metrics) {
      return {
        ...metrics,
        endpoint: clamp(metrics.endpoint + 24),
        drift: clamp(metrics.drift - 16)
      };
    }
  },
  {
    id: "flush",
    label: "Flush Reset Path",
    detail: "Clear residue before reuse or final reset.",
    apply(metrics) {
      return {
        ...metrics,
        residue: clamp(metrics.residue - 30),
        stability: clamp(metrics.stability + 3)
      };
    }
  },
  {
    id: "sweep",
    label: "Stability Sweep",
    detail: "Pause for coupled-channel review before continuing.",
    apply(metrics) {
      return {
        ...metrics,
        stability: clamp(metrics.stability + 16),
        drift: clamp(metrics.drift + 4),
        ledger: clamp(metrics.ledger - 4)
      };
    }
  }
];

export function RailRunTrainer() {
  const [profileId, setProfileId] = useState("standard");
  const [line, setLine] = useState(() => createLine("standard"));
  const profile = profiles.find((item) => item.id === line.profileId) || profiles[1];
  const phase = stages[line.stageIndex] || null;
  const nextCommand = getPrimaryCommand(line);
  const condition = getLineCondition(line.metrics, line.runState);
  const advisories = useMemo(() => getAdvisories(line), [line]);

  useEffect(() => {
    if (line.runState !== "running") return undefined;
    const interval = window.setInterval(() => {
      setLine((current) => stepLine(current));
    }, 800);
    return () => window.clearInterval(interval);
  }, [line.runState]);

  function switchProfile(nextProfileId) {
    setProfileId(nextProfileId);
    setLine(createLine(nextProfileId));
  }

  function executePrimary() {
    setLine((current) => startOrAdvance(current));
  }

  function applyProcedure(action) {
    setLine((current) => {
      if (!canUseProcedure(current)) return current;
      const nextMetrics = action.apply(current.metrics);
      return {
        ...current,
        metrics: nextMetrics,
        actions: { ...current.actions, [action.id]: true },
        events: addEvent(current.events, current.clock, "procedure", `${action.label} complete. ${action.detail}`)
      };
    });
  }

  function holdLine() {
    setLine((current) => {
      if (current.runState !== "running") return current;
      return {
        ...current,
        runState: "hold",
        events: addEvent(current.events, current.clock, "caution", "Line held by operator. Service clock paused for intervention.")
      };
    });
  }

  function resumeLine() {
    setLine((current) => {
      if (current.runState !== "hold") return current;
      return {
        ...current,
        runState: "running",
        events: addEvent(current.events, current.clock, "procedure", "Line released from hold.")
      };
    });
  }

  function abortLine() {
    setLine((current) => {
      if (["aborted", "complete", "standby"].includes(current.runState)) return current;
      return {
        ...current,
        runState: "aborted",
        failure: {
          title: "Operator abort",
          detail: "The service pass was stopped before the current phase completed.",
          recovery: "Hold the packet state, inspect support and endpoint channels, then reset before a new pass."
        },
        events: addEvent(current.events, current.clock, "abort", "Operator abort accepted. Line is in recovery state.")
      };
    });
  }

  function resetLine() {
    setLine(createLine(profileId));
  }

  return (
    <div className="rail-trainer">
      <section className="trainer-hero" aria-label="Rail trainer state">
        <div>
          <p className="eyebrow">Architecture Logic Trainer</p>
          <h3>Single Rail Service Console</h3>
          <p>
            Operate the service line through support, carry, catch, fade,
            decompression, and reset. The trainer models active-rail procedure
            and failure logic, not validated plant physics.
          </p>
        </div>
        <div className={`line-condition ${condition}`}>
          <span>{formatRunState(line.runState)}</span>
          <strong>{conditionLabel(condition)}</strong>
          <small>T+{formatClock(line.clock)}</small>
        </div>
      </section>

      <section className="service-manifest" aria-label="Service request manifest">
        <div className="manifest-head">
          <h3>Service Request</h3>
          <span>{profile.label}</span>
        </div>
        <div className="profile-grid">
          {profiles.map((item) => (
            <button
              type="button"
              key={item.id}
              className={`profile-card ${profileId === item.id ? "selected" : ""}`}
              onClick={() => switchProfile(item.id)}
              disabled={!["standby", "complete", "aborted"].includes(line.runState)}
            >
              <span>{item.badge}</span>
              <strong>{item.label}</strong>
              <small>{item.summary}</small>
            </button>
          ))}
        </div>
      </section>

      <section className="rail-map" aria-label="Active rail line map">
        <div className="rail-beam" aria-hidden="true">
          <div className="rail-beam-live" style={{ width: `${lineBeamWidth(line)}%` }} />
        </div>
        <div className="stage-track">
          {stages.map((stage, index) => (
            <div
              className={`stage-node ${stageClass(line, index)}`}
              key={stage.id}
            >
              <span>{index + 1}</span>
              <strong>{stage.label}</strong>
              <small>{stage.description}</small>
            </div>
          ))}
        </div>
      </section>

      <div className="trainer-grid">
        <section className="command-console" aria-label="Operator command console">
          <div className="console-head">
            <div>
              <p className="eyebrow">Command Console</p>
              <h3>{phase ? phase.label : "Standby"}</h3>
            </div>
            <span className="phase-progress">{Math.round(line.progress)}%</span>
          </div>

          <div className="current-order">
            <strong>{nextCommand.title}</strong>
            <p>{nextCommand.detail}</p>
          </div>

          <div className="command-row">
            <button
              type="button"
              className="primary-command"
              onClick={executePrimary}
              disabled={!nextCommand.enabled}
            >
              {nextCommand.label}
            </button>
            {line.runState === "running" ? (
              <button type="button" onClick={holdLine}>Hold Line</button>
            ) : (
              <button type="button" onClick={resumeLine} disabled={line.runState !== "hold"}>Release Hold</button>
            )}
            <button type="button" className="danger-command" onClick={abortLine} disabled={!canAbort(line)}>Abort</button>
            <button type="button" onClick={resetLine}>Reset Trainer</button>
          </div>

          <div className="procedure-grid">
            {actionDefs.map((action) => (
              <button
                type="button"
                key={action.id}
                className={line.actions[action.id] ? "procedure-done" : ""}
                onClick={() => applyProcedure(action)}
                disabled={!canUseProcedure(line)}
              >
                <strong>{action.label}</strong>
                <span>{action.detail}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="line-meters" aria-label="Line health meters">
          <div className="console-head">
            <div>
              <p className="eyebrow">Line State</p>
              <h3>Readiness And Health</h3>
            </div>
          </div>
          <div className="meter-list">
            {meterDefs.map((meter) => (
              <Meter key={meter.id} meter={meter} value={line.metrics[meter.id]} />
            ))}
          </div>
        </section>

        <section className="advisory-panel" aria-label="Line advisory panel">
          <div className="console-head">
            <div>
              <p className="eyebrow">Advisory</p>
              <h3>{line.failure ? "Recovery Required" : "Operator Notes"}</h3>
            </div>
          </div>
          {line.failure ? (
            <div className="failure-card">
              <strong>{line.failure.title}</strong>
              <p>{line.failure.detail}</p>
              <span>{line.failure.recovery}</span>
            </div>
          ) : (
            <ul className="advisory-list">
              {advisories.map((advisory) => (
                <li className={advisory.level} key={advisory.id}>
                  <strong>{advisory.title}</strong>
                  <span>{advisory.detail}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="event-log" aria-label="Service event log">
          <div className="console-head">
            <div>
              <p className="eyebrow">Event Log</p>
              <h3>Service Trace</h3>
            </div>
          </div>
          <ol>
            {line.events.map((event) => (
              <li className={event.level} key={event.id}>
                <time>T+{formatClock(event.clock)}</time>
                <span>{event.message}</span>
              </li>
            ))}
          </ol>
        </section>
      </div>
    </div>
  );
}

function Meter({ meter, value }) {
  const status = meterStatus(meter, value);
  return (
    <div className={`meter ${status}`}>
      <div className="meter-label">
        <strong>{meter.label}</strong>
        <span>{statusLabel(status)}</span>
      </div>
      <div className="meter-bar" aria-hidden="true">
        <span style={{ width: `${value}%` }} />
      </div>
      <p>{meter.description}</p>
    </div>
  );
}

function createLine(profileId) {
  const profile = profiles.find((item) => item.id === profileId) || profiles[1];
  return {
    profileId,
    runState: "standby",
    stageIndex: -1,
    progress: 0,
    clock: 0,
    metrics: { ...profile.initial },
    actions: {},
    notices: {},
    failure: null,
    events: [
      {
        id: "event-0",
        clock: 0,
        level: "system",
        message: `${profile.label} manifest loaded. Line is in standby.`
      }
    ]
  };
}

function startOrAdvance(line) {
  if (["running", "hold", "aborted", "complete"].includes(line.runState)) return line;

  if (line.runState === "standby") {
    return beginStage(line, 0, "Support command accepted. Corridor establishment underway.");
  }

  if (line.runState === "waiting") {
    if (line.stageIndex >= stages.length - 1) {
      return {
        ...line,
        runState: "complete",
        progress: 100,
        events: addEvent(line.events, line.clock, "complete", "Line secured. Service pass complete.")
      };
    }
    const nextIndex = line.stageIndex + 1;
    return beginStage(line, nextIndex, `${stages[nextIndex].command} command accepted.`);
  }

  return line;
}

function beginStage(line, stageIndex, message) {
  return {
    ...line,
    runState: "running",
    stageIndex,
    progress: 0,
    events: addEvent(line.events, line.clock, "command", message)
  };
}

function stepLine(line) {
  if (line.runState !== "running") return line;

  const profile = profiles.find((item) => item.id === line.profileId) || profiles[1];
  const stage = stages[line.stageIndex];
  const clock = line.clock + 1;
  const metrics = applyStageEffects(line.metrics, stage?.id, profile.id);
  const progress = Math.min(100, line.progress + profile.pace);
  const checked = checkFailure({ ...line, metrics, clock, progress });

  if (checked.failure) {
    return {
      ...line,
      metrics,
      clock,
      progress,
      runState: "aborted",
      failure: checked.failure,
      notices: checked.notices,
      events: addEvent(line.events, clock, "abort", checked.failure.title)
    };
  }

  const noticeResult = addThresholdNotices(line, metrics, clock);

  if (progress >= 100) {
    const completedMessage = line.stageIndex >= stages.length - 1
      ? "Reset phase complete. Secure the line when ready."
      : `${stage.label} phase complete. Awaiting next operator command.`;
    return {
      ...line,
      metrics,
      clock,
      progress: 100,
      runState: "waiting",
      notices: noticeResult.notices,
      events: addEvent(noticeResult.events, clock, "complete", completedMessage)
    };
  }

  return {
    ...line,
    metrics,
    clock,
    progress,
    notices: noticeResult.notices,
    events: noticeResult.events
  };
}

function applyStageEffects(metrics, stageId, profileId) {
  const loadFactor = profileId === "heavy" ? 1.32 : profileId === "inspection" ? 0.72 : 1;
  const timingFactor = profileId === "tight" ? 1.45 : 1;
  const reuseFactor = profileId === "reuse" ? 1.25 : 1;

  const next = { ...metrics };
  if (stageId === "support") {
    next.support += 0.4;
    next.ledger -= 0.15 * loadFactor;
    next.drift += 0.12 * timingFactor;
  }
  if (stageId === "carry") {
    next.support -= 0.9 * loadFactor;
    next.ledger -= 0.85 * loadFactor;
    next.endpoint -= 0.12 * timingFactor;
    next.drift += 0.85 * timingFactor;
    next.stability -= 0.45 * loadFactor;
  }
  if (stageId === "catch") {
    next.endpoint -= 1.05 * timingFactor;
    next.drift += 0.95 * timingFactor;
    next.support -= 0.42 * loadFactor;
    next.ledger -= 0.4 * loadFactor;
  }
  if (stageId === "fade") {
    next.support -= 0.48 * loadFactor;
    next.ledger -= 0.42 * loadFactor;
    next.stability -= 0.85 * loadFactor;
    next.residue += 0.75 * reuseFactor;
  }
  if (stageId === "decompress") {
    next.support -= 0.25;
    next.residue += 0.95 * reuseFactor;
    next.drift -= 0.22;
    next.stability -= 0.35;
  }
  if (stageId === "reset") {
    next.residue -= profileId === "reuse" ? 0.8 : 1.2;
    next.endpoint += 0.15;
    next.support += 0.08;
    next.stability += 0.08;
  }

  return clampMetrics(next);
}

function checkFailure(line) {
  const { metrics } = line;
  const stageId = stages[line.stageIndex]?.id;
  if (["support", "carry", "fade"].includes(stageId) && metrics.support < 24) {
    return {
      failure: {
        title: "Support gap lockout",
        detail: "The corridor support margin fell below the service floor while the line was active.",
        recovery: "Abort the pass, re-establish support, and rerun ledger closure before carrying another packet."
      },
      notices: line.notices
    };
  }
  if (["carry", "catch", "fade"].includes(stageId) && metrics.ledger < 22) {
    return {
      failure: {
        title: "Source ledger overdraw",
        detail: "Active demand outran the closed source roles tracked by the trainer.",
        recovery: "Hold service, close the ledger, and review which role was promoted beyond evidence."
      },
      notices: line.notices
    };
  }
  if (stageId === "catch" && metrics.endpoint < 26) {
    return {
      failure: {
        title: "Endpoint mismatch",
        detail: "Catch/rematch confidence collapsed before the packet could be handed off cleanly.",
        recovery: "Abort into endpoint recovery, run synchronization, and avoid release fade until catch is restored."
      },
      notices: line.notices
    };
  }
  if (["carry", "catch"].includes(stageId) && metrics.drift > 82) {
    return {
      failure: {
        title: "Timing window violation",
        detail: "Service drift exceeded the trainer's catch-window tolerance.",
        recovery: "Hold the line, resynchronize endpoint timing, and restart from a conservative service profile."
      },
      notices: line.notices
    };
  }
  if (["decompress", "reset"].includes(stageId) && metrics.residue > 84) {
    return {
      failure: {
        title: "Reset contamination",
        detail: "Residue accumulated faster than the reset path could clear it.",
        recovery: "Secure the line, flush the reset path, and do not declare reuse readiness."
      },
      notices: line.notices
    };
  }
  if (metrics.stability < 22) {
    return {
      failure: {
        title: "Stability review lockout",
        detail: "The trainer detected a stability posture too weak for continued service.",
        recovery: "Stop the pass and perform coupled-channel review before any new command."
      },
      notices: line.notices
    };
  }
  return { failure: null, notices: line.notices };
}

function addThresholdNotices(line, metrics, clock) {
  const notices = { ...line.notices };
  let events = line.events;

  const checks = [
    ["support", metrics.support < 48, "caution", "Support envelope is below nominal margin."],
    ["ledger", metrics.ledger < 48, "caution", "Source ledger closure is thinning under active demand."],
    ["endpoint", metrics.endpoint < 48, "caution", "Endpoint sync is degraded before catch/rematch."],
    ["drift", metrics.drift > 58, "caution", "Timing drift is approaching the service-window limit."],
    ["residue", metrics.residue > 58, "caution", "Reset residue is building and may affect reuse."],
    ["stability", metrics.stability < 48, "caution", "Stability posture needs operator attention."]
  ];

  checks.forEach(([id, active, level, message]) => {
    const key = `${id}-${line.stageIndex}`;
    if (active && !notices[key]) {
      notices[key] = true;
      events = addEvent(events, clock, level, message);
    }
  });

  return { notices, events };
}

function getPrimaryCommand(line) {
  if (line.runState === "standby") {
    return {
      enabled: true,
      label: "Arm Support",
      title: "Line is standing by",
      detail: "Load the manifest, complete useful readiness actions, then establish the support corridor."
    };
  }
  if (line.runState === "running") {
    const stage = stages[line.stageIndex];
    return {
      enabled: false,
      label: "Phase Running",
      title: stage ? `${stage.label} in progress` : "Service in progress",
      detail: "Monitor meters and hold or abort if the line develops a red condition."
    };
  }
  if (line.runState === "hold") {
    return {
      enabled: false,
      label: "Held",
      title: "Line is held",
      detail: "Use readiness procedures, then release hold when the line is safe to continue."
    };
  }
  if (line.runState === "waiting") {
    if (line.stageIndex >= stages.length - 1) {
      return {
        enabled: true,
        label: "Secure Line",
        title: "Reset complete",
        detail: "Secure the line and close the service pass."
      };
    }
    const next = stages[line.stageIndex + 1];
    return {
      enabled: true,
      label: next.command,
      title: "Awaiting operator command",
      detail: `Next authorized phase is ${next.label}. Review advisories before issuing the command.`
    };
  }
  if (line.runState === "aborted") {
    return {
      enabled: false,
      label: "Recovery Required",
      title: "Line aborted",
      detail: "Review the recovery card, then reset the trainer for a new pass."
    };
  }
  return {
    enabled: false,
    label: "Complete",
    title: "Service pass complete",
    detail: "The line is secured."
  };
}

function getAdvisories(line) {
  if (line.runState === "complete") {
    return [{
      id: "complete",
      level: "nominal",
      title: "Line secured",
      detail: "The service pass closed without an abort state."
    }];
  }

  const list = [];
  const { metrics } = line;
  if (metrics.support < 58) {
    list.push({
      id: "support",
      level: metrics.support < 36 ? "red" : "caution",
      title: "Support margin low",
      detail: "Hold or precharge before committing to active carry or fade."
    });
  }
  if (metrics.ledger < 58) {
    list.push({
      id: "ledger",
      level: metrics.ledger < 34 ? "red" : "caution",
      title: "Source ledger thin",
      detail: "Close the ledger before the active interval draws more burden."
    });
  }
  if (metrics.endpoint < 58 || metrics.drift > 46) {
    list.push({
      id: "endpoint",
      level: metrics.endpoint < 34 || metrics.drift > 70 ? "red" : "caution",
      title: "Catch window at risk",
      detail: "Run endpoint sync before catch/rematch or tight-window handoff."
    });
  }
  if (metrics.residue > 48) {
    list.push({
      id: "residue",
      level: metrics.residue > 72 ? "red" : "caution",
      title: "Reset path loaded",
      detail: "Flush the reset path before reuse readiness is declared."
    });
  }
  if (metrics.stability < 56) {
    list.push({
      id: "stability",
      level: metrics.stability < 34 ? "red" : "caution",
      title: "Stability posture weak",
      detail: "Run a stability sweep or hold for coupled-channel review."
    });
  }

  if (list.length) return list;
  return [{
    id: "nominal",
    level: "nominal",
    title: "Line is ready",
    detail: "No advisory is blocking the next command in this architecture trainer."
  }];
}

function getLineCondition(metrics, runState) {
  if (runState === "aborted") return "red";
  if (runState === "complete") return "nominal";
  const statuses = meterDefs.map((meter) => meterStatus(meter, metrics[meter.id]));
  if (statuses.includes("red")) return "red";
  if (statuses.includes("caution")) return "caution";
  return "nominal";
}

function meterStatus(meter, value) {
  if (meter.lowBad) {
    if (value <= meter.red) return "red";
    if (value <= meter.caution) return "caution";
    return "nominal";
  }
  if (value >= meter.red) return "red";
  if (value >= meter.caution) return "caution";
  return "nominal";
}

function statusLabel(status) {
  if (status === "red") return "Red";
  if (status === "caution") return "Caution";
  return "Nominal";
}

function conditionLabel(status) {
  if (status === "red") return "Red Gate";
  if (status === "caution") return "Caution";
  return "Nominal";
}

function formatRunState(state) {
  const labels = {
    standby: "Standby",
    running: "Running",
    waiting: "Awaiting command",
    hold: "Held",
    aborted: "Aborted",
    complete: "Complete"
  };
  return labels[state] || state;
}

function canUseProcedure(line) {
  return ["standby", "waiting", "hold"].includes(line.runState);
}

function canAbort(line) {
  return ["running", "waiting", "hold"].includes(line.runState);
}

function stageClass(line, index) {
  if (line.runState === "aborted" && index === line.stageIndex) return "failed";
  if (index < line.stageIndex || (line.runState === "complete" && index <= line.stageIndex)) return "complete";
  if (index === line.stageIndex) return "active";
  return "pending";
}

function lineBeamWidth(line) {
  if (line.stageIndex < 0) return 0;
  const stageSpan = 100 / stages.length;
  const base = line.stageIndex * stageSpan;
  return Math.min(100, base + (line.progress / 100) * stageSpan);
}

function addEvent(events, clock, level, message) {
  return [
    {
      id: `event-${clock}-${events.length}`,
      clock,
      level,
      message
    },
    ...events
  ].slice(0, 18);
}

function clampMetrics(metrics) {
  return Object.fromEntries(
    Object.entries(metrics).map(([key, value]) => [key, clamp(value)])
  );
}

function clamp(value) {
  return Math.max(0, Math.min(100, value));
}

function formatClock(value) {
  const minutes = Math.floor(value / 60);
  const seconds = value % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}
