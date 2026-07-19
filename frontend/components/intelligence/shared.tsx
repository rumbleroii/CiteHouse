import type { Citation } from "@/lib/intelligence";

export function CitationsList({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <ol className="text-muted-foreground mt-6 flex flex-col gap-1.5 text-xs">
      {citations.map((c, i) => {
        const label = c.title || c.source_ref || c.url || "Source";
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
  );
}

export function TagList({ items }: { items: string[] }) {
  if (!items.length) return null;
  return (
    <p className="text-ink text-sm leading-relaxed">{items.join(" · ")}</p>
  );
}

export function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-muted-foreground text-xs tracking-[0.18em] uppercase">
      {children}
    </p>
  );
}
