#!/usr/bin/env bash
set -uo pipefail

usage() {
  cat <<'EOF'
Usage:
  find-polluter.sh [options] -- <target command>

Runs a target command repeatedly, then optionally runs candidate commands before
the target to expose order-dependent or polluter failures.

Options:
  --runs N              Number of target runs per scenario. Default: 20.
  --candidates FILE    File with one candidate command per line.
                       Blank lines and lines starting with # are ignored.
  --before COMMAND     Command to run before every target invocation.
  --shell SHELL        Shell used with -lc. Default: bash.
  --stop-on-fail       Stop a scenario at the first target failure.
  --log-dir DIR        Directory for per-run logs. Default: temporary directory.
  -h, --help           Show this help.

Examples:
  find-polluter.sh --runs 25 -- "npm test -- flaky.spec.ts"
  find-polluter.sh --runs 10 --candidates suspects.txt -- "pytest tests/test_target.py"
EOF
}

runs=20
candidates_file=""
before_cmd=""
runner_shell="${SHELL:-bash}"
stop_on_fail=0
log_dir=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --runs)
      [[ $# -ge 2 ]] || { echo "error: --runs needs a value" >&2; exit 2; }
      runs="$2"
      shift 2
      ;;
    --candidates)
      [[ $# -ge 2 ]] || { echo "error: --candidates needs a file" >&2; exit 2; }
      candidates_file="$2"
      shift 2
      ;;
    --before)
      [[ $# -ge 2 ]] || { echo "error: --before needs a command" >&2; exit 2; }
      before_cmd="$2"
      shift 2
      ;;
    --shell)
      [[ $# -ge 2 ]] || { echo "error: --shell needs a shell path/name" >&2; exit 2; }
      runner_shell="$2"
      shift 2
      ;;
    --stop-on-fail)
      stop_on_fail=1
      shift
      ;;
    --log-dir)
      [[ $# -ge 2 ]] || { echo "error: --log-dir needs a directory" >&2; exit 2; }
      log_dir="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ $# -eq 0 ]]; then
  echo "error: target command is required after --" >&2
  usage >&2
  exit 2
fi

if [[ ! "$runs" =~ ^[0-9]+$ ]] || [[ "$runs" -lt 1 ]]; then
  echo "error: --runs must be a positive integer" >&2
  exit 2
fi

if [[ -n "$candidates_file" && ! -f "$candidates_file" ]]; then
  echo "error: candidates file not found: $candidates_file" >&2
  exit 2
fi

if ! command -v "$runner_shell" >/dev/null 2>&1; then
  echo "error: shell not found: $runner_shell" >&2
  exit 2
fi

target_cmd="$*"

if [[ -z "$log_dir" ]]; then
  log_dir="$(mktemp -d "${TMPDIR:-/tmp}/find-polluter.XXXXXX")"
else
  mkdir -p "$log_dir"
fi

scenario_count=0
overall_failures=0
declare -a summary_labels=()
declare -a summary_failures=()

run_command() {
  local label="$1"
  local command="$2"
  local output_file="$3"

  printf -- '---- %s ----\n' "$label" >>"$output_file"
  printf '$ %s\n' "$command" >>"$output_file"
  "$runner_shell" -lc "$command" >>"$output_file" 2>&1
}

run_scenario() {
  local label="$1"
  local candidate_cmd="$2"
  local failures=0
  local run_no output_file

  scenario_count=$((scenario_count + 1))
  printf '\n== Scenario %d: %s ==\n' "$scenario_count" "$label"

  for ((run_no = 1; run_no <= runs; run_no++)); do
    output_file="$log_dir/scenario-${scenario_count}-run-${run_no}.log"
    : >"$output_file"

    if [[ -n "$before_cmd" ]]; then
      if ! run_command "before" "$before_cmd" "$output_file"; then
        printf 'run %d/%d: before command failed\n' "$run_no" "$runs"
        failures=$((failures + 1))
        [[ "$stop_on_fail" -eq 1 ]] && break
        continue
      fi
    fi

    if [[ -n "$candidate_cmd" ]]; then
      if ! run_command "candidate" "$candidate_cmd" "$output_file"; then
        printf 'run %d/%d: candidate failed\n' "$run_no" "$runs"
        failures=$((failures + 1))
        [[ "$stop_on_fail" -eq 1 ]] && break
        continue
      fi
    fi

    if run_command "target" "$target_cmd" "$output_file"; then
      printf 'run %d/%d: pass\n' "$run_no" "$runs"
    else
      printf 'run %d/%d: target failed (log: %s)\n' "$run_no" "$runs" "$output_file"
      failures=$((failures + 1))
      [[ "$stop_on_fail" -eq 1 ]] && break
    fi
  done

  summary_labels+=("$label")
  summary_failures+=("$failures")
  overall_failures=$((overall_failures + failures))
}

printf 'target: %s\n' "$target_cmd"
printf 'runs per scenario: %s\n' "$runs"
printf 'log dir: %s\n' "$log_dir"

run_scenario "baseline target only" ""

if [[ -n "$candidates_file" ]]; then
  while IFS= read -r candidate || [[ -n "$candidate" ]]; do
    [[ -z "$candidate" ]] && continue
    [[ "$candidate" =~ ^[[:space:]]*# ]] && continue
    run_scenario "candidate before target: $candidate" "$candidate"
  done <"$candidates_file"
fi

printf '\n== Summary ==\n'
for i in "${!summary_labels[@]}"; do
  printf '%s: %s failure(s)\n' "${summary_labels[$i]}" "${summary_failures[$i]}"
done

if [[ "$overall_failures" -gt 0 ]]; then
  exit 1
fi

exit 0
