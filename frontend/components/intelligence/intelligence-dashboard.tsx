import type { CompanyIntelligenceReport } from "@/lib/intelligence";
import { BusinessModelSectionView } from "@/components/intelligence/business-model-section";
import { CompetitionSectionView } from "@/components/intelligence/competition-section";
import { IdentityHeader } from "@/components/intelligence/identity-header";
import { QualitySectionView } from "@/components/intelligence/quality-section";
import { ReportMeta } from "@/components/intelligence/report-meta";

export function IntelligenceDashboard({
  report,
}: {
  report: CompanyIntelligenceReport;
}) {
  return (
    <div className="flex flex-col gap-10">
      <IdentityHeader company={report.company} />
      <div className="border-border border-t pt-8">
        <BusinessModelSectionView section={report.business_model} />
      </div>
      <div className="border-border border-t pt-8">
        <CompetitionSectionView section={report.competition} />
      </div>
      <div className="border-border border-t pt-8">
        <QualitySectionView section={report.quality} />
      </div>
      <div className="border-border border-t pt-8">
        <ReportMeta confidence={report.confidence} gaps={report.gaps} />
      </div>
    </div>
  );
}
