# Contributing guide — conventions for OpenRCA_DTH

Read this once before your first commit. It is written for newcomers.

## 1. Branching model
```
main      ← protected, stable/release. PR-only. You cannot push here.
 └ staging ← pre-release / QA. PR-only.
    └ dev   ← integration branch (DEFAULT). Your PRs target this.
       └ feature/* ← your working branches
```
- Always branch off `dev`: `git switch dev && git pull && git switch -c feature/<scope>-<short-desc>`
- Open PRs **into `dev`**. `dev → staging → main` is done by the leader at milestones.

## 2. Branch naming
`feature/<module>-<short-desc>`, `fix/<short-desc>`, `docs/<short-desc>`, `exp/<short-desc>`
- Modules: `input`, `process`, `output`. Example: `feature/input-query-parser`.

## 3. Commit messages (Conventional Commits)
```
<type>(<scope>): <short summary in present tense>
```
- types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `exp`
- scopes: `input`, `process`, `output`, `eval`, `data`, `docs`
- Example: `feat(process): add z-score anomaly detector`
- Keep the summary < 72 chars. Add a body explaining *why* if it is not obvious.
- Link the Jira task: put the issue key in the body, e.g. `Refs DEV-123`.

## 4. Pull Requests
- One PR = one focused change. Fill in the PR template.
- A PR needs **1 approval** and a **green CI** check before it can merge.
- Target branch = `dev`. Link the Jira issue. Describe how you tested it.

## 5. Code conventions (Python)
- Python **3.10+**. Follow **PEP 8**. Format with **black**, lint with **ruff** (config in `pyproject.toml`).
  ```bash
  pip install black ruff
  black . && ruff check .
  ```
- Use **type hints** on public functions. Prefer small, pure functions.
- Names: `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Never hard-code secrets/API keys. Read them from environment variables.
- Do not commit data (`data/` is gitignored) or large result files.

## 6. Documentation conventions
- Every module function gets a docstring: **one summary line**, then args/returns if non-obvious.
- Update the relevant `docs/*.md` when you change behavior.
- Notebooks: clear outputs before committing (`Kernel → Restart & Clear Output`).
- Keep `docs/TASKS.md` and Jira in sync (the leader checks this).

## 7. Definition of Done (per task)
- [ ] Code + docstrings + a short test (or a notebook cell) demonstrating it works.
- [ ] `black`/`ruff` clean, smoke test green.
- [ ] PR opened into `dev`, linked to the Jira issue, reviewed & approved.
