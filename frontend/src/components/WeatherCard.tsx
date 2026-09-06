import React from "react";
import type { Weather } from "../types/trip";

interface WeatherCardProps {
  weather: Weather[];
}

const getWeatherDescription = (code?: number) => {
  if (code === undefined) return "Weather forecast";

  if (code === 0) return "☀️ Clear sky";
  if ([1, 2, 3].includes(code)) return "⛅ Partly cloudy";
  if ([45, 48].includes(code)) return "🌫️ Fog";
  if ([51, 53, 55].includes(code)) return "🌦️ Drizzle";
  if ([61, 63, 65].includes(code)) return "🌧️ Rain";
  if ([71, 73, 75, 77].includes(code)) return "❄️ Snow";
  if ([80, 81, 82].includes(code)) return "🌧️ Rain showers";
  if ([95, 96, 99].includes(code)) return "⛈️ Thunderstorm";

  return "🌤️ Weather forecast";
};

const WeatherCard = ({ weather }: WeatherCardProps) => {
  if (!weather || weather.length === 0) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 text-center">
        <p className="text-sm text-slate-400">
          Weather information is not available.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
      {weather.map((item, index) => {
        // Support both backend and frontend field names
        const maxTemp =
          item.temp_max ?? item.temperature_max;

        const minTemp =
          item.temp_min ?? item.temperature_min;

        const weatherCode =
          item.weathercode ?? item.weather_code;

        const description =
          item.description ??
          getWeatherDescription(weatherCode);

        return (
          <div
            key={`${item.date || "weather"}-${index}`}
            className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.05] p-5 shadow-xl backdrop-blur-xl transition duration-300 hover:-translate-y-1 hover:border-cyan-400/30 hover:bg-white/[0.08]"
          >
            {/* Date */}
            <div className="flex items-center justify-between">
              <p className="text-sm font-bold text-white">
                {item.date || "Date"}
              </p>

              <span className="text-2xl">
                {weatherCode === 0 ? "☀️" : "🌤️"}
              </span>
            </div>

            {/* Description */}
            <p className="mt-3 text-sm font-medium text-slate-300">
              {description}
            </p>

            {/* Temperature */}
            <div className="mt-5">
              <p className="text-4xl font-black text-cyan-400">
                {maxTemp !== undefined
                  ? `${maxTemp}°C`
                  : "--"}
              </p>

              {minTemp !== undefined && (
                <p className="mt-1 text-sm text-slate-400">
                  Min: {minTemp}°C
                </p>
              )}
            </div>

            {/* Weather Details */}
            <div className="mt-5 space-y-3 border-t border-white/10 pt-4">
              {item.precipitation !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">
                    🌧️ Precipitation
                  </span>

                  <span className="text-xs font-semibold text-slate-300">
                    {item.precipitation} mm
                  </span>
                </div>
              )}

              {item.precipitation_probability !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">
                    💧 Rain Probability
                  </span>

                  <span className="text-xs font-semibold text-slate-300">
                    {item.precipitation_probability}%
                  </span>
                </div>
              )}

              {item.wind_speed !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">
                    💨 Wind
                  </span>

                  <span className="text-xs font-semibold text-slate-300">
                    {item.wind_speed} km/h
                  </span>
                </div>
              )}
            </div>

            {/* Weather Code */}
            {weatherCode !== undefined && (
              <p className="mt-4 text-[10px] text-slate-600">
                Weather code: {weatherCode}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default WeatherCard;