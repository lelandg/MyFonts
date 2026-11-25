# MyFonts — security posture detail

Reference detail for the "Scanning & review" section of `AGENTS.md`. The rules
are in `AGENTS.md` and the global policy it cites; this file holds the
mechanics behind them. It is as binding as `AGENTS.md`.

## SHA-pinned actions and zizmor

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
  (GHSA-mrrh-fwg8-r2c3) at a vulnerable SHA or tag. zizmor looks up a SHA
  pin by one tag: for a root action (owner/repo@sha) the longest tag
  without a `/`, for a sub-action the longest tag under its path or its
  last directory (else the longest of all). The job fails unless that tag, and any tag tied
  with it, is a plain release version (v1, v1.2.3): an untagged commit,
  a non-version tag or a path-prefixed tag matches no advisory. Pin
  released versions.

## Dependabot alerts

- Dependabot **alerts** are a per-repo GitHub setting; a config file does not
  turn them on. Without them the config in `.github/dependabot.yml` governs
  version updates only.
  Check it by HTTP STATUS, not by exit code -- `gh api` exits 0 on success
  and 1 on any failure, and never exits 404 or 403:
  `gh api -i -X GET repos/lelandg/MyFonts/vulnerability-alerts`
  204 = on. A 403 is inconclusive until you read the response: a body that
  mentions a rate limit, a `retry-after` header, or
  `x-ratelimit-remaining: 0` means a primary or secondary rate limit (wait,
  then retry); only a 403 with none of those, from a token whose
  `.permissions.admin` (below) is not `true`, means the token lacks admin.
  A 404 means off only when the token can read the setting, and
  `gh api repos/lelandg/MyFonts --jq .permissions.admin`
  does not prove that by itself: it prints the user's role on the repository,
  not what the token may read. With a classic token (`gh auth status` lists
  its scopes, `repo` among them) `true` is enough. A fine-grained token can
  print `true` and still get a 404 for a setting that is on, because it also
  needs the "Administration" repository permission (read) and must list this
  repository among the ones it covers; unless you have confirmed both, report
  a 404 as unknown. Only an answer the token
  can read establishes the state: the 204 here, the 200 body for automatic
  security updates below. Unknown is not the same as off. Enable: same path
  with `-X PUT`.

## Automatic security updates

- Alerts and automatic security **updates** are two switches, not one. Alerts
  only report; the half that opens PRs is `automated-security-fixes`. Its
  API answers differently: `gh api repos/lelandg/MyFonts/automated-security-fixes`
  returns 200 with `{"enabled": ..., "paused": ...}` (updates are on only
  when `enabled` is true and `paused` is false), or 404 when they are
  off. A 404 is also what a token that cannot read the setting sees, so
  read it as off only when the token passes the test above (a classic token
  with `.permissions.admin` `true`, or a fine-grained token confirmed to cover
  this repository with Administration read); otherwise report it as unknown. Enable with `-X PUT`.
  It is deliberately OFF here: this repo took its first scan with a
  pre-existing advisory backlog, and enabling it would open that backlog as
  PRs at once. Turn it on per repo once the backlog is cleared.

## The `no-ai-review` label

`.coderabbit.yaml` skips a PR that carries the `no-ai-review` label when the
review would fire, so the label has to be on the PR before that moment. Two
ways do that, the same two the comments in `.coderabbit.yaml` give: put it on
at creation (`gh pr create --label no-ai-review`), or open the PR as a draft
(`drafts: false` means a draft is not reviewed), add the label, then mark it
ready. A label added to a ready PR after it opened is too late. The label did not exist
in this repo when this file was written (2026-11-25), and
`gh pr create --label` fails on a missing label. Check with
`gh label list --repo lelandg/MyFonts --search no-ai-review`; the command that
creates it is in the comments of `.coderabbit.yaml`.
