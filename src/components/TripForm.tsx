import React from "react";
import { useState } from "react";

interface TripFormProps {
  onSubmit: (message: string) => void;
  loading?: boolean;
}

const TripForm = ({
  onSubmit,
  loading = false,
}: TripFormProps) => {
  const [message, setMessage] = useState("");

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    if (!message.trim() || loading) {
      return;
    }

    onSubmit(message.trim());
  };

  const examples = [
    "Plan a 5 day trip to Dubai",
    "Plan a 7 day trip to Singapore for 2 people",
    "Plan a budget trip to Paris",
  ];

  return (
    <div className="rounded-2xl bg-white p-6 shadow-lg">
      <h2 className="mb-2 text-2xl font-bold text-slate-900">
        Plan your trip
      </h2>

      <p className="mb-6 text-sm text-slate-500">
        Tell the AI where you want to go and what kind of trip
        you want.
      </p>

      <form onSubmit={handleSubmit}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Example: Plan a 5 day trip to Dubai for 2 people..."
          rows={5}
          className="w-full resize-none rounded-xl border border-slate-300 bg-white p-4 text-sm font-medium text-slate-900 placeholder:font-normal placeholder:text-slate-400 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
        />

        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="mt-4 w-full rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {loading ? "Planning..." : "Create Trip"}
        </button>
      </form>

      <div className="mt-6">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Try an example
        </p>

        <div className="space-y-2">
          {examples.map((example) => (
            <button
              key={example}
              type="button"
              onClick={() => setMessage(example)}
              className="block w-full rounded-lg bg-slate-50 p-3 text-left text-sm text-slate-600 transition hover:bg-blue-50 hover:text-blue-700"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TripForm;