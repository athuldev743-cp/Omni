import React, { useEffect, useState } from "react";
import { api } from "../api";

declare global {
  interface Window {
    FB: any;
    fbAsyncInit: () => void;
  }
}

const ConnectMeta: React.FC = () => {
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [sdkReady, setSdkReady] = useState(false);

  const APP_ID = import.meta.env.VITE_META_APP_ID || "1270370071163693";
  const CONFIG_ID = import.meta.env.VITE_META_CONFIG_ID || "1711172183378816";

  // Load Facebook SDK
  useEffect(() => {
    if (document.getElementById("facebook-jssdk")) {
      setSdkReady(true);
      return;
    }

    window.fbAsyncInit = () => {
      window.FB.init({
        appId: APP_ID,
        cookie: true,
        xfbml: true,
        version: "v21.0",
      });
      setSdkReady(true);
    };

    const script = document.createElement("script");
    script.id = "facebook-jssdk";
    script.src = "https://connect.facebook.net/en_US/sdk.js";
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);
  }, [APP_ID]);

  const launchSignup = () => {
    if (!window.FB) {
      setStatus(
        "Facebook SDK not loaded yet. Please wait a moment and try again.",
      );
      return;
    }

    setLoading(true);
    setStatus(null);

    window.FB.login(
      async (response: any) => {
        if (!response.authResponse?.code) {
          setStatus("Meta login was cancelled or failed.");
          setLoading(false);
          return;
        }

        try {
          const { data } = await api.post("/whatsapp/onboard", {
            code: response.authResponse.code,
          });
          setStatus(
            `✅ WhatsApp connected! WABA: ${data.waba_id || "N/A"} | Phone ID: ${data.phone_number_id || "N/A"}`,
          );
        } catch (err: any) {
          setStatus(
            err?.response?.data?.detail ||
              "Failed to complete onboarding. Please try again.",
          );
        } finally {
          setLoading(false);
        }
      },
      {
        config_id: CONFIG_ID,
        response_type: "code",
        override_default_response_type: true,
        extras: {
          setup: {},
          featureType: "",
          sessionInfoVersion: "3",
        },
      },
    );
  };

  return (
    <div className="p-6 space-y-6 max-w-xl">
      <div>
        <h2 className="text-2xl font-semibold mb-1">Connect WhatsApp</h2>
        <p className="text-slate-400 text-sm">
          Click the button below to connect your WhatsApp Business Account in
          one click. You'll be prompted to log into Facebook and select your
          Business Account.
        </p>
      </div>

      <div className="bg-slate-900/70 border border-slate-700 rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
            W
          </div>
          <div>
            <div className="font-medium">WhatsApp Business</div>
            <div className="text-slate-400 text-xs">Meta Embedded Signup</div>
          </div>
        </div>

        <button
          onClick={launchSignup}
          disabled={loading || !sdkReady}
          className="w-full py-3 rounded-lg bg-green-500 hover:bg-green-400 text-white font-semibold transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin">⏳</span> Connecting...
            </>
          ) : !sdkReady ? (
            "Loading SDK..."
          ) : (
            "🔗 Connect WhatsApp Business"
          )}
        </button>

        {status && (
          <div
            className={`text-sm p-3 rounded-lg ${
              status.startsWith("✅")
                ? "bg-green-900/30 text-green-400 border border-green-800"
                : "bg-red-900/30 text-red-400 border border-red-800"
            }`}
          >
            {status}
          </div>
        )}
      </div>

      <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4 text-xs text-slate-400 space-y-1">
        <div className="font-medium text-slate-300 mb-2">
          What happens when you connect:
        </div>
        <div>1. Meta popup opens — log in with your Facebook account</div>
        <div>2. Select your WhatsApp Business Account (WABA)</div>
        <div>
          3. Your token + phone ID are encrypted and saved automatically
        </div>
        <div>
          4. OmniAgent can now send/receive WhatsApp messages for your account
        </div>
      </div>
    </div>
  );
};

export default ConnectMeta;
