# MyFonts — agent guide

MyFonts is a single-file PyQt5 desktop app (`FontViewerApp.py`). It lists every
system font with a sample, keeps a favorites list, and exports font lists to
text files. Global house rules apply (`~/.config/agents/AGENTS.md`).

## Gotchas

- The app needs a display. Run it from Windows PowerShell with `.venv`
  (`python FontViewerApp.py`). `.venv` holds the Windows PyQt5 build. Do not
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

Policy lives in `~/.config/agents/AGENTS.md` -> "Dependency, code, and secret
scanning" and "Model delegation & cross-provider review". It is not restated
here; read it there. What is specific to this repo:

- CI runs `gitleaks` and `osv-scanner` on every PR, every push to `main`, and
  weekly (`.github/workflows/security.yml`). There are no npm jobs: the repo has
  no `package-lock.json`, and `npm ci` without one is a red check, not a scan.
- Dependabot config is committed, with grouped security PRs (`.github/dependabot.yml`)
  for `requirements.txt` (pip) and the pinned action SHAs (github-actions).
- Dependabot **alerts** are a per-repo GitHub setting; a config file does not
  turn them on. Without them the config above governs version updates only.
  Check: `gh api -X GET repos/lelandg/MyFonts/vulnerability-alerts` (exit 0 = on,
  404 = off). Enable: same path with `-X PUT`.
- PR reviewers configured for this repo: **Codex** (run locally against the
  committed branch before opening the PR) and **CodeRabbit**
  (`coderabbitai[bot]`). How to read their checks -- which one re-reviews a
  push, why a green check does not mean "no findings", and which label skips
  which bot -- is in the global policy cited above and is deliberately not
  repeated here.
