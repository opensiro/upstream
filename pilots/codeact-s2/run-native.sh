#!/usr/bin/env bash
# Deterministic, separately dispatched native CodeAct concurrency replay.
# No LLM, Docker container or provider is started by the regression fixture.
set -euo pipefail

SOURCE_SHA=d607f56c9cfe9e8632ebaf65dcaf2b4b7fe1c6f8
UPSTREAM_PACKET_COMMIT=ac1bb2345d5be31be3570ffc9635e9e01b6f3c20
PACKET_BASE="https://raw.githubusercontent.com/opensiro/upstream/${UPSTREAM_PACKET_COMMIT}/pilots/codeact-s2"
RUN_ROOT="$(mktemp -d -p /tmp opensiro-b22-codeact-XXXXXXXX)"
printf 'RUN_ROOT=%s\nSOURCE_SHA=%s\nPACKET_COMMIT=%s\n' "$RUN_ROOT" "$SOURCE_SHA" "$UPSTREAM_PACKET_COMMIT"

git clone --quiet --depth 1 --no-recurse-submodules https://github.com/xingyaoww/code-act.git "$RUN_ROOT/code-act"
cd "$RUN_ROOT/code-act"
test "$(git rev-parse HEAD)" = "$SOURCE_SHA"

curl --fail --silent --show-error --location "$PACKET_BASE/native-regression.patch" --output "$RUN_ROOT/native-regression.patch"
curl --fail --silent --show-error --location "$PACKET_BASE/native-fix.patch" --output "$RUN_ROOT/native-fix.patch"
sha256sum "$RUN_ROOT/native-regression.patch" "$RUN_ROOT/native-fix.patch"

python3 -m venv "$RUN_ROOT/venv"
"$RUN_ROOT/venv/bin/python" -m pip install --disable-pip-version-check --quiet 'tornado==6.5.2'
"$RUN_ROOT/venv/bin/python" --version

git apply --check "$RUN_ROOT/native-regression.patch"
git apply "$RUN_ROOT/native-regression.patch"

set +e
"$RUN_ROOT/venv/bin/python" -m unittest discover -s scripts/chat/code_execution -p test_api_concurrency.py -v >"$RUN_ROOT/baseline.log" 2>&1
BASELINE_EXIT=$?
set -e
printf 'BASELINE_EXIT=%d\n' "$BASELINE_EXIT"
sed -n '1,130p' "$RUN_ROOT/baseline.log"
if [ "$BASELINE_EXIT" -eq 0 ]; then
  printf 'ERROR: baseline unexpectedly passed; no RED evidence\n' >&2
  exit 7
fi

git apply --check "$RUN_ROOT/native-fix.patch"
git apply "$RUN_ROOT/native-fix.patch"

set +e
"$RUN_ROOT/venv/bin/python" -m unittest discover -s scripts/chat/code_execution -p test_api_concurrency.py -v >"$RUN_ROOT/after.log" 2>&1
AFTER_EXIT=$?
set -e
printf 'AFTER_EXIT=%d\n' "$AFTER_EXIT"
sed -n '1,130p' "$RUN_ROOT/after.log"
if [ "$AFTER_EXIT" -ne 0 ]; then
  printf 'ERROR: patched regression failed\n' >&2
  exit 8
fi

"$RUN_ROOT/venv/bin/python" -m compileall -q scripts/chat/code_execution/api.py scripts/chat/code_execution/test_api_concurrency.py
git diff --check
git status --short
printf 'RUNNER_PASS: native regression RED to GREEN; logs retained under %s\n' "$RUN_ROOT"
