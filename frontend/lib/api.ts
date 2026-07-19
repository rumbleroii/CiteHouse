const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Slim company shape returned by the search API (agent-friendly). */
export type CompanyLookupResponse = {
  company_number: string;
  company_name: string;
  company_status?: string;
  company_type?: string;
  date_of_creation?: string;
  date_of_cessation?: string;
  address_snippet?: string;
};

export type AgenticSearchResponse = {
  status: "found" | "needs_clarification" | "not_found";
  message: string;
  company: CompanyLookupResponse | null;
  candidates: CompanyLookupResponse[];
};

async function readError(res: Response, fallback: string): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") return body.detail;
  } catch {
    // ignore
  }
  return fallback;
}

export async function lookupCompanyByNumber(
  companyNumber: string,
): Promise<CompanyLookupResponse> {
  const res = await fetch(
    `${API_BASE}/api/search/by-company-number/${encodeURIComponent(companyNumber)}`,
    { cache: "no-store" },
  );

  if (!res.ok) {
    throw new Error(await readError(res, "Lookup failed"));
  }

  return res.json();
}

export async function agenticSearch(input: {
  message: string;
  priorQuery?: string | null;
  candidates?: CompanyLookupResponse[];
}): Promise<AgenticSearchResponse> {
  const res = await fetch(`${API_BASE}/api/search/agentic`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: input.message,
      prior_query: input.priorQuery || undefined,
      candidates: input.candidates?.map((c) => ({
        company_number: c.company_number,
        company_name: c.company_name,
        company_status: c.company_status,
        address_snippet: c.address_snippet,
      })),
    }),
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(await readError(res, "Agentic search failed"));
  }

  return res.json();
}
