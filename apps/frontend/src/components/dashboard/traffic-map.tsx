"use client";

import * as React from "react";
import type { SegmentState } from "@/lib/types";
import { getStatusColor } from "@/lib/utils";

interface TrafficMapProps {
  segments: SegmentState[];
  selectedSegmentId?: string;
  onSegmentSelect?: (id: string) => void;
}

export function TrafficMap({ segments, selectedSegmentId, onSegmentSelect }: TrafficMapProps) {
  const mapRef = React.useRef<HTMLDivElement>(null);
  const initializedRef = React.useRef(false);

  React.useEffect(() => {
    if (!mapRef.current || initializedRef.current) return;
    initializedRef.current = true;

    const container = mapRef.current;
    let cancelled = false;
    // Keep polyline callbacks stable with a closure over current segments
    const polylineMap = new Map<string, { setStyle: (s: { color: string }) => void }>();

    async function initMap() {
      const L = await import("leaflet");

      if (cancelled || !container) return;

      // Inject Leaflet CSS once
      if (!document.getElementById("leaflet-css")) {
        const link = document.createElement("link");
        link.id = "leaflet-css";
        link.rel = "stylesheet";
        link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
        document.head.appendChild(link);
      }

      const map = L.map(container, {
        center: [31.78, 35.21],
        zoom: 13,
        preferCanvas: true,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(map);

      segments.forEach((seg) => {
        if (seg.geometry.length < 2) return;
        const color = getStatusColor(seg.status);
        const polyline = L.polyline(seg.geometry, {
          color,
          weight: selectedSegmentId === seg.id ? 6 : 4,
          opacity: 0.85,
        });
        polyline.bindTooltip(seg.name_en);
        polyline.on("click", () => {
          onSegmentSelect?.(seg.id);
        });
        polyline.addTo(map);
        polylineMap.set(seg.id, {
          setStyle: (style: { color: string }) => polyline.setStyle(style),
        });
      });

      // Store cleanup on container element via data attribute approach
      container.dataset.mapReady = "true";

      // Return cleanup fn
      return () => {
        map.remove();
        polylineMap.clear();
      };
    }

    let cleanup: (() => void) | undefined;

    void initMap().then((fn) => {
      if (!cancelled) cleanup = fn;
    });

    return () => {
      cancelled = true;
      cleanup?.();
      initializedRef.current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div
      ref={mapRef}
      className="w-full h-full rounded-lg overflow-hidden"
      style={{ minHeight: "400px" }}
    />
  );
}
