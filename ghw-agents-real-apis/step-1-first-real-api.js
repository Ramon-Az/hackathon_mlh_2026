// STEP 1:
// Calling a real API directly from Node.js.
// No Gemini. No AI. Just our application talking to an external API.

const latitude = 6.5244;
const longitude = 3.3792;

const url =
  `https://api.open-meteo.com/v1/forecast` +
  `?latitude=${latitude}` +
  `&longitude=${longitude}` +
  `&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m` +
  `&timezone=auto`;

console.log("🌍 Calling the Open-Meteo Weather API...\n");

try {
  // Send an HTTP GET request to the API
  const response = await fetch(url);

  // Check whether the request succeeded
  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}`
    );
  }

  // Convert the JSON response into a JavaScript object
  const data = await response.json();

  console.log("📦 Raw API response:\n");
  console.log(data);

  console.log("\n-----------------------------------\n");

  console.log("🌤️ Current Weather in Lagos\n");

  console.log(
    `Temperature: ${data.current.temperature_2m}${data.current_units.temperature_2m}`
  );

  console.log(
    `Feels like: ${data.current.apparent_temperature}${data.current_units.apparent_temperature}`
  );

  console.log(
    `Wind speed: ${data.current.wind_speed_10m}${data.current_units.wind_speed_10m}`
  );

  console.log(`Weather code: ${data.current.weather_code}`);
} catch (error) {
  console.error("❌ Something went wrong:");
  console.error(error.message);
}