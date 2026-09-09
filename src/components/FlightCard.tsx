import React from "react";
import type { Flight } from "../types/trip";

interface FlightCardProps {
  flight: Flight;
}

const FlightCard = ({ flight }: FlightCardProps) => {
  const price =
    flight.price !== undefined && flight.price !== null
      ? Number(flight.price).toLocaleString("en-IN")
      : null;

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md">
      {/* =====================================================
          HEADER
      ====================================================== */}
      <div className="flex items-start justify-between gap-4">
        {/* Airline */}
        <div className="flex items-center gap-3">
          {flight.airline_logo ? (
            <img
              src={flight.airline_logo}
              alt={flight.airline || "Airline"}
              className="h-10 w-10 rounded-lg object-contain"
            />
          ) : (
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-xl">
              ✈️
            </div>
          )}

          <div>
            <h3 className="font-bold text-slate-900">
              {flight.airline || "Airline"}
            </h3>

            {flight.flight_number && (
              <p className="text-xs text-slate-500">
                {flight.flight_number}
              </p>
            )}
          </div>
        </div>

        {/* Price */}
        <div className="text-right">
          {price ? (
            <>
              <p className="text-xl font-bold text-blue-600">
                {flight.currency === "INR" ? "₹" : flight.currency}{" "}
                {price}
              </p>

              <p className="text-xs text-slate-400">
                per traveler
              </p>
            </>
          ) : (
            <p className="text-sm text-slate-400">
              Price unavailable
            </p>
          )}
        </div>
      </div>

      {/* =====================================================
          ROUTE
      ====================================================== */}
      <div className="mt-6 grid grid-cols-[1fr_auto_1fr] items-center gap-4">
        {/* Departure */}
        <div>
          <p className="text-xl font-bold text-slate-900">
            {flight.departure_time || "--"}
          </p>

          <p className="mt-1 text-sm font-semibold text-slate-700">
            {flight.departure_airport || "--"}
          </p>

          {flight.departure_airport_name && (
            <p className="mt-1 text-xs text-slate-400">
              {flight.departure_airport_name}
            </p>
          )}
        </div>

        {/* Middle */}
        <div className="min-w-[100px] text-center">
          <p className="text-xs font-medium text-slate-500">
            {flight.duration_text ||
              flight.duration ||
              "--"}
          </p>

          <div className="my-2 flex items-center">
            <div className="h-px flex-1 bg-slate-300" />

            <span className="mx-2 text-lg text-blue-600">
              ✈
            </span>

            <div className="h-px flex-1 bg-slate-300" />
          </div>

          <p className="text-xs font-medium text-slate-500">
            {flight.stops_text ||
              (flight.stops === 0
                ? "Nonstop"
                : flight.stops !== undefined
                  ? `${flight.stops} stop${
                      flight.stops > 1 ? "s" : ""
                    }`
                  : "")}
          </p>
        </div>

        {/* Arrival */}
        <div className="text-right">
          <p className="text-xl font-bold text-slate-900">
            {flight.arrival_time || "--"}
          </p>

          <p className="mt-1 text-sm font-semibold text-slate-700">
            {flight.arrival_airport || "--"}
          </p>

          {flight.arrival_airport_name && (
            <p className="mt-1 text-xs text-slate-400">
              {flight.arrival_airport_name}
            </p>
          )}
        </div>
      </div>

      {/* =====================================================
          DETAILS
      ====================================================== */}
      <div className="mt-5 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
        {flight.travel_class && (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            💺 {flight.travel_class}
          </span>
        )}

        {flight.stops_text && (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            🔄 {flight.stops_text}
          </span>
        )}

        {flight.aircraft && (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            ✈️ {flight.aircraft}
          </span>
        )}

        {flight.travelers && (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">
            👤 {flight.travelers}{" "}
            {flight.travelers === 1
              ? "Traveler"
              : "Travelers"}
          </span>
        )}
      </div>

      {/* =====================================================
          SOURCE
      ====================================================== */}
      <div className="mt-4 flex items-center justify-between">
        <p className="text-xs text-slate-400">
          Flight data from Google Flights
        </p>

        {flight.price_status === "available" && (
          <span className="text-xs font-medium text-green-600">
            ✓ Price available
          </span>
        )}
      </div>
    </div>
  );
};

export default FlightCard;