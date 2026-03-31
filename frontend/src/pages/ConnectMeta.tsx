import React, { useEffect, useState } from "react";
import { api } from "../api";

declare global {
  interface Window { FB: any; fbAsyncInit: () => void; }
}

const S = {
  page: { padding: "24px 28px", maxWidth: 640 } as React.CSSProperties,
  card: {
    background: "#161929", border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: 14, padding: 22, marginBottom: 16,
  } as React.CSSProperties,
  btn: (disabled: boolean, color = "#06d6a0"): React.CSSProperties => ({
    width: "100%", padding: "13px 0", borderRadius: 11,
    background: disabled ? "rgba(255,255,255,0.04)" : `linear-gradient(135deg,${color},${color === "#06d6a0" ? "#4f6ef7" : color})`,
    border: `1px solid ${disabled ? "rgba(255,255,255,0.06)" : "transparent"}`,
    cursor: disabled ? "not-allowed" : "pointer",
    fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14,
    color: disabled ? "#4a4f72" : "#fff",
    display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
    transition: "opacity 0.2s",
  }),
};

const ConnectMeta: React.FC = () => {
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sdkReady, setSdkReady] = useState(false);

  const APP_ID = import.meta.env.VITE_META_APP_ID || "1270370071163693";
  const CONFIG_ID = import.meta.env.VITE_META_CONFIG_ID || "1711172183378816";

  useEffect(() => {
    if (document.getElementById("facebook-jssdk")) { setSdkReady(true); return; }
    window.fbAsyncInit = () => {
      window.FB.init({ appId: APP_ID, cookie: true, xfbml: true, version: "v21.0" });
      setSdkReady(true);
    };
    const script = document.createElement("script");
    script.id = "facebook-jssdk";
    script.src = "https://connect.facebook.net/en_US/sdk.js";
    script.async = true; script.defer = true;
    document.body.appendChild(script);
  }, [APP_ID]);

  const launchSignup = () => {
    if (!window.FB) { setStatus("Facebook SDK not loaded yet. Please wait and try again."); return; }
    setLoading(true);
    setStatus(null);

    window.FB.login(
      (response: any) => {
        if (!response.authResponse?.code) {
          setStatus("Meta login was cancelled or failed.");
          setLoading(false);
          return;
        }
        api.post("/whatsapp/onboard", { code: response.authResponse.code })
          .then(({ data }) => {
            setStatus(`✅ WhatsApp connected! WABA: ${data.waba_id || "N/A"} | Phone ID: ${data.phone_number_id || "N/A"}`);
          })
          .catch((err: any) => {
            setStatus(err?.response?.data?.detail || "Failed to complete onboarding. Please try again.");
          })
          .finally(() => setLoading(false));
      },
      {
        config_id: CONFIG_ID,
        response_type: "code",
        override_default_response_type: true,
        redirect_uri: "https://omni-flame-two.vercel.app",
        extras: { setup: {}, featureType: "", sessionInfoVersion: "3" },
      },
    );
  }; // ← this closing brace was missing

  const isSuccess = status?.startsWith("✅");

  return (
    <div style={S.page}>
      <div style={{ marginBottom: 22 }}>
        <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 22, fontWeight: 700, letterSpacing: -0.5, color: "#f0f2ff", marginBottom: 6 }}>
          Connect WhatsApp
        </div>
        <div style={{ fontSize: 13.5, color: "#8b90b8", lineHeight: 1.6 }}>
          Link your WhatsApp Business Account via Meta Embedded Signup. Takes under 60 seconds.
        </div>
      </div>

      <div style={S.card}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12,
            background: "linear-gradient(135deg,#06d6a0,#4f6ef7)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 20, color: "#fff", fontWeight: 800,
          }}>W</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 600, color: "#f0f2ff", fontFamily: "'Syne', sans-serif" }}>WhatsApp Business</div>
            <div style={{ fontSize: 12, color: "#4a4f72" }}>Meta Embedded Signup · One-click setup</div>
          </div>
          <div style={{ marginLeft: "auto", fontSize: 11, padding: "3px 9px", borderRadius: 20, background: "rgba(6,214,160,0.1)", color: "#06d6a0" }}>
            {sdkReady ? "SDK Ready" : "Loading..."}
          </div>
        </div>

        <button
          onClick={launchSignup}
          disabled={loading || !sdkReady}
          style={S.btn(loading || !sdkReady)}
        >
          {loading ? "⏳ Connecting..." : !sdkReady ? "Loading SDK..." : "🔗 Connect WhatsApp Business"}
        </button>

        {status && (
          <div style={{
            marginTop: 14, fontSize: 13, padding: "11px 14px", borderRadius: 10,
            background: isSuccess ? "rgba(6,214,160,0.08)" : "rgba(247,37,133,0.08)",
            border: `1px solid ${isSuccess ? "rgba(6,214,160,0.2)" : "rgba(247,37,133,0.2)"}`,
            color: isSuccess ? "#06d6a0" : "#f72585",
            lineHeight: 1.5,
          }}>{status}</div>
        )}
      </div>

      <div style={S.card}>
        <div style={{ fontSize: 12, letterSpacing: "1.5px", textTransform: "uppercase", color: "#4a4f72", fontWeight: 600, marginBottom: 16 }}>
          What happens
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {[
            { n: 1, title: "Meta popup opens", sub: "Log in with your Facebook account" },
            { n: 2, title: "Select your WABA", sub: "Choose your WhatsApp Business Account" },
            { n: 3, title: "Token saved securely", sub: "Encrypted and stored automatically" },
            { n: 4, title: "AI agent activated", sub: "OmniAgent can now send & receive WhatsApp messages" },
          ].map(({ n, title, sub }) => (
            <div key={n} style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
              <div style={{
                width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
                background: "linear-gradient(135deg,rgba(79,110,247,0.2),rgba(124,58,237,0.2))",
                border: "1px solid rgba(79,110,247,0.2)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 11, fontWeight: 700, color: "#4f6ef7",
              }}>{n}</div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500, color: "#f0f2ff", marginBottom: 2 }}>{title}</div>
                <div style={{ fontSize: 12, color: "#4a4f72" }}>{sub}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ConnectMeta;