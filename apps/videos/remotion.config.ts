// Applies to `remotion studio` and `remotion render`: https://remotion.dev/docs/config
import { Config } from "@remotion/cli/config";

Config.setRspack(true);
// Lossless frames keep thin weights and colored edges crisp before H.264 encoding.
Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);
