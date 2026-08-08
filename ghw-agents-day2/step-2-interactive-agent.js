import OpenAI from "openai";
import "dotenv/config";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const rl = readline.createInterface({
  input,
  output,
});

console.log("🤖 Welcome to your first AI Agent!");
console.log("Type 'exit' anytime to quit.\n");

while (true) {
  const question = await rl.question("You: ");

  if (question.toLowerCase() === "exit") {
    console.log("👋 Goodbye!");
    break;
  }

  const response = await client.responses.create({
    model: "gpt-5-mini",

    instructions: `
      You are a friendly AI mentor helping beginner developers.
      Keep answers concise.
      Explain technical concepts in simple language.
    `,

    input: question,
  });

  console.log(`\n🤖 Agent: ${response.output_text}\n`);
}

rl.close();
