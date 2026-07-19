import { ReportPageClient } from "@/components/intelligence/report-page-client";

type ReportPageProps = {
  params: Promise<{ companyNumber: string }>;
};

export default async function ReportPage({ params }: ReportPageProps) {
  const { companyNumber } = await params;
  const decoded = decodeURIComponent(companyNumber);

  return <ReportPageClient companyNumber={decoded} />;
}
