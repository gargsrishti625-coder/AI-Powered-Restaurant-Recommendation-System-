export interface RecommendRequest {
  location: string;
  budget: "low" | "medium" | "high";
  cuisine: string | null;
  min_rating: number | null;
  additional_preferences: string | null;
}

export interface MatchSignals {
  budget_fit: number;
  cuisine_match: number;
  rating_pass: boolean;
  baseline_score: number;
}

export interface RecommendationItem {
  rank: number;
  restaurant_id: string;
  restaurant_name: string;
  cuisine: string;
  rating: number;
  estimated_cost: number;
  votes: number;
  ai_explanation: string;
  tradeoffs: string | null;
  confidence: "low" | "medium" | "high";
  match_signals: MatchSignals;
}

export interface RecommendResponse {
  request_id: string;
  status: "success" | "no_results" | "error";
  city: string;
  total_candidates_found: number;
  recommendations: RecommendationItem[];
  fallback_used: boolean;
  error_detail: string | null;
  latency_ms: number;
}
