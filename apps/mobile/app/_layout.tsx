import { useEffect } from "react";
import { Stack, useRouter, useSegments } from "expo-router";
import { StatusBar } from "expo-status-bar";
import "../src/i18n";
import { useAuthStore } from "../src/store/authStore";
import { setupNotificationHandler } from "../src/notifications";

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { token, isLoading, hydrate } = useAuthStore();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (isLoading) return;

    const inAuthGroup = segments[0] === "(auth)";
    if (!token && !inAuthGroup) {
      router.replace("/(auth)/login");
    } else if (token && inAuthGroup) {
      router.replace("/(tabs)");
    }
  }, [token, isLoading, segments, router]);

  return <>{children}</>;
}

export default function RootLayout() {
  useEffect(() => {
    setupNotificationHandler();
  }, []);

  return (
    <AuthGuard>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: "#0b1120" },
          headerTintColor: "#e2e8f0",
          contentStyle: { backgroundColor: "#0b1120" },
        }}
      />
    </AuthGuard>
  );
}
