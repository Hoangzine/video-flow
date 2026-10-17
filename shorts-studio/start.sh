#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ -x /workspace/.onboarding/video-flow/venv/bin/python ]]; then
  studio_python=/workspace/.onboarding/video-flow/venv/bin/python
elif [[ -x .venv/bin/python ]]; then
  studio_python="$PWD/.venv/bin/python"
else
  echo 'Create .venv and install requirements.txt first.' >&2
  exit 1
fi
if curl --noproxy '*' -fsS http://127.0.0.1:8787/api/health >/dev/null 2>&1; then
  echo 'Studio is already responding on port 8787.'
  exit 0
fi
OMP_NUM_THREADS=2 nohup "$studio_python" -m uvicorn server:app --host 127.0.0.1 --port 8787 >studio.log 2>&1 </dev/null &
echo "$!" >studio.pid
for attempt in {1..60}; do
  if curl --noproxy '*' -fsS http://127.0.0.1:8787/api/health >/dev/null 2>&1; then
    echo 'Studio is ready on port 8787. Use a browser on this machine.'
    exit 0
  fi
  sleep 0.25
done
cat studio.log >&2
exit 1
