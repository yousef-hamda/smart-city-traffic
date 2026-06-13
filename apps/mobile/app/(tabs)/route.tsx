import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import { useTranslation } from "react-i18next";
import { recommendRoute, type RouteResult } from "../../src/lib/api";

interface FormErrors {
  origin?: string;
  destination?: string;
}

export default function RouteScreen() {
  const { t } = useTranslation();
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<RouteResult | null>(null);

  function validate(): boolean {
    const newErrors: FormErrors = {};
    if (!origin.trim()) newErrors.origin = t("route.originRequired");
    if (!destination.trim()) newErrors.destination = t("route.destinationRequired");
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleFindRoute() {
    if (!validate()) return;
    setIsLoading(true);
    setResult(null);
    try {
      const routeResult = await recommendRoute(origin.trim(), destination.trim());
      setResult(routeResult);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>{t("route.title")}</Text>

      <Text style={styles.label}>{t("route.origin")}</Text>
      <TextInput
        style={styles.input}
        placeholder={t("route.origin")}
        placeholderTextColor="#64748b"
        value={origin}
        onChangeText={setOrigin}
        testID="origin-input"
      />
      {errors.origin ? <Text style={styles.errorText}>{errors.origin}</Text> : null}

      <Text style={styles.label}>{t("route.destination")}</Text>
      <TextInput
        style={styles.input}
        placeholder={t("route.destination")}
        placeholderTextColor="#64748b"
        value={destination}
        onChangeText={setDestination}
        testID="destination-input"
      />
      {errors.destination ? <Text style={styles.errorText}>{errors.destination}</Text> : null}

      <TouchableOpacity
        style={[styles.button, isLoading && styles.buttonDisabled]}
        onPress={() => void handleFindRoute()}
        disabled={isLoading}
        testID="find-route-button"
      >
        {isLoading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.buttonText}>{t("route.find")}</Text>
        )}
      </TouchableOpacity>

      {result ? (
        <View style={styles.resultCard} testID="route-result">
          <Text style={styles.resultTitle}>
            {result.origin} → {result.destination}
          </Text>

          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{result.distanceKm}</Text>
              <Text style={styles.statLabel}>{t("route.km")}</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{result.durationMin}</Text>
              <Text style={styles.statLabel}>{t("route.min")}</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{result.segments.length}</Text>
              <Text style={styles.statLabel}>segments</Text>
            </View>
          </View>

          {result.segments.map((seg) => (
            <View key={seg.id} style={styles.segmentRow}>
              <View
                style={[
                  styles.statusDot,
                  {
                    backgroundColor:
                      seg.status === "free"
                        ? "#22c55e"
                        : seg.status === "moderate"
                          ? "#f59e0b"
                          : "#ef4444",
                  },
                ]}
              />
              <Text style={styles.segmentName}>{seg.name}</Text>
              <Text style={styles.segmentSpeed}>{seg.currentSpeed} km/h</Text>
            </View>
          ))}
        </View>
      ) : null}
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
    gap: 12,
  },
  heading: {
    color: "#e2e8f0",
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 8,
  },
  label: {
    color: "#94a3b8",
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 4,
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
    fontSize: 13,
  },
  resultCard: {
    backgroundColor: "#1e293b",
    borderRadius: 12,
    padding: 16,
    marginTop: 8,
    gap: 12,
  },
  resultTitle: {
    color: "#e2e8f0",
    fontSize: 16,
    fontWeight: "700",
  },
  statsRow: {
    flexDirection: "row",
    justifyContent: "space-around",
  },
  stat: {
    alignItems: "center",
  },
  statValue: {
    color: "#3b82f6",
    fontSize: 22,
    fontWeight: "700",
  },
  statLabel: {
    color: "#64748b",
    fontSize: 12,
  },
  segmentRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 6,
    borderTopWidth: 1,
    borderTopColor: "#334155",
    gap: 10,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  segmentName: {
    flex: 1,
    color: "#e2e8f0",
    fontSize: 14,
  },
  segmentSpeed: {
    color: "#94a3b8",
    fontSize: 13,
  },
});
