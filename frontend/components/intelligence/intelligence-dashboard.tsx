import type { CompanyIntelligenceReport } from "@/lib/intelligence";
import { BusinessModelSectionView } from "@/components/intelligence/business-model-section";
import { CompetitionSectionView } from "@/components/intelligence/competition-section";
import { IdentityHeader } from "@/components/intelligence/identity-header";
import { QualitySectionView } from "@/components/intelligence/quality-section";

export function IntelligenceDashboard({
  report,
}: {
  report: CompanyIntelligenceReport;
}) {
  return (
    <article className="mx-auto max-w-3xl px-5 py-12 sm:px-8 sm:py-16">
      <IdentityHeader company={report.company} />
      <BusinessModelSectionView section={report.business_model} />
      <CompetitionSectionView section={report.competition} />
      <QualitySectionView section={report.quality} />
    </article>
  );
}
