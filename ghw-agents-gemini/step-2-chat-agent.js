import { GoogleGenAI } from "@google/genai";
import "dotenv/config";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

// Create the Gemini client
const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});

// Create a chat session.
// Gemini will keep the conversation history for this session.
const chat = ai.chats.create({
  model: "gemini-3.6-flash",
  config: {
    systemInstruction: `
      You are a friendly AI mentor helping beginner developers.

      Keep your answers concise and easy to understand.
      Explain technical concepts using simple examples.
    `,
  },
});

// Create a terminal interface
const rl = readline.createInterface({
  input,
  output,
});

console.log("🤖 Gemini AI Agent");
console.log("Type 'exit' anytime to quit.\n");

while (true) {
  const question = await rl.question("You: ");

  if (question.toLowerCase() === "exit") {
    console.log("\n👋 Goodbye!");
    break;
  }

  try {
    const response = await chat.sendMessage({
      message: question,
    });

    console.log(`\n🤖 Gemini: ${response.text}\n`);
  } catch (error) {
    console.error("\n❌ Something went wrong:");
    console.error(error.message);
    console.log();
  }
}

rl.close();