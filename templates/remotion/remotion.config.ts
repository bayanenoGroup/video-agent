import { Config } from "@remotion/cli/config";
import fs from "node:fs";
// Use the pre-installed Chromium when present (cloud containers), otherwise Remotion downloads its own.
const local = ["/opt/pw-browsers/chromium", process.env.REMOTION_BROWSER].filter(Boolean) as string[];
for (const p of local) if (fs.existsSync(p)) { Config.setBrowserExecutable(p); break; }
Config.setVideoImageFormat("jpeg");
Config.setConcurrency(4);
