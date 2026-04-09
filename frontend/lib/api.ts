import type { RecommendRequest, RecommendResponse } from "./types";

const BASE = "/api";

export async function fetchLocations(): Promise<string[]> {
  const res = await fetch(`${BASE}/locations`);
  if (!res.ok) throw new Error("Failed to load locations");
  return res.json();
}

export async function fetchCuisines(): Promise<string[]> {
  const res = await fetch(`${BASE}/cuisines`);
  if (!res.ok) throw new Error("Failed to load cuisines");
  return res.json();
}

export async function fetchRecommendations(
  req: RecommendRequest
): Promise<RecommendResponse> {
  const res = await fetch(`${BASE}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err?.detail;
    const msg = Array.isArray(detail)
      ? detail.map((d: { msg: string }) => d.msg).join("; ")
      : String(detail || "Request failed");
    throw new Error(msg);
  }
  return res.json();
}
