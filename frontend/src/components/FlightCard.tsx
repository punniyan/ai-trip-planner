import React from "react";
import type { Flight } from "../types/trip";

interface FlightCardProps {
  flight: Flight;
}

const FlightCard = ({ flight }: FlightCardProps) => {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      {/* Airline */}
      <div className="flex items-start justify-between">
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

        {/* Price */}
        {flight.price !== undefined && flight.price !== null && (
          <p className="font-bold text-blue-600">
            {flight.currency || "INR"}{" "}
            {Number(flight.price).toLocaleString()}
          </p>
        )}
      </div>

      {/* Flight Route */}
      <div className="mt-5 grid grid-cols-3 items-center gap-3">
        {/* Departure */}
        <div>
          <p className="font-semibold">
            {flight.departure_time || "--"}
          </p>

          <p className="text-xs text-slate-500">
            {flight.departure_airport || "--"}
          </p>
        </div>

        {/* Duration */}
        <div className="text-center text-xs text-slate-400">
          <span className="text-xl">✈</span>

          <br />

          {flight.duration || ""}
        </div>

        {/* Arrival */}
        <div className="text-right">
          <p className="font-semibold">
            {flight.arrival_time || "--"}
          </p>

          <p className="text-xs text-slate-500">
            {flight.arrival_airport || "--"}
          </p>
        </div>
      </div>
    </div>
  );
};

export default FlightCard;