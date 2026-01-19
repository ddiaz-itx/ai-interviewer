import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient, Interview, CostStatistics } from '../api/client';

type SortField = 'id' | 'created_at';
type SortDirection = 'asc' | 'desc';

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [interviews, setInterviews] = useState<Interview[]>([]);
    const [costStats, setCostStats] = useState<CostStatistics | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [statusFilter, setStatusFilter] = useState<string>('ALL');
    const [sortField, setSortField] = useState<SortField>('created_at');
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

    useEffect(() => {
        loadInterviews();
    }, []);

    const loadInterviews = async () => {
        setLoading(true);
        try {
            const data = await apiClient.listInterviews();
            setInterviews(data);

            // Load cost statistics
            try {
                const costs = await apiClient.getCostStatistics();
                setCostStats(costs);
            } catch (err) {
                console.error('Failed to load cost stats:', err);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load interviews');
        } finally {
            setLoading(false);
        }
    };

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            // Toggle direction if same field
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
        } else {
            // New field, default to descending
            setSortField(field);
            setSortDirection('desc');
        }
    };

    const handleDelete = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation();
        if (window.confirm('Are you sure you want to delete this interview? This action cannot be undone.')) {
            try {
                await apiClient.deleteInterview(id);
                setInterviews(interviews.filter(i => i.id !== id));
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to delete interview');
            }
        }
    };

    const filteredInterviews = statusFilter === 'ALL'
        ? interviews
        : interviews.filter((i) => i.status === statusFilter);

    // Sort interviews
    const sortedInterviews = [...filteredInterviews].sort((a, b) => {
        let comparison = 0;

        if (sortField === 'id') {
            comparison = a.id - b.id;
        } else if (sortField === 'created_at') {
            comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        }

        return sortDirection === 'asc' ? comparison : -comparison;
    });

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
                    {costStats && (
                        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
                            <div className="text-sm text-purple-200 mb-1">Total API Cost</div>
                            <div className="text-2xl font-bold text-white">${costStats.total_cost.toFixed(4)}</div>
                            <div className="text-xs text-purple-300 mt-1">
                                {costStats.total_tokens.toLocaleString()} tokens | {costStats.cache_hit_rate}% cached
                            </div>
                        </div>
                    )}
                    <button
                        onClick={() => navigate('/admin/create')}
                        className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 font-semibold shadow-lg"
                    >
                        + Create Interview
                    </button>
                </div>

                {error && (
                    <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-6 py-4 rounded-lg mb-6">
                        {error}
                    </div>
                )}

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
                    {(Object.keys(statusCounts) as Array<keyof typeof statusCounts>).map((status) => (
                        <button
                            key={status}
                            onClick={() => setStatusFilter(status)}
                            className={`flex-1 px-6 py-4 rounded-xl transition-all duration-200 ${statusFilter === status
                                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg scale-105'
                                : 'bg-white/5 text-white/70 hover:bg-white/10'
                                }`}
                        >
                            <div className="text-3xl font-bold mb-1">{statusCounts[status]}</div>
                            <div className="text-sm font-medium">{status}</div>
                        </button>
                    ))}
                </div>

                {/* Interviews List */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-white/5 border-b border-white/20">
                                <tr>
                                    <th
                                        className="px-6 py-4 text-left text-sm font-semibold text-purple-200 cursor-pointer hover:text-purple-100 select-none"
                                        onClick={() => handleSort('id')}
                                    >
                                        <div className="flex items-center gap-2">
                                            ID
                                            {sortField === 'id' && (
                                                <span className="text-xs">
                                                    {sortDirection === 'asc' ? '↑' : '↓'}
                                                </span>
                                            )}
                                        </div>
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Status
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Match Score
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Final Score
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Questions
                                    </th>
                                    <th
                                        className="px-6 py-4 text-left text-sm font-semibold text-purple-200 cursor-pointer hover:text-purple-100 select-none"
                                        onClick={() => handleSort('created_at')}
                                    >
                                        <div className="flex items-center gap-2">
                                            Created
                                            {sortField === 'created_at' && (
                                                <span className="text-xs">
                                                    {sortDirection === 'asc' ? '↑' : '↓'}
                                                </span>
                                            )}
                                        </div>
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-purple-200">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/10">
                                {filteredInterviews.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} className="px-6 py-12 text-center text-white/50">
                                            No interviews found
                                        </td>
                                    </tr>
                                ) : (
                                    sortedInterviews.map((interview) => (
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
                                                {interview.match_score ? (
                                                    <div className="flex items-center">
                                                        <span className="font-semibold">
                                                            {interview.match_score}/10
                                                        </span>
                                                        <div className="ml-3 w-20 bg-white/20 rounded-full h-2">
                                                            <div
                                                                className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                                                                style={{
                                                                    width: `${(interview.match_score / 10) * 100}%`,
                                                                }}
                                                            />
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <span className="text-white/50">-</span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 text-white">
                                                {interview.interview_score ? (
                                                    <div className="flex items-center">
                                                        <span className="font-semibold">
                                                            {interview.interview_score}/10
                                                        </span>
                                                        <div className="ml-3 w-20 bg-white/20 rounded-full h-2">
                                                            <div
                                                                className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full"
                                                                style={{
                                                                    width: `${(interview.interview_score / 10) * 100}%`,
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
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            navigate(`/admin/interviews/${interview.id}`);
                                                        }}
                                                        className="px-4 py-2 bg-purple-500/30 hover:bg-purple-500/50 text-purple-100 rounded-lg transition-colors text-sm font-medium"
                                                    >
                                                        View Details
                                                    </button>
                                                    <button
                                                        onClick={(e) => handleDelete(e, interview.id)}
                                                        className="px-4 py-2 bg-red-500/30 hover:bg-red-500/50 text-red-100 rounded-lg transition-colors text-sm font-medium"
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
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
