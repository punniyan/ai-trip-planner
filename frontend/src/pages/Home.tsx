import React from "react";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen overflow-hidden bg-slate-950 text-white">
      {/* Background Effects */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-blue-600/20 blur-3xl" />
        <div className="absolute right-0 top-1/3 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-80 w-80 rounded-full bg-indigo-600/10 blur-3xl" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 shadow-lg shadow-blue-500/20">
              <span className="text-xl">✈️</span>
            </div>

            <div>
              <h2 className="text-lg font-bold tracking-tight">
                Trip<span className="text-blue-400">AI</span>
              </h2>
              <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                Smart Travel
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden items-center gap-8 text-sm text-slate-300 md:flex">
            <a
              href="#features"
              className="transition hover:text-white"
            >
              Features
            </a>

            <a
              href="#how-it-works"
              className="transition hover:text-white"
            >
              How It Works
            </a>

            <button
              onClick={() => navigate("/planner")}
              className="rounded-lg border border-white/10 bg-white/5 px-5 py-2.5 font-medium text-white transition hover:border-blue-400/40 hover:bg-blue-500/10"
            >
              Open Planner
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10">
        <section className="mx-auto max-w-7xl px-6 pb-20 pt-20 lg:px-8 lg:pb-28 lg:pt-28">
          <div className="grid items-center gap-16 lg:grid-cols-2">
            {/* Hero Content */}
            <div>
              {/* Badge */}
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-300">
                <span className="h-2 w-2 rounded-full bg-blue-400 shadow-lg shadow-blue-400/50" />
                AI-Powered Travel Planning
              </div>

              {/* Heading */}
              <h1 className="max-w-4xl text-5xl font-bold leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl">
                Travel smarter.
                <br />

                <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-blue-500 bg-clip-text text-transparent">
                  Explore better.
                </span>
              </h1>

              {/* Description */}
              <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-300 sm:text-xl">
                Build intelligent, personalized travel plans with AI-powered
                itineraries, real-time travel data, hotels, restaurants,
                attractions, weather and budget insights.
              </p>

              {/* CTA Buttons */}
              <div className="mt-9 flex flex-col gap-4 sm:flex-row">
                <button
                  onClick={() => navigate("/planner")}
                  className="group flex items-center justify-center gap-3 rounded-xl bg-blue-600 px-7 py-4 font-semibold shadow-xl shadow-blue-600/20 transition duration-300 hover:-translate-y-0.5 hover:bg-blue-500 hover:shadow-blue-500/30"
                >
                  Start Planning
                  <span className="transition-transform duration-300 group-hover:translate-x-1">
                    →
                  </span>
                </button>

                <button
                  onClick={() => navigate("/planner")}
                  className="rounded-xl border border-white/10 bg-white/5 px-7 py-4 font-semibold text-slate-200 backdrop-blur transition duration-300 hover:border-white/20 hover:bg-white/10"
                >
                  Explore Planner
                </button>
              </div>

              {/* Trust Text */}
              <div className="mt-8 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm text-slate-500">
                <span className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  Personalized itineraries
                </span>

                <span className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  Smart recommendations
                </span>

                <span className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  Budget aware
                </span>
              </div>
            </div>

            {/* Right Visual */}
            <div className="relative">
              {/* Main Card */}
              <div className="relative rounded-3xl border border-white/10 bg-white/[0.04] p-3 shadow-2xl shadow-black/30 backdrop-blur-xl">
                <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900">
                  {/* Fake Map Header */}
                  <div className="relative h-72 overflow-hidden bg-gradient-to-br from-slate-800 via-slate-900 to-blue-950">
                    {/* Grid */}
                    <div className="absolute inset-0 opacity-20">
                      <div
                        className="h-full w-full"
                        style={{
                          backgroundImage:
                            "linear-gradient(rgba(255,255,255,0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.12) 1px, transparent 1px)",
                          backgroundSize: "40px 40px",
                        }}
                      />
                    </div>

                    {/* Route */}
                    <div className="absolute left-[18%] top-[62%] h-0.5 w-[62%] rotate-[-18deg] bg-blue-400 shadow-lg shadow-blue-400/50" />

                    {/* Location Points */}
                    <div className="absolute left-[16%] top-[66%] flex h-5 w-5 items-center justify-center rounded-full bg-blue-500 ring-4 ring-blue-500/20">
                      <div className="h-2 w-2 rounded-full bg-white" />
                    </div>

                    <div className="absolute right-[18%] top-[35%] flex h-5 w-5 items-center justify-center rounded-full bg-cyan-400 ring-4 ring-cyan-400/20">
                      <div className="h-2 w-2 rounded-full bg-white" />
                    </div>

                    {/* Floating Destination Card */}
                    <div className="absolute left-6 top-6 rounded-xl border border-white/10 bg-slate-950/80 p-4 shadow-xl backdrop-blur-xl">
                      <p className="text-xs text-slate-400">
                        Your destination
                      </p>

                      <p className="mt-1 text-lg font-semibold">
                        Dubai, UAE
                      </p>

                      <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
                        <span>☀️ 38°C</span>
                        <span>•</span>
                        <span>4 Days</span>
                      </div>
                    </div>

                    {/* AI Badge */}
                    <div className="absolute bottom-5 right-5 flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-500/20 px-4 py-2 text-xs font-medium text-blue-200 backdrop-blur-xl">
                      <span>✦</span>
                      AI Optimized
                    </div>
                  </div>

                  {/* Trip Summary */}
                  <div className="p-5">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs uppercase tracking-wider text-slate-500">
                          Your Trip
                        </p>
                        <h3 className="mt-1 text-xl font-semibold">
                          Dubai Adventure
                        </h3>
                      </div>

                      <div className="rounded-lg bg-green-500/10 px-3 py-2 text-sm font-medium text-green-400">
                        Ready
                      </div>
                    </div>

                    <div className="mt-5 grid grid-cols-3 gap-3">
                      <div className="rounded-xl border border-white/5 bg-white/[0.03] p-3">
                        <p className="text-xs text-slate-500">Days</p>
                        <p className="mt-1 font-semibold">4</p>
                      </div>

                      <div className="rounded-xl border border-white/5 bg-white/[0.03] p-3">
                        <p className="text-xs text-slate-500">Places</p>
                        <p className="mt-1 font-semibold">12+</p>
                      </div>

                      <div className="rounded-xl border border-white/5 bg-white/[0.03] p-3">
                        <p className="text-xs text-slate-500">Budget</p>
                        <p className="mt-1 font-semibold">₹45K</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating AI Card */}
              <div className="absolute -bottom-6 -left-6 hidden w-56 rounded-2xl border border-white/10 bg-slate-900/90 p-4 shadow-2xl backdrop-blur-xl sm:block">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-lg">
                    ✨
                  </div>

                  <div>
                    <p className="text-xs text-slate-500">
                      AI Recommendation
                    </p>
                    <p className="text-sm font-semibold">
                      Best places found
                    </p>
                  </div>
                </div>
              </div>

              {/* Floating Weather Card */}
              <div className="absolute -right-4 top-10 hidden rounded-2xl border border-white/10 bg-slate-900/90 px-5 py-4 shadow-2xl backdrop-blur-xl lg:block">
                <p className="text-xs text-slate-500">
                  Today's Weather
                </p>

                <div className="mt-2 flex items-center gap-3">
                  <span className="text-2xl">☀️</span>
                  <div>
                    <p className="text-lg font-bold">38°C</p>
                    <p className="text-xs text-slate-500">
                      Clear Sky
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Section */}
        <section
          id="features"
          className="border-t border-white/5 bg-white/[0.02]"
        >
          <div className="mx-auto max-w-7xl px-6 py-20 lg:px-8">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
                Everything you need
              </p>

              <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
                One intelligent planner.
                <br />
                <span className="text-slate-400">
                  Your entire trip.
                </span>
              </h2>
            </div>

            <div className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
              {/* Feature 1 */}
              <div className="group rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition duration-300 hover:-translate-y-1 hover:border-blue-400/20 hover:bg-white/[0.05]">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10 text-2xl">
                  🧠
                </div>

                <h3 className="mt-5 text-lg font-semibold">
                  AI Itineraries
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Get personalized day-by-day travel plans designed around
                  your preferences.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="group rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition duration-300 hover:-translate-y-1 hover:border-blue-400/20 hover:bg-white/[0.05]">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 text-2xl">
                  🌤️
                </div>

                <h3 className="mt-5 text-lg font-semibold">
                  Live Weather
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Check weather conditions and plan activities around the
                  forecast.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="group rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition duration-300 hover:-translate-y-1 hover:border-blue-400/20 hover:bg-white/[0.05]">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-500/10 text-2xl">
                  🏨
                </div>

                <h3 className="mt-5 text-lg font-semibold">
                  Hotels & Food
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Discover hotels, restaurants and attractions suited to your
                  destination.
                </p>
              </div>

              {/* Feature 4 */}
              <div className="group rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition duration-300 hover:-translate-y-1 hover:border-blue-400/20 hover:bg-white/[0.05]">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-2xl">
                  💰
                </div>

                <h3 className="mt-5 text-lg font-semibold">
                  Smart Budget
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-400">
                  Estimate your trip expenses and understand your budget before
                  you travel.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section
          id="how-it-works"
          className="mx-auto max-w-7xl px-6 py-20 lg:px-8"
        >
          <div className="text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-400">
              Simple process
            </p>

            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              Plan your trip in three steps
            </h2>

            <p className="mx-auto mt-4 max-w-2xl text-slate-400">
              Tell us where you want to go and let AI handle the planning.
            </p>
          </div>

          <div className="mt-14 grid gap-8 md:grid-cols-3">
            {[
              {
                number: "01",
                icon: "💬",
                title: "Tell us your plan",
                text: "Enter your destination, dates, travelers and budget.",
              },
              {
                number: "02",
                icon: "✨",
                title: "AI builds your trip",
                text: "Our AI combines travel data to create a personalized itinerary.",
              },
              {
                number: "03",
                icon: "🧳",
                title: "Start exploring",
                text: "Review your trip and enjoy a smarter travel experience.",
              },
            ].map((step) => (
              <div
                key={step.number}
                className="relative rounded-2xl border border-white/10 bg-white/[0.03] p-7"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-blue-400">
                    {step.number}
                  </span>

                  <span className="text-2xl">{step.icon}</span>
                </div>

                <h3 className="mt-8 text-xl font-semibold">
                  {step.title}
                </h3>

                <p className="mt-3 text-sm leading-6 text-slate-400">
                  {step.text}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* Final CTA */}
        <section className="px-6 pb-20 lg:px-8">
          <div className="mx-auto max-w-5xl overflow-hidden rounded-3xl border border-blue-400/20 bg-gradient-to-br from-blue-600/20 via-slate-900 to-cyan-500/10 p-10 text-center shadow-2xl sm:p-16">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10 text-2xl">
              ✈️
            </div>

            <h2 className="mt-6 text-3xl font-bold sm:text-4xl">
              Your next adventure starts here.
            </h2>

            <p className="mx-auto mt-4 max-w-2xl text-slate-400">
              Let AI turn your travel ideas into a complete, personalized
              journey.
            </p>

            <button
              onClick={() => navigate("/planner")}
              className="mt-8 rounded-xl bg-blue-600 px-8 py-4 font-semibold shadow-xl shadow-blue-600/20 transition hover:bg-blue-500"
            >
              Start Planning Your Trip →
            </button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <p>
            © {new Date().getFullYear()} TripAI. Intelligent travel planning.
          </p>

          <p className="text-slate-600">
            Powered by AI • Real travel data • Smart planning
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;