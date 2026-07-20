import type { QualitySection } from "@/lib/intelligence";
import { qualityConfidenceTooltip } from "@/lib/confidence";
import {
  CitationsList,
  ConfidenceWithTooltip,
  SectionLabel,
  TagList,
} from "@/components/intelligence/shared";

const polarityClass: Record<string, string> = {
  positive: "text-green-700",
  negative: "text-red-700",
  neutral: "text-muted-foreground",
  mixed: "text-muted-foreground",
};

export function QualitySectionView({ section }: { section: QualitySection }) {
  const content = qualityConfidenceTooltip(
    section.confidence,
    section.confidence_factors,
  );

  return (
    <section className="border-line mt-12 border-t pt-12 motion-reduce:animate-none animate-[dossier-rise_0.5s_ease-out_both]">
      <SectionLabel>
        Reputation &amp; quality ·{" "}
        <ConfidenceWithTooltip
          level={section.confidence}
          content={content}
          tooltipId="quality-confidence-tooltip"
        />
      </SectionLabel>
      <p className="text-ink mt-4 max-w-prose text-base leading-relaxed">
        {section.summary}
      </p>
      <p className="text-muted-foreground mt-3 max-w-prose text-sm">
        {section.quality_rationale}
      </p>

      {section.customer_rating && (
        <div className="mt-6 flex flex-col gap-2">
          <SectionLabel>Customer rating platforms</SectionLabel>
          <TagList items={section.customer_rating.platforms} />
        </div>
      )}

      {section.theme_sentiment.length > 0 && (
        <dl className="border-line mt-8 divide-y divide-[var(--line)] border-y">
          {section.theme_sentiment.map((t) => (
            <div
              key={t.theme}
              className="flex flex-col gap-1 py-3 sm:flex-row sm:gap-6"
            >
              <dt
                className={`w-40 shrink-0 text-sm font-medium ${polarityClass[t.polarity] ?? "text-muted-foreground"}`}
              >
                {t.theme}
                <span className="text-muted-foreground font-normal">
                  {" "}
                  · {t.polarity}
                </span>
              </dt>
              <dd className="text-muted-foreground text-sm">{t.evidence}</dd>
            </div>
          ))}
        </dl>
      )}

      {(section.confidence_factors?.trade_press ||
        section.trade_press.notables.length > 0) && (
        <div className="mt-8 flex flex-col gap-2">
          <SectionLabel>Trade press · {section.trade_press.tone}</SectionLabel>
          {section.trade_press.notables.length > 0 ? (
            <ul className="text-muted-foreground flex list-disc flex-col gap-1 pl-5 text-sm">
              {section.trade_press.notables.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground text-sm">
              Trade-press coverage found; no notable headlines extracted.
            </p>
          )}
        </div>
      )}

      <CitationsList citations={section.citations} />
    </section>
  );
}
