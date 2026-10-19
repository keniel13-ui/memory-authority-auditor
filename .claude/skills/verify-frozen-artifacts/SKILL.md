---
name: verify-frozen-artifacts
description: Check that recorded research artifacts in path_a_eval_artifacts/ still reproduce from the current code, without writing anything into the working tree. Use after changing any agents/ gate module, before claiming a result still holds, or when asked whether a recorded artifact is reproducible.
---

# Verify frozen artifacts

Recorded artifacts are evidence. This procedure regenerates them in a throwaway clone and
compares, so the working tree and `path_a_eval_artifacts/` are never modified.

## Steps

1. Make a throwaway clone of the commit under test (commit or stash local edits first if you
   want them included; `git clone` copies committed state only):

   ```bash
   tmp=$(mktemp -d) && git clone -q . "$tmp/repo" && cd "$tmp/repo"
   ```

2. Authority Runtime (fixed-name files, must be byte-identical):

   ```bash
   python authority_runtime_v0_pass_a.py
   python authorityctl.py audit tests/fixtures/authority_runtime_v0_gwb_dns_replay_2026_07_21.json \
     --case authority_runtime_ar1_real_gwb_stale_cutover \
     --json-out path_a_eval_artifacts/authority_runtime_v0_gwb_stale_action_decision.json \
     --markdown-out path_a_eval_artifacts/authority_runtime_v0_gwb_stale_action_decision.md
   echo "exit=$?"          # expect 3
   git status --short      # expect no output
   ```

3. Timestamped runners: run the script, then compare its new JSON with the committed artifact
   after dropping `generated_at`, `generated_at_utc`, `run_id`, and the `YYYYMMDDTHHMMSSZ`
   slug:

   ```bash
   python - "$committed" "$fresh" <<'PY'
   import json, re, sys
   slug = re.compile(r"20\d{6}T\d{6}Z")
   def norm(v):
       if isinstance(v, dict):
           return {k: norm(x) for k, x in v.items() if k not in {"generated_at", "generated_at_utc", "run_id"}}
       if isinstance(v, list):
           return [norm(x) for x in v]
       return slug.sub("<slug>", v) if isinstance(v, str) else v
   a, b = (norm(json.load(open(p))) for p in sys.argv[1:])
   print("MATCH" if a == b else "DIFF")
   PY
   ```

   The expected status of each committed artifact is the table in `docs/DEVELOPMENT.md`
   ("Reproducing recorded artifacts"). `path_a_v2_regate.py` needs
   `--recorded-artifact path_a_eval_artifacts/path_a_eval_20260712T003706Z.json` to match the
   `20260712T005345Z` re-gate.

4. For an artifact listed as reproducing only at its recording commit, `git checkout <commit>`
   inside the throwaway clone and repeat step 3.

5. Delete the throwaway directory. Report MATCH/DIFF per artifact with the commands run.

## Rules

* Never copy regenerated files back into the real repository.
* A new DIFF on an artifact that previously matched at HEAD is a research regression to
  report, not something to "fix" by regenerating the committed file.
* `path_a_eval_runner.py` calls a live model; it is out of scope for this check.
