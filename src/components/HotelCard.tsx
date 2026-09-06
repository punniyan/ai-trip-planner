import React from "react";
import type { Hotel } from "../types/trip";

interface HotelCardProps {
  hotel: Hotel;
}

const HotelCard = ({ hotel }: HotelCardProps) => {
  const hasPrice =
    hotel.price_per_night !== null &&
    hotel.price_per_night !== undefined;

  return (
    <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
      {hotel.image_url && (
        <img
          src={hotel.image_url}
          alt={hotel.name || "Hotel"}
          className="h-44 w-full object-cover"
        />
      )}

      <div className="p-5">
        <div className="flex justify-between gap-4">
          <div>
            <h3 className="font-bold text-slate-900">
              {hotel.name || "Hotel"}
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              {hotel.address || "Address unavailable"}
            </p>
          </div>

          {hotel.rating !== null && hotel.rating !== undefined && (
            <span className="rounded-lg bg-yellow-50 px-2 py-1 text-sm font-semibold text-yellow-700">
              ★ {hotel.rating}
            </span>
          )}
        </div>

        <p className="mt-4 font-bold text-blue-600">
          {hasPrice ? (
            <>
              {hotel.currency || "INR"}{" "}
              {hotel.price_per_night!.toLocaleString()}
              <span className="font-normal text-slate-400">
                {" "}
                / night
              </span>
            </>
          ) : (
            <span className="font-normal text-slate-500">
              Price not available
            </span>
          )}
        </p>
      </div>
    </div>
  );
};

export default HotelCard;