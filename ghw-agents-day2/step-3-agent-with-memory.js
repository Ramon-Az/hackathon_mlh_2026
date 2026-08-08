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

// This array stores our conversation history.
// It acts as temporary memory while the app is running.
const history = [];

async function main() {
  console.log("🤖 AI Agent with Memory");
  console.log("Type 'exit' anytime to quit.\n");

  while (true) {
    let question;
    try {
      question = await rl.question("You: ");
    } catch {
      break;
    }

    if (question.toLowerCase() === "exit") {
      console.log("👋 Goodbye!");
      break;
    }

    // Save the user's message to memory.
    history.push({
      role: "user",
      content: question,
    });

    const response = await client.responses.create({
      model: "gpt-5-mini",

      instructions: `
        You are a friendly AI mentor helping beginner developers.
        Keep answers concise.
        Explain technical concepts in simple language.
      `,

      // Instead of sending only the newest question,
      // we send the entire conversation history.
      input: history,
    });

    const answer = response.output_text;

    console.log(`\n🤖 Agent: ${answer}\n`);

    // Save the agent's response too.
    history.push({
      role: "assistant",
      content: answer,
    });
  }
  
  rl.close();
  process.exit(0);
}

main();