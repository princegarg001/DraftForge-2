import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './components/common/Toast';
import { Navbar } from './components/common/Navbar';
import { Sidebar } from './components/common/Sidebar';
import { LandingPage } from './pages/LandingPage';
import { AuthPage } from './pages/AuthPage';
import { StudentDashboard } from './pages/StudentDashboard';
import { TeacherDashboard } from './pages/TeacherDashboard';

const MainLayout: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const isTeacher = user?.role === 'TEACHER' || user?.role === 'ADMIN';
  const [activeTab, setActiveTab] = useState(isTeacher ? 'teacher_assignments' : 'workspace');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [unauthView, setUnauthView] = useState<'landing' | 'auth'>('landing');

  useEffect(() => {
    if (isTeacher) {
      setActiveTab('teacher_assignments');
    } else {
      setActiveTab('workspace');
    }
  }, [isTeacher]);

  if (!isAuthenticated) {
    if (unauthView === 'auth') {
      return <AuthPage onBackToLanding={() => setUnauthView('landing')} />;
    }
    return <LandingPage onOpenAuth={() => setUnauthView('auth')} />;
  }

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col font-sans selection:bg-primary-500 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isMobileMenuOpen={isMobileMenuOpen}
        setIsMobileMenuOpen={setIsMobileMenuOpen}
      />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          isCollapsed={isCollapsed}
          setIsCollapsed={setIsCollapsed}
          isMobileMenuOpen={isMobileMenuOpen}
          setIsMobileMenuOpen={setIsMobileMenuOpen}
        />
        <main className="flex-1 bg-background/60 overflow-y-auto overflow-x-hidden relative">
          {isTeacher ? (
            <TeacherDashboard activeTab={activeTab} setActiveTab={setActiveTab} />
          ) : (
            <StudentDashboard activeTab={activeTab} setActiveTab={setActiveTab} />
          )}
        </main>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <ToastProvider>
        <MainLayout />
      </ToastProvider>
    </AuthProvider>
  );
};

export default App;