import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";

export default function RootLayout() {
  return (
    <>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: "#0b1120" },
          headerTintColor: "#e2e8f0",
          contentStyle: { backgroundColor: "#0b1120" },
        }}
      />
    </>
  );
}
