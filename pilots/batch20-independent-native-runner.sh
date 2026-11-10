#!/usr/bin/env bash
# Deterministic first-party test executor. Dispatch from a separate host/CI,
# not a chatbot shell. Runs no model/provider/browser agent.
set -euo pipefail
umask 077

case_id="${1:?expected lacp or voly}"
output_dir="${2:?expected unique absolute output directory}"
if [[ "${output_dir}" != /* ]]; then
  echo "output directory must be absolute" >&2
  exit 2
fi

packet_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "${case_id}" in
  lacp)
    repository="https://github.com/0xNyk/lacp.git"
    source_sha="e31f134b689afd6a71d94b0420682d1f528d6fa1"
    pilot_dir="${packet_root}/lacp-s2"
    expected_fix="17bc0d36273ee6bdc90a5ed8393afc58c9b7deeea8b35da2ccd9d8fb0faee842"
    expected_test="f71e4a766381c8cfedbb2559c644f3e11f6603006559f2ac682d3936130393a3"
    native_test=(bash scripts/ci/test-swarm.sh)
    ;;
  voly)
    repository="https://github.com/voly-codes/voly.git"
    source_sha="38aa1bf7074f7b1e0f79f559dfa3fc97d75a073d"
    pilot_dir="${packet_root}/voly-s2"
    expected_fix="6e83d590b87c2c9b0b5fec72590a0f76cc78876cdde548afd8e8bfd12eb0121c"
    expected_test="eddff42400bc7b5ccd5fe0538bc2273300ddae9483e62bab4fa28fadd82e710a"
    native_test=(python3 -m pytest -q tests/test_cwd_lock.py)
    ;;
  *) echo "unsupported case" >&2; exit 2 ;;
esac

mkdir -p "${output_dir}"
target="${output_dir}/target"
if [[ -e "${target}" ]]; then
  echo "refusing to overwrite an existing target checkout" >&2
  exit 2
fi

actual_fix="$(sha256sum "${pilot_dir}/native-fix.patch" | cut -d' ' -f1)"
actual_test="$(sha256sum "${pilot_dir}/native-regression.patch" | cut -d' ' -f1)"
[[ "${actual_fix}" == "${expected_fix}" && "${actual_test}" == "${expected_test}" ]] || {
  echo "packet hash mismatch" >&2
  exit 2
}

git init --quiet "${target}"
git -C "${target}" remote add origin "${repository}"
git -C "${target}" fetch --quiet --depth 1 origin "${source_sha}"
git -C "${target}" checkout --quiet --detach FETCH_HEAD
actual_source="$(git -C "${target}" rev-parse HEAD)"
[[ "${actual_source}" == "${source_sha}" ]] || { echo "source pin mismatch" >&2; exit 2; }

git -C "${target}" apply --check "${pilot_dir}/native-regression.patch"
git -C "${target}" apply "${pilot_dir}/native-regression.patch"

set +e
(cd "${target}" && "${native_test[@]}") > "${output_dir}/before.log" 2>&1
before_exit=$?
set -e

git -C "${target}" apply --check "${pilot_dir}/native-fix.patch"
git -C "${target}" apply "${pilot_dir}/native-fix.patch"
git -C "${target}" diff --check

set +e
(cd "${target}" && "${native_test[@]}") > "${output_dir}/after.log" 2>&1
after_exit=$?
set -e

{
  echo "case=${case_id}"
  echo "source=${repository}@${source_sha}"
  echo "fix_sha256=${actual_fix}"
  echo "test_sha256=${actual_test}"
  echo "runner_host=$(hostname)"
  echo "runner_user=$(id -un)"
  echo "python=$(python3 --version 2>&1)"
  echo "before_exit=${before_exit}"
  echo "after_exit=${after_exit}"
  echo "before_log=${output_dir}/before.log"
  echo "after_log=${output_dir}/after.log"
  echo "recorded_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${output_dir}/receipt.txt"

cat "${output_dir}/receipt.txt"
if [[ ${before_exit} -eq 0 || ${after_exit} -ne 0 ]]; then
  echo "native RED/GREEN gate not met" >&2
  exit 1
fi
echo "NATIVE_RED_GREEN_PASS case=${case_id}"
