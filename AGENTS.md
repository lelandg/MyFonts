# MyFonts — agent guide

MyFonts is a single-file PySide6 desktop app (`FontViewerApp.py`). It lists every
system font with a sample, keeps a favorites list, and exports font lists to
text files. Global house rules apply (`~/.config/agents/AGENTS.md`).

## Gotchas

- The app needs a display. Run it from Windows PowerShell with `.venv`
  (`python FontViewerApp.py`). `.venv` holds the Windows PySide6 build. Do not
  run the app from WSL.
- `config.ini` is tracked in git although `.gitignore` lists it. The app
  rewrites `config.ini` on every close (window geometry, favorites). Do not
  commit that runtime change.
- `favorites_list.txt` and `font_list.txt` are user exports (untracked). Do not
  commit them.

## Conventions

- Favorites use `sortedcontainers.SortedSet`; keep the list sorted when you
  change favorites logic.
- Double-click toggles favorites: add from "All Fonts", remove from
  "Favorites". Keep that behavior.

## Scanning & review

Policy lives in `~/.config/agents/AGENTS.md` -> "Dependencies, advisories, and
scanning" and "Model delegation & cross-provider review", with the full text
in `~/.claude/instructions/security-scanning.md` and
`~/.claude/instructions/model-delegation.md`. It is not restated here; read it
there. What is specific to this repo:

- CI runs `gitleaks`, `osv-scanner` and `zizmor` on every PR, every push to `main`, and
  weekly (`.github/workflows/security.yml`). The workflow also carries
  `npm audit` and `npm audit signatures` jobs, which skip themselves with a
  notice here: the repo has no `package-lock.json` or `npm-shrinkwrap.json`,
  so a green npm job is a skip, not a scan.
- Dependabot config is committed (`.github/dependabot.yml`): grouped security
  PRs for `requirements.txt` (pip), and **version updates only** for
  github-actions.
- Pin actions to a SHA of a plain release version (v1, v1.2.3) or the `zizmor`
  job fails. Dependabot alerts and automatic security updates are separate
  per-repo switches; updates are deliberately off until the advisory backlog
  clears. Detail: `Docs/security-posture.md`.
- **PR reviewers.** The review council in the global rules applies here; its
  members are whatever `~/.config/agents/council.toml` seats, and the runner
  and commands are in `~/.claude/instructions/model-delegation.md`. This repo
  adds **CodeRabbit** (`coderabbitai[bot]`, config `.coderabbit.yaml`), which
  reviews automatically after the PR opens and re-reviews every push; it
  skips drafts, Dependabot and Renovate PRs, and any PR opened carrying the
  `no-ai-review` label. The list is additive, not closed: nothing named here
  replaces a council member. A green CodeRabbit check does not mean "no
  findings", or even that a review ran. Read the check run's output title on
  the PR's head (`Finished` = reviewed; `Review rate limited` and
  `Review skipped` = not reviewed); the query is in the comments of
  `.coderabbit.yaml`. Findings arrive as inline comments, so read them too.
  Retrying a missed review: `~/.claude/instructions/pr-review-automation.md`.
