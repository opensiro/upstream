#!/usr/bin/env bash
# Archive-only recipe: invoke as a distinct, audited host/CI job, not a chatbot validation command.
set -euo pipefail

PIN='83a0d25aa59ef1bc8e295ec45104a9c7f0819c83'
PACKET_REV="${1:?Pass exact internal packet commit SHA}"
SOURCE_REPO="${2:?Pass checked source Git checkout}"
PACKET_REPO="${3:?Pass checked Upstream Git checkout}"
RUN_DIR="$(mktemp -d /tmp/opensiro-clouds-native.XXXXXXXX)"
mkdir -p "${RUN_DIR}/source"

test "$(git -C "${SOURCE_REPO}" cat-file -t "${PIN}")" = commit
test "$(git -C "${PACKET_REPO}" cat-file -t "${PACKET_REV}")" = commit
git -C "${SOURCE_REPO}" archive "${PIN}" | tar -x -C "${RUN_DIR}/source"
git -C "${PACKET_REPO}" show "${PACKET_REV}:pilots/clouds-coder-s2/frozen-process-regression-tests.patch" | git -C "${RUN_DIR}/source" apply --check -
git -C "${PACKET_REPO}" show "${PACKET_REV}:pilots/clouds-coder-s2/frozen-process-regression-tests.patch" | git -C "${RUN_DIR}/source" apply -

export PYTHONDONTWRITEBYTECODE=1
cd "${RUN_DIR}/source"
set +e
python3 -m unittest discover -s tests -p test_collaboration.py -k test_frozen_document_rejects_process > "${RUN_DIR}/before.log" 2>&1
BEFORE_STATUS=$?
set -e
grep -q 'Ran 2 tests' "${RUN_DIR}/before.log"
grep -q 'FAILED (failures=2)' "${RUN_DIR}/before.log"
test "${BEFORE_STATUS}" -ne 0

git -C "${PACKET_REPO}" show "${PACKET_REV}:pilots/clouds-coder-s2/frozen-process-fix.patch" | git apply --check -
git -C "${PACKET_REPO}" show "${PACKET_REV}:pilots/clouds-coder-s2/frozen-process-fix.patch" | git apply -
python3 -m unittest discover -s tests -p test_collaboration.py -k test_frozen_document_rejects_process > "${RUN_DIR}/after.log" 2>&1
python3 -m unittest discover -s tests -p test_collaboration.py -k test_process_delete_is_committed_without_empty_conflict_branch > "${RUN_DIR}/control_delete.log" 2>&1
python3 -m unittest discover -s tests -p test_collaboration.py -k test_process_same_content_retry_is_idempotent_not_conflict > "${RUN_DIR}/control_idempotent.log" 2>&1
grep -q 'Ran 2 tests' "${RUN_DIR}/after.log"
grep -q '^OK$' "${RUN_DIR}/after.log"
grep -q '^OK$' "${RUN_DIR}/control_delete.log"
grep -q '^OK$' "${RUN_DIR}/control_idempotent.log"
python3 -m compileall -q Code_Structure/collaboration/core.py tests/test_collaboration.py

echo "SOURCE_PIN=${PIN}"
echo "PACKET_PIN=${PACKET_REV}"
echo "RUN_DIR=${RUN_DIR}"
echo "BEFORE_STATUS=${BEFORE_STATUS} (two expected native failures)"
echo 'AFTER_STATUS=PASS (two regression cases, two original controls)'
sha256sum "${RUN_DIR}/before.log" "${RUN_DIR}/after.log" "${RUN_DIR}/control_delete.log" "${RUN_DIR}/control_idempotent.log"
