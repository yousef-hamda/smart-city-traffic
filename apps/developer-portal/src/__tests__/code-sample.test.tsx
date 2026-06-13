import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import CodeSample from "@/src/components/CodeSample";

// Mock prism-react-renderer so tests run without the real highlighter.
// The Highlight wrapper renders code as plain text inside a <pre>.
jest.mock("prism-react-renderer", () => ({
  Highlight: ({
    children,
    code,
  }: {
    children: (props: {
      className: string;
      style: Record<string, string>;
      tokens: { content: string; types: string[] }[][];
      getLineProps: (p: { line: unknown }) => Record<string, unknown>;
      getTokenProps: (p: { token: { content: string } }) => Record<string, unknown>;
    }) => React.ReactNode;
    code: string;
  }) =>
    children({
      className: "prism-code",
      style: {},
      // One line, one token containing the entire code string
      tokens: [[{ content: code, types: ["plain"] }]],
      getLineProps: (_p: { line: unknown }) => ({}),
      getTokenProps: ({ token }: { token: { content: string } }) => ({
        children: token.content,
      }),
    }),
  themes: {
    vsDark: {},
  },
}));

const ENDPOINT = {
  method: "GET",
  path: "/api/v1/segments",
  description: "List road segments",
};

describe("CodeSample component", () => {
  it("renders the cURL tab button", () => {
    render(<CodeSample endpoint={ENDPOINT} />);
    expect(screen.getByRole("button", { name: "cURL" })).toBeInTheDocument();
  });

  it("renders all four language tab buttons", () => {
    render(<CodeSample endpoint={ENDPOINT} />);
    expect(screen.getByRole("button", { name: "cURL" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "JavaScript" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Python" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Java" })).toBeInTheDocument();
  });

  it("default (bash) code contains curl command", () => {
    render(<CodeSample endpoint={ENDPOINT} />);
    // The <pre> element should contain the curl invocation
    const pre = document.querySelector("pre");
    expect(pre?.textContent).toMatch(/curl/i);
  });

  it("switches to JavaScript tab on click — code contains fetch", () => {
    render(<CodeSample endpoint={ENDPOINT} />);
    fireEvent.click(screen.getByRole("button", { name: "JavaScript" }));
    const pre = document.querySelector("pre");
    expect(pre?.textContent).toMatch(/fetch/i);
  });

  it("switches to Python tab on click — code contains requests", () => {
    render(<CodeSample endpoint={ENDPOINT} />);
    fireEvent.click(screen.getByRole("button", { name: "Python" }));
    const pre = document.querySelector("pre");
    expect(pre?.textContent).toMatch(/requests/i);
  });

  it("switches to Java tab on click — code contains HttpClient", () => {
    render(<CodeSample endpoint={ENDPOINT} />);
    fireEvent.click(screen.getByRole("button", { name: "Java" }));
    const pre = document.querySelector("pre");
    expect(pre?.textContent).toMatch(/HttpClient/i);
  });

  it("renders a Copy button", () => {
    render(<CodeSample endpoint={ENDPOINT} />);
    expect(screen.getByRole("button", { name: "Copy" })).toBeInTheDocument();
  });

  it("uses baseUrl prop in the generated code", () => {
    render(<CodeSample endpoint={ENDPOINT} baseUrl="https://api.example.com" />);
    const pre = document.querySelector("pre");
    expect(pre?.textContent).toMatch(/api\.example\.com/);
  });
});
