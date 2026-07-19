import type { Citation } from "@/lib/intelligence";

export function CitationsList({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <ul className="flex flex-col gap-2 text-sm">
      {citations.map((c, i) => {
        const label = c.title || c.source_ref || c.url || "Source";
        return (
          <li key={`${label}-${i}`} className="leading-snug">
            {c.url ? (
              <a
                href={c.url}
                target="_blank"
                rel="noreferrer"
                className="underline underline-offset-2"
              >
                {label}
              </a>
            ) : (
              <span>{label}</span>
            )}
            {c.source_ref && (
              <span className="text-muted-foreground"> · {c.source_ref}</span>
            )}
            {c.snippet && (
              <p className="text-muted-foreground mt-0.5 text-xs">{c.snippet}</p>
            )}
          </li>
        );
      })}
    </ul>
  );
}

export function TagList({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <ul className="flex flex-wrap gap-2 text-sm">
      {items.map((item) => (
        <li
          key={item}
          className="border-border text-muted-foreground rounded-md border px-2 py-0.5"
        >
          {item}
        </li>
      ))}
    </ul>
  );
}

export function SectionHeading({
  title,
  confidence,
}: {
  title: string;
  confidence?: string;
}) {
  return (
    <div className="flex flex-wrap items-baseline justify-between gap-2">
      <h3 className="text-lg font-medium tracking-tight">{title}</h3>
      {confidence && (
        <span className="text-muted-foreground text-xs uppercase tracking-wide">
          Confidence · {confidence}
        </span>
      )}
    </div>
  );
}
