import React, { useState } from "react";
import ChatBox from "../components/ChatBox";
import ItineraryCard from "../components/ItineraryCard";
import { sendTripMessage } from "../api/tripApi";
import type { ChatMessage, Trip } from "../types/trip";

const Chat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [trip, setTrip] = useState<Trip | null>(null);
  const [conversationId, setConversationId] = useState<string>();
  const [loading, setLoading] = useState(false);

  const handleSend = async (message: string) => {
    setLoading(true);

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
        setTrip(response.trip);
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            response.message || "I updated your itinerary.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, I could not connect to the backend. Please make sure the FastAPI server is running on port 8000.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Background Effects */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-blue-600/10 blur-3xl" />
        <div className="absolute right-0 top-1/3 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-96 w-96 rounded-full bg-indigo-600/10 blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative z-10 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 shadow-lg shadow-blue-500/20">
              <span className="text-xl">✈️</span>
            </div>

            <div>
              <h1 className="text-lg font-bold tracking-tight">
                Trip<span className="text-blue-400">AI</span>
              </h1>

              <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                Intelligent Travel Planner
              </p>
            </div>
          </div>

          {/* Status */}
          <div className="hidden items-center gap-2 rounded-full border border-green-400/10 bg-green-400/5 px-4 py-2 sm:flex">
            <span className="h-2 w-2 rounded-full bg-green-400 shadow-lg shadow-green-400/50" />
            <span className="text-xs font-medium text-green-300">
              AI Planner Ready
            </span>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="relative z-10 mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Page Heading */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-blue-400">
            <span>✦</span>
            <span>AI TRAVEL ASSISTANT</span>
          </div>

          <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
            Plan your perfect journey.
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
            Tell our AI where you want to go, your travel dates, budget and
            preferences. We'll create a personalized itinerary for you.
          </p>
        </div>

        {/* Dashboard */}
        <div className="grid gap-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
          {/* Chat Panel */}
          <section className="flex min-h-[650px] flex-col overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] shadow-2xl shadow-black/20 backdrop-blur-xl">
            {/* Chat Header */}
            <div className="border-b border-white/10 bg-white/[0.03] px-5 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-lg">
                    🤖
                  </div>

                  <div>
                    <h3 className="font-semibold text-white">
                      TripAI Assistant
                    </h3>

                    <p className="text-xs text-slate-500">
                      Your personal travel planner
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs text-green-400">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  Online
                </div>
              </div>
            </div>

            {/* Chat Content */}
            <div className="flex-1 p-4 sm:p-5">
              <div className="h-full overflow-hidden rounded-2xl border border-white/5 bg-slate-950/40">
                {messages.length === 0 ? (
                  <div className="flex min-h-[520px] items-center justify-center px-6 py-12 text-center">
                    <div className="max-w-md">
                      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl border border-blue-400/10 bg-blue-500/10 text-4xl shadow-lg shadow-blue-500/10">
                        ✈️
                      </div>

                      <h3 className="mt-6 text-2xl font-bold">
                        Where are you going?
                      </h3>

                      <p className="mt-3 text-sm leading-6 text-slate-400">
                        Start a conversation with TripAI and tell us about
                        your dream destination.
                      </p>

                      {/* Suggestions */}
                      <div className="mt-7 grid gap-3 sm:grid-cols-2">
                        <button
                          onClick={() =>
                            handleSend(
                              "Plan a 4-day trip from Chennai to Dubai"
                            )
                          }
                          disabled={loading}
                          className="rounded-xl border border-white/10 bg-white/[0.03] p-4 text-left transition hover:border-blue-400/30 hover:bg-blue-500/5 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <span className="text-lg">🌆</span>

                          <p className="mt-2 text-sm font-medium text-white">
                            Dubai Adventure
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            4-day city experience
                          </p>
                        </button>

                        <button
                          onClick={() =>
                            handleSend(
                              "Plan a budget-friendly 5-day trip"
                            )
                          }
                          disabled={loading}
                          className="rounded-xl border border-white/10 bg-white/[0.03] p-4 text-left transition hover:border-blue-400/30 hover:bg-blue-500/5 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <span className="text-lg">💰</span>

                          <p className="mt-2 text-sm font-medium text-white">
                            Budget Trip
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            Smart budget planning
                          </p>
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-full overflow-y-auto p-2">
                    <ChatBox
                      messages={messages}
                      onSend={handleSend}
                      loading={loading}
                    />
                  </div>
                )}
              </div>
            </div>
          </section>

          {/* Itinerary Panel */}
          <section className="flex min-h-[650px] flex-col overflow-hidden rounded-3xl border border-white/10 bg-white/[0.04] shadow-2xl shadow-black/20 backdrop-blur-xl">
            {/* Itinerary Header */}
            <div className="border-b border-white/10 bg-white/[0.03] px-5 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 text-lg">
                    🗺️
                  </div>

                  <div>
                    <h3 className="font-semibold text-white">
                      Your Itinerary
                    </h3>

                    <p className="text-xs text-slate-500">
                      AI-generated travel plan
                    </p>
                  </div>
                </div>

                {trip?.itinerary && trip.itinerary.length > 0 && (
                  <div className="rounded-full border border-green-400/10 bg-green-400/5 px-3 py-1.5 text-xs font-medium text-green-300">
                    ✓ Ready
                  </div>
                )}
              </div>
            </div>

            {/* Itinerary Content */}
            <div className="flex-1 p-4 sm:p-5">
              <div className="min-h-[560px] rounded-2xl border border-white/5 bg-slate-950/40 p-4">
                {trip?.itinerary &&
                trip.itinerary.length > 0 ? (
                  <div className="overflow-y-auto">
                    <ItineraryCard itinerary={trip.itinerary} />
                  </div>
                ) : (
                  <div className="flex min-h-[520px] items-center justify-center text-center">
                    <div className="max-w-sm">
                      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl border border-white/10 bg-white/[0.03] text-4xl">
                        🗺️
                      </div>

                      <h3 className="mt-6 text-xl font-semibold text-white">
                        Your itinerary is waiting
                      </h3>

                      <p className="mt-3 text-sm leading-6 text-slate-500">
                        Start chatting with TripAI. Once your trip details
                        are ready, your personalized itinerary will appear
                        here.
                      </p>

                      <div className="mt-6 flex flex-wrap justify-center gap-2">
                        <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-500">
                          ✈️ Flights
                        </span>

                        <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-500">
                          🏨 Hotels
                        </span>

                        <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-500">
                          🌤 Weather
                        </span>

                        <span className="rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-slate-500">
                          💰 Budget
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>
        </div>

        {/* Feature Strip */}
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-center gap-3">
              <span className="text-xl">🧠</span>
              <div>
                <p className="text-sm font-semibold">AI Planning</p>
                <p className="text-xs text-slate-500">
                  Personalized itineraries
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-center gap-3">
              <span className="text-xl">🌤️</span>
              <div>
                <p className="text-sm font-semibold">Weather</p>
                <p className="text-xs text-slate-500">
                  Forecast-aware planning
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-center gap-3">
              <span className="text-xl">🏨</span>
              <div>
                <p className="text-sm font-semibold">Travel Data</p>
                <p className="text-xs text-slate-500">
                  Hotels & attractions
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-center gap-3">
              <span className="text-xl">💰</span>
              <div>
                <p className="text-sm font-semibold">Smart Budget</p>
                <p className="text-xs text-slate-500">
                  Track estimated expenses
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Chat;