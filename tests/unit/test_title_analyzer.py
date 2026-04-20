"""Unit tests for TitleAnalyzer."""

from __future__ import annotations

import pytest

from src.analyzers.title_analyzer import TitleAnalyzer


@pytest.fixture()
def analyzer() -> TitleAnalyzer:
    """Create a TitleAnalyzer instance."""
    return TitleAnalyzer()


class TestTitleLength:
    """Tests for title length validation."""

    def test_good_length(self, analyzer: TitleAnalyzer) -> None:
        """A title between 10-72 chars passes."""
        results = analyzer.analyze("feat(auth): add OAuth2 login support")
        length_check = next(r for r in results if r[0] == "title_length")
        assert length_check[1] is True

    def test_too_short(self, analyzer: TitleAnalyzer) -> None:
        """A title under 10 chars fails."""
        results = analyzer.analyze("fix bug")
        length_check = next(r for r in results if r[0] == "title_length")
        assert length_check[1] is False
        assert "too short" in length_check[2]

    def test_too_long(self, analyzer: TitleAnalyzer) -> None:
        """A title over 72 chars fails."""
        long_title = "feat(auth): " + "a" * 70
        results = analyzer.analyze(long_title)
        length_check = next(r for r in results if r[0] == "title_length")
        assert length_check[1] is False
        assert "too long" in length_check[2]


class TestTitleSpecificity:
    """Tests for title specificity validation."""

    def test_descriptive_title(self, analyzer: TitleAnalyzer) -> None:
        """A multi-word title passes specificity."""
        results = analyzer.analyze("Add OAuth2 login support for Google")
        spec_check = next(r for r in results if r[0] == "title_specificity")
        assert spec_check[1] is True

    def test_vague_single_word(self, analyzer: TitleAnalyzer) -> None:
        """A single vague word fails specificity."""
        results = analyzer.analyze("update")
        spec_check = next(r for r in results if r[0] == "title_specificity")
        assert spec_check[1] is False
        assert "vague" in spec_check[2]

    def test_two_word_title(self, analyzer: TitleAnalyzer) -> None:
        """A two-word title warns about clarity."""
        results = analyzer.analyze("fix authentication")
        spec_check = next(r for r in results if r[0] == "title_specificity")
        assert spec_check[1] is False


class TestTitleConventional:
    """Tests for conventional commit format detection."""

    def test_conventional_format(self, analyzer: TitleAnalyzer) -> None:
        """A conventional-format title passes."""
        results = analyzer.analyze("feat(auth): add OAuth2 login support")
        conv_check = next(r for r in results if r[0] == "title_conventional")
        assert conv_check[1] is True

    def test_non_conventional_format(self, analyzer: TitleAnalyzer) -> None:
        """A non-conventional title does not pass."""
        results = analyzer.analyze("Add OAuth2 login support for Google")
        conv_check = next(r for r in results if r[0] == "title_conventional")
        assert conv_check[1] is False

    def test_conventional_without_scope(self, analyzer: TitleAnalyzer) -> None:
        """A conventional title without scope passes."""
        results = analyzer.analyze("fix: resolve null pointer on empty request")
        conv_check = next(r for r in results if r[0] == "title_conventional")
        assert conv_check[1] is True

    def test_conventional_with_breaking(self, analyzer: TitleAnalyzer) -> None:
        """A conventional title with breaking indicator passes."""
        results = analyzer.analyze("feat!: drop Python 3.10 support")
        conv_check = next(r for r in results if r[0] == "title_conventional")
        assert conv_check[1] is True
