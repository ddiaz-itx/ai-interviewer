import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient, Interview, CostBreakdown } from '../api/client';

export default function InterviewDetails() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [interview, setInterview] = useState<Interview | null>(null);
    const [costs, setCosts] = useState<CostBreakdown | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [assigning, setAssigning] = useState(false);
    const [completing, setCompleting] = useState(false);

    useEffect(() => {
        loadInterview();
    }, [id]);

    const loadInterview = async () => {
        if (!id) return;

        setLoading(true);
        try {
            const data = await apiClient.getInterview(parseInt(id));
            setInterview(data);

            // Load costs if interview is completed or in progress
            if (data.status === 'COMPLETED' || data.status === 'IN_PROGRESS') {
                try {
                    const costData = await apiClient.getInterviewCosts(parseInt(id));
                    setCosts(costData);
                } catch (err) {
                    console.error('Failed to load costs:', err);
                }
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load interview');
        } finally {
            setLoading(false);
        }
    };

    const handleAssign = async () => {
        if (!id) return;

        setAssigning(true);
        try {
            const updated = await apiClient.assignInterview(parseInt(id));
            setInterview(updated);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to assign interview');
        } finally {
            setAssigning(false);
        }
    };

    const handleComplete = async () => {
        if (!id) return;

        setCompleting(true);
        try {
            const updated = await apiClient.completeInterview(parseInt(id));
            setInterview(updated);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to complete interview');
        } finally {
            setCompleting(false);
        }
    };

    const copyLinkToClipboard = () => {
        if (!interview?.candidate_link_token) return;

        const link = `${window.location.origin}/interview/${interview.candidate_link_token}`;
        navigator.clipboard.writeText(link);
        alert('Candidate link copied to clipboard!');
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
                <div className="text-white text-xl">Loading...</div>
            </div>
        );
    }

    if (error || !interview) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
                <div className="max-w-4xl mx-auto bg-red-500/20 border border-red-500/50 text-red-200 px-6 py-4 rounded-lg">
                    {error || 'Interview not found'}
                </div>
            </div>
        );
    }

    const statusColors = {
        DRAFT: 'bg-gray-500',
        READY: 'bg-blue-500',
        ASSIGNED: 'bg-yellow-500',
        IN_PROGRESS: 'bg-purple-500',
        COMPLETED: 'bg-green-500',
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20 mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <h1 className="text-3xl font-bold text-white">Interview #{interview.id}</h1>
                        <span
                            className={`px-4 py-2 rounded-full text-white font-semibold ${statusColors[interview.status as keyof typeof statusColors]
                                }`}
                        >
                            {interview.status}
                        </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-white/80">
                        <div>
                            <span className="text-purple-300">Target Questions:</span>{' '}
                            <span className="font-semibold">{interview.target_questions}</span>
                        </div>
                        <div>
                            <span className="text-purple-300">Difficulty:</span>{' '}
                            <span className="font-semibold">{interview.difficulty_start}/10</span>
                        </div>
                        <div>
                            <span className="text-purple-300">Created:</span>{' '}
                            <span className="font-semibold">
                                {new Date(interview.created_at).toLocaleString()}
                            </span>
                        </div>
                        <div>
                            <span className="text-purple-300">Updated:</span>{' '}
                            <span className="font-semibold">
                                {new Date(interview.updated_at).toLocaleString()}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Match Analysis */}
                {interview.match_analysis_json && (
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20 mb-6">
                        <h2 className="text-2xl font-bold text-white mb-4">Match Analysis</h2>

                        <div className="mb-6">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-purple-200">Match Score</span>
                                <span className="text-3xl font-bold text-white">
                                    {interview.match_analysis_json.match_score}/10
                                </span>
                            </div>
                            <div className="w-full bg-white/20 rounded-full h-3">
                                <div
                                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
                                    style={{
                                        width: `${(interview.match_analysis_json.match_score / 10) * 100}%`,
                                    }}
                                />
                            </div>
                        </div>

                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-purple-200 mb-2">Summary</h3>
                            <p className="text-white/90">{interview.match_analysis_json.match_summary}</p>
                        </div>

                        <div>
                            <h3 className="text-lg font-semibold text-purple-200 mb-2">Focus Areas</h3>
                            <div className="flex flex-wrap gap-2">
                                {interview.match_analysis_json.focus_areas.map((area, index) => (
                                    <span
                                        key={index}
                                        className="px-3 py-1 bg-purple-500/30 border border-purple-500/50 rounded-full text-purple-100 text-sm"
                                    >
                                        {area}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Cost Analysis */}
                {costs && costs.total_cost > 0 && (
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20 mb-6">
                        <h2 className="text-2xl font-bold text-white mb-6">Cost Analysis</h2>

                        {/* Summary Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                                <div className="text-sm text-purple-200 mb-1">Total Cost</div>
                                <div className="text-2xl font-bold text-white">${costs.total_cost.toFixed(6)}</div>
                            </div>
                            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                                <div className="text-sm text-purple-200 mb-1">Total Tokens</div>
                                <div className="text-2xl font-bold text-white">{costs.total_tokens.toLocaleString()}</div>
                            </div>
                            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                                <div className="text-sm text-purple-200 mb-1">Cache Hit Rate</div>
                                <div className="text-2xl font-bold text-green-400">{costs.cache_hit_rate}%</div>
                                <div className="text-xs text-purple-300 mt-1">
                                    {costs.cache_hits} hits / {costs.cache_misses} misses
                                </div>
                            </div>
                        </div>

                        {/* By Agent Breakdown */}
                        {Object.keys(costs.by_agent).length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold text-purple-200 mb-3">By Agent</h3>
                                <div className="space-y-2">
                                    {Object.entries(costs.by_agent).map(([agent, stats]) => (
                                        <div key={agent} className="bg-white/5 rounded-lg p-4 border border-white/10">
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="font-semibold text-white">{agent}</span>
                                                <span className="text-purple-200">${stats.cost.toFixed(6)}</span>
                                            </div>
                                            <div className="grid grid-cols-3 gap-4 text-sm">
                                                <div>
                                                    <span className="text-purple-300">Calls:</span>
                                                    <span className="text-white ml-2">{stats.calls}</span>
                                                </div>
                                                <div>
                                                    <span className="text-purple-300">Tokens:</span>
                                                    <span className="text-white ml-2">{stats.tokens.toLocaleString()}</span>
                                                </div>
                                                <div>
                                                    <span className="text-purple-300">Cached:</span>
                                                    <span className="text-green-400 ml-2">{stats.cached}/{stats.calls}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Candidate Link */}
                {interview.candidate_link_token && (
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20 mb-6">
                        <h2 className="text-2xl font-bold text-white mb-4">Candidate Link</h2>
                        <div className="flex items-center gap-4">
                            <input
                                type="text"
                                value={`${window.location.origin}/interview/${interview.candidate_link_token}`}
                                readOnly
                                className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white"
                            />
                            <button
                                onClick={copyLinkToClipboard}
                                className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white font-semibold rounded-lg transition-colors"
                            >
                                Copy Link
                            </button>
                        </div>
                    </div>
                )}

                {/* Final Report */}
                {interview.report_json && (
                    <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20 mb-6">
                        <h2 className="text-2xl font-bold text-white mb-4">Final Report</h2>

                        <div className="mb-6">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-purple-200">Interview Score</span>
                                <span className="text-3xl font-bold text-white">
                                    {interview.report_json.interview_score}/10
                                </span>
                            </div>
                        </div>

                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-purple-200 mb-2">Summary</h3>
                            <p className="text-white/90">{interview.report_json.summary}</p>
                        </div>

                        {interview.report_json.meeting_expectations.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-green-300 mb-2">
                                    ✓ Meeting Expectations
                                </h3>
                                <ul className="list-disc list-inside text-white/90 space-y-1">
                                    {interview.report_json.meeting_expectations.map((item, index) => (
                                        <li key={index}>{item}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {interview.report_json.gaps.length > 0 && (
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold text-yellow-300 mb-2">⚠ Gaps</h3>
                                <ul className="list-disc list-inside text-white/90 space-y-1">
                                    {interview.report_json.gaps.map((item, index) => (
                                        <li key={index}>{item}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {interview.report_json.integrity_flags.length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold text-red-300 mb-2">
                                    🚨 Integrity Flags
                                </h3>
                                <div className="space-y-3">
                                    {interview.report_json.integrity_flags.map((flag, index) => (
                                        <div
                                            key={index}
                                            className="bg-red-500/20 border border-red-500/50 rounded-lg p-4"
                                        >
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="font-semibold text-red-200">
                                                    {flag.severity.toUpperCase()}
                                                </span>
                                            </div>
                                            <p className="text-white/90 mb-2">{flag.description}</p>
                                            <p className="text-sm text-red-200">Evidence: {flag.evidence}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Actions */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
                    <h2 className="text-2xl font-bold text-white mb-4">Actions</h2>
                    <div className="flex gap-4">
                        {interview.status === 'DRAFT' && (
                            <button
                                onClick={() => navigate(`/admin/interviews/${interview.id}/upload`)}
                                className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200"
                            >
                                Upload Documents
                            </button>
                        )}

                        {interview.status === 'READY' && (
                            <button
                                onClick={handleAssign}
                                disabled={assigning}
                                className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 disabled:opacity-50"
                            >
                                {assigning ? 'Assigning...' : 'Assign to Candidate'}
                            </button>
                        )}

                        {interview.status === 'IN_PROGRESS' && (
                            <button
                                onClick={handleComplete}
                                disabled={completing}
                                className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-200 disabled:opacity-50"
                            >
                                {completing ? 'Completing...' : 'Complete Interview'}
                            </button>
                        )}

                        <button
                            onClick={() => navigate('/admin')}
                            className="px-6 py-3 bg-white/10 border border-white/20 text-white font-semibold rounded-lg hover:bg-white/20 transition-colors"
                        >
                            Back to Dashboard
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
