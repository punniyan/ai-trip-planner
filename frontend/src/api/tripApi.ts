import axios from "axios";

import type {
  TripRequest,
  TripResponse,
} from "../types/trip";

const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 120000,
});

export const sendTripMessage = async (
  request: TripRequest
): Promise<TripResponse> => {
  const response = await api.post<TripResponse>(
    "/api/trip/chat",
    request
  );

  return response.data;
};

export const createTrip = async (
  request: TripRequest
): Promise<TripResponse> => {
  const response = await api.post<TripResponse>(
    "/api/trip",
    request
  );

  return response.data;
};

export const getTrip = async (
  tripId: string
): Promise<TripResponse> => {
  const response = await api.get<TripResponse>(
    `/api/trip/${tripId}`
  );

  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get("/api/health");
  return response.data;
};

export default api;