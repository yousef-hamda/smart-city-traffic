import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { Link } from "expo-router";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../src/store/authStore";

export default function LoginScreen() {
  const { t } = useTranslation();
  const { login, isLoading, error } = useAuthStore();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);

  function validate(): boolean {
    if (!email.trim()) {
      setValidationError(t("auth.emailRequired"));
      return false;
    }
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRe.test(email)) {
      setValidationError(t("auth.emailInvalid"));
      return false;
    }
    if (!password) {
      setValidationError(t("auth.passwordRequired"));
      return false;
    }
    if (password.length < 8) {
      setValidationError(t("auth.passwordTooShort"));
      return false;
    }
    setValidationError(null);
    return true;
  }

  async function handleLogin() {
    if (!validate()) return;
    await login(email, password);
  }

  const displayError = validationError ?? error;

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <Text style={styles.title}>{t("auth.loginTitle")}</Text>

      {displayError ? <Text style={styles.errorText}>{displayError}</Text> : null}

      <TextInput
        style={styles.input}
        placeholder={t("auth.email")}
        placeholderTextColor="#64748b"
        autoCapitalize="none"
        keyboardType="email-address"
        value={email}
        onChangeText={setEmail}
        testID="email-input"
      />

      <TextInput
        style={styles.input}
        placeholder={t("auth.password")}
        placeholderTextColor="#64748b"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        testID="password-input"
      />

      <TouchableOpacity
        style={[styles.button, isLoading && styles.buttonDisabled]}
        onPress={() => void handleLogin()}
        disabled={isLoading}
        testID="login-button"
      >
        {isLoading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>{t("auth.login")}</Text>
        )}
      </TouchableOpacity>

      <View style={styles.row}>
        <Text style={styles.mutedText}>{t("auth.noAccount")} </Text>
        <Link href="/(auth)/register">
          <Text style={styles.link}>{t("auth.register")}</Text>
        </Link>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0b1120",
    padding: 24,
    justifyContent: "center",
    gap: 16,
  },
  title: {
    color: "#e2e8f0",
    fontSize: 28,
    fontWeight: "700",
    marginBottom: 8,
  },
  input: {
    backgroundColor: "#1e293b",
    color: "#e2e8f0",
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: "#334155",
  },
  button: {
    backgroundColor: "#3b82f6",
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 4,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  errorText: {
    color: "#ef4444",
    fontSize: 14,
  },
  row: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    marginTop: 4,
  },
  mutedText: {
    color: "#94a3b8",
    fontSize: 14,
  },
  link: {
    color: "#3b82f6",
    fontSize: 14,
    fontWeight: "600",
  },
});
