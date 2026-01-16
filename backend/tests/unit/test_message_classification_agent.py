import pytest
from unittest.mock import AsyncMock, patch
from app.agents.message_classification import MessageClassificationAgent, classify_message
from app.schemas.interview import MessageClassification

@pytest.mark.asyncio
class TestMessageClassificationAgent:
    """Test suite for MessageClassificationAgent."""

    async def test_classify_success(self):
        """Test successful message classification."""
        agent = MessageClassificationAgent()
        
        # Mock result
        expected_classification = MessageClassification(
            type="Answer",
            confidence=0.95
        )
        
        with patch.object(agent, "invoke_with_retry_async", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = expected_classification
            
            result = await agent.classify(
                current_question="What is REST?",
                candidate_message="It's an architectural style."
            )
            
            assert result == expected_classification
            mock_invoke.assert_called_once()
            
            # Verify inputs
            call_kwargs = mock_invoke.call_args.kwargs
            assert "inputs" in call_kwargs
            inputs = call_kwargs["inputs"]
            assert inputs["current_question"] == "What is REST?"

    async def test_convenience_function(self):
        """Test the async convenience function."""
        expected_classification = MessageClassification(
            type="Clarification",
            confidence=0.8
        )
        
        with patch("app.agents.message_classification.MessageClassificationAgent.classify", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = expected_classification
            
            result = await classify_message(
                current_question="Q",
                candidate_message="I don't understand."
            )
            
            assert result == expected_classification
            mock_method.assert_called_once()
