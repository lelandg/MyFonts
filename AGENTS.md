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

Policy lives in `~/.config/agents/AGENTS.md` -> "Dependency, code, and secret
scanning" and "Model delegation & cross-provider review". It is not restated
here; read it there. What is specific to this repo:

- CI runs `gitleaks`, `osv-scanner` and `zizmor` on every PR, every push to `main`, and
  weekly (`.github/workflows/security.yml`). There are no npm jobs: the repo has
  no `package-lock.json`, and `npm ci` without one is a red check, not a scan.
- Dependabot config is committed (`.github/dependabot.yml`): grouped security
  PRs for `requirements.txt` (pip), and **version updates only** for
  github-actions.
- SHA-pinned actions get **no Dependabot alerts**: GitHub generates them only
  for actions on semantic versions (docs: "About Dependabot alerts"). So no
  security-update PR can ever fire for a pinned action, an
  `applies-to: security-updates` group over github-actions is dead config, and
  the weekly version update is their only automatic remediation -- which is why
  the github-actions block carries no semver-major ignore. DETECTION comes
  from the `zizmor` job in `security.yml`: it maps each SHA pin to its
  release tag and fails on a known-vulnerable, impostor or unpinned action.
  osv-scanner's `github/actions` plugin only lists the pinned actions: with
  osv-scanner 2.7.0 it did not flag `tj-actions/changed-files`
  (GHSA-mrrh-fwg8-r2c3) at a vulnerable SHA or tag. A SHA that no tag of
  the action's repository points at would match no advisory, so the zizmor
  job also fails on such a pin: pin released versions.
- Dependabot **alerts** are a per-repo GitHub setting; a config file does not
  turn them on. Without them the config above governs version updates only.
  Check it by HTTP STATUS, not by exit code -- `gh api` exits 0 on success
  and 1 on any failure, and never exits 404 or 403:
  `gh api -i -X GET repos/lelandg/MyFonts/vulnerability-alerts | head -1`
  204 = on, 404 = off, 403 = the token has no admin on this repo, which is
  NOT the same as off. Enable: same path with `-X PUT`.
- Alerts and automatic security **updates** are two switches, not one. Alerts
  only report; the half that opens PRs is `automated-security-fixes` (same API
  shape). It is deliberately OFF here: this repo took its first scan with a
  pre-existing advisory backlog, and enabling it would open that backlog as
  PRs at once. Turn it on per repo once the backlog is cleared.
- PR reviewers configured for this repo: **Codex** (run locally against the
  committed branch before opening the PR) and **CodeRabbit**
  (`coderabbitai[bot]`). How to read their checks -- which one re-reviews a
  push, why a green check does not mean "no findings", and which label skips
  which bot -- is in the global policy cited above and is deliberately not
  repeated here.
