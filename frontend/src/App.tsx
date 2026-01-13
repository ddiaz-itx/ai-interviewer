import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {
    return (
        <BrowserRouter>
            <div className="min-h-screen bg-gray-50">
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/admin/*" element={<div>Admin Dashboard (Coming Soon)</div>} />
                    <Route path="/interview/:token" element={<div>Candidate Interview (Coming Soon)</div>} />
                </Routes>
            </div>
        </BrowserRouter>
    )
}

function HomePage() {
    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                    AI Interviewer
                </h1>
                <p className="text-lg text-gray-600 mb-8">
                    Intelligent technical interview platform
                </p>
                <div className="space-x-4">
                    <a
                        href="/admin"
                        className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                    >
                        Admin Dashboard
                    </a>
                </div>
            </div>
        </div>
    )
}

export default App
