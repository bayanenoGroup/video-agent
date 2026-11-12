#!/usr/bin/env bash
# Video Producer agent — installs every tool the agent uses into $VIDEO_TOOLS (default ~/video-tools).
# Idempotent: safe to run again; it only fetches what is missing.
set -euo pipefail
VT="${VIDEO_TOOLS:-$HOME/video-tools}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$VT"
log(){ printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }

clone(){ # repo dir
  if [ -d "$VT/$2/.git" ]; then log "$2: already present"; else
    log "clone $1"; GIT_LFS_SKIP_SMUDGE=1 git clone -q --depth 1 "https://github.com/$1" "$VT/$2"; fi
}

# 1. Repositories
clone givemotion/givemotion        givemotion      # HTML -> video engine (main renderer)
clone lemomo-ai/Lemo-Opuscar       Lemo-Opuscar    # director guide, procedural SFX/music, TTS check
clone mexicat/pdoom-video          pdoom-video     # word alignment, beat analysis, three.js renderer
clone JohnHeibel/PDoomVideo        PDoomVideo-JH   # p5.js brush animation base + parallel subagent guide
clone yihui-dev/awesome-opus5-5-videos awesome-opus5-5-videos  # 703 code-video prompts: style references when the user sends none

# 2. Node: givemotion (no deps), Remotion workspace, bun (for pdoom-video app)
log "givemotion skill pack"
( cd "$VT/givemotion" && node src/cli.js --help >/dev/null )
if ! command -v bun >/dev/null 2>&1; then log "install bun"; npm i -g bun@1.2.23 >/dev/null 2>&1 || echo "bun install failed (only needed for pdoom-video/app)"; fi

log "Remotion workspace"
mkdir -p "$VT/remotion"
if [ ! -d "$VT/remotion/node_modules/remotion" ]; then
  cp -r --update=none "$HERE/templates/remotion/." "$VT/remotion/"
  ( cd "$VT/remotion" && npm install --silent --no-fund --no-audit )
fi

log "JS deps for PDoomVideo-JH"
[ -d "$VT/PDoomVideo-JH/node_modules" ] || ( cd "$VT/PDoomVideo-JH" && npm install --silent --no-fund --no-audit || true )

# 3. Python audio/analysis libs (Lemo-Opuscar sfx.py needs scipy; soundfile for wav io)
log "python libs"
python3 -m pip install -q --disable-pip-version-check -r "$VT/Lemo-Opuscar/requirements.txt" -r "$VT/Lemo-Opuscar/requirements-music.txt" 2>&1 | grep -v WARNING || true

# 4. Fonts (Persian + Latin) shared by every project
log "fonts"
mkdir -p "$VT/fonts"
if [ ! -f "$VT/fonts/vazirmatn-arabic-900-normal.woff2" ]; then
  tmp="$(mktemp -d)"; ( cd "$tmp" && npm pack -s @fontsource/vazirmatn@5.0.20 >/dev/null && tar xzf ./*.tgz )
  cp "$tmp"/package/files/vazirmatn-{arabic,latin}-{400,700,900}-normal.woff2 "$VT/fonts/"; rm -rf "$tmp"
fi

# 4b. Real-instrument sample libraries (optional, large). Default: fetched on demand by the agent.
#     Preinstall:  WITH_INSTRUMENTS="karoryfer vcsl" bash setup.sh   (or WITH_INSTRUMENTS=all, ~1.4 GB)
if [ -n "${WITH_INSTRUMENTS:-}" ]; then
  for lib in $WITH_INSTRUMENTS; do log "instruments: $lib"; ( cd "$VT/Lemo-Opuscar" && sh tools/fetch.sh instruments "$lib" ); done
fi

# 5. Helper scripts available on PATH
mkdir -p "$VT/bin"; cp "$HERE"/scripts/* "$VT/bin/"; chmod +x "$VT/bin/"*
log "doctor"
( cd "$VT/givemotion" && node src/cli.js doctor | head -6 ) || true
ffmpeg -version | head -1
echo
echo "Installed in $VT. Add to PATH:  export PATH=\"$VT/bin:\$PATH\"  VIDEO_TOOLS=$VT"
