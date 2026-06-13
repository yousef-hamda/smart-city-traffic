// The original home screen was replaced by the Expo Router auth redirect.
// This test now validates the app root redirect behaviour.

import React from "react";
import { render, screen } from "@testing-library/react-native";
import IndexRedirect from "../app/index";

jest.mock("expo-router", () => {
  const mockReact = jest.requireActual<typeof import("react")>("react");
  const { Text } = jest.requireActual<typeof import("react-native")>("react-native");
  return {
    Redirect: ({ href }: { href: string }) =>
      mockReact.createElement(Text, { testID: "redirect" }, href),
    Link: ({ children }: { children: React.ReactNode }) => children,
    useRouter: () => ({ replace: jest.fn() }),
    useSegments: () => [],
  };
});

jest.mock("../src/store/authStore", () => ({
  useAuthStore: () => ({
    token: null,
    user: null,
    isLoading: false,
    error: null,
    hydrate: jest.fn(),
    login: jest.fn(),
    logout: jest.fn(),
  }),
}));

describe("App root (index)", () => {
  it("redirects to login when no token", () => {
    render(<IndexRedirect />);
    expect(screen.getByTestId("redirect")).toBeTruthy();
  });
});
