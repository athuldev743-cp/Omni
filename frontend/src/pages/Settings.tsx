import React, { useState } from "react";
import { api } from "../api";

const safeParseJson = (value: string): any | null => {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 9,
  background: "#0d0f1a",
  border: "1px solid rgba(255,255,255,0.08)",
  color: "#f0f2ff",
  fontSize: 13.5,
  outline: "none",
  fontFamily: "'DM Sans', sans-serif",
};
const labelStyle: React.CSSProperties = {
  fontSize: 12,
  color: "#8b90b8",
  marginBottom: 6,
  display: "block",
  letterSpacing: "0.2px",
};
const cardStyle: React.CSSProperties = {
  background: "#161929",
  border: "1px solid rgba(255,255,255,0.06)",
  borderRadius: 14,
  padding: 22,
  marginBottom: 16,
};

const Settings: React.FC = () => {
  const [name, setName] = useState("");
  const [tone, setTone] = useState("");
  const [businessInfoRaw, setBusinessInfoRaw] = useState(
    '{\n  "industry": ""\n}',
  );
  const [productsRaw, setProductsRaw] = useState('{\n  "products": []\n}');
  const [status, setStatus] = useState<{ msg: string; ok: boolean } | null>(
    null,
  );
  const [loading, setLoading] = useState(false);

  const onSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const business_info = safeParseJson(businessInfoRaw);
      if (business_info === null)
        throw new Error("business_info must be valid JSON");
      const products = safeParseJson(productsRaw);
      if (products === null) throw new Error("products must be valid JSON");
      await api.patch("/tenants/me", {
        name: name || undefined,
        tone: tone || undefined,
        business_info,
        products,
      });
      setStatus({ msg: "Settings saved successfully.", ok: true });
    } catch (err: any) {
      setStatus({
        msg: err?.response?.data?.detail || err?.message || "Failed to save.",
        ok: false,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "24px 28px", maxWidth: 680 }}>
      <div style={{ marginBottom: 22 }}>
        <div
          style={{
            fontFamily: "'Syne', sans-serif",
            fontSize: 22,
            fontWeight: 700,
            letterSpacing: -0.5,
            color: "#f0f2ff",
            marginBottom: 4,
          }}
        >
          Settings
        </div>
        <div style={{ fontSize: 13, color: "#4a4f72" }}>
          Configure your tenant profile. Used by OmniAgent to personalize AI
          outreach content.
        </div>
      </div>

      <form onSubmit={onSave}>
        <div style={cardStyle}>
          <div
            style={{
              fontFamily: "'Syne', sans-serif",
              fontSize: 14,
              fontWeight: 600,
              color: "#f0f2ff",
              marginBottom: 18,
            }}
          >
            Tenant Profile
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={labelStyle}>Tenant Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={inputStyle}
                placeholder="e.g. Acme Corp"
              />
            </div>
            <div>
              <label style={labelStyle}>AI Tone</label>
              <input
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                style={inputStyle}
                placeholder="e.g. professional, friendly, concise"
              />
              <div style={{ fontSize: 11.5, color: "#4a4f72", marginTop: 5 }}>
                Used to adjust AI-generated messages and outreach tone.
              </div>
            </div>
          </div>
        </div>

        <div style={cardStyle}>
          <div
            style={{
              fontFamily: "'Syne', sans-serif",
              fontSize: 14,
              fontWeight: 600,
              color: "#f0f2ff",
              marginBottom: 18,
            }}
          >
            Business Data (JSON)
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={labelStyle}>Business Info</label>
              <textarea
                value={businessInfoRaw}
                onChange={(e) => setBusinessInfoRaw(e.target.value)}
                style={{
                  ...inputStyle,
                  minHeight: 110,
                  resize: "vertical",
                  fontFamily: "monospace",
                  fontSize: 12,
                }}
              />
            </div>
            <div>
              <label style={labelStyle}>Products</label>
              <textarea
                value={productsRaw}
                onChange={(e) => setProductsRaw(e.target.value)}
                style={{
                  ...inputStyle,
                  minHeight: 110,
                  resize: "vertical",
                  fontFamily: "monospace",
                  fontSize: 12,
                }}
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "13px 0",
            borderRadius: 10,
            background: loading
              ? "rgba(255,255,255,0.04)"
              : "linear-gradient(135deg,#4f6ef7,#7c3aed)",
            border: `1px solid ${loading ? "rgba(255,255,255,0.06)" : "transparent"}`,
            cursor: loading ? "not-allowed" : "pointer",
            fontFamily: "'Syne', sans-serif",
            fontWeight: 700,
            fontSize: 14,
            color: loading ? "#4a4f72" : "#fff",
          }}
        >
          {loading ? "Saving..." : "Save Settings"}
        </button>

        {status && (
          <div
            style={{
              marginTop: 12,
              fontSize: 13,
              padding: "10px 13px",
              borderRadius: 9,
              background: status.ok
                ? "rgba(6,214,160,0.08)"
                : "rgba(247,37,133,0.08)",
              border: `1px solid ${status.ok ? "rgba(6,214,160,0.2)" : "rgba(247,37,133,0.2)"}`,
              color: status.ok ? "#06d6a0" : "#f72585",
            }}
          >
            {status.msg}
          </div>
        )}
      </form>
    </div>
  );
};

export default Settings;
