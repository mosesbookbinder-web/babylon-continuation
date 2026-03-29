#!/usr/bin/env python3
import json
import hashlib
import sys
from pathlib import Path

DECISION_ORDER = {"PASS": 0, "INCOMPLETE": 1, "HALT": 2}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def parse_sha_receipt(path: Path):
    line = path.read_text(encoding="utf-8").strip()
    parts = line.split()
    if len(parts) < 2:
        raise ValueError(f"Malformed sha receipt: {path}")
    return parts[0], parts[-1]

def fail(reason: str):
    print(json.dumps({
        "verification": "HALT",
        "reason": reason
    }, indent=2))
    sys.exit(1)

def main():
    root = Path(".").resolve()

    required = [
        "paper.pdf",
        "paper.tex",
        "decision.json",
        "decision.json.sha256",
        "run_bundle.json",
        "run_bundle.json.sha256",
        "refusal_record.json",
        "refusal_record.json.sha256",
        "SHA256_MANIFEST.txt",
        "SHA256_MANIFEST.txt.sha256",
        "CONTINUATION_RECORD.json",
        "CONTINUATION_RECORD.json.sha256",
    ]
    missing = [x for x in required if not (root / x).exists()]
    if missing:
        fail(f"missing_required_files:{','.join(missing)}")

    decision = read_json(root / "decision.json")
    cont = read_json(root / "CONTINUATION_RECORD.json")

    if decision.get("decision") != "PASS":
        fail("decision_not_pass")

    if decision.get("decision_scope") != "artifact_seal":
        fail("decision_scope_not_artifact_seal")

    if decision.get("claim_strength") != "artifact_sealed_not_replay_certified":
        fail("claim_strength_mismatch")

    if cont.get("formal_classification") != "SEALED_NOT_REPLAY_CERTIFIED":
        fail("continuation_record_classification_mismatch")

    if cont.get("evaluation_scope", {}).get("replay_verified_in_this_instance") is not False:
        fail("replay_scope_field_invalid")

    expected_not_verified = {
        "deterministic_replay",
        "cross_host_reproduction",
        "execution_equivalence_under_replay"
    }
    actual_not_verified = set(decision.get("not_verified", []))
    if actual_not_verified != expected_not_verified:
        fail("decision_not_verified_set_mismatch")

    for artifact_name, key in [
        ("paper.pdf", ("artifact", "sha256")),
        ("paper.tex", ("source", "sha256")),
        ("run_bundle.json", ("run_bundle", "sha256")),
        ("refusal_record.json", ("refusal_record", "sha256")),
    ]:
        live = sha256_file(root / artifact_name)
        obj = decision
        for k in key:
            obj = obj[k]
        if live != obj:
            fail(f"live_hash_mismatch:{artifact_name}")

    for receipt_name, target_name in [
        ("decision.json.sha256", "decision.json"),
        ("run_bundle.json.sha256", "run_bundle.json"),
        ("refusal_record.json.sha256", "refusal_record.json"),
        ("SHA256_MANIFEST.txt.sha256", "SHA256_MANIFEST.txt"),
        ("CONTINUATION_RECORD.json.sha256", "CONTINUATION_RECORD.json"),
    ]:
        claimed_hash, claimed_target = parse_sha_receipt(root / receipt_name)
        target_path = root / target_name
        live_hash = sha256_file(target_path)
        if Path(claimed_target).name != target_path.name:
            fail(f"receipt_target_mismatch:{receipt_name}")
        if claimed_hash != live_hash:
            fail(f"receipt_hash_mismatch:{receipt_name}")

    manifest_lines = (root / "SHA256_MANIFEST.txt").read_text(encoding="utf-8").strip().splitlines()
    manifest_targets = set()
    for line in manifest_lines:
        parts = line.split()
        if len(parts) < 2:
            fail("manifest_malformed")
        claimed_hash = parts[0]
        claimed_target = Path(parts[-1]).name
        manifest_targets.add(claimed_target)
        live_hash = sha256_file(root / claimed_target)
        if claimed_hash != live_hash:
            fail(f"manifest_hash_mismatch:{claimed_target}")

    for needed in {"paper.pdf", "paper.tex"}:
        if needed not in manifest_targets:
            fail(f"manifest_missing_target:{needed}")

    result = {
        "verification": "PASS",
        "scope": "artifact_seal_only",
        "promotion": "none",
        "formal_classification": "SEALED_NOT_REPLAY_CERTIFIED",
        "verified_checks": decision.get("verified_checks", []),
        "not_verified": decision.get("not_verified", [])
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
