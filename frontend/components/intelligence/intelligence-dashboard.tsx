import type {
  CompanyIntelligenceReport,
  IntelligenceStage,
} from "@/lib/intelligence";
import { BusinessModelSectionView } from "@/components/intelligence/business-model-section";
import { CompetitionSectionView } from "@/components/intelligence/competition-section";
import { IdentityHeader } from "@/components/intelligence/identity-header";
import { QualitySectionView } from "@/components/intelligence/quality-section";
import { SectionLabel } from "@/components/intelligence/shared";

const STAGE_LABELS: { id: IntelligenceStage; label: string }[] = [
  { id: "profile", label: "Profile" },
  { id: "business_model", label: "Business model" },
  { id: "competition", label: "Competition" },
  { id: "quality", label: "Quality" },
  { id: "done", label: "Done" },
];

function stageIndex(stage?: IntelligenceStage): number {
  if (!stage || stage === "error") return -1;
  return STAGE_LABELS.findIndex((s) => s.id === stage);
}

function PillarPending({ label }: { label: string }) {
  return (
    <section className="border-line mt-10 border-t pt-10">
      <SectionLabel>{label}</SectionLabel>
      <p className="text-muted-foreground mt-4 text-sm">Analysing…</p>
    </section>
  );
}

export function IntelligenceDashboard({
  report,
  stage,
}: {
  report: CompanyIntelligenceReport | null;
  stage?: IntelligenceStage;
}) {
  const current = stage ?? report?.stage;
  const idx = stageIndex(current);

  return (
    <article className="mx-auto max-w-3xl px-5 py-12 sm:px-8 sm:py-16">
      <div className="mb-10 flex flex-wrap gap-2 text-xs tracking-[0.14em] uppercase">
        {STAGE_LABELS.filter((s) => s.id !== "done").map((s, i) => {
          const active = current === s.id;
          const done =
            current === "done" || (idx >= 0 && i < idx) ||
            (s.id === "business_model" && !!report?.business_model) ||
            (s.id === "competition" && !!report?.competition) ||
            (s.id === "quality" && !!report?.quality) ||
            (s.id === "profile" && !!report?.company);
          return (
            <span
              key={s.id}
              className={
                active
                  ? "text-accent"
                  : done
                    ? "text-ink"
                    : "text-muted-foreground"
              }
            >
              {s.label}
              {i < STAGE_LABELS.length - 2 ? " ·" : ""}
            </span>
          );
        })}
        {current === "done" && <span className="text-accent">Done</span>}
      </div>

      {report?.company ? (
        <IdentityHeader company={report.company} />
      ) : (
        <PillarPending label="Companies House profile" />
      )}

      {report?.business_model ? (
        <BusinessModelSectionView section={report.business_model} />
      ) : (
        (current === "business_model" ||
          current === "competition" ||
          current === "quality" ||
          current === "done" ||
          !!report?.company) && <PillarPending label="Business model" />
      )}

      {report?.competition ? (
        <CompetitionSectionView section={report.competition} />
      ) : (
        (current === "competition" ||
          current === "quality" ||
          current === "done" ||
          !!report?.business_model) && (
          <PillarPending label="Competition" />
        )
      )}

      {report?.quality ? (
        <QualitySectionView section={report.quality} />
      ) : (
        (current === "quality" || current === "done" || !!report?.competition) && (
          <PillarPending label="Reputation & quality" />
        )
      )}
    </article>
  );
}
