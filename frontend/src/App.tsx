import React from "react";
import { Link, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./useAuth";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ConnectMeta from "./pages/ConnectMeta";
import CampaignView from "./pages/CampaignView";
import Settings from "./pages/Settings";

const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="font-semibold text-lg">OmniAgent</div>
        <nav className="space-x-4 text-sm">
          <Link to="/dashboard" className="hover:text-emerald-400">
            Dashboard
          </Link>
          <Link to="/campaigns" className="hover:text-emerald-400">
            Campaigns
          </Link>
          <Link to="/connect-meta" className="hover:text-emerald-400">
            Connect Meta
          </Link>
          <Link to="/settings" className="hover:text-emerald-400">
            Settings
          </Link>
        </nav>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
};

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-slate-300">Loading...</div>
      </div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Shell>{children}</Shell>;
};

const AppRoutes: React.FC = () => (
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route
      path="/dashboard"
      element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      }
    />
    <Route
      path="/connect-meta"
      element={
        <ProtectedRoute>
          <ConnectMeta />
        </ProtectedRoute>
      }
    />
    <Route
      path="/campaigns"
      element={
        <ProtectedRoute>
          <CampaignView />
        </ProtectedRoute>
      }
    />
    <Route
      path="/settings"
      element={
        <ProtectedRoute>
          <Settings />
        </ProtectedRoute>
      }
    />
    <Route path="*" element={<Navigate to="/dashboard" replace />} />
  </Routes>
);

const App: React.FC = () => (
  <AuthProvider>
    <AppRoutes />
  </AuthProvider>
);

export default App;

