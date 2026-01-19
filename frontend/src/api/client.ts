/**
 * API client for AI Interviewer backend
 */

export interface Interview {
    id: number;
    status: string;
    target_questions: number;
    difficulty_start: number;
    match_score?: number; // From list endpoint
    interview_score?: number; // From list endpoint
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

export interface CostBreakdown {
    interview_id: number;
    total_cost: number;
    total_tokens: number;
    cache_hits: number;
    cache_misses: number;
    cache_hit_rate: number;
    by_agent: Record<string, {
        calls: number;
        tokens: number;
        cost: number;
        cached: number;
    }>;
}

export interface CostStatistics {
    total_cost: number;
    total_tokens: number;
    total_calls: number;
    cache_hits: number;
    cache_misses: number;
    cache_hit_rate: number;
}

export interface CacheStats {
    size: number;
    max_size: number;
    hits: number;
    misses: number;
    total_requests: number;
    hit_rate: number;
    default_ttl: number;
}

class ApiClient {
    private baseUrl: string;

    constructor() {
        this.baseUrl = import.meta.env?.VITE_API_URL || '/api';
    }

    private getAuthToken(): string | null {
        return localStorage.getItem('auth_token');
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;

        // Get auth token and add to headers if available
        const token = this.getAuthToken();
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...(options.headers as Record<string, string> || {}),
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (!response.ok) {
            // Handle 401 Unauthorized
            if (response.status === 401) {
                localStorage.removeItem('auth_token');
                window.location.href = '/login';
            }

            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        if (response.status === 204) {
            return {} as T;
        }

        return response.json();
    }

    // Authentication endpoints
    async login(username: string, password: string): Promise<{ access_token: string; token_type: string }> {
        return this.request<{ access_token: string; token_type: string }>('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
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
        const token = this.getAuthToken();

        const headers: Record<string, string> = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData,
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('auth_token');
                window.location.href = '/login';
            }

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

    async deleteInterview(id: number): Promise<void> {
        return this.request<void>(`/interviews/${id}`, {
            method: 'DELETE',
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

    async getInterviewCosts(id: number): Promise<CostBreakdown> {
        return this.request<CostBreakdown>(`/interviews/${id}/costs`);
    }

    async getCostStatistics(): Promise<CostStatistics> {
        return this.request<CostStatistics>('/interviews/stats/costs');
    }

    async getCacheStats(): Promise<CacheStats> {
        return this.request<CacheStats>('/interviews/cache/stats');
    }

    // Health check
    async healthCheck(): Promise<{ status: string }> {
        return this.request<{ status: string }>('/health');
    }
}

export const apiClient = new ApiClient();
