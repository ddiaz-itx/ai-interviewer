import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient, Message } from '../api/client';

export default function CandidateInterview() {
    const { token } = useParams<{ token: string }>();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [interviewId, setInterviewId] = useState<number | null>(null);
    const [targetQuestions, setTargetQuestions] = useState<number>(0);
    const [messages, setMessages] = useState<Message[]>([]);
    const [currentMessage, setCurrentMessage] = useState('');
    const [sending, setSending] = useState(false);
    const [interviewComplete, setInterviewComplete] = useState(false);
    const [messageStartTime, setMessageStartTime] = useState<number | null>(null);
    const [pasteDetected, setPasteDetected] = useState(false);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        startInterview();
    }, [token]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Track when user starts typing
        if (currentMessage && !messageStartTime) {
            setMessageStartTime(Date.now());
        }
    }, [currentMessage]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const startInterview = async () => {
        if (!token) {
            setError('Invalid interview link');
            setLoading(false);
            return;
        }

        try {
            const response = await apiClient.startInterview(token);
            setInterviewId(response.interview_id);

            // Fetch interview details to get target_questions
            const interview = await apiClient.getInterview(response.interview_id);
            setTargetQuestions(interview.target_questions);

            // Add introduction and first question as messages
            setMessages([
                {
                    id: 0,
                    interview_id: response.interview_id,
                    role: 'assistant',
                    content: response.introduction,
                    timestamp: new Date().toISOString(),
                },
                {
                    id: 1,
                    interview_id: response.interview_id,
                    role: 'assistant',
                    content: response.first_question,
                    timestamp: new Date().toISOString(),
                    question_number: 1,
                },
            ]);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start interview');
        } finally {
            setLoading(false);
        }
    };

    const handlePaste = () => {
        setPasteDetected(true);
        // Allow paste but track it
    };

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!currentMessage.trim() || !interviewId || sending) return;

        const responseTime = messageStartTime ? Date.now() - messageStartTime : 0;

        // Add user message to UI immediately
        const userMessage: Message = {
            id: messages.length,
            interview_id: interviewId,
            role: 'candidate',
            content: currentMessage,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setCurrentMessage('');
        setSending(true);
        setMessageStartTime(null);

        try {
            const response = await apiClient.sendMessage(interviewId, {
                content: currentMessage,
                telemetry: {
                    response_time_ms: responseTime,
                    paste_detected: pasteDetected,
                },
            });

            // Add AI response
            const aiMessage: Message = {
                id: messages.length + 1,
                interview_id: interviewId,
                role: 'assistant',
                content: response.response,
                timestamp: new Date().toISOString(),
                question_number: response.next_question_number,
            };

            setMessages((prev) => [...prev, aiMessage]);

            if (response.interview_complete) {
                setInterviewComplete(true);
            }

            // Reset telemetry
            setPasteDetected(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to send message');
        } finally {
            setSending(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent mb-4"></div>
                    <p className="text-white text-xl">Starting your interview...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-8">
                <div className="max-w-md bg-red-500/20 border border-red-500/50 text-red-200 px-6 py-4 rounded-lg">
                    <h2 className="text-xl font-bold mb-2">Error</h2>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    if (interviewComplete) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-8">
                <div className="max-w-2xl bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-12 border border-white/20 text-center">
                    <div className="text-6xl mb-6">🎉</div>
                    <h1 className="text-4xl font-bold text-white mb-4">Interview Complete!</h1>
                    <p className="text-xl text-purple-200 mb-8">
                        Thank you for completing the interview. Your responses have been recorded and will
                        be reviewed by our team.
                    </p>
                    <p className="text-purple-300">You may now close this window.</p>
                </div>
            </div>
        );
    }

    const questionCount = messages.filter((m) => m.role === 'assistant' && m.question_number).length;

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col">
            {/* Header */}
            <div className="bg-white/10 backdrop-blur-lg border-b border-white/20 p-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-white">AI Technical Interview</h1>
                    <div className="text-purple-200">
                        Question {questionCount} of {targetQuestions}
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4">
                <div className="max-w-4xl mx-auto space-y-4">
                    {messages.map((message, index) => (
                        <div
                            key={index}
                            className={`flex ${message.role === 'candidate' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[80%] rounded-2xl p-4 ${message.role === 'candidate'
                                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                                    : 'bg-white/10 backdrop-blur-lg border border-white/20 text-white'
                                    }`}
                            >
                                {message.question_number && (
                                    <div className="text-xs text-purple-300 mb-2 font-semibold">
                                        Question {message.question_number}
                                    </div>
                                )}
                                <p className="whitespace-pre-wrap">{message.content}</p>
                                <div className="text-xs opacity-70 mt-2">
                                    {new Date(message.timestamp).toLocaleTimeString()}
                                </div>
                            </div>
                        </div>
                    ))}

                    {sending && (
                        <div className="flex justify-start">
                            <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-4">
                                <div className="flex items-center space-x-2">
                                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                                    <div
                                        className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
                                        style={{ animationDelay: '0.2s' }}
                                    ></div>
                                    <div
                                        className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"
                                        style={{ animationDelay: '0.4s' }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input */}
            <div className="bg-white/10 backdrop-blur-lg border-t border-white/20 p-4">
                <div className="max-w-4xl mx-auto">
                    <form onSubmit={handleSendMessage} className="flex gap-4">
                        <textarea
                            ref={textareaRef}
                            value={currentMessage}
                            onChange={(e) => setCurrentMessage(e.target.value)}
                            onPaste={handlePaste}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter' && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSendMessage(e);
                                }
                            }}
                            placeholder="Type your answer here... (Shift+Enter for new line)"
                            className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                            rows={3}
                            disabled={sending}
                        />
                        <button
                            type="submit"
                            disabled={!currentMessage.trim() || sending}
                            className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {sending ? 'Sending...' : 'Send'}
                        </button>
                    </form>

                    {pasteDetected && (
                        <p className="text-yellow-300 text-sm mt-2">
                            ⚠️ Paste detected - this will be noted in your interview
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
