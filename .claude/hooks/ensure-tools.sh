#!/usr/bin/env bash
# SessionStart: install the video tools once per machine (fast no-op afterwards).
VT="${VIDEO_TOOLS:-$HOME/video-tools}"
if [ ! -d "$VT/givemotion" ] || [ ! -d "$VT/remotion/node_modules/remotion" ]; then
  bash "$CLAUDE_PROJECT_DIR/setup.sh" >"$HOME/.video-tools-setup.log" 2>&1 || echo "video-agent setup failed; see ~/.video-tools-setup.log"
fi
echo "export VIDEO_TOOLS=$VT PATH=$VT/bin:\$PATH" >> "${CLAUDE_ENV_FILE:-/dev/null}"
