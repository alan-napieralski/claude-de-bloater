const { formatWeather } = require("./format");

async function fetchWeather(city, apiKey) {
  const response = await fetch(
    `https://api.example.com/weather?city=${encodeURIComponent(city)}&key=${apiKey}`
  );
  if (!response.ok) {
    throw new Error(`Weather lookup failed for "${city}"`);
  }
  return response.json();
}

async function main() {
  const city = process.argv[2];
  const apiKey = process.env.WEATHER_API_KEY;

  if (!city) {
    console.error("Usage: node src/cli.js <city>");
    process.exit(1);
  }
  if (!apiKey) {
    console.error("Missing WEATHER_API_KEY environment variable.");
    process.exit(1);
  }

  try {
    const data = await fetchWeather(city, apiKey);
    console.log(formatWeather(city, data.tempC, data.windSpeed, data.conditions));
  } catch (error) {
    console.error(error.message);
    process.exit(1);
  }
}

main();
