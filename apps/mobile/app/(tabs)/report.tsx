import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  Alert,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { useTranslation } from "react-i18next";
import { reportIncident, type IncidentPayload } from "../../src/lib/api";

type IncidentType = "accident" | "pothole" | "blockage";

interface FormState {
  latitude: string;
  longitude: string;
  type: IncidentType | null;
  description: string;
  photoUri: string | null;
}

interface FormErrors {
  location?: string;
  type?: string;
}

export default function ReportScreen() {
  const { t } = useTranslation();
  const [form, setForm] = useState<FormState>({
    latitude: "",
    longitude: "",
    type: null,
    description: "",
    photoUri: null,
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const INCIDENT_TYPES: { value: IncidentType; label: string }[] = [
    { value: "accident", label: t("report.accident") },
    { value: "pothole", label: t("report.pothole") },
    { value: "blockage", label: t("report.blockage") },
  ];

  function validate(): boolean {
    const newErrors: FormErrors = {};
    const lat = parseFloat(form.latitude);
    const lng = parseFloat(form.longitude);
    if (!form.latitude.trim() || !form.longitude.trim() || isNaN(lat) || isNaN(lng)) {
      newErrors.location = t("report.locationRequired");
    }
    if (!form.type) {
      newErrors.type = t("report.typeRequired");
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function pickPhoto() {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 0.7,
      });
      if (!result.canceled && result.assets[0]) {
        setForm((f) => ({ ...f, photoUri: result.assets[0]?.uri ?? null }));
      }
    } catch {
      // Permission denied or not available
    }
  }

  async function handleSubmit() {
    if (!validate()) return;
    if (!form.type) return;

    setIsSubmitting(true);
    try {
      const payload: IncidentPayload = {
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        type: form.type,
        description: form.description || undefined,
        photoUri: form.photoUri || undefined,
      };
      const result = await reportIncident(payload);
      const successMsg = result.status === "queued" ? t("report.queued") : t("report.success");
      Alert.alert(t("common.appName"), successMsg);
      setForm({
        latitude: "",
        longitude: "",
        type: null,
        description: "",
        photoUri: null,
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>{t("report.title")}</Text>

      <Text style={styles.label}>{t("report.locationLabel")}</Text>
      <View style={styles.row}>
        <TextInput
          style={[styles.input, styles.flex1]}
          placeholder="Latitude"
          placeholderTextColor="#64748b"
          keyboardType="numeric"
          value={form.latitude}
          onChangeText={(v) => setForm((f) => ({ ...f, latitude: v }))}
          testID="latitude-input"
        />
        <TextInput
          style={[styles.input, styles.flex1, styles.ml8]}
          placeholder="Longitude"
          placeholderTextColor="#64748b"
          keyboardType="numeric"
          value={form.longitude}
          onChangeText={(v) => setForm((f) => ({ ...f, longitude: v }))}
          testID="longitude-input"
        />
      </View>
      {errors.location ? <Text style={styles.errorText}>{errors.location}</Text> : null}

      <Text style={styles.label}>{t("report.typeLabel")}</Text>
      <View style={styles.typeRow}>
        {INCIDENT_TYPES.map((item) => (
          <TouchableOpacity
            key={item.value}
            style={[styles.typeChip, form.type === item.value && styles.typeChipSelected]}
            onPress={() => setForm((f) => ({ ...f, type: item.value }))}
            testID={`type-${item.value}`}
          >
            <Text
              style={[styles.typeChipText, form.type === item.value && styles.typeChipTextSelected]}
            >
              {item.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      {errors.type ? <Text style={styles.errorText}>{errors.type}</Text> : null}

      <Text style={styles.label}>{t("report.description")}</Text>
      <TextInput
        style={[styles.input, styles.textArea]}
        placeholder={t("report.description")}
        placeholderTextColor="#64748b"
        multiline
        numberOfLines={3}
        value={form.description}
        onChangeText={(v) => setForm((f) => ({ ...f, description: v }))}
        testID="description-input"
      />

      <TouchableOpacity style={styles.photoButton} onPress={() => void pickPhoto()}>
        <Text style={styles.photoButtonText}>
          {form.photoUri ? "Photo selected" : t("report.photo")}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.submitButton, isSubmitting && styles.submitDisabled]}
        onPress={() => void handleSubmit()}
        disabled={isSubmitting}
        testID="submit-button"
      >
        {isSubmitting ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitText}>{t("report.submit")}</Text>
        )}
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
  textArea: {
    minHeight: 80,
    textAlignVertical: "top",
  },
  row: {
    flexDirection: "row",
  },
  flex1: {
    flex: 1,
  },
  ml8: {
    marginLeft: 8,
  },
  typeRow: {
    flexDirection: "row",
    gap: 8,
    flexWrap: "wrap",
  },
  typeChip: {
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: "#1e293b",
  },
  typeChipSelected: {
    backgroundColor: "#3b82f6",
    borderColor: "#3b82f6",
  },
  typeChipText: {
    color: "#94a3b8",
    fontSize: 14,
    fontWeight: "600",
  },
  typeChipTextSelected: {
    color: "#fff",
  },
  photoButton: {
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
    borderStyle: "dashed",
  },
  photoButtonText: {
    color: "#3b82f6",
    fontWeight: "600",
  },
  submitButton: {
    backgroundColor: "#3b82f6",
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 8,
  },
  submitDisabled: {
    opacity: 0.5,
  },
  submitText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  errorText: {
    color: "#ef4444",
    fontSize: 13,
  },
});
