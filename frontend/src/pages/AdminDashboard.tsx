import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient, Interview } from '../api/client';

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [interviews, setInterviews] = useState<Interview[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState<string>('ALL');

    useEffect(() => {
        loadInterviews();
    }, []);

    const loadInterviews = async () => {
        setLoading(true);
        try {
            const data = await apiClient.listInterviews();
            setInterviews(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load interviews');
        } finally {
            setLoading(false);
        }
    };

    const filteredInterviews =
        filter === 'ALL'
            ? interviews
            : interviews.filter((interview) => interview.status === filter);

    const statusCounts = {
        ALL: interviews.length,
        DRAFT: interviews.filter((i) => i.status === 'DRAFT').length,
        READY: interviews.filter((i) => i.status === 'READY').length,
        ASSIGNED: interviews.filter((i) => i.status === 'ASSIGNED').length,
        IN_PROGRESS: interviews.filter((i) => i.status === 'IN_PROGRESS').length,
        COMPLETED: interviews.filter((i) => i.status === 'COMPLETED').length,
    };

    const statusColors = {
        DRAFT: 'bg-gray-500',
        READY: 'bg-blue-500',
        ASSIGNED: 'bg-yellow-500',
        IN_PROGRESS: 'bg-purple-500',
        COMPLETED: 'bg-green-500',
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
                <div className="text-white text-xl">Loading...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-4xl font-bold text-white mb-2">Interview Dashboard</h1>
                        <p className="text-purple-200">Manage and monitor all interviews</p>
                    </div>
                    <button
                        onClick={() => navigate('/admin/create')}
                        className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200"
                    >
                        + Create Interview
                    </button>
                </div>

                {error && (
                    <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-6 py-4 rounded-lg mb-6">
                        {error}
                    </div>
                )}

                {/* Statistics */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
                    {Object.entries(statusCounts).map(([status, count]) => (
                        <button
                            key={status}
                            onClick={() => setFilter(status)}
                            className={`bg-white/10 backdrop-blur-lg rounded-xl p-4 border transition-all duration-200 ${filter === status
                                    ? 'border-purple-500 ring-2 ring-purple-500'
                                    : 'border-white/20 hover:border-white/40'
                                }`}
                        >
                            <div className="text-3xl font-bold text-white mb-1">{count}</div>
                            <div className="text-sm text-purple-200">{status.replace('_', ' ')}</div>
                        </button>
                    ))}
                </div>

                {/* Interviews List */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-white/5 border-b border-white/20">
                                <tr>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        ID
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Status
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Match Score
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Questions
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Created
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/10">
                                {filteredInterviews.length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-12 text-center text-white/50">
                                            No interviews found
                                        </td>
                                    </tr>
                                ) : (
                                    filteredInterviews.map((interview) => (
                                        <tr
                                            key={interview.id}
                                            className="hover:bg-white/5 transition-colors cursor-pointer"
                                            onClick={() => navigate(`/admin/interviews/${interview.id}`)}
                                        >
                                            <td className="px-6 py-4 text-white font-mono">#{interview.id}</td>
                                            <td className="px-6 py-4">
                                                <span
                                                    className={`px-3 py-1 rounded-full text-white text-sm font-semibold ${statusColors[interview.status as keyof typeof statusColors]
                                                        }`}
                                                >
                                                    {interview.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-white">
                                                {interview.match_analysis_json ? (
                                                    <div className="flex items-center">
                                                        <span className="font-semibold">
                                                            {interview.match_analysis_json.match_score}/10
                                                        </span>
                                                        <div className="ml-3 w-20 bg-white/20 rounded-full h-2">
                                                            <div
                                                                className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                                                                style={{
                                                                    width: `${(interview.match_analysis_json.match_score / 10) * 100
                                                                        }%`,
                                                                }}
                                                            />
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <span className="text-white/50">-</span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 text-white">{interview.target_questions}</td>
                                            <td className="px-6 py-4 text-white/80 text-sm">
                                                {new Date(interview.created_at).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4">
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        navigate(`/admin/interviews/${interview.id}`);
                                                    }}
                                                    className="px-4 py-2 bg-purple-500/30 hover:bg-purple-500/50 text-purple-100 rounded-lg transition-colors text-sm font-medium"
                                                >
                                                    View Details
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Empty State */}
                {interviews.length === 0 && !loading && (
                    <div className="text-center py-12">
                        <div className="text-6xl mb-4">📋</div>
                        <h3 className="text-2xl font-bold text-white mb-2">No Interviews Yet</h3>
                        <p className="text-purple-200 mb-6">
                            Create your first interview to get started
                        </p>
                        <button
                            onClick={() => navigate('/admin/create')}
                            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200"
                        >
                            Create Interview
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
