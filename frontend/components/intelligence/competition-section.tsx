import type { CompetitionSection } from "@/lib/intelligence";
import {
  CitationsList,
  SectionHeading,
  TagList,
} from "@/components/intelligence/shared";

export function CompetitionSectionView({
  section,
}: {
  section: CompetitionSection;
}) {
  return (
    <section className="flex flex-col gap-4">
      <SectionHeading title="Competition" confidence={section.confidence} />
      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Rivalry score
          </p>
          <p className="mt-1 text-2xl font-medium tabular-nums">
            {section.rivalry_score}
            <span className="text-muted-foreground text-sm font-normal">
              {" "}
              / 5
            </span>
          </p>
        </div>
        <div>
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Peer count
          </p>
          <p className="mt-1 text-2xl font-medium tabular-nums">
            {section.peer_count_estimate.toLocaleString()}
          </p>
          <p className="text-muted-foreground text-xs">
            {section.peer_count_confidence} confidence
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Arena
          </p>
          <TagList items={section.arena.sic_codes} />
          {section.arena.geography && (
            <p className="text-sm">{section.arena.geography}</p>
          )}
        </div>
      </div>
      <p className="text-sm leading-relaxed">{section.summary}</p>
      {section.rivalry_evidence.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Rivalry evidence
          </p>
          <ul className="flex list-disc flex-col gap-1 pl-5 text-sm">
            {section.rivalry_evidence.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}
      {section.peer_set.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Peer set
          </p>
          <ul className="flex flex-col gap-1 text-sm">
            {section.peer_set.map((peer) => (
              <li key={`${peer.company_number ?? peer.company_name}`}>
                <span className="font-medium">{peer.company_name}</span>
                {peer.company_number && (
                  <span className="text-muted-foreground font-mono">
                    {" "}
                    · {peer.company_number}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="flex flex-col gap-2">
        <p className="text-muted-foreground text-xs tracking-wide uppercase">
          Citations
        </p>
        <CitationsList citations={section.citations} />
      </div>
    </section>
  );
}
