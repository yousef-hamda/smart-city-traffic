/**
 * Cache layer:
 * - Segments stored in AsyncStorage (plain JSON, non-sensitive)
 * - Auth token stored in expo-secure-store (encrypted, sensitive)
 */

import AsyncStorage from "@react-native-async-storage/async-storage";
import * as SecureStore from "expo-secure-store";
import type { MobileSegment } from "./mock";

const SEGMENTS_KEY = "@smart-city/segments";
const TOKEN_KEY = "smart-city-auth-token";

export async function saveSegments(segments: MobileSegment[]): Promise<void> {
  await AsyncStorage.setItem(SEGMENTS_KEY, JSON.stringify(segments));
}

export async function loadSegments(): Promise<MobileSegment[] | null> {
  const raw = await AsyncStorage.getItem(SEGMENTS_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as MobileSegment[];
  } catch {
    return null;
  }
}

export async function clearCache(): Promise<void> {
  await AsyncStorage.removeItem(SEGMENTS_KEY);
}

export async function saveToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function loadToken(): Promise<string | null> {
  try {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch {
    return null;
  }
}

export async function clearToken(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  } catch {
    // Silently ignore if already gone
  }
}
