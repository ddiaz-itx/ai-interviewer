"""Interview state machine implementation."""
from enum import Enum


class InterviewStatus(str, Enum):
    """Interview status states."""

    DRAFT = "DRAFT"  # Interview created, documents uploaded
    READY = "READY"  # Match analysis complete
    ASSIGNED = "ASSIGNED"  # Candidate link generated
    IN_PROGRESS = "IN_PROGRESS"  # Candidate session active
    COMPLETED = "COMPLETED"  # Report generated


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""

    pass


class InterviewStateMachine:
    """Manages interview state transitions and validation."""

    # Valid state transitions
    TRANSITIONS = {
        InterviewStatus.DRAFT: [InterviewStatus.READY],
        InterviewStatus.READY: [InterviewStatus.ASSIGNED],
        InterviewStatus.ASSIGNED: [InterviewStatus.IN_PROGRESS],
        InterviewStatus.IN_PROGRESS: [InterviewStatus.COMPLETED],
        InterviewStatus.COMPLETED: [],  # Terminal state
    }

    # Preconditions for state transitions
    PRECONDITIONS = {
        InterviewStatus.READY: lambda interview: interview.match_analysis_json is not None,
        InterviewStatus.ASSIGNED: lambda interview: interview.candidate_link_token is not None,
        InterviewStatus.IN_PROGRESS: lambda interview: True,  # No additional preconditions
        InterviewStatus.COMPLETED: lambda interview: interview.report_json is not None,
    }

    @classmethod
    def can_transition(cls, current_status: InterviewStatus, new_status: InterviewStatus) -> bool:
        """Check if transition from current_status to new_status is valid."""
        return new_status in cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def validate_transition(
        cls, interview: "Interview", new_status: InterviewStatus  # type: ignore # noqa: F821
    ) -> None:
        """
        Validate state transition and preconditions.

        Raises:
            StateTransitionError: If transition is invalid or preconditions not met.
        """
        current_status = InterviewStatus(interview.status)

        # Check if transition is valid
        if not cls.can_transition(current_status, new_status):
            raise StateTransitionError(
                f"Invalid transition from {current_status} to {new_status}. "
                f"Valid transitions: {cls.TRANSITIONS.get(current_status, [])}"
            )

        # Check preconditions
        precondition = cls.PRECONDITIONS.get(new_status)
        if precondition and not precondition(interview):
            raise StateTransitionError(
                f"Preconditions not met for transition to {new_status}"
            )

    @classmethod
    def transition(
        cls, interview: "Interview", new_status: InterviewStatus  # type: ignore # noqa: F821
    ) -> None:
        """
        Transition interview to new status after validation.

        Raises:
            StateTransitionError: If transition is invalid.
        """
        cls.validate_transition(interview, new_status)
        interview.status = new_status.value
