"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { IntelligenceDashboard } from "@/components/intelligence/intelligence-dashboard";
import { buttonVariants } from "@/components/ui/button";
import { fetchIntelligenceReport } from "@/lib/api";
import type { CompanyIntelligenceReport } from "@/lib/intelligence";
import { cn } from "@/lib/utils";

function Spinner() {
  return (
    <span
      className="border-muted-foreground/30 border-t-foreground inline-block size-5 animate-spin rounded-full border-2"
      aria-hidden
    />
  );
}

export function ReportPageClient({
  companyNumber,
}: {
  companyNumber: string;
}) {
  const [report, setReport] = useState<CompanyIntelligenceReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setReport(null);

    fetchIntelligenceReport(companyNumber)
      .then((data) => {
        if (!cancelled) setReport(data);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load report",
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [companyNumber]);

  return (
    <div className="min-h-screen">
      <header className="border-line border-b">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-5 py-4 sm:px-8">
          <Link
            href="/"
            className="font-[family-name:var(--font-display)] text-lg font-medium tracking-tight"
          >
            Citehouse
          </Link>
          <Link
            href="/"
            className={cn(buttonVariants({ variant: "outline", size: "sm" }))}
          >
            New lookup
          </Link>
        </div>
      </header>

      {loading && (
        <div
          className="text-muted-foreground flex min-h-[50vh] flex-col items-center justify-center gap-3 text-sm"
          role="status"
          aria-live="polite"
        >
          <Spinner />
          <span>Generating intelligence report…</span>
        </div>
      )}

      {!loading && error && (
        <div className="mx-auto flex max-w-3xl flex-col gap-4 px-5 py-16 sm:px-8">
          <p className="text-destructive text-sm">{error}</p>
          <Link href="/" className={cn(buttonVariants({ variant: "outline" }))}>
            Back to lookup
          </Link>
        </div>
      )}

      {!loading && report && <IntelligenceDashboard report={report} />}
    </div>
  );
}
