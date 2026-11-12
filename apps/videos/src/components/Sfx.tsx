import { Audio } from "@remotion/media";
import type { Sound } from "../sfx";
import { FPS } from "../timeline";

/**
 * Plays `sound` with its anchor on frame `at`. `gain` is in dB. `semitones` repitches by resampling,
 * as a sampler does, so the sound also gets shorter going up.
 */
export const Sfx: React.FC<{ sound: Sound; at: number; gain?: number; semitones?: number }> = ({
  sound,
  at,
  gain = 0,
  semitones = 0,
}) => {
  const rate = 2 ** (semitones / 12);
  return (
    <Audio
      src={sound.src}
      from={at - Math.round((sound.anchor * FPS) / rate)}
      volume={10 ** (gain / 20)}
      playbackRate={rate}
      showInTimeline={false}
    />
  );
};
