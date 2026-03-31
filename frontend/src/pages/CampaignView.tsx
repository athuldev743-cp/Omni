import React, { useEffect, useMemo, useState } from "react";
import { createCampaign, fetchCampaigns, fetchReadyForMeetLeads, triggerCampaign, Lead, Campaign } from "../api";

const inputStyle: React.CSSProperties = {
  width: "100%", padding: "10px 12px", borderRadius: 9,
  background: "#0d0f1a", border: "1px solid rgba(255,255,255,0.08)",
  color: "#f0f2ff", fontSize: 13.5, outline: "none",
  fontFamily: "'DM Sans', sans-serif",
};
const labelStyle: React.CSSProperties = { fontSize: 12, color: "#8b90b8", marginBottom: 6, display: "block", letterSpacing: "0.2px" };
const cardStyle: React.CSSProperties = {
  background: "#161929", border: "1px solid rgba(255,255,255,0.06)",
  borderRadius: 14, padding: 22,
};
const btnStyle = (disabled: boolean, color = "#4f6ef7"): React.CSSProperties => ({
  width: "100%", padding: "12px 0", borderRadius: 10,
  background: disabled ? "rgba(255,255,255,0.04)" : `linear-gradient(135deg,${color},${color === "#4f6ef7" ? "#7c3aed" : color})`,
  border: `1px solid ${disabled ? "rgba(255,255,255,0.06)" : "transparent"}`,
  cursor: disabled ? "not-allowed" : "pointer",
  color: disabled ? "#4a4f72" : "#fff",
  fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 14,
  transition: "opacity 0.2s",
});

const CHANNEL_INFO: Record<string, { label: string; color: string; note: string }> = {
  email: { label: "Email", color: "#4f6ef7", note: "Sends via your connected Gmail account. No Meta required." },
  whatsapp: { label: "WhatsApp", color: "#06d6a0", note: "Requires Meta WhatsApp Business connected." },
  voice: { label: "Voice", color: "#f72585", note: "AI voice calls via VAPI." },
};

const CampaignView: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[] | null>(null);
  const [leads, setLeads] = useState<Lead[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [queuedInfo, setQueuedInfo] = useState<{ msg: string; ok: boolean } | null>(null);

  const [name, setName] = useState("Outreach Campaign");
  const [channel, setChannel] = useState<"email" | "whatsapp" | "voice">("whatsapp");
  const [description, setDescription] = useState("Hi! Thanks for your interest. Are you ready to schedule a quick meet?");
  const [selectedLeadIds, setSelectedLeadIds] = useState<Record<number, boolean>>({});
  const [selectedCampaignId, setSelectedCampaignId] = useState<number | null>(null);

  const selectedIds = useMemo(
    () => Object.keys(selectedLeadIds).filter((k) => selectedLeadIds[Number(k)]).map(Number),
    [selectedLeadIds],
  );

  const refresh = async () => {
    setLoading(true);
    setQueuedInfo(null);
    try {
      const [c, l] = await Promise.all([fetchCampaigns(), fetchReadyForMeetLeads()]);
      setCampaigns(c);
      setLeads(l);
      if (c.length > 0 && selectedCampaignId == null) setSelectedCampaignId(c[0].id);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void refresh(); }, []); // eslint-disable-line

  const onCreate = async () => {
    setLoading(true);
    setQueuedInfo(null);
    try {
      const created = await createCampaign({ name, description, channel });
      const updated = await fetchCampaigns();
      setCampaigns(updated);
      setSelectedCampaignId(created.id);
      setQueuedInfo({ msg: `Campaign "${created.name}" created successfully.`, ok: true });
    } finally {
      setLoading(false);
    }
  };

  const onTrigger = async () => {
    if (!selectedCampaignId) return;
    if (selectedIds.length === 0) { setQueuedInfo({ msg: "Select at least one lead.", ok: false }); return; }
    setLoading(true);
    setQueuedInfo(null);
    try {
      const resp = await triggerCampaign({ campaign_id: selectedCampaignId, lead_ids: selectedIds });
      setQueuedInfo({ msg: `Queued ${resp.queued} outreach jobs successfully.`, ok: true });
      await refresh();
      setSelectedLeadIds({});
    } finally {
      setLoading(false);
    }
  };

  const chInfo = CHANNEL_INFO[channel];

  return (
    <div style={{ padding: "24px 28px" }}>
      <div style={{ marginBottom: 22 }}>
        <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 22, fontWeight: 700, letterSpacing: -0.5, color: "#f0f2ff", marginBottom: 4 }}>
          Campaigns
        </div>
        <div style={{ fontSize: 13, color: "#4a4f72" }}>
          Create and trigger AI-powered outreach campaigns across channels.
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Create */}
        <div style={cardStyle}>
          <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 15, fontWeight: 600, color: "#f0f2ff", marginBottom: 18 }}>
            Create Campaign
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={labelStyle}>Campaign Name</label>
              <input value={name} onChange={e => setName(e.target.value)} style={inputStyle} />
            </div>

            <div>
              <label style={labelStyle}>Channel</label>
              <div style={{ display: "flex", gap: 8 }}>
                {(["whatsapp", "email", "voice"] as const).map(ch => (
                  <button key={ch} onClick={() => setChannel(ch)} style={{
                    flex: 1, padding: "9px 0", borderRadius: 8, cursor: "pointer",
                    fontFamily: "'DM Sans', sans-serif", fontSize: 12.5, fontWeight: 500,
                    border: `1px solid ${channel === ch ? CHANNEL_INFO[ch].color + "60" : "rgba(255,255,255,0.07)"}`,
                    background: channel === ch ? `${CHANNEL_INFO[ch].color}12` : "#0d0f1a",
                    color: channel === ch ? CHANNEL_INFO[ch].color : "#8b90b8",
                    transition: "all 0.15s",
                  }}>{CHANNEL_INFO[ch].label}</button>
                ))}
              </div>
              <div style={{
                marginTop: 8, fontSize: 11.5, padding: "7px 10px", borderRadius: 8,
                background: `${chInfo.color}08`, border: `1px solid ${chInfo.color}20`,
                color: chInfo.color, lineHeight: 1.5,
              }}>{chInfo.note}</div>
            </div>

            <div>
              <label style={labelStyle}>Message Template</label>
              <textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                style={{ ...inputStyle, minHeight: 100, resize: "vertical" }}
              />
            </div>

            <button onClick={() => void onCreate()} disabled={loading} style={btnStyle(loading)}>
              {loading ? "Creating..." : "Create Campaign"}
            </button>
          </div>
        </div>

        {/* Trigger */}
        <div style={cardStyle}>
          <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 15, fontWeight: 600, color: "#f0f2ff", marginBottom: 18 }}>
            Trigger Outreach
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Select Campaign</label>
            <select
              value={selectedCampaignId ?? ""}
              onChange={e => setSelectedCampaignId(Number(e.target.value))}
              disabled={!campaigns || campaigns.length === 0}
              style={{ ...inputStyle, appearance: "none" }}
            >
              {!campaigns || campaigns.length === 0
                ? <option>No campaigns yet</option>
                : campaigns.map(c => <option key={c.id} value={c.id}>{c.name} ({c.channel})</option>)
              }
            </select>
          </div>

          <div style={{ marginBottom: 14 }}>
            <label style={labelStyle}>Ready for Meet Leads</label>
            {leads === null ? (
              <div style={{ fontSize: 13, color: "#4a4f72", padding: "16px 0" }}>Loading leads...</div>
            ) : leads.length === 0 ? (
              <div style={{
                fontSize: 13, color: "#4a4f72", padding: "20px 16px", textAlign: "center",
                border: "1px dashed rgba(255,255,255,0.08)", borderRadius: 10, lineHeight: 1.6,
              }}>
                No ready leads yet.<br />
                <span style={{ fontSize: 12 }}>Connect WhatsApp to detect intent, or email leads directly.</span>
              </div>
            ) : (
              <div style={{ maxHeight: 280, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
                {leads.map(l => (
                  <label key={l.id} style={{
                    display: "flex", alignItems: "center", gap: 10,
                    padding: "10px 12px", borderRadius: 9, cursor: "pointer",
                    border: `1px solid ${selectedLeadIds[l.id] ? "rgba(79,110,247,0.3)" : "rgba(255,255,255,0.07)"}`,
                    background: selectedLeadIds[l.id] ? "rgba(79,110,247,0.07)" : "#0d0f1a",
                    transition: "all 0.15s",
                  }}>
                    <input
                      type="checkbox"
                      checked={!!selectedLeadIds[l.id]}
                      onChange={e => setSelectedLeadIds(prev => ({ ...prev, [l.id]: e.target.checked }))}
                      style={{ accentColor: "#4f6ef7" }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, fontWeight: 500, color: "#f0f2ff" }}>{l.name}</div>
                      <div style={{ fontSize: 11.5, color: "#4a4f72", marginTop: 2 }}>
                        {l.phone ?? l.email ?? "—"}
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={() => void onTrigger()}
            disabled={loading || selectedIds.length === 0 || !selectedCampaignId}
            style={btnStyle(loading || selectedIds.length === 0 || !selectedCampaignId, "#06d6a0")}
          >
            {loading ? "Queuing..." : `Start Campaign${selectedIds.length > 0 ? ` (${selectedIds.length})` : ""}`}
          </button>

          {queuedInfo && (
            <div style={{
              marginTop: 12, fontSize: 13, padding: "10px 13px", borderRadius: 9,
              background: queuedInfo.ok ? "rgba(6,214,160,0.08)" : "rgba(247,37,133,0.08)",
              border: `1px solid ${queuedInfo.ok ? "rgba(6,214,160,0.2)" : "rgba(247,37,133,0.2)"}`,
              color: queuedInfo.ok ? "#06d6a0" : "#f72585",
            }}>{queuedInfo.msg}</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CampaignView;