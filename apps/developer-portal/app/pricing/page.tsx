interface PricingTier {
  name: string;
  price: string;
  period: string;
  description: string;
  highlight: boolean;
  badge?: string;
  features: string[];
  limits: { label: string; value: string }[];
  cta: string;
  ctaStyle: "primary" | "secondary" | "outline";
}

const TIERS: PricingTier[] = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for hobbyists and early exploration of the Smart City Traffic API.",
    highlight: false,
    features: [
      "Read-only REST access",
      "Segments & incidents endpoints",
      "Community support",
      "OpenAPI documentation",
      "1 API key",
    ],
    limits: [
      { label: "Monthly calls", value: "10,000" },
      { label: "Rate limit", value: "60 req/min" },
      { label: "Data freshness", value: "60 s" },
      { label: "History retention", value: "7 days" },
      { label: "SLA", value: "None" },
    ],
    cta: "Get started free",
    ctaStyle: "outline",
  },
  {
    name: "Pro",
    price: "$49",
    period: "per month",
    description: "For developers building production-grade smart-city applications.",
    highlight: true,
    badge: "Most popular",
    features: [
      "All REST endpoints",
      "GraphQL federated access",
      "ML prediction endpoints",
      "AI assistant (100 queries/day)",
      "WebSocket subscriptions",
      "5 API keys",
      "Email support (48 h)",
      "Webhook callbacks",
    ],
    limits: [
      { label: "Monthly calls", value: "500,000" },
      { label: "Rate limit", value: "600 req/min" },
      { label: "Data freshness", value: "5 s" },
      { label: "History retention", value: "90 days" },
      { label: "SLA", value: "99.5%" },
    ],
    cta: "Start Pro trial",
    ctaStyle: "primary",
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "annual contract",
    description:
      "Dedicated infrastructure, SLA guarantees, and custom integrations for city-scale deployments.",
    highlight: false,
    features: [
      "Everything in Pro",
      "Dedicated gateway instance",
      "On-premises / private cloud",
      "Custom ML model fine-tuning",
      "Priority support (4 h SLA)",
      "SSO / SAML",
      "Audit logs & SIEM export",
      "Unlimited API keys",
      "Custom data retention",
      "Professional services credits",
    ],
    limits: [
      { label: "Monthly calls", value: "Unlimited" },
      { label: "Rate limit", value: "Custom burst" },
      { label: "Data freshness", value: "Real-time" },
      { label: "History retention", value: "Custom" },
      { label: "SLA", value: "99.9%" },
    ],
    cta: "Contact sales",
    ctaStyle: "secondary",
  },
];

function CheckIcon() {
  return (
    <svg
      className="h-4 w-4 shrink-0 text-emerald-400"
      viewBox="0 0 16 16"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M3 8l3.5 3.5 6.5-7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function TierCard({ tier }: { tier: PricingTier }) {
  const ctaClasses: Record<string, string> = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-500",
    secondary: "bg-slate-700 text-slate-100 hover:bg-slate-600",
    outline: "border border-slate-600 text-slate-300 hover:border-slate-500 hover:text-slate-100",
  };

  return (
    <div
      className={[
        "relative flex flex-col rounded-2xl border p-8 transition-shadow",
        tier.highlight
          ? "border-indigo-500/60 bg-indigo-950/30 shadow-lg shadow-indigo-900/20"
          : "border-slate-700/60 bg-slate-800/30",
      ].join(" ")}
    >
      {tier.badge !== undefined && (
        <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
          <span className="rounded-full bg-indigo-600 px-3 py-1 text-xs font-semibold text-white shadow">
            {tier.badge}
          </span>
        </div>
      )}

      <div className="mb-6">
        <h3 className="text-lg font-bold text-slate-100">{tier.name}</h3>
        <div className="mt-2 flex items-end gap-2">
          <span className="text-4xl font-bold text-slate-100">{tier.price}</span>
          <span className="mb-1 text-sm text-slate-400">{tier.period}</span>
        </div>
        <p className="mt-3 text-sm text-slate-400">{tier.description}</p>
      </div>

      {/* CTA */}
      <button
        className={[
          "mb-6 w-full rounded-lg px-4 py-2.5 text-sm font-semibold transition-colors",
          ctaClasses[tier.ctaStyle] ?? ctaClasses["outline"],
        ].join(" ")}
      >
        {tier.cta}
      </button>

      {/* Limits */}
      <div className="mb-6 rounded-lg border border-slate-700/50 bg-slate-800/40 p-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Limits</p>
        <dl className="space-y-2">
          {tier.limits.map((l) => (
            <div key={l.label} className="flex justify-between text-sm">
              <dt className="text-slate-400">{l.label}</dt>
              <dd className="font-medium text-slate-200">{l.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      {/* Features */}
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Included</p>
      <ul className="space-y-2">
        {tier.features.map((f) => (
          <li key={f} className="flex items-center gap-2.5 text-sm text-slate-300">
            <CheckIcon />
            {f}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function PricingPage() {
  return (
    <div>
      {/* Header */}
      <div className="mb-12 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-slate-100 sm:text-4xl">
          Simple, transparent pricing
        </h1>
        <p className="mt-4 mx-auto max-w-2xl text-base text-slate-400">
          Start for free, scale to Pro when you need real-time data and ML predictions, or talk to
          us for city-scale Enterprise deployments.
        </p>
      </div>

      {/* Tier cards */}
      <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-3">
        {TIERS.map((tier) => (
          <TierCard key={tier.name} tier={tier} />
        ))}
      </div>

      {/* FAQ */}
      <div className="mx-auto mt-16 max-w-2xl">
        <h2 className="mb-6 text-xl font-semibold text-slate-100 text-center">
          Frequently asked questions
        </h2>
        <div className="space-y-4">
          {[
            {
              q: "Can I upgrade or downgrade at any time?",
              a: "Yes. Plan changes take effect at the start of your next billing cycle. Unused quota does not roll over.",
            },
            {
              q: "What counts as an API call?",
              a: "Every successful HTTP response (2xx) and every GraphQL operation resolution. Validation errors (4xx) before processing are not counted.",
            },
            {
              q: "Is there a free trial for Pro?",
              a: "Yes — a 14-day Pro trial is available without a credit card. You keep your quota and keys if you upgrade.",
            },
            {
              q: "How is Enterprise pricing calculated?",
              a: "Enterprise is priced on traffic volume, data retention requirements, and support SLA tier. Contact sales for a custom quote.",
            },
          ].map(({ q, a }) => (
            <div key={q} className="rounded-xl border border-slate-700/60 bg-slate-800/30 p-5">
              <p className="font-semibold text-slate-200">{q}</p>
              <p className="mt-2 text-sm text-slate-400">{a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
