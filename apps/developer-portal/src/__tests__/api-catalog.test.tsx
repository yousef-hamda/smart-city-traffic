import { render, screen } from "@testing-library/react";
import { apiGroups, getAllEndpoints, getEndpointById } from "@/src/lib/api-catalog";

// Simple component for testing endpoint card rendering
function EndpointList() {
  const endpoints = getAllEndpoints();
  return (
    <ul>
      {endpoints.map((ep) => (
        <li key={ep.id} data-testid="endpoint-card">
          <span data-testid={`method-${ep.id}`}>{ep.method}</span>
          <span data-testid={`path-${ep.id}`}>{ep.path}</span>
          <span data-testid={`desc-${ep.id}`}>{ep.description}</span>
        </li>
      ))}
    </ul>
  );
}

function GroupList() {
  return (
    <ul>
      {apiGroups.map((g) => (
        <li key={g.group} data-testid="group-item">
          <span data-testid={`group-label-${g.group}`}>{g.label}</span>
        </li>
      ))}
    </ul>
  );
}

describe("api-catalog data", () => {
  it("exports at least 6 groups", () => {
    expect(apiGroups.length).toBeGreaterThanOrEqual(6);
  });

  it("exports at least 10 endpoints total", () => {
    const all = getAllEndpoints();
    expect(all.length).toBeGreaterThanOrEqual(10);
  });

  it("every endpoint has a non-empty id, method, path, and description", () => {
    const all = getAllEndpoints();
    for (const ep of all) {
      expect(ep.id.length).toBeGreaterThan(0);
      expect(ep.method.length).toBeGreaterThan(0);
      expect(ep.path.length).toBeGreaterThan(0);
      expect(ep.description.length).toBeGreaterThan(0);
    }
  });

  it("getEndpointById returns the correct endpoint", () => {
    const ep = getEndpointById("auth-login");
    expect(ep).toBeDefined();
    expect(ep?.method).toBe("POST");
    expect(ep?.path).toBe("/api/v1/auth/login");
  });

  it("getEndpointById returns undefined for unknown id", () => {
    expect(getEndpointById("does-not-exist")).toBeUndefined();
  });

  it("auth group contains register and login endpoints", () => {
    const authGroup = apiGroups.find((g) => g.group === "auth");
    expect(authGroup).toBeDefined();
    const ids = authGroup!.endpoints.map((e) => e.id);
    expect(ids).toContain("auth-register");
    expect(ids).toContain("auth-login");
  });
});

describe("EndpointList component", () => {
  it("renders an endpoint card for each endpoint", () => {
    const { getAllByTestId } = render(<EndpointList />);
    const cards = getAllByTestId("endpoint-card");
    expect(cards.length).toBe(getAllEndpoints().length);
  });

  it("renders the method for a known endpoint", () => {
    render(<EndpointList />);
    expect(screen.getByTestId("method-auth-login").textContent).toBe("POST");
  });

  it("renders the path for a known endpoint", () => {
    render(<EndpointList />);
    expect(screen.getByTestId("path-auth-login").textContent).toBe("/api/v1/auth/login");
  });
});

describe("GroupList component", () => {
  it("renders a group item for every api group", () => {
    const { getAllByTestId } = render(<GroupList />);
    expect(getAllByTestId("group-item").length).toBe(apiGroups.length);
  });

  it("renders the Authentication label", () => {
    render(<GroupList />);
    expect(screen.getByTestId("group-label-auth").textContent).toBe("Authentication");
  });
});
