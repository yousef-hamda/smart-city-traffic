import { Redirect } from "expo-router";
import { useAuthStore } from "../src/store/authStore";

export default function IndexRedirect() {
  const { token } = useAuthStore();
  return token ? <Redirect href="/(tabs)" /> : <Redirect href="/(auth)/login" />;
}
