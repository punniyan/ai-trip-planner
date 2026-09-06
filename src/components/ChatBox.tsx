import React from "react";
import { useState } from "react";
import type { ChatMessage } from "../types/trip";

interface ChatBoxProps {
  messages: ChatMessage[];
  onSend: (message: string) => void;
  loading?: boolean;
}

const ChatBox = ({
  messages,
  onSend,
  loading = false,
}: ChatBoxProps) => {
  const [message, setMessage] = useState("");

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    if (!message.trim() || loading) {
      return;
    }

    onSend(message.trim());
    setMessage("");
  };

  return (
    <div className="flex h-[600px] flex-col rounded-2xl bg-white shadow-lg">
      <div className="border-b p-5">
        <h2 className="text-lg font-bold text-slate-900">
          AI Trip Assistant
        </h2>

        <p className="text-sm text-slate-500">
          Modify your itinerary using natural language.
        </p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-5">
        {messages.length === 0 && (
          <div className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
            Try saying:
            <br />
            <br />
            "Remove day 3"
            <br />
            "Add a beach on day 2"
            <br />
            "Find cheaper hotels"
            <br />
            "Add Indian restaurants"
          </div>
        )}

        {messages.map((item, index) => (
          <div
            key={`${item.timestamp}-${index}`}
            className={`flex ${
              item.role === "user"
                ? "justify-end"
                : "justify-start"
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                item.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-800"
              }`}
            >
              {item.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-500">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="border-t p-4"
      >
        <div className="flex gap-2">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Modify your trip..."
            className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-500"
          />

          <button
            type="submit"
            disabled={loading || !message.trim()}
            className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:bg-slate-400"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatBox;