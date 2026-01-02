import React, { useState } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

const ForgotPassword = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1: Enter Username, 2: Answer Question
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Form Data
  const [username, setUsername] = useState("");
  const [securityQuestion, setSecurityQuestion] = useState(""); // 👈 Yahan Question Store hoga
  const [answer, setAnswer] = useState("");
  const [newPassword, setNewPassword] = useState("");

  // Step 1: Username Bhejo -> Question Mangwao
const handleFetchQuestion = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/get-security-question/", { username });
      
      console.log("Backend Response:", res.data); // 👈 Ye Check Karein Console Mein

      // Agar key 'security_question' hai to usay use karein
      const question = res.data.question || res.data.security_question; 

      if (question) {
        setSecurityQuestion(question);
        setStep(2);
      } else {
        setError("Security question not set for this user.");
      }

    } catch (err) {
      console.error(err);
      setError("Username not found! Please check again.");
    } finally {
      setLoading(false);
    }
  };
  // Step 2: Answer & New Password Submit karo
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await axios.post("http://127.0.0.1:8000/api/reset-password-secure/", {
        username,
        answer,
        new_password: newPassword
      });
      setSuccess("Password Reset Successfully! Redirecting...");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to reset password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-6">
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden"
      >
        <div className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-black text-slate-800">Account Recovery</h2>
            <p className="text-sm text-slate-500 mt-1">
              {step === 1 ? "Enter your username to find your account" : "Answer your security question to reset"}
            </p>
          </div>

          {error && (
            <div className="mb-6 p-3 bg-red-50 border border-red-200 text-red-600 text-sm font-bold rounded-lg text-center flex items-center justify-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              {error}
            </div>
          )}

          {success && (
            <div className="mb-6 p-3 bg-green-50 border border-green-200 text-green-600 text-sm font-bold rounded-lg text-center flex items-center justify-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
              {success}
            </div>
          )}

          {/* --- STEP 1: USERNAME INPUT --- */}
          {step === 1 && (
            <form onSubmit={handleFetchQuestion} className="space-y-6">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Username</label>
                <input 
                  type="text" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-bold text-slate-700"
                  placeholder="Enter your username"
                  required
                />
              </div>
              <button 
                type="submit" 
                disabled={loading}
                className="w-full py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-blue-500/30 transition-all transform active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {loading ? "Searching..." : "Find Account"}
              </button>
            </form>
          )}

          {/* --- STEP 2: SECURITY QUESTION & NEW PASSWORD --- */}
          {step === 2 && (
            <form onSubmit={handleResetPassword} className="space-y-6">
              
              {/* ✅ SECURITY QUESTION DISPLAY */}
              <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded-r-lg">
                <p className="text-xs font-bold text-blue-400 uppercase mb-1">Security Question</p>
                <p className="text-lg font-bold text-blue-900">
                  {securityQuestion || "Loading question..."}
                </p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Your Answer</label>
                <input 
                  type="text" 
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-bold text-slate-700"
                  placeholder="Type your answer here"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">New Password</label>
                <input 
                  type="password" 
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-bold text-slate-700"
                  placeholder="••••••••"
                  required
                />
              </div>

              <button 
                type="submit" 
                disabled={loading}
                className="w-full py-3.5 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl shadow-lg shadow-green-500/30 transition-all transform active:scale-95 disabled:opacity-70 disabled:cursor-not-allowed"
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>
            </form>
          )}

        </div>
        
        <div className="bg-slate-50 px-8 py-4 border-t border-slate-200 text-center">
          <Link to="/login" className="text-sm font-bold text-slate-500 hover:text-blue-600 transition-colors">
            ← Back to Login
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default ForgotPassword;