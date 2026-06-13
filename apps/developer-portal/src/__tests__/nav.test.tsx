import { render, screen } from "@testing-library/react";
import TopNav from "@/src/components/TopNav";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  usePathname: jest.fn(() => "/"),
}));

// Mock next/link
jest.mock("next/link", () => {
  const MockLink = ({
    href,
    children,
    className,
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
  }) => (
    <a href={href} className={className}>
      {children}
    </a>
  );
  MockLink.displayName = "MockLink";
  return MockLink;
});

describe("TopNav component", () => {
  it("renders the Catalog link", () => {
    render(<TopNav />);
    expect(screen.getByRole("link", { name: /catalog/i })).toBeInTheDocument();
  });

  it("renders the Explorer link", () => {
    render(<TopNav />);
    expect(screen.getByRole("link", { name: /explorer/i })).toBeInTheDocument();
  });

  it("renders the API Keys link", () => {
    render(<TopNav />);
    expect(screen.getByRole("link", { name: /api keys/i })).toBeInTheDocument();
  });

  it("renders the Pricing link", () => {
    render(<TopNav />);
    expect(screen.getByRole("link", { name: /pricing/i })).toBeInTheDocument();
  });

  it("renders the demo portal badge", () => {
    render(<TopNav />);
    expect(screen.getByText(/demo portal — no live backend/i)).toBeInTheDocument();
  });

  it("Catalog link points to /", () => {
    render(<TopNav />);
    const catalogLinks = screen.getAllByRole("link").filter((l) => l.getAttribute("href") === "/");
    expect(catalogLinks.length).toBeGreaterThan(0);
  });

  it("Explorer link points to /explore", () => {
    render(<TopNav />);
    const link = screen.getByRole("link", { name: /explorer/i });
    expect(link.getAttribute("href")).toBe("/explore");
  });

  it("API Keys link points to /keys", () => {
    render(<TopNav />);
    const link = screen.getByRole("link", { name: /api keys/i });
    expect(link.getAttribute("href")).toBe("/keys");
  });

  it("Pricing link points to /pricing", () => {
    render(<TopNav />);
    const link = screen.getByRole("link", { name: /pricing/i });
    expect(link.getAttribute("href")).toBe("/pricing");
  });

  it("renders Smart City Traffic brand text", () => {
    render(<TopNav />);
    expect(screen.getByText(/smart city traffic/i)).toBeInTheDocument();
  });
});
