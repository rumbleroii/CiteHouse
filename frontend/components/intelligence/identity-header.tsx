import type { CompanyIdentity } from "@/lib/intelligence";
import { SectionLabel, TagList } from "@/components/intelligence/shared";

export function IdentityHeader({ company }: { company: CompanyIdentity }) {
  return (
    <header className="motion-reduce:animate-none animate-[dossier-rise_0.5s_ease-out_both]">
      <SectionLabel>Company intelligence dossier</SectionLabel>
      <h1 className="text-ink mt-3 font-[family-name:var(--font-display)] text-4xl leading-[1.05] tracking-tight sm:text-5xl">
        {company.company_name}
      </h1>
      <div className="text-muted-foreground mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
        <span className="text-ink font-mono">{company.company_number}</span>
        {company.company_status && <span>· {company.company_status}</span>}
        {company.company_type && <span>· {company.company_type}</span>}
        {(company.locality || company.region) && (
          <span>
            · {[company.locality, company.region].filter(Boolean).join(", ")}
          </span>
        )}
      </div>
      {company.address_snippet && (
        <p className="text-muted-foreground mt-2 max-w-prose text-sm">
          {company.address_snippet}
        </p>
      )}
      {company.sic_codes && company.sic_codes.length > 0 && (
        <div className="mt-5 flex flex-col gap-2">
          <SectionLabel>SIC codes</SectionLabel>
          <TagList items={company.sic_codes} />
        </div>
      )}
    </header>
  );
}
