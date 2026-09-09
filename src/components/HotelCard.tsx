import React, { useState } from "react";

import type { Hotel } from "../types/trip";


interface HotelCardProps {
  hotel: Hotel;
}


// Fallback hotel image
const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1200&q=80";


const HotelCard = ({
  hotel,
}: HotelCardProps) => {

  const [imageSrc, setImageSrc] =
    useState<string>(
      hotel.image_url || FALLBACK_IMAGE
    );


  const hasPrice =
    hotel.price_per_night !== null &&
    hotel.price_per_night !== undefined;


  const handleImageError = () => {
    setImageSrc(FALLBACK_IMAGE);
  };


  return (
    <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

      {/* =====================================================
          HOTEL IMAGE
      ====================================================== */}

      <div className="relative">

        <img
          src={imageSrc}
          alt={hotel.name || "Hotel"}
          className="h-48 w-full object-cover"
          onError={handleImageError}
        />

        {/* Platform Badge */}

        {hotel.platform && (
          <span className="absolute left-3 top-3 rounded-full bg-white/90 px-3 py-1 text-xs font-semibold capitalize text-slate-700 shadow">
            {hotel.platform}
          </span>
        )}

      </div>


      {/* =====================================================
          HOTEL DETAILS
      ====================================================== */}

      <div className="p-5">

        {/* Name + Rating */}

        <div className="flex justify-between gap-4">

          <div className="min-w-0">

            <h3 className="font-bold text-slate-900">
              {hotel.name || "Hotel"}
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              {hotel.address ||
                "Address unavailable"}
            </p>

          </div>


          {/* Rating */}

          {hotel.rating !== null &&
            hotel.rating !== undefined && (

              <span className="h-fit whitespace-nowrap rounded-lg bg-yellow-50 px-2 py-1 text-sm font-semibold text-yellow-700">
                ★ {hotel.rating}
              </span>

            )}

        </div>


        {/* =================================================
            PROPERTY TYPE
        ================================================== */}

        {hotel.property_type && (

          <p className="mt-2 text-sm capitalize text-slate-500">
            {hotel.property_type}
          </p>

        )}


        {/* =================================================
            BEDROOM / BATHROOM
        ================================================== */}

        {(hotel.bedrooms !== null &&
          hotel.bedrooms !== undefined) && (

          <p className="mt-2 text-sm text-slate-600">
            🛏 {hotel.bedrooms} bedroom
            {hotel.bedrooms > 1 ? "s" : ""}

            {hotel.bathrooms !== null &&
              hotel.bathrooms !== undefined &&
              (
                <>
                  {" • "}
                  🛁 {hotel.bathrooms} bathroom
                  {hotel.bathrooms > 1
                    ? "s"
                    : ""}
                </>
              )}
          </p>

        )}


        {/* =================================================
            PRICE
        ================================================== */}

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


        {/* =================================================
            TOTAL PRICE
        ================================================== */}

        {hotel.total_price !== null &&
          hotel.total_price !== undefined && (

            <p className="mt-1 text-sm text-slate-500">

              Total:{" "}

              {hotel.currency || "INR"}{" "}

              {hotel.total_price.toLocaleString()}

              {hotel.nights
                ? ` for ${hotel.nights} nights`
                : ""}

            </p>

          )}


        {/* =================================================
            AMENITIES
        ================================================== */}

        {hotel.amenities &&
          hotel.amenities.length > 0 && (

            <div className="mt-4 flex flex-wrap gap-2">

              {hotel.amenities
                .slice(0, 5)
                .map((amenity) => (

                  <span
                    key={amenity}
                    className="rounded-full bg-slate-100 px-2 py-1 text-xs capitalize text-slate-600"
                  >
                    {amenity.replaceAll(
                      "_",
                      " "
                    )}
                  </span>

                ))}

            </div>

          )}


        {/* =================================================
            REVIEW COUNT
        ================================================== */}

        {hotel.review_count !== undefined &&
          hotel.review_count > 0 && (

            <p className="mt-3 text-xs text-slate-400">
              {hotel.review_count.toLocaleString()} reviews
            </p>

          )}


        {/* =================================================
            VIEW HOTEL BUTTON
        ================================================== */}

        {hotel.website && (

          <a
            href={hotel.website}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-block rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
          >
            View Hotel
          </a>

        )}

      </div>

    </div>
  );
};


export default HotelCard;