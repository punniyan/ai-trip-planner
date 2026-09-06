import React from "react";
import type { Budget, CurrencyConversion } from "../types/trip";

interface BudgetDashboardProps {
  budgetBreakdown?: Budget;
  currencyConversion?: CurrencyConversion;
  budget?: number;
  currency?: string;
}

const BudgetDashboard = ({
  budgetBreakdown,
  currencyConversion,
  budget,
  currency = "INR",
}: BudgetDashboardProps) => {
  const budgetData = budgetBreakdown || {};

  const formatAmount = (value?: number | null) => {
    if (value === undefined || value === null) {
      return "--";
    }

    return value.toLocaleString();
  };

  const conversion = currencyConversion;

  return (
    <div className="space-y-6">
      {/* ====================================================== */}
      {/* BUDGET SUMMARY */}
      {/* ====================================================== */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">
              💰 Budget Summary
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Estimated trip expenses
            </p>
          </div>

          <div className="rounded-lg bg-blue-50 px-4 py-2">
            <span className="text-sm font-semibold text-blue-700">
              Currency: {budgetData.currency || currency}
            </span>
          </div>
        </div>

        {/* Total Budget */}
        {budget !== undefined && (
          <div className="mt-6 rounded-xl bg-slate-50 p-5">
            <p className="text-sm text-slate-500">
              Your Budget
            </p>

            <p className="mt-1 text-3xl font-bold text-slate-900">
              {currency} {formatAmount(budget)}
            </p>
          </div>
        )}

        {/* Expense Cards */}
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border p-4">
            <p className="text-sm text-slate-500">
              ✈️ Flights
            </p>

            <p className="mt-2 text-xl font-bold text-slate-900">
              {currency} {formatAmount(budgetData.flights)}
            </p>
          </div>

          <div className="rounded-xl border p-4">
            <p className="text-sm text-slate-500">
              🏨 Hotels
            </p>

            <p className="mt-2 text-xl font-bold text-slate-900">
              {currency} {formatAmount(budgetData.hotels)}
            </p>
          </div>

          <div className="rounded-xl border p-4">
            <p className="text-sm text-slate-500">
              🍽️ Food
            </p>

            <p className="mt-2 text-xl font-bold text-slate-900">
              {currency} {formatAmount(budgetData.food)}
            </p>
          </div>

          <div className="rounded-xl border p-4">
            <p className="text-sm text-slate-500">
              🎯 Activities
            </p>

            <p className="mt-2 text-xl font-bold text-slate-900">
              {currency} {formatAmount(budgetData.activities)}
            </p>
          </div>
        </div>

        {/* Transport */}
        {budgetData.transport !== undefined &&
          budgetData.transport !== null && (
            <div className="mt-4 rounded-xl border p-4">
              <p className="text-sm text-slate-500">
                🚕 Transport
              </p>

              <p className="mt-2 text-xl font-bold text-slate-900">
                {currency} {formatAmount(budgetData.transport)}
              </p>
            </div>
          )}

        {/* Total */}
        {budgetData.total !== undefined &&
          budgetData.total !== null && (
            <div className="mt-6 rounded-xl bg-blue-50 p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600">
                    Total Estimated Cost
                  </p>

                  <p className="mt-1 text-3xl font-bold text-blue-700">
                    {budgetData.currency || currency}{" "}
                    {formatAmount(budgetData.total)}
                  </p>
                </div>

                {budgetData.estimated && (
                  <span className="rounded-full bg-yellow-100 px-3 py-1 text-xs font-semibold text-yellow-700">
                    Estimated
                  </span>
                )}
              </div>
            </div>
          )}
      </div>

      {/* ====================================================== */}
      {/* CURRENCY CONVERSION */}
      {/* ====================================================== */}

      {conversion && (
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">
                💱 Currency Conversion
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Current exchange rate for your trip
              </p>
            </div>

            <span
              className={`w-fit rounded-full px-3 py-1 text-xs font-semibold ${
                conversion.status === "success"
                  ? "bg-green-50 text-green-700"
                  : "bg-red-50 text-red-700"
              }`}
            >
              {conversion.status === "success"
                ? "✓ Available"
                : "Unavailable"}
            </span>
          </div>

          {/* From / To / Rate */}
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            {/* From Currency */}
            <div className="rounded-xl bg-slate-50 p-5">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                From Currency
              </p>

              <p className="mt-2 text-2xl font-bold text-slate-900">
                {conversion.from_currency || "--"}
              </p>
            </div>

            {/* To Currency */}
            <div className="rounded-xl bg-slate-50 p-5">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                To Currency
              </p>

              <p className="mt-2 text-2xl font-bold text-slate-900">
                {conversion.to_currency || "--"}
              </p>
            </div>

            {/* Exchange Rate */}
            <div className="rounded-xl bg-blue-50 p-5">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                Exchange Rate
              </p>

              <p className="mt-2 text-2xl font-bold text-blue-700">
                {conversion.rate !== undefined &&
                conversion.rate !== null
                  ? conversion.rate
                  : "--"}
              </p>
            </div>
          </div>

          {/* Conversion Result */}
          {conversion.converted_amount !== undefined &&
            conversion.converted_amount !== null && (
              <div className="mt-5 rounded-xl border border-blue-100 bg-blue-50 p-5">
                <p className="text-sm font-medium text-slate-600">
                  Conversion Result
                </p>

                <div className="mt-3 flex flex-wrap items-center gap-3">
                  <span className="text-2xl font-bold text-slate-900">
                    {conversion.from_currency || "--"}{" "}
                    {formatAmount(conversion.amount)}
                  </span>

                  <span className="text-xl text-slate-400">
                    →
                  </span>

                  <span className="text-2xl font-bold text-blue-700">
                    {conversion.to_currency || "--"}{" "}
                    {formatAmount(
                      conversion.converted_amount
                    )}
                  </span>
                </div>
              </div>
            )}

          {/* Source */}
          {conversion.source && (
            <div className="mt-4">
              <p className="text-xs text-slate-400">
                Exchange rate source: {conversion.source}
              </p>
            </div>
          )}

          {/* Error */}
          {conversion.error && (
            <div className="mt-4 rounded-lg bg-red-50 p-4">
              <p className="text-sm text-red-700">
                {conversion.error}
              </p>
            </div>
          )}
        </div>
      )}

      {/* ====================================================== */}
      {/* ADDITIONAL BUDGET INFORMATION */}
      {/* ====================================================== */}

      {budgetData.remaining_budget !== undefined && (
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <p className="text-sm text-slate-500">
                Travelers
              </p>

              <p className="mt-1 text-xl font-bold text-slate-900">
                {budgetData.travelers || "--"}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500">
                Trip Days
              </p>

              <p className="mt-1 text-xl font-bold text-slate-900">
                {budgetData.trip_days || "--"}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500">
                Remaining Budget
              </p>

              <p className="mt-1 text-xl font-bold text-green-600">
                {currency}{" "}
                {formatAmount(
                  budgetData.remaining_budget
                )}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ====================================================== */}
      {/* NOTE */}
      {/* ====================================================== */}

      {budgetData.note && (
        <div className="rounded-lg bg-yellow-50 p-4">
          <p className="text-sm text-yellow-800">
            ℹ️ {budgetData.note}
          </p>
        </div>
      )}
    </div>
  );
};

export default BudgetDashboard;