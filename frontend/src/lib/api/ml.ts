import { api } from "./client";

export interface PortfolioItem {
  id: string;
  freelancer_id: string;
  url: string;
  title: string;
  publication?: string;
  published_date?: string;
  word_count?: number;
  topics: string[];
  tone_profile?: Record<string, number>;
  outlet_tier?: string;
  geo_focus?: string;
  verification_status: "pending" | "verified" | "rejected" | "disputed";
  created_at: string;
}

export interface StyleFingerprint {
  id: string;
  entity_type: string;
  entity_id: string;
  style_metrics: Record<string, number>;
  created_at: string;
}

export interface TrustScore {
  freelancer_id: string;
  trust_score: number;
  previous_score?: number;
  components: Record<string, number>;
  computed_at: string;
}

// ---- Portfolio ----

export function ingestPortfolio(data: { urls: string[] }) {
  return api.post<PortfolioItem[]>("/portfolio/ingest", data);
}

export function listMyPortfolio() {
  return api.get<PortfolioItem[]>("/portfolio/my");
}

export function getPortfolioItem(itemId: string) {
  return api.get<PortfolioItem>(`/portfolio/${itemId}`);
}

export function listFreelancerPortfolio(freelancerId: string) {
  return api.get<PortfolioItem[]>(`/portfolio/freelancer/${freelancerId}`);
}

// ---- Style ----

export function computeStyleFingerprint() {
  return api.post<StyleFingerprint>("/style/compute");
}

export function getStyleFingerprint(entityType: string, entityId: string) {
  return api.get<StyleFingerprint>(`/style/fingerprint/${entityType}/${entityId}`);
}

export function findStyleMatches(data: { newsroom_id: string; limit?: number }) {
  return api.post<{ freelancer_id: string; similarity: number }[]>("/style/match", data);
}

// ---- Duplicate detection ----

export function checkDuplicate(data: { headline: string; summary: string }) {
  return api.post<{ is_duplicate: boolean; similar_pitches: { pitch_id: string; similarity: number }[] }>("/duplicate/check", data);
}

// ---- Trust score ----

export function computeTrustScore(freelancerId: string) {
  return api.post<TrustScore>("/trust-score/compute", { freelancer_id: freelancerId });
}

export function getMyTrustScore() {
  return api.get<TrustScore>("/trust-score/my");
}
