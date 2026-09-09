export interface TripRequest {
  message: string;
  conversation_id?: string;
  user_id?: string;
}

export interface Flight {
  flight_number?: string;
  airline?: string;
  airline_code?: string;

  departure_airport?: string;
  arrival_airport?: string;

  departure_airport_name?: string;
  arrival_airport_name?: string;

  departure_time?: string;
  arrival_time?: string;

  duration?: number | string;
  duration_text?: string;

  stops?: number;
  stops_text?: string;

  price?: number | string;
  currency?: string;
  price_status?: string;

  travelers?: number;
  travel_class?: string;
  aircraft?: string;

  airline_logo?: string;

  booking_token?: string;
  departure_token?: string;

  status?: string;
  source?: string;
}
// export interface Hotel {
//   name: string;
//   address?: string | null;

//   image_url?: string | null;
//   platform?: string | null;

//   rating?: number | null;
//   property_type?: string | null;

//   amenities?: string[];

//   price_per_night?: number | null;
//   currency?: string | null;

//   review_count?: number | null;

//   total_price?: number | null;
//   nights?: number | null;

//   website?: string | null;
// }
export interface Hotel {
  id?: string;

  name?: string;

  address?: string;

  latitude?: number | null;

  longitude?: number | null;

  price_per_night?: number | null;

  total_price?: number | null;

  currency?: string;

  nights?: number | null;

  rating?: number | null;

  rating_scale?: number | null;

  review_count?: number;

  star_rating?: number | null;

  property_type?: string;

  bedrooms?: number | null;

  bathrooms?: number | null;

  max_occupancy?: number | null;

  amenities?: string[];

  platform?: string;

  platform_listing_id?: string;

  website?: string | null;

  // ⭐ StayingAPI hotel image
  image_url?: string | null;

  host?: {
    name?: string;

    isSuperhost?: boolean;
  };

  source?: string;
}

export interface Restaurant {
  name?: string;
  address?: string;
  rating?: number;
  cuisine?: string;
  price_level?: string;
  latitude?: number;
  longitude?: number;
}

export interface Place {
  name?: string;
  address?: string;
  formatted?: string;
  category?: string;
  rating?: number;
  description?: string;
  latitude?: number;
  longitude?: number;
}

export interface Weather {
  date?: string;
  temperature?: number;
  temperature_min?: number;
  temperature_max?: number;
  precipitation_probability?: number;
  precipitation?: number;
  wind_speed?: number;
  weather_code?: number;
  description?: string;
  latitude?: number;
  longitude?: number;
  source?: string;
}

export interface ItineraryActivity {
  time?: string;
  type?: string;

  // Backend fields
  name?: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  duration_hours?: number;
  ticket_price?: number | null;
  price?: number | null;
  price_range?: string | null;
  currency?: string | null;
  source?: string;

  // Existing frontend-compatible fields
  title?: string;
  activity?: string;
  description?: string;
  location?: string;
  duration?: string;
  estimated_cost?: number;

  details?: string | Record<string, unknown>;
}

export interface ItineraryWeather {
  date?: string;
  temperature_max?: number;
  temperature_min?: number;
  weather_code?: number;
  description?: string;
  precipitation?: number;
  wind_speed?: number;
  latitude?: number;
  longitude?: number;
  source?: string;
}

export interface ItineraryDay {
  day: number;
  date?: string;
  destination?: string;
  weather?: ItineraryWeather;
  activities?: ItineraryActivity[];

  title?: string;
  morning?: ItineraryActivity;
  afternoon?: ItineraryActivity;
  evening?: ItineraryActivity;
}

export interface Budget {
  flights?: number | null;
  hotels?: number | null;
  food?: number | null;
  activities?: number | null;
  transport?: number | null;
  total?: number | null;

  currency?: string;
  nights?: number;
  trip_days?: number;
  travelers?: number;

  remaining_budget?: number | null;

  flight_total?: number | null;
  hotel_total?: number | null;
  known_total?: number | null;

  flight_prices_available?: number;
  hotel_prices_available?: number;

  pricing_status?: string;
  price_data_available?: boolean;
  estimated?: boolean;
  note?: string;
}

export interface CurrencyConversion {
  amount?: number;
  from_currency?: string;
  to_currency?: string;
  converted_amount?: number | null;
  rate?: number | null;
  source?: string;
  status?: string;
  error?: string;
}

export interface Trip {
  trip_id?: string;
  destination?: string;
  origin?: string;
  start_date?: string;
  end_date?: string;
  travelers?: number;
  budget?: number;
  currency?: string;

  location?: Location;

  flights?: Flight[];
  hotels?: Hotel[];
  restaurants?: Restaurant[];
  // places?: Place[];
  weather?: Weather[];
  attractions?: Place[];
  itinerary?: ItineraryDay[];

  budget_breakdown?: Budget;
  currency_conversion?: CurrencyConversion;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface TripResponse {
  conversation_id?: string;
  message?: string;
  trip?: Trip;
  missing_fields?: string[];
  requires_date?: boolean;
  error?: string;
}

export interface Location {
  name?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  address?: string;
  formatted?: string;
  source?: string;
}