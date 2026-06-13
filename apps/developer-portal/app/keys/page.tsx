import KeysClient from "./KeysClient";

export default function KeysPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-100 sm:text-4xl">
          API Key Management
        </h1>
        <p className="mt-3 max-w-2xl text-base text-slate-400">
          Generate and manage API keys to authenticate requests to the Smart City Traffic platform.
          Each key can be scoped to specific resources with configurable quotas.
        </p>
      </div>
      <KeysClient />
    </div>
  );
}
