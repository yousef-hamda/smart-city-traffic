/**
 * Zustand auth store.
 * Handles login, register, and logout.
 * Persists the JWT token via expo-secure-store through storage.ts.
 * Falls back to mock when no backend is available.
 */

import { create } from "zustand";
import * as api from "../lib/api";
import { saveToken, loadToken, clearToken } from "../lib/storage";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
}

export interface AuthState {
  token: string | null;
  user: AuthUser | null;
  isLoading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  hydrate: () => Promise<void>;
}

export type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>((set) => ({
  token: null,
  user: null,
  isLoading: false,
  error: null,

  hydrate: async () => {
    set({ isLoading: true, error: null });
    try {
      const token = await loadToken();
      if (token) {
        // Decode user info from the mock token payload (base64 middle part)
        try {
          const parts = token.split(".");
          if (parts.length === 3 && parts[1]) {
            const payload = JSON.parse(decodeURIComponent(escape(atob(parts[1])))) as {
              sub?: string;
              email?: string;
            };
            set({
              token,
              user: {
                id: payload.sub ?? "unknown",
                email: payload.email ?? "unknown",
                name: payload.email?.split("@")[0] ?? "User",
              },
            });
          } else {
            set({ token });
          }
        } catch {
          set({ token });
        }
      }
    } finally {
      set({ isLoading: false });
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const result = await api.login(email, password);
      await saveToken(result.token);
      set({ token: result.token, user: result.user, isLoading: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      set({ isLoading: false, error: message });
    }
  },

  register: async (email: string, password: string, name: string) => {
    set({ isLoading: true, error: null });
    try {
      const result = await api.register(email, password, name);
      await saveToken(result.token);
      set({ token: result.token, user: result.user, isLoading: false });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Registration failed";
      set({ isLoading: false, error: message });
    }
  },

  logout: async () => {
    await clearToken();
    set({ token: null, user: null, error: null });
  },
}));
