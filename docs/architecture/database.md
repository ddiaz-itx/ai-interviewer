# Database Schema & Data Models

## 1. Enums
**InterviewStatus** [cite: 103-110, 294-298]:
- `DRAFT`: Created, docs uploaded.
- `READY`: Analysis complete, ready for candidate.
- `IN_PROGRESS`: Candidate has started session.
- `COMPLETED`: Finished, report generated.

## 2. Tables

### Table: `interviews`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key [cite: 304] |
| `status` | Enum | Default DRAFT [cite: 305] |
| `resume_text` | Text | Extracted content |
| `role_text` | Text | Extracted content |
| `match_analysis` | JSONB | Stores `MatchAnalysis` object (score, focus areas) [cite: 308] |
| `current_difficulty` | Float | Starts at 5.0 [cite: 310] |
| `final_report` | JSONB | Stores `FinalReport` object [cite: 311] |
| `created_at` | DateTime | |

### Table: `messages`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | UUID | Primary Key [cite: 313] |
| `interview_id` | UUID | FK to interviews [cite: 317] |
| `role` | String | 'assistant' or 'candidate' [cite: 318] |
| `content` | Text | The message text [cite: 319] |
| `question_number` | Int | Nullable (for assistant msgs) [cite: 321] |
| `score` | Int | Nullable (1-10, for candidate msgs) [cite: 323] |
| `difficulty_level` | Float | The difficulty when this msg was sent [cite: 322] |
| `integrity_data` | JSONB | `{ "response_time_ms": 1200, "paste": true }` [cite: 324-326] |
| `timestamp` | DateTime | [cite: 320] |

## 3. Integrity Logic
- **Paste Detection**: Frontend must capture onPaste events and send a boolean flag with the message[cite: 366, 384].
- **Response Time**: Backend calculates `timestamp_received - timestamp_last_sent`[cite: 365].