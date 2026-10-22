/**
 * ML Client Service
 * Communicates with the Python FastAPI ML service
 */

const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';

async function predict(features) {
  try {
    const response = await fetch(`${ML_SERVICE_URL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(features),
    });

    if (!response.ok) {
      throw new Error(`ML service returned ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('ML client error:', error);
    throw error;
  }
}

async function getMetrics() {
  try {
    const response = await fetch(`${ML_SERVICE_URL}/metrics`);
    if (!response.ok) {
      throw new Error(`ML service returned ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('ML metrics error:', error);
    throw error;
  }
}

async function getFeatureImportance() {
  try {
    const response = await fetch(`${ML_SERVICE_URL}/feature-importance`);
    if (!response.ok) {
      throw new Error(`ML service returned ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Feature importance error:', error);
    throw error;
  }
}

module.exports = {
  predict,
  getMetrics,
  getFeatureImportance,
};
