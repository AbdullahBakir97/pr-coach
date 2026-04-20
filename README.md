# PR Coach

[![CI](https://github.com/AbdullahBakir97/pr-coach/actions/workflows/ci.yml/badge.svg)](https://github.com/AbdullahBakir97/pr-coach/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A GitHub App that teaches contributors how to write better pull requests. PR Coach analyzes PR title, description, and diff, then posts coaching comments with actionable suggestions.

## Features

- **Title Analysis** -- Checks length, specificity, and conventional commit format
- **Description Quality** -- Validates what/why sections, linked issues, test mentions, screenshots
- **Diff Analysis** -- Evaluates PR size, file count, single-focus, and test file inclusion
- **Quality Score 0-100** -- Weighted scoring across all checks
- **GitHub Checks** -- Creates a Check Run with pass/neutral/fail conclusion
- **Coaching Comments** -- Posts actionable suggestions with score table and tips
- **Breaking Change Detection** -- Validates breaking change documentation
- **Configurable** -- Per-repo `.github/pr-coach.yml` for thresholds and actions

## How It Works

1. A pull request is opened or updated
2. PR Coach analyzes the title, description, and diff
3. Each dimension is scored with weighted checks
4. A GitHub Check Run is created with the overall result
5. A coaching comment is posted with specific improvement suggestions

## Configuration

Add `.github/pr-coach.yml` to your repository:

```yaml
# .github/pr-coach.yml
enabled: true
min_score: 60
require_linked_issue: false
require_description: true
require_tests: false
max_files: 20
max_lines: 500
action: check  # check | comment | request-changes | block
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | `true` | Enable/disable PR Coach |
| `min_score` | `60` | Minimum score to pass (0-100) |
| `require_linked_issue` | `false` | Fail if no issue is linked |
| `require_description` | `true` | Fail if description is empty |
| `require_tests` | `false` | Fail if no test files included |
| `max_files` | `20` | Max files before size warning |
| `max_lines` | `500` | Max lines before size warning |
| `action` | `check` | What action to take |

### Actions

- `check` -- Only create a GitHub Check Run (default)
- `comment` -- Post a coaching comment on the PR
- `request-changes` -- Request changes if score is below minimum
- `block` -- Block the PR if score is below minimum

## Tech Stack

- **Python 3.12+** with type hints everywhere
- **FastAPI** for the webhook server
- **Pydantic v2** for data validation
- **httpx** for async HTTP
- **PyJWT** for GitHub App authentication
- **Clean Architecture** (domain, analyzers, application, infrastructure, api)

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the server
cp .env.example .env
# Edit .env with your GitHub App credentials
python -m src.main

# Run tests
pytest

# Lint and format
ruff check src/ tests/
ruff format src/ tests/
```

## Deployment

### Render

Click the button below or use the `render.yaml` in this repository:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Docker

```bash
docker build -t pr-coach .
docker run -p 8000:8000 --env-file .env pr-coach
```

## Architecture

```
src/
  domain/         # Entities, enums, interfaces, exceptions
  analyzers/      # Title, description, diff analyzers + scorer
  generators/     # Comment and check output builders
  application/    # Orchestrator, webhook handler
  infrastructure/ # GitHub client, auth, config loader
  api/            # FastAPI app, routes, middleware
  config/         # Settings, logging
  container.py    # Dependency injection
  main.py         # Entry point
```

## License

MIT License - see [LICENSE](LICENSE) for details.
