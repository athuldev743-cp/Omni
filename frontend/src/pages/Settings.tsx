import React, { useState } from "react";
import { api } from "../api";

const safeParseJson = (value: string): any | null => {
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
};

const Settings: React.FC = () => {
  const [name, setName] = useState("");
  const [tone, setTone] = useState("");
  const [businessInfoRaw, setBusinessInfoRaw] = useState("{\n  \"industry\": \"\"\n}");
  const [productsRaw, setProductsRaw] = useState("{\n  \"products\": []\n}");
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);
    try {
      const business_info = safeParseJson(businessInfoRaw);
      if (business_info === null) {
        throw new Error("business_info must be valid JSON");
      }
      const products = safeParseJson(productsRaw);
      if (products === null) {
        throw new Error("products must be valid JSON");
      }

      await api.patch("/tenants/me", {
        name: name || undefined,
        tone: tone || undefined,
        business_info,
        products,
      });
      setStatus("Settings updated.");
    } catch (err: any) {
      setStatus(err?.response?.data?.detail || err?.message || "Failed to save.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-semibold">Settings</h2>
      <p className="text-slate-300 text-sm">
        Update tenant tone, business info, and product metadata. These are used by OmniAgent to generate AI
        summaries and outreach content.
      </p>

      <form onSubmit={onSave} className="space-y-4 max-w-3xl">
        <div>
          <label className="text-sm text-slate-300 block mb-1">Tenant Name (optional)</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100"
          />
        </div>

        <div>
          <label className="text-sm text-slate-300 block mb-1">Tone (optional)</label>
          <input
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            className="w-full px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100"
          />
        </div>

        <div>
          <label className="text-sm text-slate-300 block mb-1">Business Info (JSON)</label>
          <textarea
            value={businessInfoRaw}
            onChange={(e) => setBusinessInfoRaw(e.target.value)}
            className="w-full min-h-[120px] px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100 font-mono text-xs"
          />
        </div>

        <div>
          <label className="text-sm text-slate-300 block mb-1">Products (JSON)</label>
          <textarea
            value={productsRaw}
            onChange={(e) => setProductsRaw(e.target.value)}
            className="w-full min-h-[120px] px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-slate-100 font-mono text-xs"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition-colors disabled:opacity-60"
        >
          {loading ? "Saving..." : "Save Settings"}
        </button>

        {status ? <div className="text-sm text-slate-300">{status}</div> : null}
      </form>
    </div>
  );
};

export default Settings;

