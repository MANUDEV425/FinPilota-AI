import React from 'react';
import './AgentStatus.css';

function AgentStatus({ agents }) {
  if (!agents) {
    return null;
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'running':
        return '⟳';
      case 'failed':
        return '✗';
      case 'skipped':
        return '⊘';
      case 'demo':
        return '◉';
      default:
        return '○';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#4fd1c5';
      case 'running':
        return '#fbbf24';
      case 'failed':
        return '#fc8181';
      case 'skipped':
        return '#a0aec0';
      case 'demo':
        return '#9f7aea';
      default:
        return '#a0aec0';
    }
  };

  const agentList = [
    { key: 'researcher', name: 'Financial Research Agent' },
    { key: 'quantitative', name: 'Quantitative Analysis Agent' },
    { key: 'ml', name: 'ML Risk Agent' },
    { key: 'reviewer', name: 'Independent Review Agent' },
  ];

  return (
    <section className="agent-status-section">
      <h2>Agent Execution Status</h2>
      <div className="agent-grid">
        {agentList.map((agent) => {
          const agentData = agents[agent.key];
          const status = agentData?.status || 'pending';
          const message = agentData?.message;

          return (
            <div
              key={agent.key}
              className="agent-card"
              style={{ borderColor: getStatusColor(status) }}
            >
              <div className="agent-header">
                <span
                  className="status-icon"
                  style={{ color: getStatusColor(status) }}
                >
                  {getStatusIcon(status)}
                </span>
                <h3>{agent.name}</h3>
              </div>
              <div className="agent-status">
                <span className="status-label">Status:</span>
                <span
                  className="status-value"
                  style={{ color: getStatusColor(status) }}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </span>
              </div>
              {message && (
                <div className="agent-message">
                  <span className="message-label">Message:</span>
                  <p className="message-text">{message}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

export default AgentStatus;
