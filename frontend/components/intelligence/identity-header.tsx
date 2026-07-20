import type { ReactNode } from "react";

import type { CompanyIdentity } from "@/lib/intelligence";
import { formatCompanyType } from "@/lib/company-type";
import { SectionLabel } from "@/components/intelligence/shared";

function ProfileField({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="py-2.5">
      <dt className="text-muted-foreground text-xs tracking-[0.14em] uppercase">
        {label}
      </dt>
      <dd className="text-ink mt-1.5 text-sm leading-relaxed">{children}</dd>
    </div>
  );
}

function formatStatus(status: string): string {
  if (!status) return status;
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatDate(value: string): string {
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return value;
  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(parsed));
}

export function IdentityHeader({ company }: { company: CompanyIdentity }) {
  const location = [company.locality, company.region, company.country]
    .filter(Boolean)
    .join(", ");

  return (
    <header className="motion-reduce:animate-none animate-[dossier-rise_0.5s_ease-out_both]">
      <SectionLabel>Company profile</SectionLabel>
      <h1 className="text-ink mt-3 font-[family-name:var(--font-display)] text-4xl leading-[1.05] tracking-tight sm:text-5xl">
        {company.company_name}
      </h1>

      <dl className="mt-8 max-w-xl">
        <ProfileField label="Company number">
          <span className="font-mono tracking-wide">
            {company.company_number}
          </span>
        </ProfileField>

        {company.company_status && (
          <ProfileField label="Status">
            {formatStatus(company.company_status)}
          </ProfileField>
        )}

        {company.company_type && (
          <ProfileField label="Company type">
            {formatCompanyType(company.company_type)}
          </ProfileField>
        )}

        {company.date_of_creation && (
          <ProfileField label="Date of incorporation">
            {formatDate(company.date_of_creation)}
          </ProfileField>
        )}

        {company.date_of_cessation && (
          <ProfileField label="Date of cessation">
            {formatDate(company.date_of_cessation)}
          </ProfileField>
        )}

        {company.address_snippet && (
          <ProfileField label="Registered office address">
            {company.address_snippet}
          </ProfileField>
        )}

        {location && !company.address_snippet && (
          <ProfileField label="Location">{location}</ProfileField>
        )}

        {company.sic_codes && company.sic_codes.length > 0 && (
          <ProfileField label="Standard Industrial Classification">
            <span className="font-mono">{company.sic_codes.join(", ")}</span>
          </ProfileField>
        )}
      </dl>
    </header>
  );
}
