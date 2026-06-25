# Git & PR workflow (read before pushing!)

> `main` and `staging` are **protected** — you literally cannot push to them. Use PRs.

## One-time setup
```bash
git clone git@github.com:ThienHuynhNgoc/OpenRCA_DTH.git
cd OpenRCA_DTH
git switch dev            # dev is the default working branch
```

## Daily flow
```bash
git switch dev && git pull                       # get latest
git switch -c feature/input-load-real-data       # branch off dev
# ... edit code ...
git add -p
git commit -m "feat(input): read real metric files"
git push -u origin feature/input-load-real-data  # push the FEATURE branch (never main)
```
Then open a **Pull Request into `dev`** on GitHub. Fill the template, link the Jira issue.

## Branch names
`feature/<module>-<desc>`, `fix/<desc>`, `docs/<desc>`, `exp/<desc>`  (modules: input/process/output)

## Commit messages (Conventional Commits)
`<type>(<scope>): <summary>` — types: feat/fix/docs/refactor/test/chore/exp.
Example: `fix(process): handle empty metric series`. Put `Refs DEV-123` in the body.

## Merging up
`feature/* → dev` (you, via PR). `dev → staging → main` (leader, at milestones).

## Common fixes
- Pushed to the wrong branch? `git switch -c feature/x` then re-push.
- Behind dev? `git switch dev && git pull && git switch - && git merge dev`.
