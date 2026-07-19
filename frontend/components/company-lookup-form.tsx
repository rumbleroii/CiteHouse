"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { lookupCompanyByNumber } from "@/lib/api";
import { parseCompanyQuery } from "@/lib/company-query";

export function CompanyLookupForm() {
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [companyName, setCompanyName] = useState<string | null>(null);
  const [companyNumber, setCompanyNumber] = useState<string | null>(null);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setCompanyName(null);
    setCompanyNumber(null);

    const result = parseCompanyQuery(query);
    if (!result.ok) {
      setError(result.error);
      return;
    }

    if (result.type !== "number") {
      setError("For now, enter an exact Companies House registration number");
      return;
    }

    setError(null);
    setLoading(true);
    try {
      const data = await lookupCompanyByNumber(result.value);
      setCompanyName(data.company_name);
      setCompanyNumber(data.company_number);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lookup failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex w-full max-w-md flex-col gap-4">
      <div className="flex flex-col gap-2">
        <Label htmlFor="company-query">Company</Label>
        <Input
          id="company-query"
          name="company-query"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (error) setError(null);
          }}
          placeholder="e.g. 00000006"
          autoComplete="off"
          disabled={loading}
          aria-invalid={!!error}
          aria-describedby={
            error ? "company-query-error" : "company-query-hint"
          }
        />
        {error ? (
          <p id="company-query-error" className="text-destructive text-sm">
            {error}
          </p>
        ) : (
          <p id="company-query-hint" className="text-muted-foreground text-sm">
            Enter an exact Companies House registration number
          </p>
        )}
      </div>

      <Button type="submit" className="w-full sm:w-auto" disabled={loading}>
        {loading ? "Looking up…" : "Look up"}
      </Button>

      {companyName && (
        <div className="flex flex-col gap-1 text-sm">
          <p className="text-muted-foreground">Company name</p>
          <p className="text-lg font-medium tracking-tight">{companyName}</p>
          {companyNumber && (
            <p className="text-muted-foreground">{companyNumber}</p>
          )}
        </div>
      )}
    </form>
  );
}
