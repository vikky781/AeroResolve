import React from "react";

const agents = [
  { id: "assessment", label: "Assessment", icon: "🔍", desc: "Analyze Impact" },
  { id: "policy", label: "Policy", icon: "📋", desc: "Check Rules" },
  { id: "solution", label: "Solution", icon: "🎯", desc: "Find & Rank" },
  { id: "execution", label: "Execution", icon: "🚀", desc: "Book & Notify" },
];

export default function PipelineView({ status, result }) {
  const getAgentStatus = (agentId) => {
    if (!result) return "idle";
    if (status === "completed" || result?.sms_status) return "done";

    // Simple heuristic from logs
    const logs = result?.logs || [];
    const agentMention = logs.some((log) =>
      log.toLowerCase().includes(agentId)
    );
    if (agentMention) return "done";
    return "idle";
  };

  return (
    <div className="pipeline-view">
      <h2 className="section-title">Agent Pipeline</h2>
      <div className="pipeline-agents">
        {agents.map((agent, index) => {
          const agentStatus = getAgentStatus(agent.id);
          return (
            <React.Fragment key={agent.id}>
              <div className={`pipeline-node ${agentStatus}`}>
                <div className="node-icon">{agent.icon}</div>
                <div className="node-label">{agent.label}</div>
                <div className="node-desc">{agent.desc}</div>
                {agentStatus === "done" && (
                  <div className="node-check">✓</div>
                )}
              </div>
              {index < agents.length - 1 && (
                <div className={`pipeline-connector ${agentStatus === "done" ? "active" : ""}`}>
                  <span>→</span>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
