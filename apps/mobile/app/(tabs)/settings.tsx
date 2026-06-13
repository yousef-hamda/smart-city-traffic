import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from "react-native";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../../src/store/authStore";
import { applyRtl } from "../../src/i18n";
import type { SupportedLocale } from "../../src/i18n";

const LANGUAGES: { code: SupportedLocale; label: string }[] = [
  { code: "en", label: "English" },
  { code: "he", label: "עברית" },
  { code: "ar", label: "العربية" },
];

export default function SettingsScreen() {
  const { t, i18n } = useTranslation();
  const { user, logout } = useAuthStore();

  async function handleLanguageChange(lang: SupportedLocale) {
    await i18n.changeLanguage(lang);
    applyRtl(lang);
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>{t("settings.title")}</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t("settings.account")}</Text>
        {user ? (
          <View style={styles.card}>
            <View style={styles.row}>
              <Text style={styles.rowLabel}>{t("settings.email")}</Text>
              <Text style={styles.rowValue}>{user.email}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.rowLabel}>{t("settings.name")}</Text>
              <Text style={styles.rowValue}>{user.name}</Text>
            </View>
          </View>
        ) : (
          <Text style={styles.mutedText}>Not logged in</Text>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t("settings.language")}</Text>
        <View style={styles.langRow}>
          {LANGUAGES.map((lang) => (
            <TouchableOpacity
              key={lang.code}
              style={[styles.langChip, i18n.language === lang.code && styles.langChipActive]}
              onPress={() => void handleLanguageChange(lang.code)}
              testID={`lang-${lang.code}`}
            >
              <Text
                style={[
                  styles.langChipText,
                  i18n.language === lang.code && styles.langChipTextActive,
                ]}
              >
                {lang.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{t("settings.version")}</Text>
        <Text style={styles.mutedText}>0.1.0 (Phase 14)</Text>
      </View>

      <TouchableOpacity
        style={styles.logoutButton}
        onPress={() => void logout()}
        testID="logout-button"
      >
        <Text style={styles.logoutText}>{t("auth.logout")}</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0b1120",
  },
  content: {
    padding: 24,
    gap: 24,
  },
  heading: {
    color: "#e2e8f0",
    fontSize: 24,
    fontWeight: "700",
  },
  section: {
    gap: 10,
  },
  sectionTitle: {
    color: "#94a3b8",
    fontSize: 13,
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: 0.8,
  },
  card: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    gap: 12,
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  rowLabel: {
    color: "#64748b",
    fontSize: 14,
  },
  rowValue: {
    color: "#e2e8f0",
    fontSize: 14,
    fontWeight: "500",
  },
  mutedText: {
    color: "#64748b",
    fontSize: 14,
  },
  langRow: {
    flexDirection: "row",
    gap: 10,
  },
  langChip: {
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: "#1e293b",
  },
  langChipActive: {
    backgroundColor: "#3b82f6",
    borderColor: "#3b82f6",
  },
  langChipText: {
    color: "#94a3b8",
    fontSize: 14,
    fontWeight: "600",
  },
  langChipTextActive: {
    color: "#fff",
  },
  logoutButton: {
    backgroundColor: "#ef4444",
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 8,
  },
  logoutText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
});
