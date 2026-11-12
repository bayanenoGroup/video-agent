import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
export const Hello: React.FC = () => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f, fps, config: { damping: 14 } });
  return (
    <AbsoluteFill style={{ background: "#3D40FE", justifyContent: "center", alignItems: "center" }}>
      <div style={{ color: "white", fontSize: 160, fontWeight: 900, transform: `scale(${s})`, opacity: interpolate(f, [0, 10], [0, 1]) }}>Remotion OK</div>
    </AbsoluteFill>
  );
};
