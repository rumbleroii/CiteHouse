import type { ReactNode } from "react";

import type { Citation, ConfidenceLevel } from "@/lib/intelligence";
import type { ConfidenceTooltipContent } from "@/lib/confidence";

export function formatConfidence(level: ConfidenceLevel | string): string {
  const label = level.charAt(0).toUpperCase() + level.slice(1);
  return `Confidence: ${label}`;
}

export function ConfidenceWithTooltip({
  level,
  content,
  tooltipId = "confidence-tooltip",
}: {
  level: ConfidenceLevel | string;
  content: ConfidenceTooltipContent;
  tooltipId?: string;
}) {
  return (
    <span className="group relative inline-block cursor-help">
      <span
        className="decoration-accent/40 underline decoration-dotted underline-offset-4"
        tabIndex={0}
        aria-describedby={tooltipId}
      >
        {formatConfidence(level)}
      </span>
      <span
        id={tooltipId}
        role="tooltip"
        className="bg-ink text-background pointer-events-none absolute top-full left-0 z-20 mt-2 w-72 max-w-[min(18rem,calc(100vw-2rem))] rounded-md px-3 py-2.5 text-[0.7rem] leading-snug tracking-normal normal-case opacity-0 shadow-md transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
      >
        <ul className="flex flex-col gap-1.5">
          {content.criteria.map((item) => (
            <li key={item.label} className="flex items-start gap-2">
              <span
                aria-hidden
                className={`mt-px w-3 shrink-0 font-medium ${item.met ? "text-accent" : ""}`}
              >
                {item.met ? "✓" : "–"}
              </span>
              <span className={item.met ? "" : "opacity-70"}>{item.label}</span>
            </li>
          ))}
        </ul>
        <p className="border-background/20 mt-2.5 border-t pt-2 leading-relaxed opacity-90">
          {content.reasoning}
        </p>
      </span>
    </span>
  );
}

function formatCitationLabel(c: Citation): string {
  if (c.title) return c.title;
  if (c.source_ref) {
    if (c.source_ref.startsWith("companies_house:")) {
      return c.source_ref
        .replace("companies_house:", "Companies House · ")
        .replaceAll(".", " · ")
        .replaceAll("_", " ");
    }
    return c.source_ref;
  }
  if (c.url) return c.url;
  return "Source";
}

export function CitationsList({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <div className="mt-8">
      <SectionLabel>Citations</SectionLabel>
      <ol className="text-muted-foreground mt-3 flex flex-col gap-1.5 text-xs">
        {citations.map((c, i) => {
          const label = formatCitationLabel(c);
          return (
            <li key={`${label}-${i}`}>
              <span className="tabular-nums">[{i + 1}]</span>{" "}
              {c.url ? (
                <a
                  href={c.url}
                  target="_blank"
                  rel="noreferrer"
                  className="decoration-line hover:text-accent hover:decoration-accent underline underline-offset-4 transition-colors"
                >
                  {label}
                </a>
              ) : (
                <span>{label}</span>
              )}
              {c.snippet && (
                <span className="text-muted-foreground/80"> — {c.snippet}</span>
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

export function TagList({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <p className="text-ink text-sm leading-relaxed">{items.join(" · ")}</p>
  );
}

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <p className="text-muted-foreground flex items-center gap-2.5 text-xs tracking-[0.18em] uppercase">
      <span
        className="bg-accent h-3 w-0.5 shrink-0 rounded-full"
        aria-hidden
      />
      <span>{children}</span>
    </p>
  );
}
