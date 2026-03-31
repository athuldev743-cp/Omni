import React, { useEffect, useState } from "react";
import { fetchReadyForMeetLeads, fetchWallet, Lead, Wallet } from "../api";
import { useAuth } from "../useAuth";

const s = {
  page: { padding: "24px 28px" } as React.CSSProperties,
  statusBar: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "9px 14px",
    background: "rgba(6,214,160,0.06)",
    border: "1px solid rgba(6,214,160,0.18)",
    borderRadius: 10,
    marginBottom: 22,
  } as React.CSSProperties,
  dot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    background: "#06d6a0",
    flexShrink: 0,
  } as React.CSSProperties,
  kpiGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(4,1fr)",
    gap: 14,
    marginBottom: 24,
  } as React.CSSProperties,
  kpi: (color: string): React.CSSProperties => ({
    background: "#161929",
    border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: 14,
    padding: "18px 18px 14px",
    position: "relative",
    overflow: "hidden",
    cursor: "default",
  }),
  kpiBar: (color: string): React.CSSProperties => ({
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: 2,
    background: `linear-gradient(90deg,${color},transparent)`,
  }),
  kpiIcon: (color: string): React.CSSProperties => ({
    width: 36,
    height: 36,
    borderRadius: 9,
    background: `${color}18`,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 16,
    marginBottom: 12,
    color,
  }),
  kpiLabel: {
    fontSize: 11.5,
    color: "#8b90b8",
    marginBottom: 5,
  } as React.CSSProperties,
  kpiValue: {
    fontFamily: "'Syne', sans-serif",
    fontSize: 28,
    fontWeight: 700,
    letterSpacing: -1,
    lineHeight: 1,
    color: "#f0f2ff",
  } as React.CSSProperties,
  kpiSub: {
    fontSize: 11,
    color: "#4a4f72",
    marginTop: 6,
  } as React.CSSProperties,
  midGrid: {
    display: "grid",
    gridTemplateColumns: "1.6fr 1fr",
    gap: 16,
    marginBottom: 24,
  } as React.CSSProperties,
  card: {
    background: "#161929",
    border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: 14,
    padding: 20,
  } as React.CSSProperties,
  cardHead: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 16,
  } as React.CSSProperties,
  cardTitle: {
    fontFamily: "'Syne', sans-serif",
    fontSize: 14,
    fontWeight: 600,
    color: "#f0f2ff",
  } as React.CSSProperties,
  badge: (color: string): React.CSSProperties => ({
    fontSize: 10.5,
    padding: "3px 9px",
    borderRadius: 20,
    background: `${color}18`,
    color,
  }),
  actItem: {
    display: "flex",
    alignItems: "center",
    gap: 11,
    padding: "9px 0",
    borderBottom: "1px solid rgba(255,255,255,0.05)",
  } as React.CSSProperties,
  actDot: (color: string): React.CSSProperties => ({
    width: 7,
    height: 7,
    borderRadius: "50%",
    background: color,
    flexShrink: 0,
  }),
  actText: {
    flex: 1,
    fontSize: 13,
    color: "#8b90b8",
    lineHeight: 1.4,
  } as React.CSSProperties,
  actTime: {
    fontSize: 11,
    color: "#4a4f72",
    flexShrink: 0,
  } as React.CSSProperties,
  qaGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3,1fr)",
    gap: 12,
    marginBottom: 24,
  } as React.CSSProperties,
  qaBtn: {
    background: "#161929",
    border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: 12,
    padding: "15px 15px 13px",
    display: "flex",
    flexDirection: "column",
    gap: 8,
    cursor: "pointer",
    transition: "all 0.2s",
    textAlign: "left",
  } as React.CSSProperties,
  sectionHead: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 16,
  } as React.CSSProperties,
  sectionTitle: {
    fontSize: 11,
    letterSpacing: "1.8px",
    textTransform: "uppercase" as const,
    color: "#4a4f72",
    fontWeight: 600,
  },
  emptyBox: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    justifyContent: "center",
    padding: "44px 20px",
    textAlign: "center" as const,
    border: "1px dashed rgba(255,255,255,0.1)",
    borderRadius: 12,
  },
  leadCard: {
    background: "#12152a",
    border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: 10,
    padding: "12px 14px",
    marginBottom: 8,
    display: "flex",
    alignItems: "center",
    gap: 12,
  } as React.CSSProperties,
};

const KPI: React.FC<{
  icon: string;
  label: string;
  value: string | number;
  sub: string;
  color: string;
}> = ({ icon, label, value, sub, color }) => (
  <div style={s.kpi(color)}>
    <div style={s.kpiBar(color)} />
    <div style={s.kpiIcon(color)}>{icon}</div>
    <div style={s.kpiLabel}>{label}</div>
    <div style={s.kpiValue}>{value}</div>
    <div style={s.kpiSub}>{sub}</div>
  </div>
);

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [leads, setLeads] = useState<Lead[] | null>(null);
  const [loadingLeads, setLoadingLeads] = useState(false);

  useEffect(() => {
    fetchWallet()
      .then(setWallet)
      .catch(() => setWallet(null));
    setLoadingLeads(true);
    fetchReadyForMeetLeads()
      .then(setLeads)
      .catch(() => setLeads([]))
      .finally(() => setLoadingLeads(false));
  }, []);

  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div style={s.page}>
      {/* Greeting */}
      <div style={{ marginBottom: 20 }}>
        <div
          style={{
            fontFamily: "'Syne', sans-serif",
            fontSize: 22,
            fontWeight: 700,
            letterSpacing: -0.5,
            marginBottom: 3,
          }}
        >
          {greeting()},{" "}
          <span
            style={{
              background: "linear-gradient(135deg,#4f6ef7,#7c3aed)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            {user?.email?.split("@")[0] ?? "there"}
          </span>{" "}
          👋
        </div>
        <div style={{ fontSize: 13, color: "#4a4f72" }}>
          Here's what's happening with your AI agent today.
        </div>
      </div>

      {/* Status bar */}
      <div style={s.statusBar}>
        <div style={s.dot} />
        <div style={{ fontSize: 12.5, color: "#06d6a0" }}>
          All systems operational &nbsp;
          <span style={{ color: "#4a4f72" }}>
            · AI agent active · Last sync just now
          </span>
        </div>
      </div>

      {/* KPIs */}
      <div style={s.kpiGrid}>
        <KPI
          icon="◈"
          label="Credit Balance"
          value={wallet ? wallet.wallet_balance : "—"}
          sub="Available credits"
          color="#4f6ef7"
        />
        <KPI
          icon="⬡"
          label="Active Campaigns"
          value={0}
          sub="No campaigns yet"
          color="#7c3aed"
        />
        <KPI
          icon="◎"
          label="Total Leads"
          value={leads?.length ?? "—"}
          sub={`Ready for meet: ${leads?.filter((l) => l.ready_for_meet).length ?? 0}`}
          color="#06d6a0"
        />
        <KPI
          icon="⚡"
          label="Messages Sent"
          value={0}
          sub="Via AI channels"
          color="#f72585"
        />
      </div>

      {/* Quick actions */}
      <div style={s.qaGrid}>
        {[
          {
            icon: "◈",
            label: "New Campaign",
            sub: "Launch AI-powered outreach",
            color: "#4f6ef7",
          },
          {
            icon: "⬡",
            label: "Connect WhatsApp",
            sub: "Link your Meta Business",
            color: "#06d6a0",
          },
          {
            icon: "⊕",
            label: "Add Credits",
            sub: "Top up your wallet",
            color: "#f72585",
          },
        ].map(({ icon, label, sub, color }) => (
          <div
            key={label}
            style={s.qaBtn}
            onMouseEnter={(e) =>
              (e.currentTarget.style.borderColor = "rgba(255,255,255,0.14)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.borderColor = "rgba(255,255,255,0.06)")
            }
          >
            <div style={{ fontSize: 18, color }}>{icon}</div>
            <div style={{ fontSize: 13, fontWeight: 500, color: "#f0f2ff" }}>
              {label}
            </div>
            <div style={{ fontSize: 11.5, color: "#4a4f72" }}>{sub}</div>
          </div>
        ))}
      </div>

      {/* Mid grid */}
      <div style={s.midGrid}>
        <div style={s.card}>
          <div style={s.cardHead}>
            <div style={s.cardTitle}>Recent Activity</div>
            <div style={s.badge("#4f6ef7")}>Live</div>
          </div>
          {[
            {
              color: "#4f6ef7",
              text: (
                <>
                  <strong style={{ color: "#f0f2ff" }}>Account created</strong>{" "}
                  — Welcome to OmniAgent
                </>
              ),
              time: "now",
            },
            {
              color: "#06d6a0",
              text: (
                <>
                  <strong style={{ color: "#f0f2ff" }}>Google OAuth</strong>{" "}
                  connected successfully
                </>
              ),
              time: "2m ago",
            },
            {
              color: "#7c3aed",
              text: (
                <>
                  <strong style={{ color: "#f0f2ff" }}>Tenant workspace</strong>{" "}
                  initialized
                </>
              ),
              time: "2m ago",
            },
            {
              color: "#f72585",
              text: (
                <>
                  Connect{" "}
                  <strong style={{ color: "#f0f2ff" }}>Meta WhatsApp</strong> to
                  start receiving leads
                </>
              ),
              time: "pending",
            },
            {
              color: "#4f6ef7",
              text: (
                <>
                  Create your first{" "}
                  <strong style={{ color: "#f0f2ff" }}>AI campaign</strong> to
                  engage leads
                </>
              ),
              time: "pending",
            },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                ...s.actItem,
                ...(i === 4 ? { borderBottom: "none" } : {}),
              }}
            >
              <div style={s.actDot(item.color)} />
              <div style={s.actText}>{item.text}</div>
              <div style={s.actTime}>{item.time}</div>
            </div>
          ))}
        </div>

        <div style={s.card}>
          <div style={s.cardHead}>
            <div style={s.cardTitle}>Setup Checklist</div>
            <div style={s.badge("#06d6a0")}>1/4 done</div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[
              { done: true, label: "Google account connected" },
              { done: false, label: "Connect Meta WhatsApp" },
              { done: false, label: "Add credits to wallet" },
              { done: false, label: "Launch first campaign" },
            ].map(({ done, label }, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  fontSize: 13,
                }}
              >
                <div
                  style={{
                    width: 20,
                    height: 20,
                    borderRadius: "50%",
                    flexShrink: 0,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 10,
                    background: done ? "rgba(6,214,160,0.15)" : "transparent",
                    border: done ? "none" : "1px solid rgba(255,255,255,0.1)",
                    color: done ? "#06d6a0" : "#4a4f72",
                  }}
                >
                  {done ? "✓" : i + 1}
                </div>
                <span style={{ color: done ? "#8b90b8" : "#4a4f72" }}>
                  {label}
                </span>
              </div>
            ))}
          </div>

          <div
            style={{
              marginTop: 22,
              paddingTop: 18,
              borderTop: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            <div
              style={{
                fontSize: 12,
                color: "#4a4f72",
                marginBottom: 10,
                letterSpacing: "1.5px",
                textTransform: "uppercase",
                fontWeight: 600,
              }}
            >
              Channels
            </div>
            {[
              { label: "WhatsApp", color: "#06d6a0", pct: 0 },
              { label: "Email", color: "#4f6ef7", pct: 0 },
              { label: "Voice", color: "#f72585", pct: 0 },
            ].map(({ label, color, pct }) => (
              <div
                key={label}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  marginBottom: 10,
                }}
              >
                <div
                  style={{
                    fontSize: 12,
                    color: "#8b90b8",
                    width: 62,
                    flexShrink: 0,
                  }}
                >
                  {label}
                </div>
                <div
                  style={{
                    flex: 1,
                    height: 4,
                    background: "#0d0f1a",
                    borderRadius: 3,
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: `${pct}%`,
                      background: color,
                      borderRadius: 3,
                    }}
                  />
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: "#4a4f72",
                    width: 28,
                    textAlign: "right",
                  }}
                >
                  {pct}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Leads */}
      <div style={s.sectionHead}>
        <div style={s.sectionTitle}>Ready for Meet Leads</div>
        <div
          style={{
            fontSize: 12,
            color: "#4f6ef7",
            cursor: "pointer",
            padding: "4px 10px",
            borderRadius: 7,
            border: "1px solid rgba(79,110,247,0.25)",
          }}
        >
          View All →
        </div>
      </div>

      {loadingLeads ? (
        <div style={{ fontSize: 13, color: "#4a4f72", padding: "20px 0" }}>
          Loading leads...
        </div>
      ) : leads && leads.length > 0 ? (
        <div>
          {leads.map((l) => (
            <div key={l.id} style={s.leadCard}>
              <div
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: "50%",
                  flexShrink: 0,
                  background: "linear-gradient(135deg,#4f6ef7,#7c3aed)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 13,
                  fontWeight: 700,
                  color: "#fff",
                }}
              >
                {l.name[0]?.toUpperCase()}
              </div>
              <div style={{ flex: 1 }}>
                <div
                  style={{ fontSize: 13.5, fontWeight: 500, color: "#f0f2ff" }}
                >
                  {l.name}
                </div>
                <div style={{ fontSize: 11.5, color: "#4a4f72", marginTop: 2 }}>
                  {l.email ?? "—"} &nbsp;·&nbsp; {l.phone ?? "—"} &nbsp;·&nbsp;{" "}
                  {l.source ?? "—"}
                </div>
              </div>
              <div
                style={{
                  fontSize: 10.5,
                  padding: "3px 9px",
                  borderRadius: 20,
                  background: "rgba(6,214,160,0.12)",
                  color: "#06d6a0",
                }}
              >
                Ready
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={s.emptyBox}>
          <div
            style={{
              width: 48,
              height: 48,
              borderRadius: 13,
              background: "rgba(79,110,247,0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 20,
              marginBottom: 14,
            }}
          >
            ◎
          </div>
          <div
            style={{
              fontFamily: "'Syne', sans-serif",
              fontSize: 15,
              fontWeight: 600,
              marginBottom: 6,
              color: "#f0f2ff",
            }}
          >
            No leads ready yet
          </div>
          <div
            style={{
              fontSize: 13,
              color: "#4a4f72",
              maxWidth: 260,
              lineHeight: 1.6,
            }}
          >
            Leads marked as READY_FOR_MEET via WhatsApp AI intent detection will
            appear here automatically.
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
