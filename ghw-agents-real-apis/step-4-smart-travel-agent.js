// STEP 4:
// A full agent loop with Groq deciding which REAL APIs to call.
//
// 3 real tools:
//   - getWeather      → Open-Meteo
//   - getCountryInfo  → REST Countries
//   - convertCurrency → ExchangeRate-API
//
// The agent loops: model → tool call → real API → result → model
// until it has everything it needs, then gives the final answer.

import OpenAI from "openai";
import "dotenv/config";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

const client = new OpenAI({
  apiKey: process.env.GROQ_API_KEY,
  baseURL: "https://api.groq.com/openai/v1",
});

const MODEL = process.env.GROQ_MODEL || "llama-3.3-70b-versatile";

// -----------------------------------
// REAL TOOLS (no LLM involved)
// -----------------------------------

async function getWeather(city) {
  console.log(`\n🔍 Looking up weather for "${city}"...`);

  const geocodingUrl =
    `https://geocoding-api.open-meteo.com/v1/search` +
    `?name=${encodeURIComponent(city)}` +
    `&count=1&language=en&format=json`;

  const locationResponse = await fetch(geocodingUrl);
  if (!locationResponse.ok) {
    throw new Error("Could not reach the geocoding API.");
  }

  const locationData = await locationResponse.json();
  if (!locationData.results?.length) {
    return { error: `Could not find a location called "${city}".` };
  }

  const location = locationData.results[0];

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

async function getCountryInfo(country) {
  console.log(`\n🔍 Looking up info for "${country}"...`);

  // REST Countries v1-v4 was deprecated and now requires a paid API key.
  // CountriesNow is a free alternative that needs no key.
  // We fire 3 real API requests in parallel:
  const [capitalData, currencyData, populationData] = await Promise.all([
    fetch("https://countriesnow.space/api/v0.1/countries/capital").then(
      (r) => r.json()
    ),
    fetch("https://countriesnow.space/api/v0.1/countries/currency").then(
      (r) => r.json()
    ),
    fetch("https://countriesnow.space/api/v0.1/countries/population").then(
      (r) => r.json()
    ),
  ]);

  const lower = country.toLowerCase();

  const capitalEntry = capitalData.data?.find(
    (c) => c.name.toLowerCase() === lower
  );
  const currencyEntry = currencyData.data?.find(
    (c) => c.name.toLowerCase() === lower
  );
  const populationEntry = populationData.data?.find(
    (c) => c.country.toLowerCase() === lower || c.code === country.toUpperCase()
  );

  if (!capitalEntry || !currencyEntry) {
    return { error: `Could not find a country called "${country}".` };
  }

  const lastPopulation = populationEntry?.populationCounts?.at(-1);

  return {
    name: capitalEntry.name,
    capital: capitalEntry.capital,
    population: lastPopulation?.value,
    populationYear: lastPopulation?.year,
    currency: currencyEntry.currency,
    currencySymbol: currencyEntry.symbol ?? "N/A",
  };
}

async function convertCurrency(amount, fromCurrency, toCurrency) {
  console.log(
    `\n🔍 Converting ${amount} ${fromCurrency} to ${toCurrency}...`
  );

  const from = fromCurrency.toUpperCase();
  const to = toCurrency.toUpperCase();

  const url = `https://open.er-api.com/v6/latest/${from}`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Could not reach the exchange rate API.");
  }

  const data = await response.json();

  if (data.result !== "success") {
    return { error: `Could not convert ${from}.` };
  }

  const rate = data.rates[to];
  if (!rate) {
    return { error: `No exchange rate found for "${to}".` };
  }

  return {
    from: { currency: from, amount },
    to: { currency: to, amount: Number((amount * rate).toFixed(2)) },
    rate: data.rates[to],
  };
}

// -----------------------------------
// TELL GROQ ABOUT THE TOOLS (OpenAI format)
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

const countryTool = {
  type: "function",
  function: {
    name: "getCountryInfo",
    description:
      "Get real information about a country: capital, population, currency and currency symbol.",
    parameters: {
      type: "object",
      properties: {
        country: {
          type: "string",
          description: "The country to get information about.",
        },
      },
      required: ["country"],
    },
  },
};

const currencyTool = {
  type: "function",
  function: {
    name: "convertCurrency",
    description:
      "Convert an amount from one real-world currency to another using live exchange rates.",
    parameters: {
      type: "object",
      properties: {
        amount: {
          type: "number",
          description: "The amount of money to convert.",
        },
        fromCurrency: {
          type: "string",
          description: "The currency code to convert from (e.g. USD, BRL).",
        },
        toCurrency: {
          type: "string",
          description: "The currency code to convert to (e.g. EUR, JPY).",
        },
      },
      required: ["amount", "fromCurrency", "toCurrency"],
    },
  },
};

const tools = [weatherTool, countryTool, currencyTool];

// -----------------------------------
// AGENT LOOP
// -----------------------------------

const SYSTEM_PROMPT =
  "You are a helpful travel assistant. When the user asks about " +
  "weather, country info or currency conversion, use the tools to " +
  "get REAL, UP-TO-DATE data. Use all the tools you need before " +
  "answering. Always answer in the user's language.";

async function executeTool({ name, args }) {
  switch (name) {
    case "getWeather":
      return await getWeather(args.city);
    case "getCountryInfo":
      return await getCountryInfo(args.country);
    case "convertCurrency":
      return await convertCurrency(
        args.amount,
        args.fromCurrency,
        args.toCurrency
      );
    default:
      return { error: `Unknown tool: ${name}` };
  }
}

async function runAgent(userQuestion) {
  const MAX_STEPS = 5;

  const messages = [
    { role: "system", content: SYSTEM_PROMPT },
    { role: "user", content: userQuestion },
  ];

  for (let step = 1; step <= MAX_STEPS; step++) {
    console.log(`\n🔄 Agent loop — step ${step} of ${MAX_STEPS}`);

    // 1. Groq decides: answer now or call a tool?
    const response = await client.chat.completions.create({
      model: MODEL,
      messages,
      tools,
    });

    const message = response.choices[0].message;

    // 2. No tool calls → the agent is done
    if (!message.tool_calls?.length) {
      return message.content || "The agent completed the task.";
    }

    messages.push(message);

    // 3. Execute every tool call Groq requested (real APIs!)
    for (const toolCall of message.tool_calls) {
      const args = JSON.parse(toolCall.function.arguments);

      console.log(`\n🧠 Groq chose: ${toolCall.function.name}`);
      console.log("Arguments:", args);

      const result = await executeTool({
        name: toolCall.function.name,
        args,
      });

      console.log("\n📡 Real API result:");
      console.log(result);

      // 4. Send the real result back to Groq
      messages.push({
        role: "tool",
        tool_call_id: toolCall.id,
        content: JSON.stringify(result),
      });
    }
  }

  throw new Error(`Agent exceeded ${MAX_STEPS} steps.`);
}

// -----------------------------------
// CHAT LOOP
// -----------------------------------

const rl = readline.createInterface({ input, output });

console.log("🧳 Smart Travel Agent (Groq)");
console.log("Ask me about weather, country info and currency conversion.");
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
    const answer = await runAgent(userQuestion);
    console.log(`\n🤖 Groq: ${answer}\n`);
  } catch (error) {
    console.error("\n❌ Something went wrong:");
    console.error(error.message);
    console.log();
  }
}

rl.close();
