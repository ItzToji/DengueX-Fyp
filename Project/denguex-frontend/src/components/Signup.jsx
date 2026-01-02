import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";

const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ 
    username: "", 
    password: "", 
    security_question: "", 
    security_answer: "" 
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  // --- 🔒 REAL-TIME PASSWORD CHECK LOGIC ---
  const password = formData.password;
  const validations = {
    length: password.length >= 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    number: /\d/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post("http://127.0.0.1:8000/api/signup/", formData);
      alert("🎉 Account created! Login now.");
      navigate("/login");
    } catch (err) {
      alert("Error: " + (err.response?.data?.error || "Signup Failed"));
    } finally { setLoading(false); }
  };

  // Helper Component for Checklist Item
  const Requirement = ({ met, text }) => (
    <div className={`flex items-center gap-2 text-xs font-medium transition-all duration-300 ${met ? "text-green-600" : "text-red-400"}`}>
      <span>{met ? "✅" : "❌"}</span>
      <span className={met ? "line-through opacity-70" : ""}>{text}</span>
    </div>
  );

  // Floating Card Component (Decoration)
  const FloatingCard = ({ title, value, icon, delay, className }) => (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay, duration: 0.8 }}
      className={`absolute hidden xl:flex flex-col items-center justify-center w-40 h-32 bg-white border border-slate-100 rounded-xl shadow-xl text-slate-700 ${className}`}
    >
      <div className="text-3xl mb-1">{icon}</div>
      <div className="text-xs text-slate-400 uppercase font-bold tracking-wider">{title}</div>
      <div className="text-lg font-bold text-blue-600">{value}</div>
    </motion.div>
  );

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-slate-50">
      
      {/* --- BACKGROUND DECORATION --- */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
          <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-100/50 rounded-full blur-[100px]"></div>
          <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-teal-100/50 rounded-full blur-[100px]"></div>
      </div>

      {/* --- FLOATING INFO CARDS --- */}
      <FloatingCard className="top-[20%] left-[15%]" icon="🛡️" title="Secure" value="Encrypted" delay={0.2} />
      <FloatingCard className="bottom-[20%] left-[10%]" icon="👩‍⚕️" title="Support" value="24/7 AI" delay={0.4} />
      <FloatingCard className="top-[25%] right-[15%]" icon="📉" title="Recovery" value="98.5%" delay={0.6} />
      <FloatingCard className="bottom-[25%] right-[12%]" icon="🦟" title="Tracking" value="Live" delay={0.8} />

      {/* --- MAIN FORM --- */}
      <motion.div 
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-lg bg-white p-10 rounded-2xl shadow-2xl border border-slate-200"
      >
        <div className="text-center mb-6">
            <h2 className="text-3xl font-extrabold text-slate-800">Create Account</h2>
            <p className="text-slate-500 text-sm mt-2">Join DengueX Health Network</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          
          {/* Username */}
          <div>
              <label className="block text-slate-700 text-xs font-bold mb-1 uppercase ml-1">Username</label>
              <input type="text" name="username" required onChange={handleChange} className="w-full p-3 bg-slate-50 border border-slate-300 rounded-lg text-slate-800 focus:ring-2 focus:ring-blue-500 outline-none transition" />
          </div>
            
          {/* Password with Live Validation */}
          <div>
              <label className="block text-slate-700 text-xs font-bold mb-1 uppercase ml-1">Password</label>
              <input 
                type="password" 
                name="password" 
                required 
                onChange={handleChange} 
                className={`w-full p-3 bg-slate-50 border rounded-lg text-slate-800 focus:ring-2 outline-none transition ${
                    validations.length && validations.upper && validations.lower && validations.number && validations.special 
                    ? "border-green-400 focus:ring-green-200" 
                    : "border-slate-300 focus:ring-blue-500"
                }`}
              />
              
              {/* --- PASSWORD CHECKLIST UI --- */}
              <div className="mt-3 grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <Requirement met={validations.length} text="At least 8 chars" />
                  <Requirement met={validations.upper} text="1 Uppercase (A-Z)" />
                  <Requirement met={validations.lower} text="1 Lowercase (a-z)" />
                  <Requirement met={validations.number} text="1 Number (0-9)" />
                  <Requirement met={validations.special} text="1 Special (!@#$)" />
              </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
                <label className="block text-slate-700 text-xs font-bold mb-1 uppercase ml-1">Security Question</label>
                <input type="text" name="security_question" placeholder="e.g. Pet Name?" required onChange={handleChange} className="w-full p-3 bg-slate-50 border border-slate-300 rounded-lg text-slate-800 focus:ring-2 focus:ring-blue-500 outline-none transition" />
            </div>
            <div>
                <label className="block text-slate-700 text-xs font-bold mb-1 uppercase ml-1">Security Answer</label>
                <input type="text" name="security_answer" placeholder="Answer" required onChange={handleChange} className="w-full p-3 bg-slate-50 border border-slate-300 rounded-lg text-slate-800 focus:ring-2 focus:ring-blue-500 outline-none transition" />
            </div>
          </div>

          <motion.button 
            whileHover={{ scale: 1.01 }} 
            whileTap={{ scale: 0.99 }} 
            type="submit" 
            disabled={loading} 
            className="w-full bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-700 hover:to-teal-600 text-white font-bold py-3.5 rounded-lg shadow-md transition-all mt-4"
          >
            {loading ? "Creating Account..." : "Create Account"}
          </motion.button>
        </form>
        
        <p className="text-center mt-6 text-slate-500 text-sm">
          Already a member? <Link to="/login" className="text-blue-600 font-bold hover:underline">Login here</Link>
        </p>
      </motion.div>
    </div>
  );
};

export default Signup;