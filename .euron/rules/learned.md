<!-- Written by Euron Code after each task. It is rewritten automatically: put your own rules in
     another file in .euron/rules/. -->

# Learned in this project

- Tests: `cd C:/Lak-Learn/Lak_AI/SpeakNara/backend; python -m pytest -v` works here (passed 7x, last 2026-11-10). Use it to verify changes.
- Tests: `cd C:/Lak-Learn/Lak_AI/SpeakNara/backend && python -m pytest -v --tb=short 2>&1` works here (passed 4x, last 2026-11-10). Use it to verify changes.
- Lint / type check: `cd C:/Lak-Learn/Lak_AI/SpeakNara/frontend; npm run lint` works here (passed 5x, last 2026-11-10). Use it to verify changes.
- Lint / type check: `cd C:/Lak-Learn/Lak_AI/SpeakNara/frontend; npm run lint 2>&1` works here (passed 2x, last 2026-11-11). Use it to verify changes.
- Build: `cd C:/Lak-Learn/Lak_AI/SpeakNara/frontend; npm run build` works here (passed 3x, last 2026-11-10). Use it to verify changes.
- Build: `cd C:/Lak-Learn/Lak_AI/SpeakNara/frontend; npm run build 2>&1` works here (passed 1x, last 2026-11-11). Use it to verify changes.

## Security (from .euron/security/assessment.md)
- This code base has had: sql built from a string (SEC020). Use parameterised queries (placeholders + parameters), never f-strings, % or + in SQL. Do not add more; fix the existing ones when you touch those files.
