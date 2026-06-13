import React, { useEffect } from "react";
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator } from "react-native";
import MapView, { Polyline } from "react-native-maps";
import { useTranslation } from "react-i18next";
import { useSegmentStore } from "../../src/store/segmentStore";
import { getSegmentColor } from "../../src/utils/segmentColor";

const JERUSALEM_REGION = {
  latitude: 31.7683,
  longitude: 35.2137,
  latitudeDelta: 0.12,
  longitudeDelta: 0.12,
};

export default function LiveMapScreen() {
  const { t } = useTranslation();
  const { segments, isOffline, isLoading, fetchSegments, refreshSegments } = useSegmentStore();

  useEffect(() => {
    void fetchSegments();
  }, [fetchSegments]);

  return (
    <View style={styles.container}>
      {isOffline ? (
        <View style={styles.offlineBanner}>
          <Text style={styles.offlineText}>{t("map.offline")}</Text>
        </View>
      ) : null}

      {isLoading && segments.length === 0 ? (
        <View style={styles.loader}>
          <ActivityIndicator size="large" color="#3b82f6" />
          <Text style={styles.loadingText}>{t("common.loading")}</Text>
        </View>
      ) : (
        <MapView style={styles.map} initialRegion={JERUSALEM_REGION} testID="map-view">
          {segments.map((segment) => (
            <Polyline
              key={segment.id}
              coordinates={segment.coordinates}
              strokeColor={getSegmentColor(segment.currentSpeed, segment.speedLimit)}
              strokeWidth={4}
            />
          ))}
        </MapView>
      )}

      <TouchableOpacity
        style={styles.refreshButton}
        onPress={() => void refreshSegments()}
        testID="refresh-button"
      >
        <Text style={styles.refreshText}>{t("map.refresh")}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0b1120",
  },
  map: {
    flex: 1,
  },
  offlineBanner: {
    backgroundColor: "#f59e0b",
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: "center",
  },
  offlineText: {
    color: "#0b1120",
    fontWeight: "600",
    fontSize: 13,
  },
  loader: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
  },
  loadingText: {
    color: "#94a3b8",
    fontSize: 16,
  },
  refreshButton: {
    position: "absolute",
    bottom: 24,
    right: 16,
    backgroundColor: "#3b82f6",
    borderRadius: 24,
    paddingVertical: 10,
    paddingHorizontal: 20,
    elevation: 4,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  refreshText: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 15,
  },
});
