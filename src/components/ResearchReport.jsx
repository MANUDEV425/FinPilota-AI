import React from 'react';
import './ResearchReport.css';

function ResearchReport({ data, isDemo }) {
  if (!data) {
    return (
      <div className="card research-report">
        <h2>Research Report</h2>
        <p className="placeholder">No research report available</p>
      </div>
    );
  }

  return (
    <div className="card research-report">
      <h2>Research Report</h2>
      {isDemo && <div className="demo-badge">Demo Data</div>}

      {data.mainFindings && (
        <div className="report-section">
          <h3>Main Findings</h3>
          <ul className="findings-list">
            {data.mainFindings.map((finding, index) => (
              <li key={index}>{finding}</li>
            ))}
          </ul>
        </div>
      )}

      {data.positiveEvidence && data.positiveEvidence.length > 0 && (
        <div className="report-section">
          <h3>Positive Evidence</h3>
          <ul className="evidence-list positive">
            {data.positiveEvidence.map((evidence, index) => (
              <li key={index}>{evidence}</li>
            ))}
          </ul>
        </div>
      )}

      {data.negativeEvidence && data.negativeEvidence.length > 0 && (
        <div className="report-section">
          <h3>Negative Evidence</h3>
          <ul className="evidence-list negative">
            {data.negativeEvidence.map((evidence, index) => (
              <li key={index}>{evidence}</li>
            ))}
          </ul>
        </div>
      )}

      {data.missingInformation && data.missingInformation.length > 0 && (
        <div className="report-section">
          <h3>Missing Information</h3>
          <ul className="missing-list">
            {data.missingInformation.map((info, index) => (
              <li key={index}>{info}</li>
            ))}
          </ul>
        </div>
      )}

      {data.riskFactors && data.riskFactors.length > 0 && (
        <div className="report-section">
          <h3>Risk Factors</h3>
          <ul className="risk-list">
            {data.riskFactors.map((risk, index) => (
              <li key={index}>{risk}</li>
            ))}
          </ul>
        </div>
      )}

      {data.reviewerComments && data.reviewerComments.length > 0 && (
        <div className="report-section reviewer-section">
          <h3>Independent Reviewer Comments</h3>
          <ul className="reviewer-list">
            {data.reviewerComments.map((comment, index) => (
              <li key={index}>{comment}</li>
            ))}
          </ul>
        </div>
      )}

      {data.citations && data.citations.length > 0 && (
        <div className="report-section citations-section">
          <h3>Citations & Sources</h3>
          <ul className="citations-list">
            {data.citations.map((citation, index) => (
              <li key={index}>
                {citation.url ? (
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="citation-link"
                  >
                    {citation.text || citation.url}
                  </a>
                ) : (
                  <span>{citation.text || citation}</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.disclaimer && (
        <div className="report-disclaimer">
          <strong>Disclaimer:</strong> {data.disclaimer}
        </div>
      )}
    </div>
  );
}

export default ResearchReport;
