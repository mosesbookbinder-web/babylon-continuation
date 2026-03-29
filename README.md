# The Babylon Continuation

**J. M. Bookbinder**  
Witness Grade Analytics (WGA)

This repository contains the sealed artifact bundle for:

**Deterministic Replay and Refusal-First Execution Control in Declared Processes**

## Bundle Contents

- `paper.pdf`
- `paper.tex`
- `run_bundle.json`
- `decision.json`
- `decision_receipt.json`
- `refusal_record.json`
- `SHA256_MANIFEST.txt`

## Tightened Decision

- **WAUR-style admissibility result:** INCOMPLETE
- **Decision precedence:** HALT > INCOMPLETE > PASS
- **Reason:** artifact and linkage are present, but replay determinism is not yet certified in this bundle

## Verification

Run:

```bash
shasum -a 256 -c SHA256_MANIFEST.txt
shasum -a 256 -c SHA256_MANIFEST.txt.sha256
```

