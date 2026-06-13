import { Stack } from "expo-router";

export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: "#0b1120" },
        headerTintColor: "#e2e8f0",
        contentStyle: { backgroundColor: "#0b1120" },
      }}
    />
  );
}
