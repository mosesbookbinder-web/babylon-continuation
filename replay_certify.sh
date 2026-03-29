#!/bin/zsh
set -euo pipefail

echo "=== REPLAY CERTIFICATION GATE ==="

./verify_continuation_record.py

if [[ ! -f replay_result.json ]]; then
  echo '{"verification":"INCOMPLETE","reason":"replay_result_missing","promotion":"none"}'
  exit 0
fi

python3 <<'PY'
import json
from pathlib import Path

with open("replay_result.json", "r", encoding="utf-8") as f:
    r = json.load(f)

required = {
    "replay_verified": True,
    "cross_host_reproduction": True,
    "execution_equivalence_under_replay": True
}

missing = [k for k in required if k not in r]
if missing:
    print(json.dumps({
        "verification": "INCOMPLETE",
        "reason": f"replay_result_missing_fields:{','.join(missing)}",
        "promotion": "none"
    }, indent=2))
    raise SystemExit(0)

bad = [k for k, v in required.items() if r.get(k) != v]
if bad:
    print(json.dumps({
        "verification": "HALT",
        "reason": f"replay_conditions_failed:{','.join(bad)}",
        "promotion": "none"
    }, indent=2))
    raise SystemExit(1)

print(json.dumps({
    "verification": "PASS",
    "reason": "replay_conditions_satisfied",
    "promotion": "eligible_for_reclassification"
}, indent=2))
PY
