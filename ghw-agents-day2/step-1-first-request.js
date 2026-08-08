import OpenAI from "openai";
import "dotenv/config";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const response = await client.responses.create({
  model: "gpt-5-mini",
  input: "Explain what an AI agent is to a beginner in 3 sentences.",
});

console.log(response.output_text);
