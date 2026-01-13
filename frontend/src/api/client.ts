/**
 * API client for AI Interviewer backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Interview {
    id: number;
    status: string;
    target_questions: number;
    difficulty_start: number;
    match_analysis_json?: {
        match_score: number;
        match_summary: string;
        focus_areas: string[];
    };
    candidate_link_token?: string;
    report_json?: {
        interview_score: number;
        summary: string;
        gaps: string[];
        meeting_expectations: string[];
        integrity_flags: Array<{
            severity: string;
            description: string;
            evidence: string;
        }>;
    };
    created_at: string;
    updated_at: string;
}

export interface Message {
    id: number;
    interview_id: number;
    role: 'assistant' | 'candidate';
    content: string;
    timestamp: string;
    question_number?: number;
    answer_quality_score?: number;
    cheat_certainty?: number;
}

export interface CreateInterviewRequest {
    target_questions: number;
    difficulty_start: number;
}

export interface SendMessageRequest {
    content: string;
    telemetry: {
        response_time_ms: number;
        paste_detected: boolean;
    };
}

export interface SendMessageResponse {
    response: string;
    interview_complete: boolean;
    evaluation?: {
        score: number;
        rationale: string;
        evidence: string;
        followup_hint?: string;
    };
    next_question_number?: number;
}

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    // Interview endpoints
    async createInterview(data: CreateInterviewRequest): Promise<Interview> {
        return this.request<Interview>('/interviews/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    async listInterviews(): Promise<Interview[]> {
        return this.request<Interview[]>('/interviews/');
    }

    async getInterview(id: number): Promise<Interview> {
        return this.request<Interview>(`/interviews/${id}`);
    }

    async uploadDocuments(
        id: number,
        resume: File,
        roleDescription: File,
        jobOffering: File
    ): Promise<Interview> {
        const formData = new FormData();
        formData.append('resume', resume);
        formData.append('role_description', roleDescription);
        formData.append('job_offering', jobOffering);

        const url = `${this.baseUrl}/interviews/${id}/upload`;
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    }

    async assignInterview(id: number): Promise<Interview> {
        return this.request<Interview>(`/interviews/${id}/assign`, {
            method: 'POST',
        });
    }

    async completeInterview(id: number): Promise<Interview> {
        return this.request<Interview>(`/interviews/${id}/complete`, {
            method: 'POST',
        });
    }

    // Chat endpoints
    async startInterview(token: string): Promise<{
        interview_id: number;
        introduction: string;
        first_question: string;
    }> {
        return this.request(`/chat/start/${token}`, {
            method: 'POST',
        });
    }

    async getMessages(interviewId: number): Promise<Message[]> {
        return this.request<Message[]>(`/chat/${interviewId}/messages`);
    }

    async sendMessage(
        interviewId: number,
        data: SendMessageRequest
    ): Promise<SendMessageResponse> {
        return this.request<SendMessageResponse>(`/chat/${interviewId}/message`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // Health check
    async healthCheck(): Promise<{ status: string }> {
        return this.request<{ status: string }>('/health');
    }
}

export const apiClient = new ApiClient();
