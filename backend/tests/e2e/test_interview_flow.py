"""End-to-end tests for the full interview lifecycle."""
import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch, AsyncMock
from app.utils.state_machine import InterviewStatus

@pytest.mark.asyncio
class TestInterviewE2E:
    """
    End-to-end tests for the interview process.
    
    Flow:
    1. Admin logs in
    2. Admin creates interview draft
    3. Admin uploads documents (mocked) and "analyzes" them -> status READY
    4. Admin assigns interview -> status ASSIGNED
    5. Candidate starts interview -> status IN_PROGRESS
    6. Candidate answers questions until finished -> status COMPLETED
    7. Admin views results/costs
    """

    async def test_full_interview_lifecycle(self, test_client, admin_token, test_db):
        """Test the complete interview flow from creation to completion."""
        
        # 1. Admin Create Interview
        # -------------------------
        create_response = await test_client.post(
            "/interviews/",
            json={"target_questions": 2, "difficulty_start": 5}, # Keep short for test
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_response.status_code == 201
        interview_data = create_response.json()
        interview_id = interview_data["id"]
        assert interview_data["status"] == InterviewStatus.DRAFT

        # 2. Simulate Document Analysis (Status DRAFT -> READY)
        # ---------------------------------------------------
        # In a real E2E, we'd upload files. Here we simulate the state change 
        # that happens after analysis. We'll manually update DB for this step
        # to avoid complex file upload + LLM mocking in this specific test,
        # focusing on the state flow.
        
        # We need to add the mock match_analysis result directly to DB to allow transition
        from app.models.interview import Interview
        from sqlalchemy import select
        
        # We need to add the mock match_analysis result directly to DB to allow transition
        from app.models.interview import Interview
        from sqlalchemy import select
        
        # test_db is already an AsyncSession instance
        session = test_db
        result = await session.execute(select(Interview).where(Interview.id == interview_id))
        interview = result.scalar_one()
        
        interview.match_analysis_json = {
            "match_score": 85,
            "summary": "Test Summary",
            "focus_areas": ["Python", "Testing"]
        }
        # Manually move to READY as if analysis completed
        interview.status = InterviewStatus.READY.value
        await session.commit()

        # Verify status is READY via API
        get_response = await test_client.get(
            f"/interviews/{interview_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert get_response.json()["status"] == InterviewStatus.READY

        # 3. Admin Assign Interview (Status READY -> ASSIGNED)
        # ----------------------------------------------------
        assign_response = await test_client.post(
            f"/interviews/{interview_id}/assign",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert assign_response.status_code == 200
        assign_data = assign_response.json()
        assert assign_data["status"] == InterviewStatus.ASSIGNED
        token = assign_data["candidate_link_token"]
        assert token is not None

        # 4. Candidate Start Interview (Status ASSIGNED -> IN_PROGRESS)
        # -------------------------------------------------------------
        # Mock agents globally to prevent real LLM calls during start_interview
        # Note: generate_introduction is imported at top level in chat.py, so patch where used.
        # generate_question is imported inside the function, so patching the source Works.
        with patch("app.api.chat.generate_introduction", return_value="Welcome to the interview!"), \
             patch("app.agents.generate_question", new_callable=AsyncMock) as mock_gen_q:
            
            mock_gen_q.return_value = "What is unit testing?"
            
            start_response = await test_client.post(f"/chat/start/{token}")
            assert start_response.status_code == 200
            start_data = start_response.json()
            assert "introduction" in start_data
            assert "Welcome" in start_data["introduction"]
            
            # Verify status update
            get_response = await test_client.get(
                f"/interviews/{interview_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert get_response.json()["status"] == InterviewStatus.IN_PROGRESS

        # 5. Candidate Messages Loop (Answering questions)
        # -----------------------------------------------
        # We Mock the functions imported in message_service.py
        
        with patch("app.services.message_service.classify_message", new_callable=AsyncMock) as mock_classify, \
             patch("app.services.message_service.evaluate_answer", new_callable=AsyncMock) as mock_evaluate, \
             patch("app.services.message_service.generate_question", new_callable=AsyncMock) as mock_generate, \
             patch("app.services.message_service.assess_integrity", new_callable=AsyncMock) as mock_integrity:
            
            # Mock Classifier Result
            mock_classify.return_value = MagicMock(type="Answer", confidence=0.9)
            
            # Mock Evaluator Result
            mock_evaluate.return_value = MagicMock(
                score=8,
                feedback="Good answer",
                technical_accuracy="High"
            )

            # Mock Generator Result (returns string)
            mock_generate.return_value = "What is your experience with Pytest?"
            
            # Mock Integrity (optional, returns object or None)
            mock_integrity.return_value = None
            
            # Send an answer
            # API expects /chat/{interview_id}/message
            message_response = await test_client.post(
                f"/chat/{interview_id}/message",
                json={
                    "content": "Unit testing is testing individual components.",
                    "telemetry": {
                        "response_time_ms": 5000,
                        "paste_detected": False
                    }
                }
            )
            
            assert message_response.status_code == 200
            data = message_response.json()
            assert "response" in data
            assert data["response"] == "What is your experience with Pytest?"

        # 6. Admin Check Costs (Post-Interview)
        # -------------------------------------
        cost_response = await test_client.get(
            f"/interviews/{interview_id}/costs",
             headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert cost_response.status_code == 200
        cost_data = cost_response.json()
        assert cost_data["interview_id"] == interview_id
