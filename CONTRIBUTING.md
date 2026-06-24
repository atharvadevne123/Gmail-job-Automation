# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running tests

```bash
make test
```

## Code style

This project uses `ruff` for linting and formatting.

```bash
make lint      # check for issues
make fix       # auto-fix what ruff can
```

## Commit conventions

Use conventional commit prefixes:
- `feat:` new feature
- `fix:` bug fix
- `refactor:` code restructure without behaviour change
- `test:` test additions or fixes
- `docs:` documentation only
- `chore:` tooling / config

## Submitting changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Make atomic commits with descriptive messages
4. Run `make lint test` before pushing
5. Open a pull request against `main`

## Running the full check suite

```bash
make lint test
```
