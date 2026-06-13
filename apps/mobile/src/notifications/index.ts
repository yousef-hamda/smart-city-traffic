/**
 * Push notification helpers.
 * All functions are guarded for web/non-device environments.
 */

import { Platform } from "react-native";
import * as Notifications from "expo-notifications";
import Constants from "expo-constants";

function isPhysicalDevice(): boolean {
  // Constants.appOwnership is "expo" in Expo Go, undefined in bare workflow
  // isDevice is available in expo-device but we use Constants here
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const appOwnership = (Constants as Record<string, unknown>)["appOwnership"];
  // On a real device in Expo Go, appOwnership === 'expo'; in bare, undefined.
  // For emulators / simulators, we rely on Platform checks.
  // We block web always.
  if (Platform.OS === "web") return false;
  // For headless tests and simulators, expo constants won't have this
  if (typeof appOwnership === "string" && appOwnership === "storeClient") return false;
  return true;
}

export async function registerForPushNotifications(): Promise<string | null> {
  if (!isPhysicalDevice()) return null;

  try {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== "granted") {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== "granted") {
      return null;
    }

    const tokenData = await Notifications.getExpoPushTokenAsync();
    return tokenData.data;
  } catch {
    return null;
  }
}

export function setupNotificationHandler(): void {
  if (Platform.OS === "web") return;

  try {
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: false,
      }),
    });
  } catch {
    // Ignore in environments without native notification support
  }
}
