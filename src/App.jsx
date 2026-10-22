import React, { useState } from 'react';
import FinancialSnapshot from './components/FinancialSnapshot';
import AgentStatus from './components/AgentStatus';
import MlRiskCard from './components/MlRiskCard';
import ResearchReport from './components/ResearchReport';
import './App.css';

function App() {
  const [researchQuery, setResearchQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isDemoMode, setIsDemoMode] = useState(false);

  const handleAnalyze = async (useDemo = false) => {
    setIsAnalyzing(true);
    setIsDemoMode(useDemo);
    setAnalysisResult(null);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3001';
      const endpoint = useDemo ? '/api/analyze-demo' : '/api/analyze';
      const response = await fetch(`${apiUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(useDemo ? {} : { query: researchQuery }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (error) {
      console.error('Analysis failed:', error);
      setAnalysisResult({
        error: error.message,
        agents: {
          researcher: { status: 'failed', message: error.message },
          quantitative: { status: 'failed', message: error.message },
          ml: { status: 'failed', message: error.message },
          reviewer: { status: 'failed', message: error.message },
        },
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">FinancePilot AI</h1>
        <p className="app-subtitle">
          Multi-Model Agentic Financial Intelligence Platform
        </p>
      </header>

      <main className="app-main">
        <section className="overview-section">
          <div className="input-container">
            <textarea
              className="research-input"
              placeholder="Enter your financial research question or company name..."
              value={researchQuery}
              onChange={(e) => setResearchQuery(e.target.value)}
              disabled={isAnalyzing}
              rows={4}
            />
            <div className="button-group">
              <button
                className="analyze-button primary"
                onClick={() => handleAnalyze(false)}
                disabled={isAnalyzing || !researchQuery.trim()}
              >
                {isAnalyzing ? 'Analyzing...' : 'Analyze'}
              </button>
              <button
                className="analyze-button secondary"
                onClick={() => handleAnalyze(true)}
                disabled={isAnalyzing}
              >
                Demo Mode
              </button>
            </div>
          </div>

          {isDemoMode && (
            <div className="demo-banner">
              <strong>Demo Mode:</strong> Using preloaded historical data for demonstration
            </div>
          )}
        </section>

        {analysisResult && (
          <>
            <AgentStatus agents={analysisResult.agents} />

            <div className="dashboard-grid">
              <FinancialSnapshot
                data={analysisResult.financialSnapshot}
                isDemo={isDemoMode}
              />

              <MlRiskCard
                data={analysisResult.mlPrediction}
                isDemo={isDemoMode}
              />

              <ResearchReport
                data={analysisResult.researchReport}
                isDemo={isDemoMode}
              />
            </div>

            {analysisResult.evaluation && (
              <section className="evaluation-section">
                <h2>Model Evaluation Metrics</h2>
                <div className="evaluation-grid">
                  {Object.entries(analysisResult.evaluation).map(([key, value]) => (
                    <div key={key} className="evaluation-item">
                      <span className="evaluation-label">{key}:</span>
                      <span className="evaluation-value">
                        {typeof value === 'number' ? value.toFixed(4) : value}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>
          <strong>Disclaimer:</strong> FinancePilot AI is for research and educational purposes only.
          It does not provide personalized investment advice or validated credit scoring.
          ML predictions are uncertain and depend on training data distribution.
        </p>
      </footer>
    </div>
  );
}

export default App;
