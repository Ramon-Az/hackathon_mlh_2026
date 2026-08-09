import { GoogleGenAI, Type } from "@google/genai";
import "dotenv/config";
import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});

const rl = readline.createInterface({
  input,
  output,
});

// Tool 1: Weather (real API - OpenWeatherMap)
async function getWeather(location) {
  const apiKey = process.env.OPENWEATHER_API_KEY;
  
  if (!apiKey) {
    // Fallback to mock data if no API key
    const weatherData = {
      lagos: { temperature: 30, condition: "Sunny", humidity: 70, windSpeed: 5 },
      london: { temperature: 18, condition: "Cloudy", humidity: 80, windSpeed: 10 },
      "new york": { temperature: 24, condition: "Partly cloudy", humidity: 65, windSpeed: 8 },
    };
    const result = weatherData[location.toLowerCase()];
    if (!result) {
      return { location, message: "Weather data not available for this location." };
    }
    return { location, ...result, source: "mock" };
  }

  // Normalize input: remove extra spaces, fix common patterns
  const cleanLocation = location.trim()
    .replace(/\s*,\s*/g, ",")           // "São Paulo , BR" -> "São Paulo,BR"
    .replace(/\s+/g, " ");              // multiple spaces -> single

  // Generate multiple query variations to try
  const queries = generateLocationQueries(cleanLocation);

  for (const query of queries) {
    try {
      const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(query)}&units=metric&appid=${apiKey}&lang=pt_br`;
      const response = await fetch(url);
      
      if (response.ok) {
        const data = await response.json();
        return formatWeatherResponse(data, query);
      }
      
      if (response.status === 401) {
        // Invalid/unauthorized API key - fall back to mock immediately
        console.warn("⚠️ OpenWeatherMap API key invalid (401). Using mock data.");
        return getMockWeather(cleanLocation);
      }
      
      if (response.status !== 404) {
        throw new Error(`API error: ${response.status}`);
      }
      // 404 = try next query variation
    } catch (error) {
      if (error.message.includes("API error")) throw error;
      // Network error = try next variation
    }
  }

  // All variations failed
  return { 
    location: cleanLocation, 
    message: `City not found. Tried: ${queries.join(", ")}`,
    suggestions: getSuggestions(cleanLocation)
  };
}

function generateLocationQueries(location) {
  const queries = new Set();
  const lower = location.toLowerCase();
  
  // Original as typed
  queries.add(location);
  
  // If contains comma, try parts separately
  if (location.includes(",")) {
    const parts = location.split(",").map(p => p.trim());
    queries.add(parts[0]);                    // Just city: "Parintins"
    queries.add(`${parts[0]},${parts[1]}`);   // City,State: "Parintins,AM"
    queries.add(`${parts[0]},${parts[1]},${parts[2] || "BR"}`); // City,State,Country
  } else {
    // No comma - try with common Brazilian state codes
    const brStates = ["AM", "SP", "RJ", "MG", "RS", "SC", "PR", "BA", "CE", "PE", "GO", "DF", "ES", "PA", "PB", "RN", "PI", "MA", "MT", "MS", "RO", "RR", "TO", "AC", "AP", "SE", "AL"];
    queries.add(`${location},BR`);
    for (const state of brStates) {
      queries.add(`${location},${state},BR`);
    }
    // Also try just the city name (OpenWeather sometimes resolves it)
    queries.add(location);
  }
  
  // Remove duplicates, limit attempts
  return Array.from(queries).slice(0, 10);
}

function formatWeatherResponse(data, queryUsed) {
  return {
    location: data.name,
    state: data.sys.state || "",
    country: data.sys.country,
    temperature: Math.round(data.main.temp),
    feelsLike: Math.round(data.main.feels_like),
    condition: data.weather[0].main,
    description: data.weather[0].description,
    humidity: data.main.humidity,
    windSpeed: data.wind.speed,
    windDirection: data.wind.deg,
    pressure: data.main.pressure,
    sunrise: new Date(data.sys.sunrise * 1000).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
    sunset: new Date(data.sys.sunset * 1000).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
    source: "openweathermap",
    queryUsed
  };
}

function getSuggestions(location) {
  // Common Brazilian cities for suggestions
  const commonCities = [
    "São Paulo,SP,BR", "Rio de Janeiro,RJ,BR", "Brasília,DF,BR", 
    "Salvador,BA,BR", "Fortaleza,CE,BR", "Belo Horizonte,MG,BR",
    "Manaus,AM,BR", "Curitiba,PR,BR", "Recife,PE,BR", "Porto Alegre,RS,BR",
    "Belém,PA,BR", "Goiânia,GO,BR", "Guarulhos,SP,BR", "Campinas,SP,BR",
    "São Luís,MA,BR", "São Gonçalo,RJ,BR", "Maceió,AL,BR", "Duque de Caxias,RJ,BR",
    "Natal,RN,BR", "Teresina,PI,BR", "Campo Grande,MS,BR", "João Pessoa,PB,BR",
    "Jaboatão dos Guararapes,PE,BR", "São José dos Campos,SP,BR", "Ribeirão Preto,SP,BR",
    "Uberlândia,MG,BR", "Sorocaba,SP,BR", "Contagem,MG,BR", "Aracaju,SE,BR",
    "Feira de Santana,BA,BR", "Cuiabá,MT,BR", "Joinville,SC,BR", "Juiz de Fora,MG,BR",
    "Londrina,PR,BR", "Niterói,RJ,BR", "Ananindeua,PA,BR", "São Bernardo do Campo,SP,BR",
    "Parintins,AM,BR"
  ];
  
  const lower = location.toLowerCase();
  return commonCities
    .filter(c => c.toLowerCase().includes(lower) || lower.includes(c.split(",")[0].toLowerCase()))
    .slice(0, 5);
}

function getMockWeather(location) {
  const lower = location.toLowerCase();
  
  // Try to match known cities
  const mockData = {
    "parintins": { temperature: 28, condition: "Clouds", description: "nuvens dispersas", humidity: 85, windSpeed: 3, feelsLike: 31 },
    "manaus": { temperature: 29, condition: "Rain", description: "chuva leve", humidity: 88, windSpeed: 4, feelsLike: 33 },
    "são paulo": { temperature: 22, condition: "Clouds", description: "nublado", humidity: 70, windSpeed: 8, feelsLike: 23 },
    "rio de janeiro": { temperature: 28, condition: "Clear", description: "céu limpo", humidity: 65, windSpeed: 6, feelsLike: 30 },
    "brasilia": { temperature: 25, condition: "Clear", description: "ensolarado", humidity: 55, windSpeed: 10, feelsLike: 25 },
    "salvador": { temperature: 27, condition: "Clouds", description: "parcialmente nublado", humidity: 75, windSpeed: 12, feelsLike: 29 },
    "fortaleza": { temperature: 30, condition: "Clear", description: "sol", humidity: 70, windSpeed: 15, feelsLike: 32 },
    "belo horizonte": { temperature: 24, condition: "Clouds", description: "nublado", humidity: 68, windSpeed: 7, feelsLike: 25 },
    "curitiba": { temperature: 18, condition: "Rain", description: "chuva", humidity: 80, windSpeed: 5, feelsLike: 17 },
    "recife": { temperature: 28, condition: "Clouds", description: "parcialmente nublado", humidity: 75, windSpeed: 10, feelsLike: 30 },
    "porto alegre": { temperature: 16, condition: "Rain", description: "chuva moderada", humidity: 85, windSpeed: 12, feelsLike: 14 },
  };
  
  // Find best match
  let match = null;
  for (const [city, data] of Object.entries(mockData)) {
    if (lower.includes(city) || city.includes(lower)) {
      match = data;
      break;
    }
  }
  
  if (!match) {
    // Generic tropical default
    match = { temperature: 26, condition: "Clouds", description: "parcialmente nublado", humidity: 75, windSpeed: 5, feelsLike: 28 };
  }
  
  return {
    location: location.split(",")[0],
    country: "BR",
    temperature: match.temperature,
    feelsLike: match.feelsLike,
    condition: match.condition,
    description: match.description,
    humidity: match.humidity,
    windSpeed: match.windSpeed,
    pressure: 1013,
    sunrise: "06:00",
    sunset: "18:00",
    source: "mock",
    note: "Using mock data - OpenWeatherMap API key invalid or not activated"
  };
}

// Tool 2: Calculator (real math)
function calculate(expression) {
  try {
    // Safe eval alternative - only allows basic math
    const sanitized = expression.replace(/[^0-9+\-*/().\s]/g, "");
    const result = Function(`"use strict"; return (${sanitized})`)();
    return { expression, result };
  } catch (e) {
    return { expression, error: "Invalid expression" };
  }
}

// Tool 3: Web Search (simulated)
function searchWeb(query) {
  const mockResults = {
    "javascript": [
      { title: "JavaScript - MDN Web Docs", url: "https://developer.mozilla.org/en-US/docs/Web/JavaScript", snippet: "JavaScript is a lightweight, interpreted programming language." },
      { title: "JavaScript Tutorial - W3Schools", url: "https://www.w3schools.com/js/", snippet: "Learn JavaScript with interactive exercises." },
    ],
    "node.js": [
      { title: "Node.js Official Website", url: "https://nodejs.org/", snippet: "Node.js is a JavaScript runtime built on Chrome's V8 engine." },
      { title: "Node.js Docs", url: "https://nodejs.org/en/docs/", snippet: "Official Node.js documentation and guides." },
    ],
    "gemini api": [
      { title: "Google AI for Developers - Gemini API", url: "https://ai.google.dev/", snippet: "Build with Gemini API - Google's most capable AI model." },
      { title: "Gemini API Documentation", url: "https://ai.google.dev/docs", snippet: "Complete reference for the Gemini API." },
    ],
  };

  const key = query.toLowerCase();
  const results = mockResults[key] || [
    { title: `Search results for "${query}"`, url: "https://www.google.com", snippet: "Mock search result - replace with real search API." },
  ];

  return { query, results, count: results.length };
}

// Tool 4: Currency Converter (simulated with fixed rates)
function convertCurrency({ from, to, amount }) {
  const rates = {
    USD: { BRL: 5.2, EUR: 0.92, GBP: 0.79, JPY: 150 },
    BRL: { USD: 0.19, EUR: 0.18, GBP: 0.15, JPY: 28.8 },
    EUR: { USD: 1.09, BRL: 5.65, GBP: 0.86, JPY: 163 },
    GBP: { USD: 1.27, BRL: 6.58, EUR: 1.16, JPY: 190 },
    JPY: { USD: 0.0067, BRL: 0.035, EUR: 0.0061, GBP: 0.0053 },
  };

  const fromUpper = from.toUpperCase();
  const toUpper = to.toUpperCase();

  if (!rates[fromUpper] || !rates[fromUpper][toUpper]) {
    return { from, to, amount, error: `Conversion from ${from} to ${to} not available.` };
  }

  const rate = rates[fromUpper][toUpper];
  const converted = (amount * rate).toFixed(2);

  return { from: fromUpper, to: toUpper, amount, rate, converted: Number(converted) };
}

// Tell Gemini about BOTH tools
const weatherTool = {
  name: "getWeather",
  description: "Get the current weather for a location.",
  parameters: {
    type: Type.OBJECT,
    properties: {
      location: { type: Type.STRING, description: "The city to get weather for." },
    },
    required: ["location"],
  },
};

const calculatorTool = {
  name: "calculate",
  description: "Evaluate a mathematical expression.",
  parameters: {
    type: Type.OBJECT,
    properties: {
      expression: { type: Type.STRING, description: "Math expression like '2 + 2' or '10 * 5.5'" },
    },
    required: ["expression"],
  },
};

const searchTool = {
  name: "searchWeb",
  description: "Search the web for information on a topic.",
  parameters: {
    type: Type.OBJECT,
    properties: {
      query: { type: Type.STRING, description: "Search query, e.g. 'javascript tutorial' or 'node.js best practices'" },
    },
    required: ["query"],
  },
};

const currencyTool = {
  name: "convertCurrency",
  description: "Convert an amount from one currency to another.",
  parameters: {
    type: Type.OBJECT,
    properties: {
      from: { type: Type.STRING, description: "Source currency code (e.g. USD, BRL, EUR)" },
      to: { type: Type.STRING, description: "Target currency code (e.g. USD, BRL, EUR)" },
      amount: { type: Type.NUMBER, description: "Amount to convert" },
    },
    required: ["from", "to", "amount"],
  },
};

console.log("🤖 Gemini Tool Agent (Weather + Calculator + Search + Currency)");
console.log("Ask me something. Type 'exit' to quit.\n");

while (true) {
  const userQuestion = await rl.question("You: ");

  if (userQuestion.toLowerCase() === "exit") {
    console.log("\n👋 Goodbye!");
    break;
  }

  try {
    const response = await ai.models.generateContent({
      model: "gemini-3.6-flash",
      contents: userQuestion,
config: {
      tools: [
        {
          functionDeclarations: [weatherTool, calculatorTool, searchTool, currencyTool],
        },
      ],
    },
    });

    const functionCall = response.functionCalls?.[0];

    if (!functionCall) {
      console.log(`\n🤖 Gemini: ${response.text}\n`);
      continue;
    }

    console.log("\n🔧 Gemini decided to use a tool:");
    console.log(functionCall);

    // Execute the appropriate tool
    let toolResult;
    if (functionCall.name === "getWeather") {
      toolResult = await getWeather(functionCall.args.location);
    } else if (functionCall.name === "calculate") {
      toolResult = calculate(functionCall.args.expression);
    } else if (functionCall.name === "searchWeb") {
      toolResult = searchWeb(functionCall.args.query);
    } else if (functionCall.name === "convertCurrency") {
      toolResult = convertCurrency(functionCall.args);
    } else {
      toolResult = { error: `Unknown tool: ${functionCall.name}` };
    }

    console.log("\n📊 Tool result:");
    console.log(toolResult);

    const modelContent = response.candidates[0].content;

    const finalResponse = await ai.models.generateContent({
      model: "gemini-3.6-flash",
      contents: [
        { role: "user", parts: [{ text: userQuestion }] },
        modelContent,
        {
          role: "user",
          parts: [
            {
              functionResponse: {
                name: functionCall.name,
                response: toolResult,
              },
            },
          ],
        },
      ],
      config: {
        tools: [
          { functionDeclarations: [weatherTool, calculatorTool, searchTool, currencyTool] },
        ],
      },
    });

    console.log(`\n🤖 Gemini: ${finalResponse.text}\n`);
  } catch (error) {
    console.error("\n❌ Something went wrong:");
    console.error(error.message);
    console.log();
  }
}

rl.close();