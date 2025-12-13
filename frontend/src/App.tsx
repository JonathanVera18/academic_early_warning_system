import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import SAT_Dashboard from './pages/SAT_Dashboard';
import InstitutionalView from './pages/InstitutionalView';
import StudentProfile from './pages/StudentProfile';
import LoginPage from './pages/LoginPage';
import { StudentDataProvider } from './context/StudentDataContext';
import { AuthProvider, useAuth } from './context/AuthContext';

// Loading spinner component
const LoadingScreen: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
    <div className="text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
        <svg
          className="animate-spin h-12 w-12 text-rose-500"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
      <p className="text-slate-400">Cargando...</p>
    </div>
  </div>
);

// Protected app content
const AppContent: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <StudentDataProvider>
      <MainLayout>
        <Routes>
          <Route path="/" element={<SAT_Dashboard />} />
          <Route path="/institutional" element={<InstitutionalView />} />
          <Route path="/student/:studentId" element={<StudentProfile />} />
        </Routes>
      </MainLayout>
    </StudentDataProvider>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
