"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { IntelligenceDashboard } from "@/components/intelligence/intelligence-dashboard";
import { buttonVariants } from "@/components/ui/button";
import {
  intelligenceStreamUrl,
  startIntelligenceRun,
} from "@/lib/api";
import type {
  CompanyIntelligenceReport,
  IntelligenceStage,
} from "@/lib/intelligence";
import { cn } from "@/lib/utils";

function Spinner() {
  return (
    <span
      className="border-accent-weak border-t-accent inline-block size-5 animate-spin rounded-full border-2"
      aria-hidden
    />
  );
}

function stageLabel(stage: IntelligenceStage | undefined): string {
  switch (stage) {
    case "profile":
      return "Building company profile…";
    case "business_model":
      return "Analysing business model…";
    case "competition":
      return "Mapping competition…";
    case "quality":
      return "Assessing reputation & quality…";
    case "done":
      return "Report ready";
    default:
      return "Starting intelligence agents…";
  }
}

export function ReportPageClient({
  companyNumber,
}: {
  companyNumber: string;
}) {
  const [report, setReport] = useState<CompanyIntelligenceReport | null>(null);
  const [stage, setStage] = useState<IntelligenceStage | undefined>("profile");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let source: EventSource | null = null;

    async function run() {
      setLoading(true);
      setError(null);
      setReport(null);
      setStage("profile");

      try {
        const { run_id } = await startIntelligenceRun(companyNumber);
        if (cancelled) return;

        source = new EventSource(intelligenceStreamUrl(run_id));

        source.addEventListener("stage", (ev) => {
          try {
            const data = JSON.parse((ev as MessageEvent).data) as {
              stage?: IntelligenceStage;
            };
            if (data.stage) setStage(data.stage);
          } catch {
            // ignore
          }
        });

        source.addEventListener("report", (ev) => {
          try {
            const data = JSON.parse(
              (ev as MessageEvent).data,
            ) as CompanyIntelligenceReport;
            setReport((prev) => ({ ...(prev || {}), ...data }));
            if (data.stage) setStage(data.stage);
            setLoading(false);
          } catch {
            // ignore
          }
        });

        source.addEventListener("done", (ev) => {
          try {
            const data = JSON.parse(
              (ev as MessageEvent).data,
            ) as CompanyIntelligenceReport;
            setReport((prev) => ({ ...(prev || {}), ...data }));
            setStage("done");
            setLoading(false);
          } catch {
            // ignore
          }
          source?.close();
        });

        source.addEventListener("run_error", (ev) => {
          try {
            const data = JSON.parse((ev as MessageEvent).data) as {
              detail?: string;
            };
            if (!cancelled) {
              setError(data.detail || "Intelligence run failed");
              setLoading(false);
            }
          } catch {
            if (!cancelled) {
              setError("Intelligence run failed");
              setLoading(false);
            }
          }
          source?.close();
        });
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to start report",
          );
          setLoading(false);
        }
      }
    }

    void run();

    return () => {
      cancelled = true;
      source?.close();
    };
  }, [companyNumber]);

  return (
    <div className="page-wash min-h-screen">
      <header className="border-line/80 border-b bg-background/60 backdrop-blur-sm">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-4 px-5 py-4 sm:px-8">
          <Link
            href="/"
            className="brand-mark font-[family-name:var(--font-display)] text-lg font-medium tracking-tight"
          >
            Citehouse
          </Link>
          <Link
            href="/"
            className={cn(
              buttonVariants({ variant: "outline", size: "sm" }),
              "hover:border-accent/40 hover:text-accent",
            )}
          >
            New lookup
          </Link>
        </div>
      </header>

      {loading && !report && (
        <div
          className="text-muted-foreground flex min-h-[40vh] flex-col items-center justify-center gap-3 text-sm"
          role="status"
          aria-live="polite"
        >
          <Spinner />
          <span>{stageLabel(stage)}</span>
        </div>
      )}

      {error && (
        <div className="mx-auto flex max-w-3xl flex-col gap-4 px-5 py-16 sm:px-8">
          <p className="text-destructive text-sm leading-relaxed">{error}</p>
          <Link
            href="/"
            className={cn(
              buttonVariants({ variant: "outline" }),
              "w-fit hover:border-accent/40 hover:text-accent",
            )}
          >
            Back to lookup
          </Link>
        </div>
      )}

      {!error && (report || (!loading && stage)) && (
        <IntelligenceDashboard report={report} stage={stage} />
      )}
    </div>
  );
}
