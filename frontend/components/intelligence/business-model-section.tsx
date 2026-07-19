import type { BusinessModelSection } from "@/lib/intelligence";
import {
  CitationsList,
  SectionHeading,
  TagList,
} from "@/components/intelligence/shared";

export function BusinessModelSectionView({
  section,
}: {
  section: BusinessModelSection;
}) {
  return (
    <section className="flex flex-col gap-4">
      <SectionHeading title="Business model" confidence={section.confidence} />
      <p className="text-sm leading-relaxed">{section.summary}</p>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="flex flex-col gap-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Revenue model
          </p>
          <TagList items={section.revenue_model_tags} />
        </div>
        <div className="flex flex-col gap-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Customer segments
          </p>
          <TagList items={section.customer_segments} />
        </div>
        <div className="flex flex-col gap-2 sm:col-span-2">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Products &amp; services
          </p>
          <TagList items={section.products_services} />
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <p className="text-muted-foreground text-xs tracking-wide uppercase">
          Citations
        </p>
        <CitationsList citations={section.citations} />
      </div>
    </section>
  );
}
