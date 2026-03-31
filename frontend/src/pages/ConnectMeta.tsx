import React, { useState } from "react";
import { api } from "../api";

const ConnectMeta: React.FC = () => {
  const [metaAccessToken, setMetaAccessToken] = useState("");
  const [metaWhatsappPhoneId, setMetaWhatsappPhoneId] = useState("");
  const [metaWhatsappVerifyToken, setMetaWhatsappVerifyToken] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      await api.post("/auth/meta/connect", {
        meta_access_token: metaAccessToken,
        meta_whatsapp_phone_id: metaWhatsappPhoneId,
        meta_whatsapp_verify_token: metaWhatsappVerifyToken || undefined,
      });
      setStatus("Meta WhatsApp connected.");
    } catch (err: any) {
      setStatus(err?.response?.data?.detail || "Failed to connect Meta.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-semibold">Connect Meta (WhatsApp)</h2>
      <p className="text-slate-300 text-sm">
        Paste your Meta WhatsApp access token and phone number ID. OmniAgent will encrypt and store them
        for sending auto-replies and triggering voice calls.
      </p>

      <form onSubmit={onConnect} className="space-y-3 max-w-xl">
        <div>
          <label className="text-sm text-slate-300 block mb-1">Meta Access Token</label>
          <input
            value={metaAccessToken}
            onChange={(e) => setMetaAccessToken(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100"
            required
          />
        </div>

        <div>
          <label className="text-sm text-slate-300 block mb-1">WhatsApp Phone Number ID</label>
          <input
            value={metaWhatsappPhoneId}
            onChange={(e) => setMetaWhatsappPhoneId(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100"
            required
          />
        </div>

        <div>
          <label className="text-sm text-slate-300 block mb-1">Webhook Verify Token (optional)</label>
          <input
            value={metaWhatsappVerifyToken}
            onChange={(e) => setMetaWhatsappVerifyToken(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition-colors disabled:opacity-60"
        >
          {loading ? "Connecting..." : "Connect Meta"}
        </button>

        {status ? <div className="text-sm text-slate-300">{status}</div> : null}
      </form>
    </div>
  );
};

export default ConnectMeta;

