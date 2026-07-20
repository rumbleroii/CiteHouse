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
      { label: "Trustpilot /review/ page names company", met: trustpilot },
      { label: "Trade-press URL names company", met: tradePress },
      { label: "Profile/address corroborated", met: profileVerify },
    ],
    reasoning: all
      ? "Medium: Trustpilot review page, trade press, and profile/address corroboration all matched."
      : "Low: Need a Trustpilot /review/ page naming the company and a trade-press URL first; profile/address only counts when both of those pass. Generic Trustpilot category/platform hits do not count.",
  };
}
