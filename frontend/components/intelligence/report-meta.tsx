import type { ReportConfidence } from "@/lib/intelligence";

export function ReportMeta({
  confidence,
  gaps,
}: {
  confidence: ReportConfidence;
  gaps: string[];
}) {
  return (
    <section className="flex flex-col gap-4">
      <h3 className="text-lg font-medium tracking-tight">Report meta</h3>
      <dl className="grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-muted-foreground">Overall confidence</dt>
          <dd className="capitalize">{confidence.overall}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Business model</dt>
          <dd className="capitalize">{confidence.business_model}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Competition</dt>
          <dd className="capitalize">{confidence.competition}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Quality</dt>
          <dd className="capitalize">{confidence.quality}</dd>
        </div>
      </dl>
      {gaps.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Gaps
          </p>
          <ul className="flex list-disc flex-col gap-1 pl-5 text-sm">
            {gaps.map((gap) => (
              <li key={gap}>{gap}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
