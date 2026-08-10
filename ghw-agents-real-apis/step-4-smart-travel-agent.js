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
// Keeps a sliding window of conversation history across turns,
// so follow-ups like "and what about Tokyo?" keep their context.

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
// UTILITIES (timeout + safe parse)
// -----------------------------------

async function fetchWithTimeout(url, ms = 10000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

function parseArgs(argString) {
  try {
    return JSON.parse(argString);
  } catch {
    return { error: "Model returned invalid JSON arguments." };
  }
}

// WMO weather codes -> human-readable description
// (see https://open-meteo.com/en/docs)
const WMO_WEATHER_CODES = {
  0: "clear sky",
  1: "mainly clear",
  2: "partly cloudy",
  3: "overcast",
  45: "fog",
  48: "depositing rime fog",
  51: "light drizzle",
  53: "moderate drizzle",
  55: "dense drizzle",
  56: "light freezing drizzle",
  57: "dense freezing drizzle",
  61: "slight rain",
  63: "moderate rain",
  65: "heavy rain",
  66: "light freezing rain",
  67: "heavy freezing rain",
  71: "slight snowfall",
  73: "moderate snowfall",
  75: "heavy snowfall",
  77: "snow grains",
  80: "slight rain showers",
  81: "moderate rain showers",
  82: "violent rain showers",
  85: "slight snow showers",
  86: "heavy snow showers",
  95: "thunderstorm",
  96: "thunderstorm with slight hail",
  99: "thunderstorm with heavy hail",
};

function describeWeatherCode(code) {
  return WMO_WEATHER_CODES[code] ?? `unknown weather code ${code}`;
}

// Groq wrapper with retry:
// - 429 (rate limit): waits and retries
// - 400 "Failed to call a function": the model generated an invalid
//   tool_call (hallucinated name/args). Usually intermittent, so a
//   second attempt often succeeds with a different generation.
async function callGroq(messages, tools) {
  const MAX_ATTEMPTS = 2;
  let lastError;

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      return await client.chat.completions.create({
        model: MODEL,
        messages,
        tools,
        // One tool at a time is far more reliable on Groq/llama:
        // parallel tool calls are the main source of invalid generations.
        parallel_tool_calls: false,
      });
    } catch (error) {
      lastError = error;

      if (error.status === 429) {
        await new Promise((r) => setTimeout(r, attempt * 2000));
        continue;
      }

      if (error.status === 400 && attempt < MAX_ATTEMPTS) {
        continue;
      }

      throw lastError;
    }
  }

  throw lastError;
}

// -----------------------------------
// CACHES (avoid re-downloading near-static data)
// -----------------------------------

const GEOCODE_CACHE = new Map(); // city -> location object
let countriesCache = null; // full countries lists, loaded once
const RATE_CACHE = new Map(); // base currency -> { rates, fetchedAt }
const RATE_TTL = 60 * 60 * 1000; // exchange rates are valid for 1h

// -----------------------------------
// REAL TOOLS (no LLM involved)
// -----------------------------------

async function getWeather(city) {
  console.log(`\n🔍 Looking up weather for "${city}"...`);

  // Geocoding is cached per city (coordinates barely change)
  let location = GEOCODE_CACHE.get(city.toLowerCase());
  if (!location) {
    const geocodingUrl =
      `https://geocoding-api.open-meteo.com/v1/search` +
      `?name=${encodeURIComponent(city)}` +
      `&count=1&language=en&format=json`;

    const locationResponse = await fetchWithTimeout(geocodingUrl);
    if (!locationResponse.ok) {
      throw new Error("Could not reach the geocoding API.");
    }

    const locationData = await locationResponse.json();
    if (!locationData.results?.length) {
      return { error: `Could not find a location called "${city}".` };
    }

    location = locationData.results[0];
    GEOCODE_CACHE.set(city.toLowerCase(), location);
  }

  const weatherUrl =
    `https://api.open-meteo.com/v1/forecast` +
    `?latitude=${location.latitude}` +
    `&longitude=${location.longitude}` +
    `&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m` +
    `&timezone=auto`;

  const weatherResponse = await fetchWithTimeout(weatherUrl);
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
    sky: describeWeatherCode(weatherData.current.weather_code),
    units: {
      temperature: weatherData.current_units.temperature_2m,
      windSpeed: weatherData.current_units.wind_speed_10m,
    },
  };
}

async function fetchCountriesData() {
  if (countriesCache) return countriesCache;

  // REST Countries v1-v4 was deprecated and now requires a paid API key.
  // CountriesNow is a free alternative that needs no key.
  // We fire 3 real API requests in parallel, but only ONCE per session:
  const urls = [
    "https://countriesnow.space/api/v0.1/countries/capital",
    "https://countriesnow.space/api/v0.1/countries/currency",
    "https://countriesnow.space/api/v0.1/countries/population",
  ];

  const responses = await Promise.all(urls.map((url) => fetchWithTimeout(url)));
  const failed = responses.find((r) => !r.ok);
  if (failed) {
    throw new Error("Could not reach the country info API.");
  }

  const [capitalData, currencyData, populationData] = await Promise.all(
    responses.map((r) => r.json())
  );

  countriesCache = { capitalData, currencyData, populationData };
  return countriesCache;
}

async function getCountryInfo(country) {
  console.log(`\n🔍 Looking up info for "${country}"...`);

  const { capitalData, currencyData, populationData } =
    await fetchCountriesData();

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

  // Cache rates per base currency, refreshed at most once per hour
  let cached = RATE_CACHE.get(from);
  if (!cached || Date.now() - cached.fetchedAt > RATE_TTL) {
    const url = `https://open.er-api.com/v6/latest/${from}`;

    const response = await fetchWithTimeout(url);
    if (!response.ok) {
      throw new Error("Could not reach the exchange rate API.");
    }

    const data = await response.json();

    if (data.result !== "success") {
      return { error: `Could not convert ${from}.` };
    }

    cached = { rates: data.rates, fetchedAt: Date.now() };
    RATE_CACHE.set(from, cached);
  }

  const rate = cached.rates[to];
  if (!rate) {
    return { error: `No exchange rate found for "${to}".` };
  }

  return {
    from: { currency: from, amount },
    to: { currency: to, amount: Number((amount * rate).toFixed(2)) },
    rate,
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
      "Convert an amount from one real-world currency to another using live exchange rates. amount must be a plain number (e.g. 100, never '100 reais'). fromCurrency and toCurrency must be 3-letter ISO codes (e.g. USD, BRL, JPY).",
    parameters: {
      type: "object",
      properties: {
        amount: {
          type: "number",
          description: "The amount of money to convert, as a plain number.",
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
  "answering. Always answer in the user's language. " +
  "Only call the tools provided: getWeather, getCountryInfo, " +
  "convertCurrency. Never invent function names or parameters — " +
  "match the JSON schema exactly.";

const MAX_HISTORY_MESSAGES = 10; // sliding window of past turns

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

async function runAgent(userQuestion, history = []) {
  const MAX_STEPS = 5;

  const messages = [
    { role: "system", content: SYSTEM_PROMPT },
    ...history,
    { role: "user", content: userQuestion },
  ];

  for (let step = 1; step <= MAX_STEPS; step++) {
    console.log(`\n🔄 Agent loop — step ${step} of ${MAX_STEPS}`);

    // 1. Groq decides: answer now or call a tool?
    const response = await callGroq(messages, tools);

    const message = response.choices[0].message;

    // 2. No tool calls → the agent is done
    if (!message.tool_calls?.length) {
      const answer = message.content || "The agent completed the task.";
      return {
        answer,
        turn: [
          { role: "user", content: userQuestion },
          { role: "assistant", content: answer },
        ],
      };
    }

    messages.push(message);

    // 3. Execute every tool call Groq requested (real APIs!)
    for (const toolCall of message.tool_calls) {
      // Safely parse args: a malformed JSON must not crash the agent
      const args = parseArgs(toolCall.function.arguments);

      let result;
      if (args.error) {
        result = args;
      } else {
        console.log(`\n🧠 Groq chose: ${toolCall.function.name}`);
        console.log("Arguments:", args);

        try {
          result = await executeTool({
            name: toolCall.function.name,
            args,
          });
        } catch (error) {
          // Tool failure becomes a message for the model, not a crash
          result = { error: error.message };
        }

        console.log("\n📡 Real API result:");
        console.log(result);
      }

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

let conversationHistory = []; // cross-turn memory (sliding window)

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
    const { answer, turn } = await runAgent(userQuestion, conversationHistory);

    // Keep the new turn and trim the oldest messages
    conversationHistory.push(...turn);
    if (conversationHistory.length > MAX_HISTORY_MESSAGES) {
      conversationHistory = conversationHistory.slice(-MAX_HISTORY_MESSAGES);
    }

    console.log(`\n🤖 Groq: ${answer}\n`);
  } catch (error) {
    console.error("\n❌ Something went wrong:");
    console.error(error.message);
    console.log();
  }
}

rl.close();
