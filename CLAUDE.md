# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyFonts is a PyQt5 desktop application that displays all system fonts with preview samples. Users can browse fonts, add favorites, and export font lists to text files.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python FontViewerApp.py
```

Note: Requires a display environment (GUI). On Windows, run from PowerShell. The .venv contains PyQt5 for Windows.

## Architecture

This is a single-file PyQt5 application (`FontViewerApp.py`):

- **FontViewer class**: Main QWidget containing two QTableWidget sections:
  - "All Fonts" table: Lists every system font with sample text
  - "Favorites" table: User-selected fonts (persisted across sessions)

- **Key behaviors**:
  - Double-click in "All Fonts" adds to favorites
  - Double-click in "Favorites" removes from favorites
  - Window size, position, and favorites persist to `config.ini`
  - Uses `sortedcontainers.SortedSet` for favorites (alphabetically sorted)

## Configuration

`config.ini` stores:
- `[Settings]`: Window size and position
- `[Favorites]`: Comma-separated list of favorite font names
- Settings auto-save on window close and auto-load on startup

## User Data Files (gitignored)

- `font_list.txt`: Exported list of all system fonts
- `favorites_list.txt`: Exported favorites list
- `config.ini`: User preferences
