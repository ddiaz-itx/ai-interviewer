import pytest
from unittest.mock import AsyncMock, patch
from app.agents.integrity_judgment import IntegrityJudgmentAgent, assess_integrity
from app.schemas.interview import IntegrityAssessment

@pytest.mark.asyncio
class TestIntegrityJudgmentAgent:
    """Test suite for IntegrityJudgmentAgent."""

    async def test_assess_success(self):
        """Test successful integrity assessment."""
        agent = IntegrityJudgmentAgent()
        
        # Mock result
        expected_assessment = IntegrityAssessment(
            cheat_certainty=15.0,
            indicators=["Fast response"]
        )
        
        with patch.object(agent, "invoke_with_retry_async", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = expected_assessment
            
            result = await agent.assess(
                question="What is this question about?",
                answer="A",
                response_time_ms=1000,
                paste_detected=False,
                previous_answers=[]
            )
            
            assert result == expected_assessment
            mock_invoke.assert_called_once()
            
            # Verify inputs to invoke
            call_kwargs = mock_invoke.call_args.kwargs
            assert "inputs" in call_kwargs
            inputs = call_kwargs["inputs"]
            assert inputs["question"] == "What is this question about?"
            assert inputs["response_time_ms"] == 1000

    async def test_convenience_function(self):
        """Test the async convenience function."""
        expected_assessment = IntegrityAssessment(
            cheat_certainty=0.0,
            indicators=[]
        )
        
        with patch("app.agents.integrity_judgment.IntegrityJudgmentAgent.assess", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = expected_assessment
            
            result = await assess_integrity(
                question="What is this question about?",
                answer="A"
            )
            
            assert result == expected_assessment
            mock_method.assert_called_once()
