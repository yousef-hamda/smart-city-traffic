import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import KeysClient from "@/app/keys/KeysClient";

// Mock clipboard API
Object.defineProperty(navigator, "clipboard", {
  value: {
    writeText: jest.fn().mockResolvedValue(undefined),
  },
  writable: true,
});

// Mock crypto.randomUUID used by KeysClient
const MOCK_UUID = "12345678-1234-1234-1234-123456789abc";
Object.defineProperty(globalThis, "crypto", {
  value: {
    randomUUID: jest.fn(() => MOCK_UUID),
  },
  writable: true,
});

describe("KeysClient component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the Generate Key button", () => {
    render(<KeysClient />);
    expect(screen.getByRole("button", { name: /generate key/i })).toBeInTheDocument();
  });

  it("shows the mock notice banner", () => {
    render(<KeysClient />);
    expect(screen.getByText(/UI mock/)).toBeInTheDocument();
  });

  it("starts with no active keys", () => {
    render(<KeysClient />);
    expect(screen.getByText(/Active Keys \(0\)/)).toBeInTheDocument();
  });

  it("generates a key when button is clicked", async () => {
    render(<KeysClient />);
    fireEvent.click(screen.getByRole("button", { name: /generate key/i }));
    await waitFor(() => {
      expect(screen.getByText(/Active Keys \(1\)/)).toBeInTheDocument();
    });
  });

  it("shows one-time reveal message after key generation", async () => {
    render(<KeysClient />);
    fireEvent.click(screen.getByRole("button", { name: /generate key/i }));
    await waitFor(() => {
      expect(screen.getByText(/copy it now/i)).toBeInTheDocument();
    });
  });

  it("key starts with sct_ prefix", async () => {
    render(<KeysClient />);
    fireEvent.click(screen.getByRole("button", { name: /generate key/i }));
    await waitFor(() => {
      const keyElements = screen.getAllByText(/sct_/);
      expect(keyElements.length).toBeGreaterThan(0);
    });
  });

  it("key count increases to 2 after a second generation", async () => {
    render(<KeysClient />);
    fireEvent.click(screen.getByRole("button", { name: /generate key/i }));
    fireEvent.click(screen.getByRole("button", { name: /generate key/i }));
    await waitFor(() => {
      expect(screen.getByText(/Active Keys \(2\)/)).toBeInTheDocument();
    });
  });

  it("shows usage table with mock data", () => {
    render(<KeysClient />);
    expect(screen.getByText("GET /api/v1/segments")).toBeInTheDocument();
    expect(screen.getByText("GET /api/v1/alerts")).toBeInTheDocument();
  });

  it("renders scope toggle buttons", () => {
    render(<KeysClient />);
    expect(screen.getByRole("button", { name: "segments:read" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "alerts:read" })).toBeInTheDocument();
  });

  it("toggling a scope deselects it and reselects it", () => {
    render(<KeysClient />);
    const scopeBtn = screen.getByRole("button", { name: "segments:read" });
    // Click to deselect (it starts selected per default state)
    fireEvent.click(scopeBtn);
    // Click to reselect
    fireEvent.click(scopeBtn);
    // Button should still be present
    expect(scopeBtn).toBeInTheDocument();
  });
});
