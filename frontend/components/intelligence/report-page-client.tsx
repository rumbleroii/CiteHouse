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

const STREAM_IDLE_MS = 120_000;

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
  const [stage, setStage] = useState<IntelligenceStage | undefined>("profile");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let finished = false;
    let source: EventSource | null = null;
    let idleTimer: ReturnType<typeof setTimeout> | null = null;

    function clearIdle() {
      if (idleTimer) {
        clearTimeout(idleTimer);
        idleTimer = null;
      }
    }

    function fail(message: string) {
      if (cancelled || finished) return;
      finished = true;
      setError(message);
      setLoading(false);
      clearIdle();
      source?.close();
    }

    function bumpIdle() {
      if (finished) return;
      clearIdle();
      idleTimer = setTimeout(() => {
        fail("Intelligence stream timed out. Please try again.");
      }, STREAM_IDLE_MS);
    }

    async function run() {
      setLoading(true);
      setError(null);
      setReport(null);
      setStage("profile");

      try {
        const { run_id } = await startIntelligenceRun(companyNumber);
        if (cancelled) return;

        source = new EventSource(intelligenceStreamUrl(run_id));
        bumpIdle();

        source.onerror = () => {
          // EventSource also fires onerror when the server closes after done.
          fail("Lost connection to the intelligence stream. Please try again.");
        };

        source.addEventListener("stage", (ev) => {
          bumpIdle();
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
          bumpIdle();
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
          finished = true;
          clearIdle();
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
            fail(data.detail || "Intelligence run failed");
          } catch {
            fail("Intelligence run failed");
          }
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
      clearIdle();
      source?.close();
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

      {loading && !report && !error && (
        <div
          className="text-muted-foreground flex min-h-[40vh] flex-col items-center justify-center gap-3 text-sm"
          role="status"
          aria-live="polite"
        >
          <Spinner />
          <span>Starting intelligence agents…</span>
        </div>
      )}

      {error && (
        <div className="mx-auto flex max-w-3xl flex-col gap-3 px-5 pt-8 sm:px-8">
          <p className="text-destructive text-sm" role="alert">
            {error}
          </p>
          {!report && (
            <Link
              href="/"
              className={cn(buttonVariants({ variant: "outline" }), "w-fit")}
            >
              Back to lookup
            </Link>
          )}
        </div>
      )}

      {(report || (!loading && !error && stage)) && (
        <IntelligenceDashboard report={report} stage={stage} />
      )}
    </div>
  );
}
