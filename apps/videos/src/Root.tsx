import { type CalculateMetadataFunction, Composition } from "remotion";
import { SANS_URL, countGlyphs } from "./fonts";
import { Launch, type LaunchProps } from "./Launch";
import { HEIGHT, WIDTH } from "./theme";
import { CUE, FPS } from "./timeline";

// The glyph count caption is read from the staged font, so it follows every release.
const calculateMetadata: CalculateMetadataFunction<LaunchProps> = async ({ props, abortSignal }) => {
  const response = await fetch(SANS_URL, { signal: abortSignal });
  if (!response.ok) throw new Error(`Could not load ${SANS_URL}. Run \`pnpm fonts\` first.`);
  return { props: { ...props, glyphCount: countGlyphs(await response.arrayBuffer()) } };
};

export const Root: React.FC = () => (
  <Composition
    id="GoeistLaunch"
    component={Launch}
    durationInFrames={CUE.end}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
    defaultProps={{ glyphCount: 0 }}
    calculateMetadata={calculateMetadata}
  />
);
