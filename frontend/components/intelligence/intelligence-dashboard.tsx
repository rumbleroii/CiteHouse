import type {
  CompanyIntelligenceReport,
  IntelligenceStage,
} from "@/lib/intelligence";
import { BusinessModelSectionView } from "@/components/intelligence/business-model-section";
import { CompetitionSectionView } from "@/components/intelligence/competition-section";
import { IdentityHeader } from "@/components/intelligence/identity-header";
import { QualitySectionView } from "@/components/intelligence/quality-section";
import { SectionLabel } from "@/components/intelligence/shared";

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

  return (
    <article className="mx-auto max-w-3xl px-5 py-12 sm:px-8 sm:py-16">
      {report?.company ? (
        <IdentityHeader company={report.company} />
      ) : (
        <PillarPending label="Company profile" />
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
