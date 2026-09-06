import React from "react";
import type { Restaurant } from "../types/trip";

interface RestaurantCardProps {
  restaurant: Restaurant;
}

const RestaurantCard = ({
  restaurant,
}: RestaurantCardProps) => {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-bold text-slate-900">
            {restaurant.name || "Restaurant"}
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            {restaurant.address || "Address unavailable"}
          </p>
        </div>

        {restaurant.rating !== undefined && (
          <span className="rounded-lg bg-green-50 px-2 py-1 text-sm font-semibold text-green-700">
            ★ {restaurant.rating}
          </span>
        )}
      </div>

      <div className="mt-4 flex gap-2">
        {restaurant.cuisine && (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs">
            {restaurant.cuisine}
          </span>
        )}

        {restaurant.price_level && (
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs">
            {restaurant.price_level}
          </span>
        )}
      </div>
    </div>
  );
};

export default RestaurantCard;