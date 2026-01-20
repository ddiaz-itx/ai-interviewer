# LangChain Agents & Prompts Specification

## 1. Document Analysis Agent

**Trigger**: When Admin uploads Resume + Role Description.

**Input**: `resume_text`, `role_description_text`.

**Output Schema (Pydantic)**:
```python
class MatchAnalysis(BaseModel):
    match_score: int = Field(..., description="1-10 score of fit")
    match_summary: str = Field(..., description="Short explanation of score")
    focus_areas: List[str] = Field(..., description="Top 3-5 areas to probe in interview")
```

**Goal**: Analyze fit and determine what to ask.

---

## 2. Answer Evaluation Agent

**Trigger**: Every time the candidate sends a message (Answer).

**Input**: `current_question`, `candidate_answer`, `rubric`.

**Output Schema**:
```python
class AnswerEvaluation(BaseModel):
    score: int = Field(..., description="1-10 quality score")
    rationale: str = Field(..., description="Why this score was given")
    evidence: str = Field(..., description="Quote from the answer supporting the score")
    followup_hint: Optional[str] = Field(None, description="Idea for the next question")
```

**Rubric Guidelines**: Assess technical correctness, problem-solving, and communication.

---

## 3. Question Generation Agent

**Trigger**: After answer evaluation, if the interview is not over.

**Input**: `focus_areas`, `chat_history`, `current_difficulty` (3-10).

**Logic**:
- If previous answer score >= 7, increase difficulty by 0.5.
- If previous answer score <= 4, decrease difficulty by 0.5.
- Generate a question that targets a remaining `focus_area`.

---

## 4. Report Generation Agent

**Trigger**: When the interview loop finishes.

**Input**: Full `chat_transcript`, `match_analysis`.

**Output Schema**:
```python
class FinalReport(BaseModel):
    interview_score: int = Field(..., description="Overall 1-10 score")
    summary: str = Field(..., description="Performance summary")
    gaps: List[str] = Field(..., description="Areas needing improvement")
    meeting_expectations: List[str] = Field(..., description="Areas meeting expectations")
    integrity_flags: List[str] = Field(..., description="List of suspicious behaviors")
```

---
 
 ## 5. Message Classification Agent
 
 **Trigger**: On every candidate message.
 
 **Input**: `message`.
 
 **Goal**: Classify message as `ANSWER`, `CLARIFICATION`, or `GREETING` to determine flow.
 
 ---
 
 ## 6. Integrity Judgment Agent
 
 **Trigger**: After every answer.
 
 **Input**: `question`, `answer`.
 
 **Logic**:
 - Checks for suspicious patterns (e.g., pasting large blocks of text, unnatural phrasing).
 - Tracks response time (telemetry).
 
 **Output Schema**:
 ```python
 class IntegrityCheck(BaseModel):
     is_suspicious: bool
     flags: List[str]
     confidence: float
 ```
