import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

export default function CreateInterview() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        targetQuestions: 5,
        difficultyStart: 5,
    });
    const [files, setFiles] = useState<{
        resume: File | null;
        roleDescription: File | null;
        jobOffering: File | null;
    }>({
        resume: null,
        roleDescription: null,
        jobOffering: null,
    });
    const [step, setStep] = useState<'config' | 'upload' | 'analyzing'>('config');
    const [interviewId, setInterviewId] = useState<number | null>(null);

    const handleCreateInterview = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const interview = await apiClient.createInterview({
                target_questions: formData.targetQuestions,
                difficulty_start: formData.difficultyStart,
            });

            setInterviewId(interview.id);
            setStep('upload');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create interview');
        } finally {
            setLoading(false);
        }
    };

    const handleUploadDocuments = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!files.resume || !files.roleDescription || !files.jobOffering) {
            setError('Please select all required files');
            return;
        }

        if (!interviewId) {
            setError('No interview ID found');
            return;
        }

        setLoading(true);
        setError(null);
        setStep('analyzing');

        try {
            const interview = await apiClient.uploadDocuments(
                interviewId,
                files.resume,
                files.roleDescription,
                files.jobOffering
            );

            // Navigate to interview details page
            navigate(`/admin/interviews/${interview.id}`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to upload documents');
            setStep('upload');
        } finally {
            setLoading(false);
        }
    };

    const handleFileChange = (field: 'resume' | 'roleDescription' | 'jobOffering') => (
        e: React.ChangeEvent<HTMLInputElement>
    ) => {
        const file = e.target.files?.[0] || null;
        setFiles((prev) => ({ ...prev, [field]: file }));
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
            <div className="max-w-2xl mx-auto">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
                    <h1 className="text-3xl font-bold text-white mb-2">Create New Interview</h1>
                    <p className="text-purple-200 mb-8">
                        Configure interview settings and upload required documents
                    </p>

                    {/* Progress Steps */}
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center ${step === 'config'
                                        ? 'bg-purple-500 text-white'
                                        : 'bg-green-500 text-white'
                                    }`}
                            >
                                {step === 'config' ? '1' : '✓'}
                            </div>
                            <span className="ml-2 text-white font-medium">Configure</span>
                        </div>

                        <div className="flex-1 h-1 mx-4 bg-white/20">
                            <div
                                className={`h-full bg-purple-500 transition-all duration-500 ${step !== 'config' ? 'w-full' : 'w-0'
                                    }`}
                            />
                        </div>

                        <div className="flex items-center">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center ${step === 'upload'
                                        ? 'bg-purple-500 text-white'
                                        : step === 'analyzing'
                                            ? 'bg-green-500 text-white'
                                            : 'bg-white/20 text-white/50'
                                    }`}
                            >
                                {step === 'analyzing' ? '✓' : '2'}
                            </div>
                            <span
                                className={`ml-2 font-medium ${step !== 'config' ? 'text-white' : 'text-white/50'
                                    }`}
                            >
                                Upload
                            </span>
                        </div>

                        <div className="flex-1 h-1 mx-4 bg-white/20">
                            <div
                                className={`h-full bg-purple-500 transition-all duration-500 ${step === 'analyzing' ? 'w-full' : 'w-0'
                                    }`}
                            />
                        </div>

                        <div className="flex items-center">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center ${step === 'analyzing'
                                        ? 'bg-purple-500 text-white'
                                        : 'bg-white/20 text-white/50'
                                    }`}
                            >
                                3
                            </div>
                            <span
                                className={`ml-2 font-medium ${step === 'analyzing' ? 'text-white' : 'text-white/50'
                                    }`}
                            >
                                Analyze
                            </span>
                        </div>
                    </div>

                    {error && (
                        <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-6">
                            {error}
                        </div>
                    )}

                    {/* Step 1: Configuration */}
                    {step === 'config' && (
                        <form onSubmit={handleCreateInterview} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-purple-200 mb-2">
                                    Number of Questions
                                </label>
                                <input
                                    type="number"
                                    min="3"
                                    max="20"
                                    value={formData.targetQuestions}
                                    onChange={(e) =>
                                        setFormData((prev) => ({
                                            ...prev,
                                            targetQuestions: parseInt(e.target.value),
                                        }))
                                    }
                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    required
                                />
                                <p className="mt-1 text-sm text-purple-300">
                                    Recommended: 5-10 questions for a thorough interview
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-purple-200 mb-2">
                                    Starting Difficulty (1-10)
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    max="10"
                                    step="0.5"
                                    value={formData.difficultyStart}
                                    onChange={(e) =>
                                        setFormData((prev) => ({
                                            ...prev,
                                            difficultyStart: parseFloat(e.target.value),
                                        }))
                                    }
                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                    required
                                />
                                <p className="mt-1 text-sm text-purple-300">
                                    1 = Basic, 5 = Intermediate, 10 = Expert
                                </p>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Creating...' : 'Continue to Upload'}
                            </button>
                        </form>
                    )}

                    {/* Step 2: Document Upload */}
                    {step === 'upload' && (
                        <form onSubmit={handleUploadDocuments} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-purple-200 mb-2">
                                    Candidate Resume (PDF)
                                </label>
                                <input
                                    type="file"
                                    accept=".pdf"
                                    onChange={handleFileChange('resume')}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-500 file:text-white hover:file:bg-purple-600"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-purple-200 mb-2">
                                    Role Description (PDF)
                                </label>
                                <input
                                    type="file"
                                    accept=".pdf"
                                    onChange={handleFileChange('roleDescription')}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-500 file:text-white hover:file:bg-purple-600"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-purple-200 mb-2">
                                    Job Offering (PDF)
                                </label>
                                <input
                                    type="file"
                                    accept=".pdf"
                                    onChange={handleFileChange('jobOffering')}
                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-purple-500 file:text-white hover:file:bg-purple-600"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Uploading...' : 'Upload & Analyze'}
                            </button>
                        </form>
                    )}

                    {/* Step 3: Analyzing */}
                    {step === 'analyzing' && (
                        <div className="text-center py-12">
                            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mb-4"></div>
                            <h3 className="text-xl font-semibold text-white mb-2">
                                Analyzing Documents...
                            </h3>
                            <p className="text-purple-200">
                                Our AI is analyzing the candidate-role match. This may take a moment.
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
