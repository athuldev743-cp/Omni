import React, { useEffect, useMemo, useState } from "react";
import { createCampaign, fetchCampaigns, fetchReadyForMeetLeads, triggerCampaign, Lead, Campaign } from "../api";

const CampaignView: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[] | null>(null);
  const [leads, setLeads] = useState<Lead[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [queuedInfo, setQueuedInfo] = useState<string | null>(null);

  const [name, setName] = useState("Outreach Campaign");
  const [channel, setChannel] = useState<"email" | "whatsapp" | "voice">("whatsapp");
  const [description, setDescription] = useState("Hi! Thanks for your interest. Are you ready to schedule a quick meet?");
  const [selectedLeadIds, setSelectedLeadIds] = useState<Record<number, boolean>>({});
  const [selectedCampaignId, setSelectedCampaignId] = useState<number | null>(null);

  const selectedIds = useMemo(() => Object.keys(selectedLeadIds).filter((k) => selectedLeadIds[Number(k)]).map((k) => Number(k)), [selectedLeadIds]);

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

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onCreate = async () => {
    setLoading(true);
    setQueuedInfo(null);
    try {
      const created = await createCampaign({ name, description, channel });
      const updated = await fetchCampaigns();
      setCampaigns(updated);
      setSelectedCampaignId(created.id);
    } finally {
      setLoading(false);
    }
  };

  const onTrigger = async () => {
    if (!selectedCampaignId) return;
    if (selectedIds.length === 0) {
      setQueuedInfo("Select at least one lead.");
      return;
    }
    setLoading(true);
    setQueuedInfo(null);
    try {
      const resp = await triggerCampaign({ campaign_id: selectedCampaignId, lead_ids: selectedIds });
      setQueuedInfo(`Queued ${resp.queued} outreach jobs.`);
      await refresh();
      setSelectedLeadIds({});
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-semibold">Campaigns</h2>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4 space-y-4">
          <h3 className="font-semibold">Create Campaign</h3>

          <div className="space-y-3">
            <div>
              <label className="text-sm text-slate-300 block mb-1">Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100"
              />
            </div>

            <div>
              <label className="text-sm text-slate-300 block mb-1">Channel</label>
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value as any)}
                className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100"
              >
                <option value="email">email</option>
                <option value="whatsapp">whatsapp</option>
                <option value="voice">voice</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-slate-300 block mb-1">Description / Template</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full min-h-[110px] px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100"
              />
            </div>

            <button
              onClick={() => void onCreate()}
              disabled={loading}
              className="w-full py-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition-colors disabled:opacity-60"
            >
              {loading ? "Working..." : "Create Campaign"}
            </button>
          </div>
        </div>

        <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4 space-y-4">
          <h3 className="font-semibold">Trigger Outreach</h3>

          <div className="space-y-2">
            <label className="text-sm text-slate-300 block">Choose Campaign</label>
            <select
              value={selectedCampaignId ?? ""}
              onChange={(e) => setSelectedCampaignId(Number(e.target.value))}
              className="w-full px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-slate-100"
              disabled={!campaigns || campaigns.length === 0}
            >
              {(campaigns ?? []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.channel})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-300 block mb-2">Ready for Meet Leads</label>
            {leads === null ? (
              <div className="text-slate-300 text-sm">Loading leads...</div>
            ) : leads.length === 0 ? (
              <div className="text-slate-300 text-sm">No ready leads. Connect WhatsApp and message a lead to generate intent.</div>
            ) : (
              <div className="max-h-[320px] overflow-auto space-y-2">
                {leads.map((l) => (
                  <label key={l.id} className="flex items-start gap-3 p-2 rounded-lg border border-slate-800 bg-slate-950/30">
                    <input
                      type="checkbox"
                      checked={!!selectedLeadIds[l.id]}
                      onChange={(e) =>
                        setSelectedLeadIds((prev) => ({ ...prev, [l.id]: e.target.checked }))
                      }
                      className="mt-1"
                    />
                    <span>
                      <span className="block font-medium">{l.name}</span>
                      <span className="block text-xs text-slate-400">
                        {l.phone ? `Phone: ${l.phone}` : "Phone: —"}
                      </span>
                    </span>
                  </label>
                ))}
              </div>
            )}
          </div>

          <button
            onClick={() => void onTrigger()}
            disabled={loading || selectedIds.length === 0 || !selectedCampaignId}
            className="w-full py-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition-colors disabled:opacity-60"
          >
            {loading ? "Queuing..." : "Start Campaign"}
          </button>

          {queuedInfo ? <div className="text-sm text-slate-300">{queuedInfo}</div> : null}
        </div>
      </div>
    </div>
  );
};

export default CampaignView;

