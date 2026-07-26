---
alwaysApply: true
---

## Core Rules

- With code writing, move on step by step, only one task/functionality at a time. After implementig the task, ask the permission to go on with the next task.

## Code Quality

- Write clean, modular, and maintainable Python code.
- Writing code, prefer simplicity over complexity.
- Prefer small functions with single responsibility.
- Avoid duplication and hardcoded values where possible.
- Use type hints where reasonable.
- Add short, clear comments where they improve code understanding.
- Create relevant separate folders for code files.

## Project Consistency

- Keep `requirements.txt` updated whenever dependencies change.
- Keep `.env.example` updated with all required environment variables, using placeholder values (never real secrets).
- Keep `.gitignore` updated to exclude local files, caches, and sensitive data.
- Keep `README.md` updated when functionality or workflow changes.
- With every step made update plan in .cursor, what is done or changed.

## Security

- Store all sensitive environment variables (API keys, tokens, webhook URLs etc) in `.env`.
- Never commit `.env` to version control.
- Ensure `.env` is listed in `.gitignore`.

## Execution Safety

- Ensure scripts can be run manually without side effects on previous successful runs.

## Architecture

- Separate concerns.
- Follow best practicing of python projects.