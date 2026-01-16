import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.answer_evaluation import AnswerEvaluationAgent, evaluate_answer
from app.schemas.message import AnswerEvaluation

@pytest.mark.asyncio
class TestAnswerEvaluationAgent:
    """Test suite for AnswerEvaluationAgent."""

    async def test_evaluate_success(self):
        """Test successful answer evaluation."""
        agent = AnswerEvaluationAgent()
        
        # Mock result
        expected_evaluation = AnswerEvaluation(
            score=7,
            rationale="Good answer.",
            evidence="Mentioned key concepts",
            followup_hint="Ask about trade-offs."
        )
        
        with patch.object(agent, "invoke_with_retry_async", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = expected_evaluation
            
            result = await agent.evaluate(
                question="Explain REST.",
                answer="Representational State Transfer."
            )
            
            assert result == expected_evaluation
            mock_invoke.assert_called_once()
            
            # Verify inputs
            call_kwargs = mock_invoke.call_args.kwargs
            assert "inputs" in call_kwargs
            inputs = call_kwargs["inputs"]
            assert inputs["question"] == "Explain REST."

    async def test_convenience_function(self):
        """Test the async convenience function."""
        expected_evaluation = AnswerEvaluation(
            score=8,
            rationale="Great.",
            evidence="Evidence found.",
            followup_hint=""
        )
        
        with patch("app.agents.answer_evaluation.AnswerEvaluationAgent.evaluate", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = expected_evaluation
            
            result = await evaluate_answer(
                question="Q",
                answer="A"
            )
            
            assert result == expected_evaluation
            mock_method.assert_called_once()
