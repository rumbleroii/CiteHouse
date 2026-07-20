"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";

import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  agenticSearch,
  lookupCompanyByNumber,
  type CompanyLookupResponse,
} from "@/lib/api";
import { parseCompanyQuery } from "@/lib/company-query";
import { formatCompanyType } from "@/lib/company-type";
import { cn } from "@/lib/utils";

function Spinner({ className = "" }: { className?: string }) {
  return (
    <span
      className={`border-muted-foreground/30 border-t-accent inline-block size-4 animate-spin rounded-full border-2 ${className}`}
      aria-hidden
    />
  );
}

function StatusChip({ status }: { status: string }) {
  return (
    <span className="bg-accent-weak text-accent inline-flex rounded-md px-2 py-0.5 text-xs font-medium capitalize">
      {status}
    </span>
  );
}

function CompanyPanel({
  company,
  candidates,
  loading,
  onSelectCandidate,
}: {
  company: CompanyLookupResponse | null;
  candidates: CompanyLookupResponse[];
  loading: boolean;
  onSelectCandidate: (item: CompanyLookupResponse) => void;
}) {
  if (loading) {
    return (
      <div
        className="text-muted-foreground flex min-h-48 items-center justify-center gap-2 text-sm"
        role="status"
        aria-live="polite"
      >
        <Spinner />
        Searching…
      </div>
    );
  }

  if (company) {
    return (
      <div className="motion-reduce:animate-none flex flex-col gap-6 animate-[dossier-rise_0.45s_ease-out_both]">
        <div className="flex flex-col gap-4">
          <p className="text-muted-foreground text-xs tracking-[0.18em] uppercase">
            Matched company
          </p>
          <div className="flex flex-col gap-2">
            <h2 className="font-[family-name:var(--font-display)] text-2xl font-medium tracking-tight sm:text-3xl">
              {company.company_name}
            </h2>
          </div>
          <dl className="grid gap-3 text-sm">
            <div>
              <dt className="text-muted-foreground">Company number</dt>
              <dd className="font-mono">{company.company_number}</dd>
            </div>
            {company.company_status && (
              <div>
                <dt className="text-muted-foreground">Status</dt>
                <dd className="mt-1">
                  <StatusChip status={company.company_status} />
                </dd>
              </div>
            )}
            {company.company_type && (
              <div>
                <dt className="text-muted-foreground">Type</dt>
                <dd>{formatCompanyType(company.company_type)}</dd>
              </div>
            )}
            {company.date_of_creation && (
              <div>
                <dt className="text-muted-foreground">Created</dt>
                <dd>{company.date_of_creation}</dd>
              </div>
            )}
            {company.date_of_cessation && (
              <div>
                <dt className="text-muted-foreground">Ceased</dt>
                <dd>{company.date_of_cessation}</dd>
              </div>
            )}
            {company.address_snippet && (
              <div>
                <dt className="text-muted-foreground">Address</dt>
                <dd>{company.address_snippet}</dd>
              </div>
            )}
          </dl>
        </div>

        <Link
          href={`/report/${encodeURIComponent(company.company_number)}`}
          className={cn(buttonVariants({ size: "lg" }), "w-full sm:w-auto")}
        >
          Generate report
        </Link>
      </div>
    );
  }

  if (candidates.length > 0) {
    return (
      <div className="motion-reduce:animate-none flex flex-col gap-4 animate-[dossier-rise_0.45s_ease-out_both]">
        <p className="text-muted-foreground text-xs tracking-[0.18em] uppercase">
          Suggestions
        </p>
        <ul className="flex flex-col gap-1">
          {candidates.map((item) => (
            <li key={item.company_number}>
              <button
                type="button"
                onClick={() => onSelectCandidate(item)}
                className="hover:bg-accent-weak/60 focus-visible:ring-ring w-full rounded-md px-3 py-2.5 text-left text-sm transition-colors focus-visible:ring-2 focus-visible:outline-none"
              >
                <span className="font-medium">{item.company_name}</span>
                <span className="text-muted-foreground mt-0.5 block text-xs leading-snug">
                  Company number {item.company_number}
                  {item.address_snippet ? ` · ${item.address_snippet}` : ""}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className="text-muted-foreground flex min-h-48 items-center justify-center text-sm">
      Matched company will appear here
    </div>
  );
}

export function CompanyLookupForm() {
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [agentMessage, setAgentMessage] = useState<string | null>(null);
  const [priorQuery, setPriorQuery] = useState<string | null>(null);
  const [awaitingFollowUp, setAwaitingFollowUp] = useState(false);
  const [company, setCompany] = useState<CompanyLookupResponse | null>(null);
  const [candidates, setCandidates] = useState<CompanyLookupResponse[]>([]);

  function resetSession() {
    setCompany(null);
    setCandidates([]);
    setAgentMessage(null);
    setAwaitingFollowUp(false);
    setPriorQuery(null);
  }

  function selectCandidate(item: CompanyLookupResponse) {
    setCompany(item);
    setCandidates([]);
    setAgentMessage(null);
    setAwaitingFollowUp(false);
    setPriorQuery(null);
    setQuery("");
    setError(null);
  }

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    const result = parseCompanyQuery(query);
    if (!result.ok) {
      setError(result.error);
      return;
    }

    setLoading(true);
    try {
      if (result.type === "number" && !awaitingFollowUp) {
        resetSession();
        try {
          const data = await lookupCompanyByNumber(result.value);
          setCompany(data);
          setQuery("");
        } catch (err) {
          setCompany(null);
          setAgentMessage(
            err instanceof Error
              ? err.message
              : "Couldn’t find that company number. Check it and try again.",
          );
          setQuery("");
        }
        return;
      }

      const userText =
        result.type === "number" ? result.value : result.query;
      const isFollowUp = awaitingFollowUp;

      if (!isFollowUp) {
        resetSession();
      }

      const data = await agenticSearch({
        message: userText,
        priorQuery: isFollowUp ? priorQuery : null,
        candidates: isFollowUp ? candidates : undefined,
      });

      if (data.status === "not_found") {
        resetSession();
        setAgentMessage(data.message || "No matching company found.");
        setQuery("");
        return;
      }

      if (data.status === "found") {
        setAwaitingFollowUp(false);
        setPriorQuery(null);
        setCandidates([]);
        setAgentMessage(data.message);
        setCompany(data.company);
        setQuery("");
        return;
      }

      setPriorQuery(isFollowUp ? priorQuery : userText);
      setAwaitingFollowUp(true);
      setCompany(null);
      setCandidates(data.candidates);
      setAgentMessage(data.message);
      setQuery("");
    } catch (err) {
      setCompany(null);
      setAgentMessage(
        err instanceof Error
          ? err.message
          : "Search couldn’t be completed. Please try again.",
      );
      setQuery("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid w-full max-w-5xl grid-cols-1 md:grid-cols-[1fr_auto_1fr] md:items-stretch">
      <section className="flex flex-col justify-center gap-8 px-2 py-6 md:px-8 md:py-4">
        <div className="flex flex-col gap-3">
          <h1 className="brand-mark font-[family-name:var(--font-display)] text-4xl font-semibold tracking-tight sm:text-5xl">
            Citehouse
          </h1>
          <p className="text-muted-foreground max-w-sm text-sm leading-relaxed">
            Identify a UK registered company by legal name or Companies House
            number
          </p>
        </div>

        <form onSubmit={onSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="company-query">
              {awaitingFollowUp ? "Add a detail" : "Company"}
            </Label>
            <Input
              id="company-query"
              name="company-query"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (error) setError(null);
              }}
              placeholder={
                awaitingFollowUp
                  ? "e.g. in London, active, incorporated 2019"
                  : "Name or number, e.g. Tesco or 00000006"
              }
              autoComplete="off"
              disabled={loading}
              aria-invalid={!!error}
              aria-describedby={error ? "company-query-error" : undefined}
            />
            {error && (
              <p id="company-query-error" className="text-destructive text-sm">
                {error}
              </p>
            )}
          </div>

          <Button type="submit" className="w-full sm:w-auto" disabled={loading}>
            {loading ? (
              <span className="inline-flex items-center gap-2">
                <Spinner className="border-primary-foreground/30 border-t-primary-foreground" />
                Searching Companies…
              </span>
            ) : awaitingFollowUp ? (
              "Continue"
            ) : (
              "Look up"
            )}
          </Button>
        </form>

        {!loading && agentMessage && (
          <aside
            className="border-accent border-l-2 pl-4"
            aria-live="polite"
          >
            {(company || !(awaitingFollowUp || candidates.length > 0)) && (
              <p className="text-muted-foreground mb-1.5 text-xs tracking-[0.14em] uppercase">
                {company ? "Match" : "No match"}
              </p>
            )}
            <p className="text-[0.9375rem] leading-relaxed text-pretty">
              {agentMessage}
            </p>
          </aside>
        )}
      </section>

      <div
        className="border-accent/25 my-2 border-t md:mx-0 md:my-0 md:h-auto md:w-px md:self-stretch md:border-t-0 md:border-l"
        aria-hidden
      />

      <section className="flex flex-col justify-center px-2 py-6 md:px-8 md:py-4">
        <CompanyPanel
          company={company}
          candidates={candidates}
          loading={loading}
          onSelectCandidate={selectCandidate}
        />
      </section>
    </div>
  );
}
