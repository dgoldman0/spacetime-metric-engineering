# v0.5.2 packaging fix

- Adds `tabulate` to package dependencies for markdown report generation.
- Adds a CSV fallback if `tabulate` is unavailable.
- Ensures `scripts/run_local_smoke.sh` creates `runs/` before validation outputs are written.
