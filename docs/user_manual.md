# User Manual

Welcome to the AI Interviewer User Manual. This guide explains how to use the application for both Administrators and Candidates.

## For Administrators

### 1. Dashboard Overview
Upon logging in, you will see the **Interview Dashboard**.
- **Metrics**: View total interviews, active sessions, and completed interviews.
- **Cost Summary**: See total estimated costs for LLM usage.
- **Interview List**: A table of all interviews with status, candidate info, and match scores.

### 2. Creating an Interview
1. Click the **"New Interview"** button.
2. **Upload Documents**:
   - **Resume**: The candidate's CV (PDF).
   - **Job Description**: The role requirements (PDF).
3. **Configure Settings**:
   - **Target Questions**: Number of questions to ask (e.g., 5).
   - **Difficulty**: Starting difficulty level (1-10).
4. **Analysis**: The system will analyze the match between the resume and job description, providing a **Match Score** and **Focus Areas**.
5. Click **"Save & Generate Link"**.

### 3. Managing Interviews
- **Assigning**: Copy the generated **Candidate Link** and send it to the candidate.
- **Monitoring**:
  - **In Progress**: You can see when a candidate starts the interview.
  - **Completed**: Once finished, the status changes to `COMPLETED`.
- **Reviewing Results**:
  - Click on an interview to view details.
  - **Transcript**: Read the full chat history.
  - **Report**: View the AI-generated assessment report, including technical score and communication skills.
  - **Cost Analysis**: Check the token usage and cost for that specific interview.

### 4. Cost Tracking
- Navigate to the **Cost Analysis** tab in the dashboard or an interview detail view.
- Monitor your API spending by model (GPT-4 vs. Gemini) and agent type.

---

## For Candidates

### 1. Starting the Interview
1. Click the unique link provided by the recruiter.
2. You will see a welcome screen with an overview of the role and interview process.
3. Click **"Start Interview"** to begin.

### 2. The Interview Process
- **Chat Interface**: The AI interviewer will introduce itself and ask questions one by one.
- **Answering**: Type your answer in the text box and press Enter or Send.
  - *Tip: Be clear and concise. You can ask for clarification if needed.*
- **Feedback**: The AI may ask follow-up questions based on your response.

### 3. Completion
- Once all questions are asked, the AI will conclude the interview.
- You will see a "Thank You" screen.
- You may close the browser window. The results are automatically sent to the recruiter.

---

## Troubleshooting

- **Login Issues**: Ensure you are using the correct admin credentials.
- **Upload Errors**: Make sure PDFs are readable and under the size limit (e.g., 5MB).
- **Interview Stuck**: Refresh the page. The session state is saved automatically.
- **Rate Limit**: If you see a "Too Many Requests" error, wait a minute and try again.
