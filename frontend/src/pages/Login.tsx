import React from "react";

const Login: React.FC = () => {
  const handleGoogleLogin = () => {
    // Must go to backend, not Vercel frontend
    const backendUrl =
      import.meta.env.VITE_API_URL?.replace("/api", "") ??
      "https://omni-backend-phxz.onrender.com";
    window.location.href = `${backendUrl}/api/auth/google/login`;
  };

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "#07080f", fontFamily: "'DM Sans', sans-serif", position: "relative", overflow: "hidden",
    }}>
      {/* Background glow orbs */}
      <div style={{
        position: "absolute", top: "20%", left: "30%",
        width: 400, height: 400, borderRadius: "50%",
        background: "radial-gradient(circle,rgba(79,110,247,0.12),transparent 70%)",
        pointerEvents: "none",
      }} />
      <div style={{
        position: "absolute", bottom: "20%", right: "25%",
        width: 300, height: 300, borderRadius: "50%",
        background: "radial-gradient(circle,rgba(124,58,237,0.1),transparent 70%)",
        pointerEvents: "none",
      }} />

      <div style={{
        background: "#0d0f1a", border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 20, padding: "44px 40px",
        width: "100%", maxWidth: 400,
        position: "relative", zIndex: 1,
        boxShadow: "0 0 60px rgba(79,110,247,0.08)",
      }}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 32 }}>
          <div style={{
            width: 38, height: 38, borderRadius: 11,
            background: "linear-gradient(135deg,#4f6ef7,#7c3aed)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 800, fontSize: 15, color: "#fff", fontFamily: "'Syne', sans-serif",
          }}>OA</div>
          <div>
            <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 18, color: "#f0f2ff" }}>
              Omni<span style={{ color: "#4f6ef7" }}>Agent</span>
            </div>
            <div style={{ fontSize: 10, color: "#4a4f72", letterSpacing: "1.5px", textTransform: "uppercase" }}>AI Platform</div>
          </div>
        </div>

        <div style={{ marginBottom: 28 }}>
          <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 22, fontWeight: 700, letterSpacing: -0.5, color: "#f0f2ff", marginBottom: 8 }}>
            Welcome back
          </div>
          <div style={{ fontSize: 13.5, color: "#8b90b8", lineHeight: 1.6 }}>
            Sign in with Google to access your AI-powered multi-channel outreach platform.
          </div>
        </div>

        {/* Divider */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 22 }}>
          <div style={{ flex: 1, height: 1, background: "rgba(255,255,255,0.06)" }} />
          <div style={{ fontSize: 11, color: "#4a4f72", letterSpacing: "1px", textTransform: "uppercase" }}>Continue with</div>
          <div style={{ flex: 1, height: 1, background: "rgba(255,255,255,0.06)" }} />
        </div>

        <button
          onClick={handleGoogleLogin}
          style={{
            width: "100%", padding: "13px 0", borderRadius: 11,
            background: "linear-gradient(135deg,#4f6ef7,#7c3aed)",
            border: "none", cursor: "pointer",
            fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14.5,
            color: "#fff", letterSpacing: -0.2,
            display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
            transition: "opacity 0.2s",
          }}
          onMouseEnter={e => (e.currentTarget.style.opacity = "0.88")}
          onMouseLeave={e => (e.currentTarget.style.opacity = "1")}
        >
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#fff" fillOpacity=".9"/>
            <path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#fff" fillOpacity=".75"/>
            <path d="M3.964 10.706A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.706V4.962H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.038l3.007-2.332z" fill="#fff" fillOpacity=".6"/>
            <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.962L3.964 7.294C4.672 5.167 6.656 3.58 9 3.58z" fill="#fff" fillOpacity=".85"/>
          </svg>
          Continue with Google
        </button>

        <div style={{ marginTop: 20, fontSize: 11.5, color: "#4a4f72", textAlign: "center", lineHeight: 1.6 }}>
          By continuing, you agree to our Terms of Service.<br />Your data is encrypted and secure.
        </div>

        {/* Feature pills */}
        <div style={{ display: "flex", gap: 8, marginTop: 24, justifyContent: "center", flexWrap: "wrap" }}>
          {["WhatsApp AI", "Email Campaigns", "Voice Outreach"].map(f => (
            <div key={f} style={{
              fontSize: 11, padding: "4px 10px", borderRadius: 20,
              background: "rgba(79,110,247,0.1)", color: "#4f6ef7",
              border: "1px solid rgba(79,110,247,0.2)",
            }}>{f}</div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Login;