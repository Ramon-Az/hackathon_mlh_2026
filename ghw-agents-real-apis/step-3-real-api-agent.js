// STEP 3:
// Let Groq decide when to call a REAL API.
//
// Groq is OpenAI-compatible, so we use the OpenAI SDK
// pointed at https://api.groq.com/openai/v1.
//
// User
//   ↓
// Groq (LLaMA 3.3 70B)
//   ↓
// Need the weather tool?
//   ↓
// getWeather() → real Open-Meteo API
//   ↓
// Tool result
//   ↓
// Groq gives the final answer

import OpenAI from "openai";
import "dotenv/config";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

const client = new OpenAI({
  apiKey: process.env.GROQ_API_KEY,
  baseURL: "https://api.groq.com/openai/v1",
});

const MODEL = process.env.GROQ_MODEL || "llama-3.3-70b-versatile";

const rl = readline.createInterface({
  input,
  output,
});

// -----------------------------------
// REAL WEATHER TOOL
// -----------------------------------

async function getWeather(city) {
  console.log(`\n🔍 Looking up "${city}"...`);

  // 1. Find city coordinates
  const geocodingUrl =
    `https://geocoding-api.open-meteo.com/v1/search` +
    `?name=${encodeURIComponent(city)}` +
    `&count=1` +
    `&language=en` +
    `&format=json`;

  const locationResponse = await fetch(geocodingUrl);

  if (!locationResponse.ok) {
    throw new Error("Could not reach the geocoding API.");
  }

  const locationData = await locationResponse.json();

  if (!locationData.results?.length) {
    return {
      error: `Could not find a location called "${city}".`,
    };
  }

  const location = locationData.results[0];

  // 2. Fetch real weather
  const weatherUrl =
    `https://api.open-meteo.com/v1/forecast` +
    `?latitude=${location.latitude}` +
    `&longitude=${location.longitude}` +
    `&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m` +
    `&timezone=auto`;

  const weatherResponse = await fetch(weatherUrl);

  if (!weatherResponse.ok) {
    throw new Error("Could not reach the weather API.");
  }

  const weatherData = await weatherResponse.json();

  // 3. Return clean data
  return {
    city: location.name,
    country: location.country,
    temperature: weatherData.current.temperature_2m,
    feelsLike: weatherData.current.apparent_temperature,
    windSpeed: weatherData.current.wind_speed_10m,
    weatherCode: weatherData.current.weather_code,
    units: {
      temperature: weatherData.current_units.temperature_2m,
      windSpeed: weatherData.current_units.wind_speed_10m,
    },
  };
}

// -----------------------------------
// TELL GROQ ABOUT THE TOOL (OpenAI format)
// -----------------------------------

const weatherTool = {
  type: "function",
  function: {
    name: "getWeather",
    description:
      "Get the current real-world weather for a city using a live weather API.",
    parameters: {
      type: "object",
      properties: {
        city: {
          type: "string",
          description: "The city to get current weather information for.",
        },
      },
      required: ["city"],
    },
  },
};

console.log("🤖 Real API Weather Agent (Groq)");
console.log("Ask me about the weather in any city.");
console.log("Type 'exit' to quit.\n");

while (true) {
  const userQuestion = await rl.question("You: ").catch(() => null);

  // EOF (e.g. piped input ended) → stop gracefully
  if (userQuestion === null) break;

  if (userQuestion.toLowerCase() === "exit") {
    console.log("\n👋 Goodbye!");
    break;
  }

  try {
    // Conversation so far: just the user's question
    const messages = [{ role: "user", content: userQuestion }];

    // Ask Groq what to do
    const response = await client.chat.completions.create({
      model: MODEL,
      messages,
      tools: [weatherTool],
    });

    const message = response.choices[0].message;

    const toolCall = message.tool_calls?.[0];

    // Groq does not need a tool
    if (!toolCall) {
      console.log(`\n🤖 Groq: ${message.content}\n`);
      continue;
    }

    console.log("\n🧠 Groq decided to use:");
    console.log(toolCall.function.name, toolCall.function.arguments);

    // Execute the real tool
    const args = JSON.parse(toolCall.function.arguments);
    const toolResult = await getWeather(args.city);

    console.log("\n🌍 Real API result:");
    console.log(toolResult);

    // Send the real-world result back to Groq
    messages.push(message);
    messages.push({
      role: "tool",
      tool_call_id: toolCall.id,
      content: JSON.stringify(toolResult),
    });

    const finalResponse = await client.chat.completions.create({
      model: MODEL,
      messages,
      tools: [weatherTool],
    });

    console.log(`\n🤖 Groq: ${finalResponse.choices[0].message.content}\n`);
  } catch (error) {
    console.error("\n❌ Something went wrong:");
    console.error(error.message);
    console.log();
  }
}

rl.close();
