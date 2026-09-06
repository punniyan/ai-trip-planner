import React from "react";
import type { Trip } from "../types/trip";

interface TripSummaryProps {
  trip: Trip;
}

const TripSummary = ({ trip }: TripSummaryProps) => {
  return (
    <div className="space-y-6">
      {/* =========================================================
          TRIP SUMMARY
      ========================================================= */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-bold text-gray-800">
          Trip Summary
        </h2>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {/* Origin */}
          <div>
            <p className="text-sm text-gray-500">Origin</p>
            <p className="font-semibold text-gray-800">
              {trip.origin || "Not available"}
            </p>
          </div>

          {/* Destination */}
          <div>
            <p className="text-sm text-gray-500">Destination</p>
            <p className="font-semibold text-gray-800">
              {trip.destination || "Not available"}
            </p>
          </div>

          {/* Start Date */}
          <div>
            <p className="text-sm text-gray-500">Start Date</p>
            <p className="font-semibold text-gray-800">
              {trip.start_date || "Not available"}
            </p>
          </div>

          {/* End Date */}
          <div>
            <p className="text-sm text-gray-500">End Date</p>
            <p className="font-semibold text-gray-800">
              {trip.end_date || "Not available"}
            </p>
          </div>

          {/* Travelers */}
          <div>
            <p className="text-sm text-gray-500">Travelers</p>
            <p className="font-semibold text-gray-800">
              {trip.travelers ?? "Not available"}
            </p>
          </div>

          {/* Budget */}
          <div>
            <p className="text-sm text-gray-500">Budget</p>
            <p className="font-semibold text-gray-800">
              {trip.currency || "INR"}{" "}
              {trip.budget?.toLocaleString() || "0"}
            </p>
          </div>
        </div>
      </div>

      {/* =========================================================
          LOCATION / GEOCODING
      ========================================================= */}
      {trip.location && (
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <span className="text-2xl">📍</span>

            <div>
              <h2 className="text-xl font-bold text-gray-800">
                Location
              </h2>

              <p className="text-sm text-gray-500">
                Geocoding information
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {/* Location Name */}
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">Location Name</p>

              <p className="mt-1 font-semibold text-gray-800">
                {trip.location.name || trip.destination || "Not available"}
              </p>
            </div>

            {/* Country */}
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">Country</p>

              <p className="mt-1 font-semibold text-gray-800">
                {trip.location.country || "Not available"}
              </p>
            </div>

            {/* Formatted Address */}
            <div className="rounded-lg bg-gray-50 p-4 md:col-span-2">
              <p className="text-sm text-gray-500">
                Formatted Address
              </p>

              <p className="mt-1 font-semibold text-gray-800">
                {trip.location.formatted ||
                  trip.location.address ||
                  "Not available"}
              </p>
            </div>

            {/* Latitude */}
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">Latitude</p>

              <p className="mt-1 font-semibold text-gray-800">
                {trip.location.latitude !== undefined
                  ? trip.location.latitude
                  : "Not available"}
              </p>
            </div>

            {/* Longitude */}
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-sm text-gray-500">Longitude</p>

              <p className="mt-1 font-semibold text-gray-800">
                {trip.location.longitude !== undefined
                  ? trip.location.longitude
                  : "Not available"}
              </p>
            </div>

            {/* Source */}
            <div className="rounded-lg bg-gray-50 p-4 md:col-span-2">
              <p className="text-sm text-gray-500">Data Source</p>

              <p className="mt-1 font-semibold capitalize text-gray-800">
                {trip.location.source || "Not available"}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================
          BUDGET SUMMARY
      ========================================================= */}
      {trip.budget_breakdown && (
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-bold text-gray-800">
            Estimated Budget
          </h2>

          <div className="rounded-lg bg-gray-50 p-4">
            <p className="text-sm text-gray-500">
              Total Estimated Cost
            </p>

            <p className="mt-1 text-2xl font-bold text-gray-800">
              {trip.budget_breakdown.currency ||
                trip.currency ||
                "INR"}{" "}
              {trip.budget_breakdown.total?.toLocaleString() || "0"}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TripSummary;