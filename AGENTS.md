# Repository Guidelines

## Project Structure & Module Organization

- Core Python code lives in `src/md2angebot/` (`core/` for business logic, `ui/` for PyQt UI, `utils/` for helpers).
- The entry point for development is `main.py` in the project root.
- Templates (HTML/CSS) are in `templates/`; static assets such as logos are in `assets/`.
- Example markdown/config files are in `examples/`. Keep new examples small and focused.

## Build, Test, and Development Commands

- Install dependencies: `pip install -r requirements.txt`.
- Run the app in development: `python3 main.py`.
- Quick end‑to‑end pipeline smoke test: `python3 test_core.py`.
- Build the macOS app bundle: `./build_app.sh`; optionally create a DMG with `./create_dmg.sh`.

## Coding Style & Naming Conventions

- Use Python 3 style with 4‑space indentation and UTF‑8 source files.
- Prefer type hints and small, well‑named functions (e.g., `render_offer_preview`, not `doStuff`).
- Keep core logic independent of UI where possible (put business rules in `core/`, wiring in `ui/`).
- When touching templates, preserve existing structure and comments; keep CSS selectors descriptive.

## Testing Guidelines

- Add tests in files named `test_*.py` (e.g., extend `test_core.py` or add new ones alongside modules).
- Favor fast unit tests that isolate `md2angebot.core` behavior; avoid relying on external network or user config.
- Run `python3 test_core.py` after changes to the parsing/rendering pipeline; ensure it completes without errors.

## Commit & Pull Request Guidelines

- Use concise, imperative commit messages (e.g., `Fix template caching in dev mode`), referencing scope when helpful.
- Group related changes in a single commit; avoid mixing refactors with behavioral changes when possible.
- Pull requests should include a short summary, key implementation notes, and screenshots or PDFs if UI/output changes.

## Agent-Specific Instructions

- Prefer minimal, focused edits that respect the existing structure and naming.
- Do not modify build scripts, packaging specs, or template files unless the task explicitly requires it.
- When adding new modules or tests, follow the directory patterns and naming conventions described above.

