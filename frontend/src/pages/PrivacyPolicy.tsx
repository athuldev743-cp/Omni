import React from "react";

const PrivacyPolicy: React.FC = () => {
  return (
    <div style={{
      minHeight: "100vh", background: "#07080f",
      fontFamily: "'DM Sans', sans-serif", color: "#f0f2ff",
      padding: "48px 24px",
    }}>
      <div style={{ maxWidth: 720, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 48 }}>
          <div style={{
            width: 38, height: 38, borderRadius: 11,
            background: "linear-gradient(135deg,#4f6ef7,#7c3aed)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 800, fontSize: 15, color: "#fff", fontFamily: "'Syne', sans-serif",
          }}>OA</div>
          <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 700, fontSize: 18, color: "#f0f2ff" }}>
            Omni<span style={{ color: "#4f6ef7" }}>Agent</span>
          </div>
        </div>

        <h1 style={{ fontFamily: "'Syne', sans-serif", fontSize: 32, fontWeight: 800, marginBottom: 8 }}>
          Privacy Policy
        </h1>
        <p style={{ color: "#8b90b8", marginBottom: 48 }}>Last updated: April 1, 2026</p>

        {[
          {
            title: "1. Information We Collect",
            content: `We collect information you provide when creating an account, including your name, email address, and business information. When you connect your WhatsApp Business Account, we store encrypted access tokens and associated account identifiers. We also collect usage data such as message logs and campaign performance metrics to provide our services.`,
          },
          {
            title: "2. How We Use Your Information",
            content: `We use your information to provide, operate, and improve OmniAgent's AI-powered outreach platform. This includes sending and receiving WhatsApp messages on your behalf, managing email campaigns, processing voice outreach, and generating AI-driven responses. We do not sell your personal data to third parties.`,
          },
          {
            title: "3. WhatsApp and Meta Data",
            content: `OmniAgent integrates with Meta's WhatsApp Business API. When you connect your WhatsApp Business Account, we receive and store an encrypted access token provided by Meta. We use this token solely to send and receive messages on your behalf. We comply with Meta's Platform Terms and WhatsApp Business Policy.`,
          },
          {
            title: "4. Data Storage and Security",
            content: `Your data is stored securely on encrypted servers. Access tokens are encrypted using industry-standard Fernet symmetric encryption before being stored in our database. We use HTTPS for all data transmission. We retain your data for as long as your account is active or as needed to provide services.`,
          },
          {
            title: "5. Third-Party Services",
            content: `OmniAgent uses the following third-party services: Meta (WhatsApp Business API), Google (OAuth authentication and Gmail API), and cloud infrastructure providers. Each of these services has their own privacy policies which govern their use of your data.`,
          },
          {
            title: "6. Your Rights",
            content: `You have the right to access, correct, or delete your personal data at any time. You can disconnect your WhatsApp Business Account or delete your OmniAgent account by contacting us. Upon account deletion, we will remove your personal data from our systems within 30 days.`,
          },
          {
            title: "7. Cookies",
            content: `We use a single authentication cookie (omniagent_token) to keep you logged in. This cookie is httpOnly, secure, and is not used for tracking or advertising purposes.`,
          },
          {
            title: "8. Contact Us",
            content: `If you have any questions about this Privacy Policy or how we handle your data, please contact us at: support@omniagent.ai`,
          },
        ].map(({ title, content }) => (
          <div key={title} style={{ marginBottom: 36 }}>
            <h2 style={{
              fontFamily: "'Syne', sans-serif", fontSize: 18, fontWeight: 700,
              color: "#f0f2ff", marginBottom: 12,
            }}>{title}</h2>
            <p style={{ color: "#8b90b8", lineHeight: 1.8, fontSize: 15 }}>{content}</p>
          </div>
        ))}

        <div style={{
          marginTop: 48, padding: "20px 24px", borderRadius: 12,
          background: "#0d0f1a", border: "1px solid rgba(255,255,255,0.06)",
          color: "#4a4f72", fontSize: 13, lineHeight: 1.6,
        }}>
          This privacy policy applies to OmniAgent SaaS platform. By using our service you agree to the collection and use of information in accordance with this policy.
        </div>

      </div>
    </div>
  );
};

export default PrivacyPolicy;