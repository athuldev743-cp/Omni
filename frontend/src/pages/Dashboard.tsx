import React, { useEffect, useState } from "react";
import { fetchReadyForMeetLeads, fetchWallet, Lead, Wallet } from "../api";

const Dashboard: React.FC = () => {
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

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-semibold">Dashboard</h2>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4">
          <h3 className="font-semibold mb-2">Credit Balance</h3>
          <p className="text-3xl font-bold text-emerald-400">
            {wallet ? wallet.wallet_balance : "..."}
          </p>
        </div>
        <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-4 md:col-span-2">
          <h3 className="font-semibold mb-2">Ready for Meet Leads</h3>
          <p className="text-slate-300 text-sm mb-4">
            Leads marked as <span className="text-emerald-400">READY_FOR_MEET</span> via WhatsApp intent
            detection will appear here.
          </p>

          {loadingLeads ? (
            <div className="text-slate-300 text-sm">Loading leads...</div>
          ) : leads && leads.length > 0 ? (
            <div className="space-y-3">
              {leads.map((l) => (
                <div key={l.id} className="border border-slate-800 rounded-lg p-3">
                  <div className="font-medium">{l.name}</div>
                  <div className="text-slate-300 text-xs mt-1">
                    {l.email ? `Email: ${l.email}` : "Email: —"}
                  </div>
                  <div className="text-slate-300 text-xs mt-1">
                    {l.phone ? `Phone: ${l.phone}` : "Phone: —"}
                  </div>
                  <div className="text-slate-500 text-xs mt-1">
                    Source: {l.source || "—"}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-300 text-sm">No leads ready for meet yet.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

