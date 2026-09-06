import React from "react";
import type { Weather } from "../types/trip";

interface WeatherCardProps {
  weather: Weather[];
}

const WeatherCard = ({ weather }: WeatherCardProps) => {
  if (!weather || weather.length === 0) {
    return null;
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {weather.map((item, index) => (
        <div
          key={`${item.date || "weather"}-${index}`}
          className="rounded-xl border bg-white p-5 shadow-sm"
        >
          {/* Date */}
          <p className="text-sm font-semibold text-slate-900">
            {item.date || "Date"}
          </p>

          {/* Weather Description */}
          {item.description && (
            <p className="mt-2 text-sm font-medium text-slate-500">
              {item.description}
            </p>
          )}

          {/* Temperature */}
          <div className="mt-4">
            <p className="text-3xl font-bold text-blue-600">
              {item.temperature_max !== undefined
                ? `${item.temperature_max}°C`
                : "--"}
            </p>

            {item.temperature_min !== undefined && (
              <p className="mt-1 text-sm text-slate-500">
                Min: {item.temperature_min}°C
              </p>
            )}
          </div>

          {/* Additional Weather Details */}
          <div className="mt-4 space-y-2 border-t pt-4">
            {item.precipitation !== undefined && (
              <p className="text-xs text-slate-500">
                🌧 Precipitation: {item.precipitation} mm
              </p>
            )}

            {item.wind_speed !== undefined && (
              <p className="text-xs text-slate-500">
                💨 Wind: {item.wind_speed} km/h
              </p>
            )}

            {item.weather_code !== undefined && (
              <p className="text-xs text-slate-400">
                Weather code: {item.weather_code}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default WeatherCard;