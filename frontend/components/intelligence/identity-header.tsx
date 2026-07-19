import type { CompanyIdentity } from "@/lib/intelligence";
import { TagList } from "@/components/intelligence/shared";

export function IdentityHeader({ company }: { company: CompanyIdentity }) {
  return (
    <header className="flex flex-col gap-4">
      <p className="text-muted-foreground text-xs tracking-wide uppercase">
        Intelligence report
      </p>
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-medium tracking-tight sm:text-3xl">
          {company.company_name}
        </h2>
        <p className="font-mono text-sm">{company.company_number}</p>
      </div>
      <dl className="grid gap-3 text-sm sm:grid-cols-2">
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
        {company.address_snippet && (
          <div className="sm:col-span-2">
            <dt className="text-muted-foreground">Address</dt>
            <dd>{company.address_snippet}</dd>
          </div>
        )}
      </dl>
      {company.sic_codes && company.sic_codes.length > 0 && (
        <div className="flex flex-col gap-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            SIC codes
          </p>
          <TagList items={company.sic_codes} />
        </div>
      )}
    </header>
  );
}
