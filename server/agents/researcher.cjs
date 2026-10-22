/**
 * Financial Research Agent
 * Uses Gemini to analyze financial queries and generate research reports
 */

async function analyze(query, model, financialSnapshot) {
  const prompt = `You are a financial research assistant. Analyze the following query and provide a structured research report.

Query: ${query}

Available financial data: ${JSON.stringify(financialSnapshot || {})}

Provide a response in the following JSON format:
{
  "mainFindings": ["finding 1", "finding 2", ...],
  "positiveEvidence": ["positive point 1", "positive point 2", ...],
  "negativeEvidence": ["negative point 1", "negative point 2", ...],
  "missingInformation": ["missing info 1", "missing info 2", ...],
  "riskFactors": ["risk 1", "risk 2", ...],
  "citations": [{"text": "source description", "url": "https://..."}]
}

Important constraints:
- Only state facts that are supported by the provided data or general financial knowledge
- Clearly distinguish between verified data and assumptions
- Do not invent external sources or financial figures
- If you don't have sufficient information, state it clearly in missingInformation
- Keep findings concise and actionable
- For citations, only include sources you actually referenced (or note if no external sources were used)`;

  try {
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    // Try to parse JSON from the response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]);
    }

    // Fallback if JSON parsing fails
    return {
      mainFindings: ['Unable to parse structured response'],
      positiveEvidence: [],
      negativeEvidence: [],
      missingInformation: ['Structured parsing failed'],
      riskFactors: [],
      citations: [{ text: 'AI-generated content', url: null }],
    };
  } catch (error) {
    console.error('Research agent error:', error);
    throw new Error(`Research agent failed: ${error.message}`);
  }
}

module.exports = { analyze };
