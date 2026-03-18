/*
  app/page.js  (Home Page — route: "/")
  --------------------------------------
  This is what a visitor sees when they open the website.

  It's intentionally simple — it just renders <HeroSection />.
  All the visual complexity lives inside HeroSection.jsx.

  Later you can add more sections here (Features, Pricing, FAQ etc.)
  by importing and dropping in more components.
*/

import HeroSection from "@/components/HeroSection";

export default function HomePage() {
    return (
        <>
            {/* Hero — the big first impression */}
            <HeroSection />

            {/*
        ──────────────────────────────────────────
        Add more sections below as the project grows, e.g.:
          <FeaturesSection />
          <PricingSection />
          <FAQSection />
        ──────────────────────────────────────────
      */}
        </>
    );
}
