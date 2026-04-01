import React from "react";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./useAuth";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ConnectMeta from "./pages/ConnectMeta";
import CampaignView from "./pages/CampaignView";
import Settings from "./pages/Settings";
import PrivacyPolicy from "./pages/PrivacyPolicy";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "⊞" },
  { to: "/campaigns", label: "Campaigns", icon: "◈" },
  { to: "/connect-meta", label: "Connect Meta", icon: "⬡" },
  { to: "/settings", label: "Settings", icon: "⚙" },
];

const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const location = useLocation();

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#07080f",
        color: "#f0f2ff",
        fontFamily: "'DM Sans', sans-serif",
      }}
    >
      {/* Sidebar */}
      <aside
        style={{
          width: 232,
          flexShrink: 0,
          background: "#0d0f1a",
          borderRight: "1px solid rgba(255,255,255,0.06)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: "26px 20px 22px",
            borderBottom: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 34,
                height: 34,
                borderRadius: 10,
                background: "linear-gradient(135deg,#4f6ef7,#7c3aed)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 800,
                fontSize: 13,
                color: "#fff",
                fontFamily: "'Syne', sans-serif",
              }}
            >
              OA
            </div>
            <div>
              <div
                style={{
                  fontFamily: "'Syne', sans-serif",
                  fontWeight: 700,
                  fontSize: 16,
                }}
              >
                Omni<span style={{ color: "#4f6ef7" }}>Agent</span>
              </div>
              <div
                style={{
                  fontSize: 10,
                  color: "#4a4f72",
                  letterSpacing: "1.5px",
                  textTransform: "uppercase",
                }}
              >
                AI Platform
              </div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "18px 10px" }}>
          <div
            style={{
              fontSize: 10,
              letterSpacing: "1.8px",
              textTransform: "uppercase",
              color: "#4a4f72",
              padding: "0 10px",
              marginBottom: 8,
            }}
          >
            Main
          </div>
          {NAV_ITEMS.map(({ to, label, icon }) => {
            const active = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "9px 10px",
                  borderRadius: 10,
                  textDecoration: "none",
                  color: active ? "#f0f2ff" : "#8b90b8",
                  background: active ? "#1c2035" : "transparent",
                  marginBottom: 2,
                  fontSize: 13.5,
                  position: "relative",
                  transition: "all 0.2s",
                }}
              >
                {active && (
                  <div
                    style={{
                      position: "absolute",
                      left: 0,
                      top: "50%",
                      transform: "translateY(-50%)",
                      width: 3,
                      height: 18,
                      borderRadius: "0 3px 3px 0",
                      background: "linear-gradient(180deg,#4f6ef7,#7c3aed)",
                    }}
                  />
                )}
                <div
                  style={{
                    width: 30,
                    height: 30,
                    borderRadius: 8,
                    fontSize: 14,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: active ? "rgba(79,110,247,0.15)" : "#12152a",
                  }}
                >
                  {icon}
                </div>
                {label}
              </Link>
            );
          })}
        </nav>

        {/* User */}
        <div
          style={{
            padding: "14px 10px 18px",
            borderTop: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "9px 10px",
              borderRadius: 10,
            }}
          >
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: "50%",
                background: "linear-gradient(135deg,#f72585,#7c3aed)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 12,
                fontWeight: 700,
                color: "#fff",
                flexShrink: 0,
              }}
            >
              {user?.email?.[0]?.toUpperCase() ?? "U"}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div
                style={{
                  fontSize: 12.5,
                  fontWeight: 500,
                  color: "#f0f2ff",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {user?.email ?? "User"}
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: "#06d6a0",
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                <div
                  style={{
                    width: 5,
                    height: 5,
                    borderRadius: "50%",
                    background: "#06d6a0",
                  }}
                />
                Pro Plan
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Topbar */}
        <div
          style={{
            height: 60,
            flexShrink: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 28px",
            background: "#0d0f1a",
            borderBottom: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <div
            style={{
              fontFamily: "'Syne', sans-serif",
              fontSize: 18,
              fontWeight: 700,
              letterSpacing: -0.5,
            }}
          >
            {NAV_ITEMS.find((n) => n.to === location.pathname)?.label ??
              "OmniAgent"}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 7,
                background: "#161929",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 9,
                padding: "0 14px",
                height: 34,
                fontSize: 12.5,
                color: "#4a4f72",
                cursor: "text",
              }}
            >
              🔍 &nbsp;Search...
            </div>
            <div
              style={{
                width: 34,
                height: 34,
                borderRadius: 9,
                background: "#161929",
                border: "1px solid rgba(255,255,255,0.06)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 14,
                cursor: "pointer",
              }}
            >
              🔔
            </div>
          </div>
        </div>
        <main style={{ flex: 1, overflowY: "auto" }}>{children}</main>
      </div>
    </div>
  );
};

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#07080f",
          color: "#8b90b8",
          fontFamily: "'DM Sans', sans-serif",
        }}
      >
        <div>Loading...</div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
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
    <Route path="/privacy" element={<PrivacyPolicy />} />
  </Routes>
);

const App: React.FC = () => (
  <AuthProvider>
    <AppRoutes />
  </AuthProvider>
);

export default App;
