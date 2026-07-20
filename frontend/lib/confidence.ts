import type {
  CompetitionConfidenceFactors,
  ConfidenceLevel,
  QualityConfidenceFactors,
} from "@/lib/intelligence";

export type ConfidenceCriterion = {
  label: string;
  met: boolean;
};

export type ConfidenceTooltipContent = {
  criteria: ConfidenceCriterion[];
  reasoning: string;
};

/** Mirrors backend business_model_confidence. */
export function businessModelConfidenceTooltip(
  _level: ConfidenceLevel | string,
  sicCodes: string[] | null | undefined,
): ConfidenceTooltipContent {
  const hasSic = Boolean(sicCodes?.length);
  return {
    criteria: [{ label: "SIC codes present", met: hasSic }],
    reasoning: hasSic
      ? "Medium: statutory activity codes ground the business-model inference."
      : "Low: without SIC codes there is little Companies House grounding.",
  };
}

/** Mirrors backend competition_confidence. */
export function competitionConfidenceTooltip(
  _level: ConfidenceLevel | string,
  factors?: CompetitionConfidenceFactors | null,
  peerCount?: number,
): ConfidenceTooltipContent {
  const hasPeers =
    factors?.peer_set ?? (typeof peerCount === "number" ? peerCount > 0 : false);
  const hasWeb = factors?.web_company_refs ?? false;
  const hasProfile = factors?.profile_verify ?? false;

  let reasoning: string;
  if (hasPeers && hasWeb && hasProfile) {
    reasoning =
      "High: peer set, web results naming this company, and profile/address corroboration all passed.";
  } else if (hasPeers) {
    reasoning =
      "Medium: peer set is available, but web name and/or profile corroboration are incomplete.";
  } else {
    reasoning = "Low: no peer set from Companies House for this arena.";
  }

  return {
    criteria: [
      { label: "Peer set available", met: hasPeers },
      { label: "Web search contains company", met: hasWeb },
      { label: "Profile/address corroborated", met: hasProfile },
    ],
    reasoning,
  };
}

/** Mirrors backend quality_confidence. */
export function qualityConfidenceTooltip(
  _level: ConfidenceLevel | string,
  factors?: QualityConfidenceFactors | null,
): ConfidenceTooltipContent {
  const trustpilot = factors?.trustpilot ?? false;
  const tradePress = factors?.trade_press ?? false;
  const profileVerify = factors?.profile_verify ?? false;
  const all = trustpilot && tradePress && profileVerify;

  return {
    criteria: [
      { label: "Trustpilot mentions company", met: trustpilot },
      { label: "Trade press mentions company", met: tradePress },
      { label: "Profile/address corroborated", met: profileVerify },
    ],
    reasoning: all
      ? "Medium: Trustpilot, trade press, and a profile detail match all passed."
      : "Low: Trustpilot, trade press, and profile corroboration are all required.",
  };
}
