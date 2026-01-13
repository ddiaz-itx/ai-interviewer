import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AdminDashboard from './pages/AdminDashboard';
import CreateInterview from './pages/CreateInterview';
import InterviewDetails from './pages/InterviewDetails';
import CandidateInterview from './pages/CandidateInterview';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Redirect root to admin dashboard */}
                <Route path="/" element={<Navigate to="/admin" replace />} />

                {/* Admin routes */}
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/admin/create" element={<CreateInterview />} />
                <Route path="/admin/interviews/:id" element={<InterviewDetails />} />

                {/* Candidate route */}
                <Route path="/interview/:token" element={<CandidateInterview />} />

                {/* 404 */}
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}

function NotFound() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
            <div className="text-center">
                <h1 className="text-6xl font-bold text-white mb-4">404</h1>
                <p className="text-xl text-purple-200 mb-8">Page not found</p>
                <a
                    href="/admin"
                    className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all duration-200 inline-block"
                >
                    Go to Dashboard
                </a>
            </div>
        </div>
    );
}

export default App;
