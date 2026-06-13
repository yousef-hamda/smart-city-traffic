"use client";

// Socket.io client — gracefully handles missing backend by emitting nothing.

import type { SegmentUpdate, Alert, GlobalStats } from "./types";

interface EventMap {
  "segment:update": SegmentUpdate;
  "segment:alert": Alert;
  alert: Alert;
  "global-stats": GlobalStats;
  connect: undefined;
  disconnect: undefined;
  connect_error: Error;
}

type Listener<T> = (data: T) => void;
type AnyListener = (data: unknown) => void;

function createSocketClient() {
  const listeners = new Map<string, Set<AnyListener>>();
  let connected = false;
  let socket: { disconnect: () => void } | null = null;

  function on<K extends keyof EventMap>(event: K, fn: Listener<EventMap[K]>): void {
    if (!listeners.has(event)) listeners.set(event, new Set());
    listeners.get(event)!.add(fn as AnyListener);
  }

  function off<K extends keyof EventMap>(event: K, fn: Listener<EventMap[K]>): void {
    listeners.get(event)?.delete(fn as AnyListener);
  }

  function emit<K extends keyof EventMap>(event: K, data?: EventMap[K]): void {
    listeners.get(event)?.forEach((fn) => fn(data));
  }

  function subscribe(segmentIds: string[]): void {
    if (!connected) return;
    void segmentIds;
  }

  async function connect(): Promise<void> {
    if (typeof window === "undefined") return;
    const REALTIME_URL = process.env.NEXT_PUBLIC_REALTIME_URL ?? "http://localhost:8088";
    try {
      const { io } = await import("socket.io-client");
      const s = io(REALTIME_URL, {
        timeout: 3000,
        reconnectionAttempts: 2,
        autoConnect: true,
      });
      socket = s;

      s.on("connect", () => {
        connected = true;
        emit("connect");
      });
      s.on("disconnect", () => {
        connected = false;
        emit("disconnect");
      });
      s.on("connect_error", (err: Error) => {
        emit("connect_error", err);
      });
      s.on("segment:update", (data: SegmentUpdate) => emit("segment:update", data));
      s.on("segment:alert", (data: Alert) => emit("segment:alert", data));
      s.on("alert", (data: Alert) => emit("alert", data));
      s.on("global-stats", (data: GlobalStats) => emit("global-stats", data));
    } catch {
      // Socket.io unavailable — UI falls back to mock/polling data
    }
  }

  function disconnect(): void {
    socket?.disconnect();
    connected = false;
  }

  function isConnected(): boolean {
    return connected;
  }

  return { on, off, subscribe, connect, disconnect, isConnected };
}

type SocketClient = ReturnType<typeof createSocketClient>;
let socketInstance: SocketClient | null = null;

export function getSocketClient(): SocketClient | null {
  if (typeof window === "undefined") return null;
  if (!socketInstance) {
    socketInstance = createSocketClient();
    void socketInstance.connect();
  }
  return socketInstance;
}
