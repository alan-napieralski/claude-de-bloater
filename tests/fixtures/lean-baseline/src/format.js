function toFahrenheit(celsius) {
  return Math.round((celsius * 9) / 5 + 32);
}

function formatWeather(city, celsius, windSpeed, conditions) {
  const fahrenheit = toFahrenheit(celsius);
  return [
    city,
    `${celsius}°C (${fahrenheit}°F)`,
    `${conditions}, wind ${windSpeed}`,
  ].join("\n");
}

module.exports = { formatWeather, toFahrenheit };
