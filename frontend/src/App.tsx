import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import CreateInterview from './pages/CreateInterview';
import InterviewDetails from './pages/InterviewDetails';
import UploadDocuments from './pages/UploadDocuments';
import CandidateInterview from './pages/CandidateInterview';

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    {/* Public routes */}
                    <Route path="/login" element={<Login />} />
                    <Route path="/interview/:token" element={<CandidateInterview />} />

                    {/* Protected admin routes */}
                    <Route
                        path="/admin"
                        element={
                            <ProtectedRoute>
                                <AdminDashboard />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/admin/create"
                        element={
                            <ProtectedRoute>
                                <CreateInterview />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/admin/interviews/:id"
                        element={
                            <ProtectedRoute>
                                <InterviewDetails />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/admin/interviews/:id/upload"
                        element={
                            <ProtectedRoute>
                                <UploadDocuments />
                            </ProtectedRoute>
                        }
                    />

                    {/* Default redirect */}
                    <Route path="/" element={<Navigate to="/admin" replace />} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    );
}

export default App;
