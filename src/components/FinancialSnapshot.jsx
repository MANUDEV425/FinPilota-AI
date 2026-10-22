import React from 'react';
import './FinancialSnapshot.css';

function FinancialSnapshot({ data, isDemo }) {
  if (!data) {
    return (
      <div className="card financial-snapshot">
        <h2>Financial Snapshot</h2>
        <p className="placeholder">No financial data available</p>
      </div>
    );
  }

  return (
    <div className="card financial-snapshot">
      <h2>Financial Snapshot</h2>
      {isDemo && <div className="demo-badge">Demo Data</div>}

      <div className="metrics-grid">
        {data.revenueGrowth !== undefined && (
          <div className="metric-item">
            <span className="metric-label">Revenue Growth</span>
            <span className="metric-value">
              {typeof data.revenueGrowth === 'number'
                ? `${(data.revenueGrowth * 100).toFixed(2)}%`
                : data.revenueGrowth}
            </span>
          </div>
        )}

        {data.profitMargin !== undefined && (
          <div className="metric-item">
            <span className="metric-label">Profit Margin</span>
            <span className="metric-value">
              {typeof data.profitMargin === 'number'
                ? `${(data.profitMargin * 100).toFixed(2)}%`
                : data.profitMargin}
            </span>
          </div>
        )}

        {data.liquidityRatio !== undefined && (
          <div className="metric-item">
            <span className="metric-label">Liquidity Ratio</span>
            <span className="metric-value">
              {typeof data.liquidityRatio === 'number'
                ? data.liquidityRatio.toFixed(2)
                : data.liquidityRatio}
            </span>
          </div>
        )}

        {data.leverageRatio !== undefined && (
          <div className="metric-item">
            <span className="metric-label">Leverage Ratio</span>
            <span className="metric-value">
              {typeof data.leverageRatio === 'number'
                ? data.leverageRatio.toFixed(2)
                : data.leverageRatio}
            </span>
          </div>
        )}
      </div>

      {data.reportingPeriod && (
        <div className="meta-info">
          <p>
            <strong>Reporting Period:</strong> {data.reportingPeriod}
          </p>
          {data.currency && (
            <p>
              <strong>Currency:</strong> {data.currency}
            </p>
          )}
        </div>
      )}

      {data.isSynthetic && (
        <div className="synthetic-warning">
          ⚠️ This data is synthetic/illustrative for demonstration purposes
        </div>
      )}
    </div>
  );
}

export default FinancialSnapshot;
