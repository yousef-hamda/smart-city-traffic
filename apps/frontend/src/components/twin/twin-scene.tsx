"use client";

import * as React from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text, Environment } from "@react-three/drei";
import type { SegmentState } from "@/lib/types";
import { getStatusColor } from "@/lib/utils";

interface RoadSegmentMeshProps {
  segment: SegmentState;
  index: number;
  onSelect: (id: string) => void;
  isSelected: boolean;
}

function RoadSegmentMesh({ segment, index, onSelect, isSelected }: RoadSegmentMeshProps) {
  const color = getStatusColor(segment.status);
  const x = (segment.lng - 35.21) * 200;
  const z = (segment.lat - 31.78) * 200;
  const len = 2;

  return (
    <group position={[x, 0, z]}>
      <mesh
        onClick={(e) => {
          e.stopPropagation();
          onSelect(segment.id);
        }}
        castShadow
      >
        <boxGeometry args={[0.3, 0.05, len]} />
        <meshStandardMaterial
          color={color}
          emissive={isSelected ? color : "#000000"}
          emissiveIntensity={isSelected ? 0.5 : 0}
          roughness={0.4}
          metalness={0.1}
        />
      </mesh>
      {isSelected && (
        <Text
          position={[0, 0.5, 0]}
          fontSize={0.2}
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
        >
          {segment.live_speed} km/h
        </Text>
      )}
      {/* Speed pillar indicating congestion level */}
      <mesh position={[0.3, (segment.live_speed / segment.speed_limit) * 0.5, 0]}>
        <cylinderGeometry args={[0.05, 0.05, (segment.live_speed / segment.speed_limit) * 1, 8]} />
        <meshStandardMaterial color={color} opacity={0.7} transparent />
      </mesh>
    </group>
  );
}

interface TwinSceneProps {
  segments: SegmentState[];
  selectedId?: string;
  onSelectSegment?: (id: string) => void;
}

export function TwinScene({ segments, selectedId, onSelectSegment }: TwinSceneProps) {
  return (
    <Canvas
      shadows
      camera={{ position: [0, 8, 12], fov: 55 }}
      style={{ width: "100%", height: "100%" }}
    >
      <color attach="background" args={["#020617"]} />
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 20, 10]} intensity={1.2} castShadow />
      <pointLight position={[0, 10, 0]} intensity={0.5} color="#6366f1" />
      <Environment preset="city" />

      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        minDistance={3}
        maxDistance={40}
        maxPolarAngle={Math.PI / 2.2}
      />

      {/* Ground plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.03, 0]} receiveShadow>
        <planeGeometry args={[50, 50]} />
        <meshStandardMaterial color="#0f172a" roughness={0.9} />
      </mesh>

      {/* Grid lines */}
      <gridHelper args={[50, 50, "#1e293b", "#1e293b"]} position={[0, 0, 0]} />

      {/* Road segments */}
      {segments.map((seg, i) => (
        <RoadSegmentMesh
          key={seg.id}
          segment={seg}
          index={i}
          isSelected={seg.id === selectedId}
          onSelect={(id) => onSelectSegment?.(id)}
        />
      ))}
    </Canvas>
  );
}
