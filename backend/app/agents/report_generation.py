"""Report Generation Agent - creates final interview reports."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.agents.base import BaseAgent
from app.agents.llm_factory import get_llm
from app.agents.prompts import REPORT_GENERATION_PROMPT
from app.schemas.interview import FinalReport


class ReportGenerationAgent(BaseAgent):
    """Agent for generating final interview reports."""

    def __init__(self):
        """Initialize the report generation agent."""
        super().__init__(agent_name="report_generation")
        self.llm = get_llm(temperature=0.0)  # Deterministic for consistency
        self.parser = PydanticOutputParser(pydantic_object=FinalReport)

    async def generate_report(
        self,
        match_analysis: dict,
        transcript: str,
        question_scores: list[dict],
        telemetry_summary: str,
        db: Optional[AsyncSession] = None,
        interview_id: Optional[int] = None,
    ) -> FinalReport:
        """
        Generate a final interview report.

        Args:
            match_analysis: Initial match analysis results
            transcript: Full interview transcript
            question_scores: List of per-question scores and evaluations
            telemetry_summary: Summary of telemetry data (paste events, response times)
            db: Database session for cost tracking
            interview_id: Interview ID for cost tracking

        Returns:
            FinalReport with score, summary, gaps, and integrity flags
        """
        # Validate inputs
        self.validate_inputs(transcript=transcript, telemetry_summary=telemetry_summary)

        # Create the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert technical recruiter creating interview reports."),
                (
                    "human",
                    REPORT_GENERATION_PROMPT
                    + "\n\n{format_instructions}\n\nProvide your report:",
                ),
            ]
        )

        # Create the chain
        chain = prompt | self.llm | self.parser

        # Format the data
        match_analysis_str = (
            f"Match Score: {match_analysis.get('match_score')}/10\n"
            f"Summary: {match_analysis.get('match_summary')}\n"
            f"Focus Areas: {', '.join(match_analysis.get('focus_areas', []))}"
        )

        question_scores_str = "\n".join(
            [
                f"Q{i+1}: Score {score.get('score', 'N/A')}/10 - {score.get('rationale', 'N/A')}"
                for i, score in enumerate(question_scores)
            ]
        )

        inputs = {
            "match_analysis": match_analysis_str,
            "transcript": transcript,
            "question_scores": question_scores_str,
            "telemetry_summary": telemetry_summary,
            "format_instructions": self.parser.get_format_instructions(),
        }

        # Execute report generation
        result = await self.invoke_with_retry_async(
            chain=chain,
            inputs=inputs,
            model=getattr(self.llm, "model_name", "unknown"),
            temperature=0.0,
            db=db,
            interview_id=interview_id,
        )

        return result


# Convenience function
async def generate_report(
    match_analysis: dict,
    transcript: str,
    question_scores: list[dict],
    telemetry_summary: str = "",
    db: Optional[AsyncSession] = None,
    interview_id: Optional[int] = None,
) -> FinalReport:
    """
    Generate final interview report.

    Args:
        match_analysis: Match analysis data
        transcript: Full transcript
        question_scores: Per-question scores
        telemetry_summary: Telemetry summary
        db: Database session
        interview_id: Interview ID

    Returns:
        FinalReport object
    """
    agent = ReportGenerationAgent()
    return await agent.generate_report(
        match_analysis, transcript, question_scores, telemetry_summary, db, interview_id
    )
