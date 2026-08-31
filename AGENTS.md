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
