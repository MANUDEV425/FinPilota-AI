import React from 'react';
import './MlRiskCard.css';

function MlRiskCard({ data, isDemo }) {
  if (!data) {
    return (
      <div className="card ml-risk-card">
        <h2>ML Risk Assessment</h2>
        <p className="placeholder">No ML prediction available</p>
      </div>
    );
  }

  const getRiskLevel = (probability) => {
    if (probability >= 0.7) return { label: 'High', color: '#fc8181' };
    if (probability >= 0.4) return { label: 'Medium', color: '#fbbf24' };
    return { label: 'Low', color: '#4fd1c5' };
  };

  const riskLevel = getRiskLevel(data.model_estimated_probability_of_default || 0);

  return (
    <div className="card ml-risk-card">
      <h2>ML Risk Assessment</h2>
      {isDemo && <div className="demo-badge">Demo Data</div>}

      <div className="prediction-section">
        <div className="prediction-header">
          <span className="prediction-label">Prediction:</span>
          <span className="prediction-value">
            {data.prediction === 1 ? 'Default Risk' : 'No Default Risk'}
          </span>
        </div>

        <div className="probability-section">
          <span className="probability-label">
            Model Estimated Probability of Default:
          </span>
          <div className="probability-bar-container">
            <div
              className="probability-bar"
              style={{
                width: `${(data.model_estimated_probability_of_default || 0) * 100}%`,
                backgroundColor: riskLevel.color,
              }}
            />
            <span className="probability-value">
              {((data.model_estimated_probability_of_default || 0) * 100).toFixed(2)}%
            </span>
          </div>
          <div className="risk-badge" style={{ backgroundColor: riskLevel.color, color: '#0a1929' }}>
            {riskLevel.label} Risk
          </div>
        </div>
      </div>

      <div className="model-info">
        <h3>Model Information</h3>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Model Type:</span>
            <span className="info-value">{data.model_type}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Version:</span>
            <span className="info-value">{data.model_version}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Dataset:</span>
            <span className="info-value">{data.dataset}</span>
          </div>
          <div className="info-item">
            <span className="info-label">Probability Calibrated:</span>
            <span className="info-value">
              {data.probability_is_calibrated ? 'Yes' : 'No'}
            </span>
          </div>
        </div>
      </div>

      {data.feature_importance && (
        <div className="feature-importance">
          <h3>Feature Importance</h3>
          <div className="importance-list">
            {Object.entries(data.feature_importance)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 5)
              .map(([feature, importance]) => (
                <div key={feature} className="importance-item">
                  <span className="feature-name">{feature}</span>
                  <div className="importance-bar-container">
                    <div
                      className="importance-bar"
                      style={{ width: `${importance * 100}%` }}
                    />
                    <span className="importance-value">
                      {(importance * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {data.limitations && data.limitations.length > 0 && (
        <div className="limitations">
          <h3>Model Limitations</h3>
          <ul className="limitations-list">
            {data.limitations.map((limitation, index) => (
              <li key={index}>{limitation}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default MlRiskCard;
