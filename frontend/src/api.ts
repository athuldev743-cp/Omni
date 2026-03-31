import axios from "axios";

export const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL ??
    "https://omni-backend-phxz.onrender.com/api",
  withCredentials: true,
});

export interface User {
  id: number;
  email: string;
  tenant_id: number;
}

export interface Wallet {
  tenant_id: number;
  wallet_balance: number;
}

export interface Lead {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  source?: string;
  ready_for_meet: boolean;
  created_at: string;
}

export interface Campaign {
  id: number;
  name: string;
  description?: string;
  channel: string;
  created_at: string;
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

export async function fetchWallet(): Promise<Wallet> {
  const { data } = await api.get<Wallet>("/billing/wallet");
  return data;
}

export async function fetchReadyForMeetLeads(): Promise<Lead[]> {
  const { data } = await api.get<Lead[]>("/leads/ready_for_meet");
  return data;
}

export async function fetchCampaigns(): Promise<Campaign[]> {
  const { data } = await api.get<Campaign[]>("/campaigns");
  return data;
}

export async function createCampaign(input: {
  name: string;
  description?: string;
  channel: string;
}): Promise<Campaign> {
  const { data } = await api.post<Campaign>("/campaigns", input);
  return data;
}

export async function triggerCampaign(input: {
  campaign_id: number;
  lead_ids: number[];
}): Promise<{ queued: number }> {
  const { data } = await api.post<{ queued: number }>("/campaigns/trigger", input);
  return data;
}

