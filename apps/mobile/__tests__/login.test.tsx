import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react-native";
import LoginScreen from "../app/(auth)/login";

// Mock expo-router before importing the component
jest.mock("expo-router", () => ({
  Link: ({ children }: { children: React.ReactNode }) => children,
  useRouter: () => ({ replace: jest.fn(), push: jest.fn() }),
  useSegments: () => [],
  Redirect: () => null,
  Stack: { Screen: () => null },
}));

// Mock i18next / react-i18next
jest.mock("react-i18next", () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: {
      changeLanguage: jest.fn(),
      language: "en",
    },
  }),
  initReactI18next: { type: "3rdParty", init: jest.fn() },
}));

// Mock the i18n setup module to avoid side effects
jest.mock("../src/i18n", () => ({
  default: {
    isInitialized: true,
    language: "en",
    t: (k: string) => k,
    changeLanguage: jest.fn(),
  },
  isRtl: jest.fn().mockReturnValue(false),
  applyRtl: jest.fn(),
}));

const mockLoginFn = jest.fn();
const mockStoreFn = jest.fn();

// Mock the auth store
jest.mock("../src/store/authStore", () => ({
  useAuthStore: () => ({
    login: mockLoginFn,
    register: mockStoreFn,
    isLoading: false,
    error: null,
    token: null,
    user: null,
    logout: jest.fn(),
    hydrate: jest.fn(),
  }),
}));

describe("LoginScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders correctly", () => {
    render(<LoginScreen />);
    expect(screen.getByTestId("email-input")).toBeTruthy();
    expect(screen.getByTestId("password-input")).toBeTruthy();
    expect(screen.getByTestId("login-button")).toBeTruthy();
  });

  it("shows validation error when submitting with empty email", async () => {
    render(<LoginScreen />);
    fireEvent.press(screen.getByTestId("login-button"));

    await waitFor(() => {
      expect(screen.getByText("auth.emailRequired")).toBeTruthy();
    });
    expect(mockLoginFn).not.toHaveBeenCalled();
  });

  it("shows validation error for invalid email format", async () => {
    render(<LoginScreen />);
    fireEvent.changeText(screen.getByTestId("email-input"), "notanemail");
    fireEvent.press(screen.getByTestId("login-button"));

    await waitFor(() => {
      expect(screen.getByText("auth.emailInvalid")).toBeTruthy();
    });
    expect(mockLoginFn).not.toHaveBeenCalled();
  });

  it("shows validation error for missing password", async () => {
    render(<LoginScreen />);
    fireEvent.changeText(screen.getByTestId("email-input"), "user@test.com");
    fireEvent.press(screen.getByTestId("login-button"));

    await waitFor(() => {
      expect(screen.getByText("auth.passwordRequired")).toBeTruthy();
    });
    expect(mockLoginFn).not.toHaveBeenCalled();
  });

  it("shows validation error for short password", async () => {
    render(<LoginScreen />);
    fireEvent.changeText(screen.getByTestId("email-input"), "user@test.com");
    fireEvent.changeText(screen.getByTestId("password-input"), "short");
    fireEvent.press(screen.getByTestId("login-button"));

    await waitFor(() => {
      expect(screen.getByText("auth.passwordTooShort")).toBeTruthy();
    });
    expect(mockLoginFn).not.toHaveBeenCalled();
  });

  it("calls authStore.login with valid credentials", async () => {
    mockLoginFn.mockResolvedValue(undefined);
    render(<LoginScreen />);

    fireEvent.changeText(screen.getByTestId("email-input"), "user@example.com");
    fireEvent.changeText(screen.getByTestId("password-input"), "password123");
    fireEvent.press(screen.getByTestId("login-button"));

    await waitFor(() => {
      expect(mockLoginFn).toHaveBeenCalledWith("user@example.com", "password123");
    });
  });
});
