import pytest
from unittest.mock import AsyncMock, patch
from app.agents.report_generation import ReportGenerationAgent, generate_report
from app.schemas.interview import FinalReport

@pytest.mark.asyncio
class TestReportGenerationAgent:
    """Test suite for ReportGenerationAgent."""

    async def test_generate_report_success(self):
        """Test successful report generation."""
        agent = ReportGenerationAgent()
        
        # Mock result
        expected_report = FinalReport(
            interview_score=8,
            summary="Strong candidate.",
            gaps=["None"],
            meeting_expectations=["Technical skills"],
            integrity_flags=[]
        )
        
        with patch.object(agent, "invoke_with_retry_async", new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = expected_report
            
            result = await agent.generate_report(
                match_analysis={"match_score": 8, "match_summary": "Good", "focus_areas": ["Valid"]},
                transcript="Q: ... A: ...",
                question_scores=[{"score": 8, "rationale": "Good"}],
                telemetry_summary="No issues."
            )
            
            assert result == expected_report
            mock_invoke.assert_called_once()
            
            # Verify inputs to invoke
            call_kwargs = mock_invoke.call_args.kwargs
            assert "inputs" in call_kwargs
            inputs = call_kwargs["inputs"]
            assert "match_analysis" in inputs
            assert "transcript" in inputs

    async def test_convenience_function(self):
        """Test the async convenience function."""
        expected_report = FinalReport(
            interview_score=9,
            summary="Excellent.",
            gaps=[],
            meeting_expectations=["All"],
            integrity_flags=[]
        )
        
        with patch("app.agents.report_generation.ReportGenerationAgent.generate_report", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = expected_report
            
            result = await generate_report(
                match_analysis={},
                transcript="",
                question_scores=[],
                telemetry_summary=""
            )
            
            assert result == expected_report
            mock_method.assert_called_once()
