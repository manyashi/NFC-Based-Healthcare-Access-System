import { useEffect } from 'react'; // <--- FIXED: Added this import
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import PatientDashboard from './pages/PatientDashboard';
import StaffDashboard from './pages/StaffDashboard';
import PatientRecordView from './pages/PatientRecordView';

// --- HELPER COMPONENTS ---

// 1. AuthSuccess: Handles the redirect back from Google
const AuthSuccess = () => {
    const { checkUserStatus } = useAuth();
    
    useEffect(() => { 
        // Force a re-check of the session cookie immediately
        checkUserStatus(); 
    }, []); 

    // Redirect to home (which will then route to staff/patient dashboard)
    return <Navigate to="/" />;
};

// 2. ProtectedRoute: Handles "Not Logged In" and "Session Expired"
const ProtectedRoute = ({ children, role }) => {
    const { user, loading } = useAuth();

    // Still checking session? Show nothing or a spinner
    if (loading) return <div className="p-10 text-center">Loading secure session...</div>;

    // A. Not Logged In? -> Redirect to Login
    if (!user) {
        return <Navigate to="/login" replace />;
    }

    // B. Wrong Role? -> Redirect to Unauthorized (or Home)
    if (role && user.role !== role) {
        return <div className="p-10 text-red-600">Unauthorized Access</div>;
    }

    // C. Access Granted
    return children;
};

// --- MAIN ROUTING LOGIC ---

function AppRoutes() {
    const { user, loading } = useAuth();

    if (loading) return <div>Loading...</div>;

    return (
        <Routes>
            {/* Public Route: Login */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Auth Callback Route (Used by Google) */}
            <Route path="/auth-success" element={<AuthSuccess />} />
            
            {/* --- PROTECTED ROUTES --- */}
            
            {/* Patient Area */}
            <Route path="/patient" element={
                <ProtectedRoute role="patient">
                    <PatientDashboard />
                </ProtectedRoute>
            } />
            
            {/* Staff Area */}
            <Route path="/staff" element={
                <ProtectedRoute role="staff">
                    <StaffDashboard />
                </ProtectedRoute>
            } />

            {/* Staff: View Specific Patient */}
            <Route path="/staff/patient/:id" element={
                <ProtectedRoute role="staff">
                    <PatientRecordView />
                </ProtectedRoute>
            } />

            {/* Default Redirection Logic */}
            <Route path="/" element={
                // If logged in as staff -> Go to Staff Dashboard
                user?.role === 'staff' ? <Navigate to="/staff" /> : 
                // If logged in as patient -> Go to Patient Dashboard
                user?.role === 'patient' ? <Navigate to="/patient" /> : 
                // If NOT logged in -> Go to Login
                <Navigate to="/login" />
            } />
            
            {/* Catch-all for 404s */}
            <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <Router>
                <AppRoutes />
            </Router>
        </AuthProvider>
    );
}