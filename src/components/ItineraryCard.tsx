import React from "react";

import type {
  ItineraryActivity,
  ItineraryDay,
} from "../types/trip";

interface ItineraryCardProps {
  itinerary: ItineraryDay[];
}

const ItineraryCard = ({
  itinerary,
}: ItineraryCardProps) => {
  return (
    <div className="space-y-6">
      {itinerary.map((day) => (
        <div
          key={day.day}
          className="overflow-hidden rounded-2xl border bg-white shadow-sm"
        >
          {/* Day Header */}
          <div className="border-b bg-slate-50 px-5 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-slate-900">
                  Day {day.day}
                </h3>

                {day.date && (
                  <p className="mt-1 text-sm text-slate-500">
                    {day.date}
                  </p>
                )}

                {day.destination && (
                  <p className="mt-1 text-sm font-medium text-slate-600">
                    📍 {day.destination}
                  </p>
                )}
              </div>

              {/* Weather */}
              {day.weather && (
                <div className="rounded-xl bg-white px-4 py-3 text-right shadow-sm">
                  <p className="text-sm font-semibold text-slate-700">
                    🌤 {day.weather.description || "Weather"}
                  </p>

                  {day.weather.temperature_max !== undefined &&
                    day.weather.temperature_min !== undefined && (
                      <p className="mt-1 text-sm text-slate-500">
                        {day.weather.temperature_min}°C -{" "}
                        {day.weather.temperature_max}°C
                      </p>
                    )}
                </div>
              )}
            </div>
          </div>

          {/* Activities */}
          <div className="space-y-4 p-5">
            {day.activities && day.activities.length > 0 ? (
              day.activities.map(
                (activity: ItineraryActivity, index: number) => (
                  <div
                    key={index}
                    className="rounded-xl border border-slate-200 p-4"
                  >
                    <div className="flex gap-4">
                      {/* Time */}
                      <div className="min-w-[65px]">
                        <span className="text-sm font-bold text-blue-600">
                          {activity.time || "--:--"}
                        </span>
                      </div>

                      {/* Activity Details */}
                      <div className="flex-1">
                        <div className="flex flex-wrap items-start justify-between gap-2">
                          <h4 className="font-bold text-slate-900">
                            {activity.name ||
                              activity.title ||
                              activity.activity ||
                              "Activity"}
                          </h4>

                          {activity.type && (
                            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold capitalize text-blue-700">
                              {activity.type}
                            </span>
                          )}
                        </div>

                        {/* Address */}
                        {activity.address && (
                          <p className="mt-2 text-sm text-slate-500">
                            📍 {activity.address}
                          </p>
                        )}

                        {/* Duration */}
                        {activity.duration_hours !== undefined && (
                          <p className="mt-2 text-sm text-slate-600">
                            ⏱ Duration:{" "}
                            {activity.duration_hours} hours
                          </p>
                        )}

                        {/* Ticket Price */}
                        {activity.ticket_price !== null &&
                          activity.ticket_price !== undefined && (
                            <p className="mt-2 text-sm text-slate-600">
                              🎟 Ticket:{" "}
                              {activity.ticket_price}{" "}
                              {activity.currency || ""}
                            </p>
                          )}

                        {/* Restaurant Price */}
                        {activity.price !== null &&
                          activity.price !== undefined && (
                            <p className="mt-2 text-sm text-slate-600">
                              💰 Price:{" "}
                              {activity.price}{" "}
                              {activity.currency || ""}
                            </p>
                          )}
                      </div>
                    </div>
                  </div>
                )
              )
            ) : (
              <p className="text-sm text-slate-500">
                No activities available for this day.
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ItineraryCard;