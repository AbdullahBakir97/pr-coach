"""Shared test fixtures for PR Coach."""

from __future__ import annotations

import pytest


@pytest.fixture()
def good_pr_title() -> str:
    """A well-formed PR title."""
    return "feat(auth): add OAuth2 login with Google provider"


@pytest.fixture()
def bad_pr_title() -> str:
    """A vague, low-quality PR title."""
    return "fix"


@pytest.fixture()
def good_pr_description() -> str:
    """A detailed PR description with all quality signals."""
    return """## What
This PR adds OAuth2 login support with Google as a provider.

## Why
Users have requested social login to reduce friction during sign-up.
Closes #42

## Testing
- Added unit tests for the OAuth2 flow
- Tested manually with a Google test account

## Screenshots
![Login page](https://example.com/screenshot.png)

## Checklist
- [x] Code compiles without warnings
- [x] Tests pass
- [x] Documentation updated
"""


@pytest.fixture()
def empty_pr_description() -> str:
    """An empty PR description."""
    return ""


@pytest.fixture()
def minimal_pr_description() -> str:
    """A minimal PR description with only basic info."""
    return "Fixed the login bug that was reported last week."


@pytest.fixture()
def sample_files() -> list[dict[str, object]]:
    """A realistic set of changed files for a PR."""
    return [
        {"filename": "src/auth/oauth.py", "additions": 120, "deletions": 5},
        {"filename": "src/auth/providers.py", "additions": 45, "deletions": 0},
        {"filename": "tests/test_oauth.py", "additions": 80, "deletions": 0},
        {"filename": "docs/auth.md", "additions": 20, "deletions": 3},
    ]


@pytest.fixture()
def large_pr_files() -> list[dict[str, object]]:
    """A set of files representing a very large PR."""
    return [{"filename": f"src/module_{i}/handler.py", "additions": 100, "deletions": 50} for i in range(25)]


@pytest.fixture()
def sample_diff() -> str:
    """A simple diff for testing."""
    return """diff --git a/src/auth/oauth.py b/src/auth/oauth.py
new file mode 100644
--- /dev/null
+++ b/src/auth/oauth.py
@@ -0,0 +1,50 @@
+class OAuthProvider:
+    def authenticate(self):
+        pass
"""


@pytest.fixture()
def sample_webhook_payload() -> dict:
    """A realistic pull_request webhook payload."""
    return {
        "action": "opened",
        "pull_request": {
            "number": 42,
            "title": "feat(auth): add OAuth2 login support",
            "body": "## What\nAdds OAuth2 login.\n\nCloses #10",
            "head": {"sha": "abc1234567890"},
        },
        "repository": {
            "name": "my-repo",
            "owner": {"login": "octocat"},
        },
        "installation": {"id": 12345},
    }
