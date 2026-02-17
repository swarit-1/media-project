// User types
export type UserRole = "freelancer" | "editor" | "admin";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  first_name?: string;
  last_name?: string;
  display_name: string;
  avatar_url?: string;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  display_name: string;
  role: UserRole;
}

// Pitch types
export type PitchWindowStatus = "draft" | "open" | "closed" | "cancelled";
export type PitchStatus = "draft" | "submitted" | "under_review" | "accepted" | "rejected" | "withdrawn";
export type AssignmentStatus = "assigned" | "in_progress" | "submitted" | "revision_requested" | "approved" | "published" | "killed";
export type PaymentStatus = "pending" | "escrow_held" | "release_triggered" | "processing" | "completed" | "failed" | "refunded";

export interface PitchWindow {
  id: string;
  newsroom_id: string;
  editor_id: string;
  title: string;
  description: string;
  beats: string[];
  requirements?: string;
  budget_min?: number;
  budget_max?: number;
  rate_type: string;
  max_pitches: number;
  current_pitch_count: number;
  opens_at: string;
  closes_at: string;
  status: PitchWindowStatus;
  created_at: string;
}

export interface Pitch {
  id: string;
  pitch_window_id: string;
  freelancer_id: string;
  headline: string;
  summary: string;
  approach?: string;
  estimated_word_count?: number;
  proposed_rate?: number;
  proposed_rate_type?: string;
  estimated_delivery_days?: number;
  status: PitchStatus;
  editor_notes?: string;
  rejection_reason?: string;
  submitted_at?: string;
  reviewed_at?: string;
  created_at: string;
}

export interface Assignment {
  id: string;
  pitch_id: string;
  freelancer_id: string;
  editor_id: string;
  newsroom_id: string;
  agreed_rate: number;
  rate_type: string;
  word_count_target?: number;
  deadline: string;
  status: AssignmentStatus;
  revision_count: number;
  max_revisions: number;
  revision_notes?: string;
  content_url?: string;
  final_word_count?: number;
  kill_fee_percentage: number;
  draft_url?: string;
  final_url?: string;
  cms_post_id?: string;
  published_at?: string;
  started_at?: string;
  submitted_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: string;
  assignment_id: string;
  newsroom_id: string;
  freelancer_id: string;
  payment_type: string;
  gross_amount: number;
  platform_fee: number;
  net_amount: number;
  status: PaymentStatus;
  description?: string;
  created_at: string;
  completed_at?: string;
}

// Discovery types
export interface FreelancerProfile {
  id: string;
  user_id: string;
  display_name: string;
  bio: string;
  home_city: string;
  home_state: string;
  home_country: string;
  primary_beats: string[];
  secondary_beats: string[];
  languages: string[];
  availability_status: string;
  per_word_rate?: number;
  hourly_rate_min?: number;
  hourly_rate_max?: number;
  identity_verified: boolean;
  portfolio_verified: boolean;
  trust_score: number;
  quality_score: number;
  reliability_score: number;
}

// Pagination
export interface PaginationMeta {
  page: number;
  per_page: number;
  total_results: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  results: T[];
  pagination: PaginationMeta;
}

// KPI
export interface KPIStat {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
}
