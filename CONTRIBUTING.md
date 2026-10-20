# Contributing

This repository is a research workbench first and a deployed demo second. Read
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) before changing code and
[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the verified setup commands.

## Branch workflow

`main` holds frozen, recorded work. Integrate through a `dev` branch:

1. Create `dev` once from `main` if it does not exist:
   `git switch -c dev origin/main && git push -u origin dev`
2. Cut a topic branch from `dev`: `git switch -c <topic> origin/dev`
3. Open the pull request against `dev`. Keep each PR to one concern.
4. Promote `dev` to `main` in a separate PR once the batch is verified.

Never force-push `main` or `dev`.

## Research integrity rules

These keep recorded results meaningful. A change that breaks one of them needs a new,
dated preregistration or addendum, not an edit.

* **Preregistrations are frozen.** Do not edit a `*_PREREGISTRATION*` file after its
  freeze commit. Add a dated addendum instead.
* **Fixtures are frozen.** Files under `tests/fixtures/` back recorded results. Additions
  go in a new dated fixture file; existing cases stay byte-unchanged.
* **Recorded artifacts are records.** Do not regenerate, rename, or delete files in
  `path_a_eval_artifacts/`. The runner scripts write new timestamped files there on every
  run, so run them in a throwaway clone (see DEVELOPMENT.md) and commit a new artifact only
  when the run is itself a new, intended result.
* **Results and claims stay as written.** Result notes, release notes, and claim-boundary
  reviews describe what was true at their commit. Correct them with a new dated note.
* **Expected limitations stay visible.** Do not delete `xfail` markers or skip conditions to
  make the suite green.

## Before opening a PR

```bash
python -m pytest -q
python audit_cli.py samples/sample_agents.md > /dev/null
```

If you touched `agents/authority_runtime.py`, `agents/resource_mapping.py`, or
`agents/anchor_contract.py`, also re-run `authority_runtime_v0_pass_a.py` in a throwaway
clone and confirm the fixed-name artifacts are byte-identical.

Do not commit secrets, `.env` files, or real customer memory files. External audit inputs
are handled under `EXTERNAL_AUDIT_INTAKE.md`.
