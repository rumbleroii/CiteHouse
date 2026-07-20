import type { CompetitionSection } from "@/lib/intelligence";
import { competitionConfidenceTooltip } from "@/lib/confidence";
import {
  CitationsList,
  ConfidenceWithTooltip,
  SectionLabel,
  TagList,
} from "@/components/intelligence/shared";

export function CompetitionSectionView({
  section,
}: {
  section: CompetitionSection;
}) {
  const content = competitionConfidenceTooltip(
    section.confidence,
    section.confidence_factors,
    section.peer_set?.length ?? section.peer_count_estimate,
  );

  return (
    <section className="border-line mt-12 border-t pt-12 motion-reduce:animate-none animate-[dossier-rise_0.5s_ease-out_both]">
      <SectionLabel>
        Competition ·{" "}
        <ConfidenceWithTooltip
          level={section.confidence}
          content={content}
          tooltipId="competition-confidence-tooltip"
        />
      </SectionLabel>
      <p className="text-ink mt-4 max-w-prose text-base leading-relaxed">
        {section.summary}
      </p>

      <div className="mt-6 flex flex-col gap-2">
        <SectionLabel>Arena</SectionLabel>
        <TagList items={section.arena.sic_codes} />
        {section.arena.geography && (
          <p className="text-sm">{section.arena.geography}</p>
        )}
      </div>

      {section.rivalry_evidence.length > 0 && (
        <ul className="text-muted-foreground mt-6 flex list-disc flex-col gap-1.5 pl-5 text-sm">
          {section.rivalry_evidence.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}

      {section.peer_set.length > 0 && (
        <div className="mt-8">
          <SectionLabel>Peer set</SectionLabel>
          <ul
            className={
              section.peer_set.length > 5
                ? "border-line mt-3 max-h-[16.25rem] divide-y divide-[var(--line)] overflow-y-auto border-y"
                : "border-line mt-3 divide-y divide-[var(--line)] border-y"
            }
          >
            {section.peer_set.map((peer) => (
              <li
                key={`${peer.company_number ?? peer.company_name}`}
                className="flex flex-wrap items-baseline justify-between gap-2 py-3 text-sm"
              >
                <span className="font-medium">{peer.company_name}</span>
                {peer.company_number && (
                  <span className="text-muted-foreground font-mono text-xs">
                    {peer.company_number}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      <CitationsList citations={section.citations} />
    </section>
  );
}
