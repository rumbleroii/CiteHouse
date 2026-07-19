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
import { cn } from "@/lib/utils";

function Spinner({ className = "" }: { className?: string }) {
  return (
    <span
      className={`border-muted-foreground/30 border-t-foreground inline-block size-4 animate-spin rounded-full border-2 ${className}`}
      aria-hidden
    />
  );
}

function CompanyPanel({
  company,
  loading,
}: {
  company: CompanyLookupResponse | null;
  loading: boolean;
}) {
  if (loading) {
    return (
      <div
        className="text-muted-foreground flex h-full flex-col items-center justify-center gap-3 text-sm"
        role="status"
        aria-live="polite"
      >
        <Spinner className="size-6" />
        <span>Searching…</span>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="text-muted-foreground flex h-full items-center justify-center text-sm">
        Matched company will appear here
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col justify-center gap-6">
      <div className="flex flex-col gap-4">
        <p className="text-muted-foreground text-xs tracking-[0.18em] uppercase">
          Matched company
        </p>
        <div className="flex flex-col gap-2">
          <h2 className="font-[family-name:var(--font-display)] text-2xl font-medium tracking-tight sm:text-3xl">
            {company.company_name}
          </h2>
          <p className="font-mono text-sm">{company.company_number}</p>
        </div>
        <dl className="grid gap-3 text-sm">
          {company.company_status && (
            <div>
              <dt className="text-muted-foreground">Status</dt>
              <dd>{company.company_status}</dd>
            </div>
          )}
          {company.company_type && (
            <div>
              <dt className="text-muted-foreground">Type</dt>
              <dd>{company.company_type}</dd>
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
        const data = await lookupCompanyByNumber(result.value);
        setCompany(data);
        setQuery("");
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
      setError(err instanceof Error ? err.message : "Lookup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-[70vh] w-full grid-cols-1 md:grid-cols-2">
      <section className="flex flex-col gap-8 px-6 py-10 md:pr-10 lg:px-12">
        <div className="flex flex-col gap-2">
          <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight">
            Citehouse
          </h1>
          <p className="text-muted-foreground text-sm">
            Look up a UK company by name or Companies House number
          </p>
        </div>

        <form onSubmit={onSubmit} className="flex max-w-lg flex-col gap-4">
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
                Searching…
              </span>
            ) : awaitingFollowUp ? (
              "Continue"
            ) : (
              "Look up"
            )}
          </Button>
        </form>

        {loading && (
          <p
            className="text-muted-foreground flex max-w-lg items-center gap-2 text-sm"
            role="status"
            aria-live="polite"
          >
            <Spinner />
            Searching Companies House…
          </p>
        )}

        {!loading && agentMessage && (
          <p className="max-w-lg text-sm leading-relaxed">{agentMessage}</p>
        )}

        {!loading && !company && candidates.length > 0 && (
          <ul className="flex max-w-lg flex-col gap-2 text-sm">
            {candidates.map((item) => (
              <li key={item.company_number} className="leading-snug">
                <span className="font-medium">{item.company_name}</span>
                <span className="text-muted-foreground">
                  {" "}
                  · {item.company_number}
                  {item.address_snippet ? ` · ${item.address_snippet}` : ""}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="border-border border-t px-6 py-10 md:border-t-0 md:border-l md:pl-10 lg:px-12">
        <CompanyPanel company={company} loading={loading} />
      </section>
    </div>
  );
}
