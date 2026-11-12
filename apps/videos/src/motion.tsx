import type { CSSProperties, ReactNode } from "react";
import { Easing, interpolate } from "remotion";

export const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1);

/** 0 → 1 over `duration` frames starting at frame 0, decelerating. */
export const reveal = (frame: number, duration: number) =>
  interpolate(frame, [0, duration], [0, 1], { easing: EASE_OUT, ...CLAMP });

/** Rises out of a blur as `progress` goes 0 → 1; offsets scale with the font `size`. */
export const blurIn = (progress: number, size: number): CSSProperties => ({
  opacity: progress,
  transform: `translateY(${(1 - progress) * size * 0.16}px)`,
  filter: progress < 1 ? `blur(${(1 - progress) * size * 0.08}px)` : undefined,
});

/** The first frame from 0 at which `reached` holds: turns an animation curve into a sound cue. */
export const firstFrame = (reached: (frame: number) => boolean) => {
  let frame = 0;
  while (!reached(frame)) frame++;
  return frame;
};

/** One character that accepts transforms, which inline elements ignore. */
export const Glyph: React.FC<{ children: ReactNode; style?: CSSProperties }> = ({ children, style }) => (
  <span style={{ display: "inline-block", ...style }}>{children}</span>
);
