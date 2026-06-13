"use client";

import { useState } from "react";
import { Highlight, themes } from "prism-react-renderer";

export type Language = "bash" | "javascript" | "python" | "java";

interface Tab {
  id: Language;
  label: string;
}

const TABS: Tab[] = [
  { id: "bash", label: "cURL" },
  { id: "javascript", label: "JavaScript" },
  { id: "python", label: "Python" },
  { id: "java", label: "Java" },
];

interface CodeSampleProps {
  endpoint: {
    method: string;
    path: string;
    description?: string;
  };
  baseUrl?: string;
}

function buildSample(language: Language, method: string, path: string, baseUrl: string): string {
  const url = `${baseUrl}${path}`;
  const upper = method.toUpperCase();
  const hasBody = upper === "POST" || upper === "PUT" || upper === "PATCH";
  const bodyJson = `{"key": "value"}`;

  if (language === "bash") {
    const bodyFlag = hasBody ? ` \\\n  -d '${bodyJson}'` : "";
    return `curl -X ${upper} '${url}' \\
  -H 'Authorization: Bearer <YOUR_TOKEN>' \\
  -H 'Content-Type: application/json'${bodyFlag}`;
  }

  if (language === "javascript") {
    const body = hasBody ? `\n  body: JSON.stringify(${bodyJson}),` : "";
    return `const response = await fetch('${url}', {
  method: '${upper}',
  headers: {
    'Authorization': 'Bearer <YOUR_TOKEN>',
    'Content-Type': 'application/json',
  },${body}
});

const data = await response.json();
console.log(data);`;
  }

  if (language === "python") {
    const bodyArg = hasBody ? `, json=${bodyJson}` : "";
    return `import requests

headers = {
    "Authorization": "Bearer <YOUR_TOKEN>",
    "Content-Type": "application/json",
}

response = requests.${upper.toLowerCase()}(
    "${url}",
    headers=headers${bodyArg},
)

print(response.json())`;
  }

  // java
  const bodyBlock = hasBody
    ? `
        String body = "${bodyJson.replace(/"/g, '\\"')}";
        request.setEntity(new StringEntity(body, ContentType.APPLICATION_JSON));`
    : "";
  return `import java.net.http.*;
import java.net.URI;

HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("${url}"))
    .header("Authorization", "Bearer <YOUR_TOKEN>")
    .${upper === "GET" ? "GET()" : `method("${upper}", HttpRequest.BodyPublishers.ofString("${bodyJson.replace(/"/g, '\\"')}"))`}
    .build();${bodyBlock}

HttpResponse<String> response = client.send(
    request, HttpResponse.BodyHandlers.ofString()
);
System.out.println(response.body());`;
}

export default function CodeSample({
  endpoint,
  baseUrl = "http://localhost:3000",
}: CodeSampleProps) {
  const [activeTab, setActiveTab] = useState<Language>("bash");
  const [copied, setCopied] = useState(false);

  const code = buildSample(activeTab, endpoint.method, endpoint.path, baseUrl);

  function handleCopy() {
    void navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-700/60 bg-slate-900">
      {/* Tab bar */}
      <div className="flex items-center border-b border-slate-700/60 bg-slate-800/50 px-3 py-1 gap-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={[
              "rounded px-3 py-1 text-xs font-medium transition-colors",
              activeTab === tab.id
                ? "bg-indigo-600/30 text-indigo-300"
                : "text-slate-400 hover:text-slate-200",
            ].join(" ")}
          >
            {tab.label}
          </button>
        ))}
        <div className="flex-1" />
        <button
          onClick={handleCopy}
          className="rounded px-2.5 py-1 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>

      {/* Code */}
      <Highlight theme={themes.vsDark} code={code} language={activeTab}>
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
          <pre className={`${className} overflow-x-auto p-4 text-sm leading-relaxed`} style={style}>
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line })}>
                {line.map((token, key) => (
                  <span key={key} {...getTokenProps({ token })} />
                ))}
              </div>
            ))}
          </pre>
        )}
      </Highlight>
    </div>
  );
}
