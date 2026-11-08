"""Append one attempt record: python scripts/log_attempt.py UNIT N PASS|FAIL "reason" [evidence]"""
import json, sys, datetime, pathlib
unit, n, verdict, reason = sys.argv[1:5]
evidence = sys.argv[5] if len(sys.argv) > 5 else ""
rec = {"unit": unit, "attempt": int(n), "verdict": verdict, "reason": reason, "evidence": evidence,
       "at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
p = pathlib.Path(__file__).resolve().parents[1] / "evidence" / "attempts.jsonl"
with p.open("a", encoding="utf-8") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
