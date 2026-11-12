import { useCurrentFrame } from "remotion";
import type { Line } from "../script";
import { Runs, sliceRuns } from "../text";
import { CAPTION, MARGIN } from "../theme";
import { captionAt } from "../typewriter";
import { Caret, caretOn } from "./Caret";

/** The line under the title. `caret` is false while the specimen row owns the caret. */
export const Caption: React.FC<{ lines: Line[]; accent: string; caret: boolean }> = ({ lines, accent, caret }) => {
  const frame = useCurrentFrame();
  const state = captionAt(lines, frame);
  if (!state) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: MARGIN,
        top: CAPTION.top,
        fontSize: CAPTION.size,
        lineHeight: 1,
        whiteSpace: "pre",
      }}
    >
      <Runs runs={sliceRuns(state.runs, state.chars)} />
      <Caret color={accent} visible={caret && caretOn(frame, state.idleSince)} />
    </div>
  );
};
