import type { BusinessModelSection } from "@/lib/intelligence";
import {
  CitationsList,
  SectionLabel,
  TagList,
} from "@/components/intelligence/shared";

export function BusinessModelSectionView({
  section,
}: {
  section: BusinessModelSection;
}) {
  return (
    <section className="border-line mt-10 border-t pt-10 motion-reduce:animate-none animate-[dossier-rise_0.5s_ease-out_both]">
      <SectionLabel>Business model · {section.confidence}</SectionLabel>
      <p className="text-ink mt-4 max-w-prose font-[family-name:var(--font-display)] text-xl leading-snug">
        {section.summary}
      </p>
      <div className="mt-8 grid gap-8 sm:grid-cols-2">
        <div className="flex flex-col gap-2">
          <SectionLabel>Revenue model</SectionLabel>
          <TagList items={section.revenue_model_tags} />
        </div>
        <div className="flex flex-col gap-2">
          <SectionLabel>Customer segments</SectionLabel>
          <TagList items={section.customer_segments} />
        </div>
        <div className="flex flex-col gap-2 sm:col-span-2">
          <SectionLabel>Products &amp; services</SectionLabel>
          <TagList items={section.products_services} />
        </div>
      </div>
      <CitationsList citations={section.citations} />
    </section>
  );
}
