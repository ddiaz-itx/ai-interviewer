import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.question_generation import QuestionGenerationAgent, generate_question

@pytest.mark.asyncio
class TestQuestionGenerationAgent:
    """Test suite for QuestionGenerationAgent."""

    async def test_generate_question_success(self):
        """Test successful question generation."""
        agent = QuestionGenerationAgent()
        
        # Mock LLM and chain invocation
        mock_result = MagicMock()
        mock_result.content = "What is dependency injection?"
        
        # We need to mock get_llm to return something we can use
        # But BaseAgent invokes chain. invoke_with_retry_async calls chain.invoke
        # We can mock invoke_with_retry_async directly to avoid testing BaseAgent logic here
        
        with patch.object(agent, "invoke_with_retry_async", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_result
            
            question = await agent.generate_question(
                focus_areas=["Python", "FastAPI"],
                difficulty_level=5.0,
                chat_history="",
                questions_asked=0
            )
            
            assert question == "What is dependency injection?"
            mock_invoke.assert_called_once()
            
            # Verify inputs were correctly passed to invoke_with_retry_async
            call_kwargs = mock_invoke.call_args.kwargs
            assert "inputs" in call_kwargs
            inputs = call_kwargs["inputs"]
            assert inputs["focus_areas"] == "Python, FastAPI"
            assert inputs["difficulty_level"] == 5.0

    async def test_convenience_function(self):
        """Test the async convenience function."""
        with patch("app.agents.question_generation.QuestionGenerationAgent.generate_question", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = "What is async?"
            
            result = await generate_question(
                focus_areas=["AsyncIO"],
                difficulty_level=7.0
            )
            
            assert result == "What is async?"
            mock_method.assert_called_once() 
