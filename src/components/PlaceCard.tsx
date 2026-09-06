import React from "react";
import type { Place } from "../types/trip";

interface PlaceCardProps {
  place: Place;
}

const PlaceCard = ({ place }: PlaceCardProps) => {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-bold text-slate-900">
            {place.name || "Place"}
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            {place.address || place.formatted || ""}
          </p>
        </div>

        {place.rating !== undefined && (
          <span className="rounded-lg bg-yellow-50 px-2 py-1 text-sm font-semibold text-yellow-700">
            ★ {place.rating}
          </span>
        )}
      </div>

      {place.category && (
        <span className="mt-4 inline-block rounded-full bg-blue-50 px-3 py-1 text-xs text-blue-700">
          {place.category}
        </span>
      )}

      {place.description && (
        <p className="mt-3 text-sm leading-6 text-slate-600">
          {place.description}
        </p>
      )}
    </div>
  );
};

export default PlaceCard;