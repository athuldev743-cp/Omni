import React from "react";

const Login: React.FC = () => {
  const handleGoogleLogin = () => {
    window.location.href = "/api/auth/google/login";
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="bg-slate-900/70 border border-slate-700 rounded-2xl p-10 shadow-2xl max-w-md w-full">
        <h1 className="text-3xl font-semibold mb-6 text-center">OmniAgent Login</h1>
        <p className="text-slate-300 text-sm mb-8 text-center">
          Connect your Google account to start multi-channel outreach.
        </p>
        <button
          onClick={handleGoogleLogin}
          className="w-full py-3 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold transition-colors"
        >
          Continue with Google
        </button>
      </div>
    </div>
  );
};

export default Login;

