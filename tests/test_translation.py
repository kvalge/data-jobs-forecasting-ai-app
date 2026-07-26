"""Tests for OpenRouterTranslator (HTTP mocked)."""

from unittest.mock import MagicMock, patch

from src.llm.translation import OpenRouterTranslator


def test_to_english_returns_english_field():
    translator = OpenRouterTranslator()
    with patch.object(translator, "_translate_with_fallback", return_value="Analyst"):
        assert translator.to_english("Analüütik") == "Analyst"


def test_to_english_falls_back_to_original_on_error():
    translator = OpenRouterTranslator()
    with patch.object(translator, "_translate_with_fallback", side_effect=RuntimeError("down")):
        assert translator.to_english("  Analüütik  ") == "Analüütik"


def test_to_english_empty_passthrough():
    assert OpenRouterTranslator().to_english("   ") == ""
