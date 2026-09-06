import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import TripForm from "../components/TripForm";
import TripSummary from "../components/TripSummary";
import FlightCard from "../components/FlightCard";
import HotelCard from "../components/HotelCard";
import RestaurantCard from "../components/RestaurantCard";
import PlaceCard from "../components/PlaceCard";
import WeatherCard from "../components/WeatherCard";
import ItineraryCard from "../components/ItineraryCard";
import Loading from "../components/Loading";
import BudgetDashboard from "../components/BudgetDashboard";

import { sendTripMessage } from "../api/tripApi";

import type { ChatMessage, Trip } from "../types/trip";

const TripPlanner = () => {
  const navigate = useNavigate();

  const [trip, setTrip] = useState<Trip | null>(null);

  const [conversationId, setConversationId] =
    useState<string | undefined>();

  const [messages, setMessages] =
    useState<ChatMessage[]>([]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const handleSubmit = async (message: string) => {
    setLoading(true);
    setError("");

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
      },
    ]);

    try {
      const response = await sendTripMessage({
        message,
        conversation_id: conversationId,
      });

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      if (response.trip) {
        console.log("FULL TRIP:", response.trip);

        console.log(
          "ITINERARY:",
          response.trip.itinerary
        );

        console.log(
          "ITINERARY LENGTH:",
          response.trip.itinerary?.length
        );

        setTrip(response.trip);
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            response.message ||
            "Your trip has been created successfully.",
          timestamp: new Date().toISOString(),
        },
      ]);

      if (response.requires_date) {
        setError(
          "Please provide your travel dates before we search flights and hotels."
        );
      }
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the trip planner backend. Please make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen overflow-hidden bg-slate-950 text-white">

      {/* =====================================================
          COLORFUL BACKGROUND
      ====================================================== */}

      <div className="pointer-events-none fixed inset-0 overflow-hidden">

        <div className="absolute -left-40 -top-40 h-[500px] w-[500px] rounded-full bg-blue-600/20 blur-[120px]" />

        <div className="absolute right-[-150px] top-[15%] h-[500px] w-[500px] rounded-full bg-fuchsia-600/15 blur-[120px]" />

        <div className="absolute bottom-[-150px] left-[25%] h-[500px] w-[500px] rounded-full bg-cyan-500/15 blur-[120px]" />

        <div className="absolute bottom-[10%] right-[20%] h-[300px] w-[300px] rounded-full bg-violet-600/10 blur-[100px]" />

        <div
          className="absolute inset-0 opacity-[0.035]"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.8) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
          }}
        />
      </div>

      {/* =====================================================
          HEADER
      ====================================================== */}

      <header className="relative z-20 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">

        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">

          {/* Logo */}

          <button
            onClick={() => navigate("/")}
            className="group flex items-center gap-3"
          >
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 via-violet-500 to-fuchsia-500 shadow-lg shadow-blue-500/30 transition duration-300 group-hover:scale-105"
            >
              <span className="text-2xl">
                ✈️
              </span>
            </div>

            <div className="text-left">

              <h1 className="text-xl font-extrabold tracking-tight">
                Trip
                <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  AI
                </span>
              </h1>

              <p className="text-[10px] uppercase tracking-[0.25em] text-slate-500">
                Smart Travel Planner
              </p>

            </div>
          </button>

          {/* Header Actions */}

          <div className="flex items-center gap-3">

            <div className="hidden items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 sm:flex">

              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400 shadow-lg shadow-emerald-400/70" />

              <span className="text-xs font-bold text-emerald-300">
                AI Online
              </span>

            </div>

            <button
              onClick={() => navigate("/")}
              className="rounded-xl border border-white/10 bg-white/5 px-5 py-2.5 text-sm font-semibold text-slate-300 transition-all hover:border-cyan-400/30 hover:bg-cyan-400/10 hover:text-white"
            >
              Home
            </button>

          </div>
        </div>
      </header>

      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="relative z-10 mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">

        {/* =================================================
            PAGE HEADING
        ================================================== */}

        <div className="mb-10">

          <div className="inline-flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-500/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-blue-300">

            AI Travel Planner

          </div>

          <div className="mt-5 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">

            <div>

              <h2 className="max-w-4xl text-4xl font-black leading-tight tracking-tight sm:text-5xl lg:text-6xl">

                Build your{" "}

                <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-400 bg-clip-text text-transparent">
                  perfect journey.
                </span>

              </h2>

              <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-400 sm:text-base">
                Tell us where you want to go, when you want to travel,
                who is travelling and your budget. TripAI will organize
                your complete journey using intelligent travel data.
              </p>

            </div>

            {trip && (
              <div className="flex w-fit items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-5 py-2.5 text-xs font-bold text-emerald-300">

                <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />

                Trip Generated

              </div>
            )}

          </div>
        </div>

        {/* =================================================
            PLANNER GRID
        ================================================== */}

        <div className="grid gap-7 lg:grid-cols-[360px_minmax(0,1fr)]">

          {/* =================================================
              LEFT SIDEBAR
          ================================================== */}

          <aside className="space-y-6">

            {/* =================================================
                ORIGINAL CHAT BOX CONTAINER
            ================================================= */}

            <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-2 shadow-2xl backdrop-blur-xl">

              {/* IMPORTANT:
                  TripForm itself is NOT modified.
                  Its original white Chat Box style remains.
              */}

              <TripForm
                onSubmit={handleSubmit}
                loading={loading}
              />

            </div>

            {/* =================================================
                CONVERSATION
            ================================================= */}

            {messages.length > 0 && (
              <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] shadow-xl backdrop-blur-xl">

                <div className="border-b border-white/10 bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 px-5 py-4">

                  <div className="flex items-center gap-3">

                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-500/15 text-lg">
                      💬
                    </div>

                    <div>

                      <h3 className="font-bold text-white">
                        Conversation
                      </h3>

                      <p className="text-xs text-slate-500">
                        AI planning history
                      </p>

                    </div>

                  </div>
                </div>

                <div className="max-h-[420px] space-y-3 overflow-y-auto p-4">

                  {messages.map((message, index) => (

                    <div
                      key={index}
                      className={`rounded-2xl border p-4 ${
                        message.role === "user"
                          ? "border-blue-400/20 bg-blue-500/10"
                          : "border-white/10 bg-white/[0.03]"
                      }`}
                    >

                      <div className="mb-2 flex items-center gap-2">

                        <span className="text-sm">
                          {message.role === "user"
                            ? "👤"
                            : "🤖"}
                        </span>

                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                          {message.role}
                        </span>

                      </div>

                      <p
                        className={`text-sm leading-6 ${
                          message.role === "user"
                            ? "text-blue-100"
                            : "text-slate-300"
                        }`}
                      >
                        {message.content}
                      </p>

                    </div>

                  ))}

                </div>
              </div>
            )}

            {/* =================================================
                FEATURES
            ================================================== */}

            <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 shadow-xl">

              <p className="text-xs font-bold uppercase tracking-[0.15em] text-slate-500">
                Included in your plan
              </p>

              <div className="mt-5 space-y-3">

                {[
                  ["🧠", "AI Itinerary"],
                  ["✈️", "Flight Search"],
                  ["🏨", "Hotel Recommendations"],
                  ["🍽️", "Restaurant Discovery"],
                  ["🌤️", "Weather Forecast"],
                  ["💰", "Budget Analysis"],
                ].map(([icon, title]) => (

                  <div
                    key={title}
                    className="group flex items-center gap-3 rounded-xl p-2.5 text-sm text-slate-400 transition hover:bg-white/5 hover:text-white"
                  >

                    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/5">
                      {icon}
                    </span>

                    <span>
                      {title}
                    </span>

                    <span className="ml-auto text-emerald-400">
                      ✓
                    </span>

                  </div>

                ))}

              </div>
            </div>

          </aside>

          {/* =================================================
              RIGHT CONTENT
          ================================================== */}

          <div className="min-w-0">

            {/* =================================================
                LOADING
            ================================================== */}

            {loading && (
              <div className="mb-6 overflow-hidden rounded-3xl border border-blue-400/20 bg-gradient-to-r from-blue-500/10 via-violet-500/10 to-cyan-500/10 p-6 shadow-xl">

                <div className="flex items-center gap-4">

                  <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-500/10">

                    <span className="animate-pulse text-2xl">
                      ✨
                    </span>

                  </div>

                  <div>

                    <p className="font-bold text-white">
                      AI is building your trip...
                    </p>

                    <p className="mt-1 text-sm text-slate-500">
                      Searching destinations, hotels,
                      restaurants, weather and travel information.
                    </p>

                  </div>

                </div>

                <div className="mt-5">
                  <Loading />
                </div>

              </div>
            )}

            {/* =================================================
                ERROR
            ================================================== */}

            {error && (
              <div className="mb-6 flex items-start gap-3 rounded-2xl border border-red-400/20 bg-red-500/10 p-5">

                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-500/10">
                  ⚠️
                </div>

                <div>

                  <p className="font-bold text-red-300">
                    Something went wrong
                  </p>

                  <p className="mt-1 text-sm leading-6 text-red-200/70">
                    {error}
                  </p>

                </div>

              </div>
            )}

            {/* =================================================
                EMPTY STATE
            ================================================== */}

            {!trip && !loading && (
              <div className="relative flex min-h-[680px] items-center justify-center overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-blue-500/[0.07] via-white/[0.03] to-fuchsia-500/[0.05] p-8 shadow-2xl backdrop-blur-xl">

                <div className="absolute left-8 top-8 h-40 w-40 rounded-full border border-blue-400/10" />

                <div className="absolute right-10 top-20 h-24 w-24 rounded-full border border-fuchsia-400/10" />

                <div className="absolute bottom-10 right-10 h-48 w-48 rounded-full border border-cyan-400/10" />

                <div className="relative max-w-lg text-center">

                  <div className="mx-auto flex h-28 w-28 items-center justify-center rounded-[2rem] border border-white/10 bg-gradient-to-br from-blue-500/20 via-violet-500/20 to-fuchsia-500/20 text-5xl shadow-2xl shadow-blue-500/20">
                    ✈️
                  </div>

                  <h2 className="mt-8 text-3xl font-black sm:text-4xl">

                    Your journey{" "}

                    <span className="bg-gradient-to-r from-cyan-400 to-violet-400 bg-clip-text text-transparent">
                      starts here
                    </span>

                  </h2>

                  <p className="mt-4 text-sm leading-7 text-slate-400 sm:text-base">
                    Enter your travel details on the left and let our
                    AI create a personalized itinerary with flights,
                    hotels, restaurants, attractions, weather and
                    budget insights.
                  </p>

                  <div className="mt-9 grid grid-cols-2 gap-3 sm:grid-cols-4">

                    {[
                      ["🗺️", "Itinerary"],
                      ["🏨", "Hotels"],
                      ["🍽️", "Food"],
                      ["🌤️", "Weather"],
                    ].map(([icon, title]) => (

                      <div
                        key={title}
                        className="group rounded-2xl border border-white/10 bg-white/[0.04] p-4 transition hover:-translate-y-1 hover:border-blue-400/20 hover:bg-blue-500/10"
                      >

                        <div className="text-2xl transition group-hover:scale-110">
                          {icon}
                        </div>

                        <p className="mt-2 text-xs font-semibold text-slate-500 group-hover:text-slate-300">
                          {title}
                        </p>

                      </div>

                    ))}

                  </div>

                </div>
              </div>
            )}

            {/* =================================================
                TRIP RESULTS
            ================================================== */}

            {trip && (
              <div className="space-y-10">

                {/* =================================================
                    TRIP SUMMARY
                ================================================== */}

                <section>
                  <TripSummary trip={trip} />
                </section>

                {/* =================================================
                    ITINERARY
                ================================================== */}

                {trip.itinerary &&
                  trip.itinerary.length > 0 && (

                    <section>

                      <div className="mb-5 flex items-center gap-3">

                        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-400/10 text-lg">
                          🗓️
                        </div>

                        <div>

                          <h2 className="text-2xl font-black">
                            Itinerary
                          </h2>

                          <p className="text-sm text-slate-500">
                            Your AI-generated daily plan
                          </p>

                        </div>

                      </div>

                      <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] p-4 shadow-xl backdrop-blur-xl sm:p-6">

                        <ItineraryCard
                          itinerary={trip.itinerary}
                        />

                      </div>

                    </section>
                  )}

                {/* =================================================
                    BUDGET
                ================================================== */}

                <section>

                  <BudgetDashboard
                    budgetBreakdown={trip.budget_breakdown}
                    currencyConversion={
                      trip.currency_conversion
                    }
                    budget={trip.budget}
                    currency={trip.currency}
                  />

                </section>

                {/* =================================================
                    HOTELS
                ================================================== */}

                {trip.hotels &&
                  trip.hotels.length > 0 && (

                    <section>

                      <div className="mb-5 flex items-center gap-3">

                        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500/20 to-fuchsia-400/10 text-lg">
                          🏨
                        </div>

                        <div>

                          <h2 className="text-2xl font-black">
                            Hotels
                          </h2>

                          <p className="text-sm text-slate-500">
                            Recommended places to stay
                          </p>

                        </div>

                      </div>

                      <div className="grid gap-5 md:grid-cols-2">

                        {trip.hotels.map(
                          (hotel, index) => (

                            <HotelCard
                              key={index}
                              hotel={hotel}
                            />

                          )
                        )}

                      </div>

                    </section>
                  )}

                {/* =================================================
                    ATTRACTIONS
                ================================================== */}

                {trip.attractions &&
                  trip.attractions.length > 0 && (

                    <section>

                      <div className="mb-5 flex items-center gap-3">

                        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500/20 to-yellow-400/10 text-lg">
                          📍
                        </div>

                        <div>

                          <h2 className="text-2xl font-black">
                            Attractions
                          </h2>

                          <p className="text-sm text-slate-500">
                            Places worth exploring
                          </p>

                        </div>

                      </div>

                      <div className="grid gap-5 md:grid-cols-2">

                        {trip.attractions.map(
                          (place, index) => (

                            <PlaceCard
                              key={index}
                              place={place}
                            />

                          )
                        )}

                      </div>

                    </section>
                  )}

                {/* =================================================
                    RESTAURANTS
                ================================================== */}

                {trip.restaurants &&
                  trip.restaurants.length > 0 && (

                    <section>

                      <div className="mb-5 flex items-center gap-3">

                        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-red-500/20 to-orange-400/10 text-lg">
                          🍽️
                        </div>

                        <div>

                          <h2 className="text-2xl font-black">
                            Restaurants
                          </h2>

                          <p className="text-sm text-slate-500">
                            Recommended dining options
                          </p>

                        </div>

                      </div>

                      <div className="grid gap-5 md:grid-cols-2">

                        {trip.restaurants.map(
                          (restaurant, index) => (

                            <RestaurantCard
                              key={index}
                              restaurant={restaurant}
                            />

                          )
                        )}

                      </div>

                    </section>
                  )}

                {/* =================================================
                    FLIGHTS
                ================================================== */}

                {trip.flights &&
                  trip.flights.length > 0 && (

                    <section>

                      <div className="mb-5 flex items-center gap-3">

                        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-sky-500/20 to-blue-400/10 text-lg">
                          ✈️
                        </div>

                        <div>

                          <h2 className="text-2xl font-black">
                            Flights
                          </h2>

                          <p className="text-sm text-slate-500">
                            Available flight options
                          </p>

                        </div>

                      </div>

                      <div className="grid gap-5 lg:grid-cols-2">

                        {trip.flights.map(
                          (flight, index) => (

                            <FlightCard
                              key={`${
                                flight.flight_number ||
                                "flight"
                              }-${index}`}
                              flight={flight}
                            />

                          )
                        )}

                      </div>

                    </section>
                  )}

                {/* =================================================
                    WEATHER
                ================================================== */}

                {trip.weather &&
                  trip.weather.length > 0 && (

                    <section>

                      <div className="mb-5 flex items-center gap-3">

                        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-yellow-500/20 to-orange-400/10 text-lg">
                          🌤️
                        </div>

                        <div>

                          <h2 className="text-2xl font-black">
                            Weather
                          </h2>

                          <p className="text-sm text-slate-500">
                            Forecast for your travel dates
                          </p>

                        </div>

                      </div>

                      <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] p-4 shadow-xl backdrop-blur-xl sm:p-6">

                        <WeatherCard
                          weather={trip.weather}
                        />

                      </div>

                    </section>
                  )}

              </div>
            )}

          </div>
        </div>
      </main>

      {/* =====================================================
          FOOTER
      ====================================================== */}

      <footer className="relative z-10 mt-12 border-t border-white/10 bg-slate-950/60">

        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-7 text-xs text-slate-600 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">

          <p>
            © {new Date().getFullYear()} TripAI
          </p>

          <p className="text-center sm:text-right">
            AI-powered travel planning • Smart recommendations •
            Budget insights
          </p>

        </div>

      </footer>

    </div>
  );
};

export default TripPlanner;