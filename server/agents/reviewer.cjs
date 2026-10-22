/**
 * Independent Review Agent
 * Uses Gemini to review the research agent's claims and flag issues
 */

async function review(query, researchReport, financialSnapshot, model) {
  const prompt = `You are an independent financial reviewer. Review the research report below and identify any issues, unsupported claims, or missing caveats.

Original Query: ${query}

Research Report:
${JSON.stringify(researchReport, null, 2)}

Financial Data: ${JSON.stringify(financialSnapshot || {})}

Provide a response in the following JSON format:
{
  "comments": [
    "Issue 1: description of the problem",
    "Issue 2: description of the problem",
    ...
  ]
}

Review criteria:
- Check if claims are supported by available evidence
- Identify any numerical inconsistencies
- Flag missing caveats or limitations
- Note any assumptions that should be explicit
- Highlight statements that appear to be presented as facts without verification
- Be specific and constructive in your feedback`;

  try {
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    // Try to parse JSON from the response
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return { comments: parsed.comments || [] };
    }

    // Fallback if JSON parsing fails
    return {
      comments: ['Unable to parse structured review response'],
    };
  } catch (error) {
    console.error('Reviewer agent error:', error);
    throw new Error(`Reviewer agent failed: ${error.message}`);
  }
}

module.exports = { review };
