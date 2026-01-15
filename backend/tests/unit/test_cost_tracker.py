"""Unit tests for cost tracker utility."""
import pytest
from app.utils.cost_tracker import CostTracker


class TestCostTracker:
    """Test cases for cost tracking."""

    def test_estimate_tokens_openai(self):
        """Test token estimation for OpenAI models."""
        prompt = "Hello, how are you?"
        
        tokens = CostTracker.estimate_tokens(prompt, "gpt-4")
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_estimate_tokens_gemini(self):
        """Test token estimation for Gemini models (character-based)."""
        prompt = "A" * 400  # 400 characters
        
        tokens = CostTracker.estimate_tokens(prompt, "gemini-pro")
        # Should be approximately 100 tokens (4 chars per token)
        assert 90 <= tokens <= 110

    def test_calculate_cost_gpt4(self):
        """Test cost calculation for GPT-4."""
        cost = CostTracker.calculate_cost(
            prompt_tokens=1000,
            completion_tokens=500,
            model="gpt-4"
        )
        
        # GPT-4: $0.03/1K prompt, $0.06/1K completion
        expected = (1000 * 0.03 / 1000) + (500 * 0.06 / 1000)
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_gpt35(self):
        """Test cost calculation for GPT-3.5."""
        cost = CostTracker.calculate_cost(
            prompt_tokens=1000,
            completion_tokens=500,
            model="gpt-3.5-turbo"
        )
        
        # GPT-3.5: $0.0015/1K prompt, $0.002/1K completion
        expected = (1000 * 0.0015 / 1000) + (500 * 0.002 / 1000)
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_gemini(self):
        """Test cost calculation for Gemini."""
        cost = CostTracker.calculate_cost(
            prompt_tokens=1000,
            completion_tokens=500,
            model="gemini-pro"
        )
        
        # Gemini: $0.00025/1K prompt, $0.0005/1K completion
        expected = (1000 * 0.00025 / 1000) + (500 * 0.0005 / 1000)
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_unknown_model(self):
        """Test cost calculation for unknown models uses Gemini pricing."""
        cost = CostTracker.calculate_cost(
            prompt_tokens=1000,
            completion_tokens=500,
            model="unknown-model"
        )
        # Unknown models default to Gemini pricing
        expected = (1000 * 0.00025 / 1000) + (500 * 0.0005 / 1000)
        assert abs(cost - expected) < 0.0001

    def test_get_token_counts(self):
        """Test getting token counts with estimation."""
        prompt = "Test prompt"
        response = "Test response"
        
        counts = CostTracker.get_token_counts(
            prompt=prompt,
            response=response,
            model="gemini-pro"
        )
        
        assert "prompt_tokens" in counts
        assert "completion_tokens" in counts
        assert "total_tokens" in counts
        assert counts["total_tokens"] == counts["prompt_tokens"] + counts["completion_tokens"]

