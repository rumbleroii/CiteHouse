import type { QualitySection } from "@/lib/intelligence";
import {
  CitationsList,
  SectionHeading,
  TagList,
} from "@/components/intelligence/shared";

export function QualitySectionView({ section }: { section: QualitySection }) {
  const rating = section.customer_rating;

  return (
    <section className="flex flex-col gap-4">
      <SectionHeading title="Quality" confidence={section.confidence} />
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Quality score
          </p>
          <p className="mt-1 text-2xl font-medium tabular-nums">
            {section.quality_score}
            <span className="text-muted-foreground text-sm font-normal">
              {" "}
              / 5
            </span>
          </p>
          <p className="text-muted-foreground mt-1 text-sm">
            {section.quality_rationale}
          </p>
        </div>
        {rating && (
          <div>
            <p className="text-muted-foreground text-xs tracking-wide uppercase">
              Customer rating
            </p>
            <p className="mt-1 text-2xl font-medium tabular-nums">
              {rating.score != null ? rating.score : "—"}
              {rating.scale != null && (
                <span className="text-muted-foreground text-sm font-normal">
                  {" "}
                  / {rating.scale}
                </span>
              )}
            </p>
            {rating.n_reviews != null && (
              <p className="text-muted-foreground text-xs">
                {rating.n_reviews.toLocaleString()} reviews
              </p>
            )}
            <div className="mt-2">
              <TagList items={rating.platforms} />
            </div>
          </div>
        )}
      </div>
      <p className="text-sm leading-relaxed">{section.summary}</p>
      {section.theme_sentiment.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Themes
          </p>
          <ul className="flex flex-col gap-3 text-sm">
            {section.theme_sentiment.map((theme) => (
              <li key={theme.theme}>
                <p className="font-medium">
                  {theme.theme}{" "}
                  <span className="text-muted-foreground font-normal">
                    · {theme.polarity}
                  </span>
                </p>
                <p className="text-muted-foreground mt-0.5">{theme.evidence}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="flex flex-col gap-2">
        <p className="text-muted-foreground text-xs tracking-wide uppercase">
          Trade press · {section.trade_press.tone}
        </p>
        {section.trade_press.notables.length > 0 && (
          <ul className="flex list-disc flex-col gap-1 pl-5 text-sm">
            {section.trade_press.notables.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        )}
      </div>
      <div className="flex flex-col gap-2">
        <p className="text-muted-foreground text-xs tracking-wide uppercase">
          Citations
        </p>
        <CitationsList citations={section.citations} />
      </div>
    </section>
  );
}
