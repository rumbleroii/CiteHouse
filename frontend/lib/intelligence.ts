/** Mirrors backend/schema CompanyIntelligenceReport for the dashboard. */

export type ConfidenceLevel = "high" | "medium" | "low";
export type Polarity = "positive" | "neutral" | "negative" | "mixed";
export type TradePressTone = Polarity;

export type Citation = {
  title?: string | null;
  url?: string | null;
  source_ref?: string | null;
  snippet?: string | null;
};

export type CompanyIdentity = {
  company_number: string;
  company_name: string;
  company_status?: string | null;
  company_type?: string | null;
  date_of_creation?: string | null;
  date_of_cessation?: string | null;
  address_snippet?: string | null;
  locality?: string | null;
  region?: string | null;
  country?: string | null;
  sic_codes?: string[] | null;
};

export type BusinessModelSection = {
  sic_codes: string[];
  revenue_model_tags: string[];
  customer_segments: string[];
  products_services: string[];
  summary: string;
  citations: Citation[];
  confidence: ConfidenceLevel;
};

export type CompetitionArena = {
  sic_codes: string[];
  geography?: string | null;
};

export type PeerCompany = {
  company_name: string;
  company_number?: string | null;
};

export type CompetitionSection = {
  arena: CompetitionArena;
  peer_set: PeerCompany[];
  peer_count_estimate: number;
  peer_count_confidence: ConfidenceLevel;
  rivalry_score: number;
  rivalry_evidence: string[];
  summary: string;
  citations: Citation[];
  confidence: ConfidenceLevel;
};

export type CustomerRating = {
  score?: number | null;
  scale?: number | null;
  n_reviews?: number | null;
  platforms: string[];
};

export type ThemeSentiment = {
  theme: string;
  polarity: Polarity;
  evidence: string;
};

export type TradePress = {
  tone: TradePressTone;
  notables: string[];
};

export type QualitySection = {
  customer_rating?: CustomerRating | null;
  theme_sentiment: ThemeSentiment[];
  trade_press: TradePress;
  quality_score: number;
  quality_rationale: string;
  summary: string;
  citations: Citation[];
  confidence: ConfidenceLevel;
};

export type ReportConfidence = {
  overall: ConfidenceLevel;
  business_model: ConfidenceLevel;
  competition: ConfidenceLevel;
  quality: ConfidenceLevel;
};

export type IntelligenceStage =
  | "profile"
  | "business_model"
  | "competition"
  | "quality"
  | "done"
  | "error";

/** Progressive report — pillars appear as each agent finishes. */
export type CompanyIntelligenceReport = {
  company?: CompanyIdentity;
  business_model?: BusinessModelSection;
  competition?: CompetitionSection;
  quality?: QualitySection;
  confidence?: ReportConfidence;
  gaps?: string[];
  stage?: IntelligenceStage;
};
