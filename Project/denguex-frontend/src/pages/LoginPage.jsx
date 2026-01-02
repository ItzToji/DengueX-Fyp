import React, { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";
import { motion } from "framer-motion";

const LoginPage = ({ setUser }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://127.0.0.1:8000/api/login/", formData);
      
      // ✅ FIX: Token Save karna Zaroori hai
      if (response.data.token) {
          localStorage.setItem("token", response.data.token);
          localStorage.setItem("username", response.data.username);
          localStorage.setItem("is_admin", response.data.is_admin);
          setUser(response.data.username);
          navigate("/"); // Dashboard par jao
      } else {
          setError("❌ Login Successful but No Token Received.");
      }

    } catch (err) {
      console.error(err);
      setError("❌ Invalid username or password");
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const details = jwtDecode(credentialResponse.credential);
      const res = await axios.post("http://127.0.0.1:8000/api/google-login/", {
        email: details.email, name: details.name
      });

      // ✅ FIX: Google Login mein bhi Token Save karo
      if (res.data.token) {
          localStorage.setItem("token", res.data.token);
          localStorage.setItem("username", res.data.username);
          
          setUser(res.data.username);
          navigate("/");
      }
      
    } catch (err) {
      console.error(err);
      setError("❌ Google Login Failed.");
    }
  };

  return (
    <div className="min-h-screen flex bg-white font-sans">
      
      {/* --- LEFT SIDE: BRANDING --- */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-blue-600 to-blue-800 relative items-center justify-center overflow-hidden">
        <div className="absolute w-[500px] h-[500px] border border-white/20 rounded-full animate-pulse opacity-30"></div>
        <div className="absolute w-[300px] h-[300px] bg-white/10 rounded-full blur-3xl"></div>

        <motion.div
          className="absolute text-5xl z-10 opacity-80"
          animate={{ x: [0, 40, -40, 0], y: [0, -40, 40, 0], rotate: [0, 15, -15, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
        >
          🦟
        </motion.div>

        <div className="relative z-10 text-center px-10 text-white">
          <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.8 }}>
             <h1 className="text-6xl font-extrabold mb-4 tracking-tight">DengueX</h1>
             <p className="text-xl text-blue-100 font-light max-w-md mx-auto">
               Enterprise Grade Dengue Surveillance & Analytics System
             </p>
          </motion.div>
        </div>
      </div>

      {/* --- RIGHT SIDE: LOGIN FORM --- */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-slate-50">
        
        <motion.div 
          initial={{ x: 20, opacity: 0 }} 
          animate={{ x: 0, opacity: 1 }} 
          transition={{ duration: 0.6 }}
          className="w-full max-w-md bg-white p-10 rounded-2xl shadow-xl border border-slate-200"
        >
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-slate-800">Welcome Back</h2>
            <p className="text-slate-500 text-sm mt-2">Please login to your account</p>
          </div>

          {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-6 text-sm text-center border border-red-200">{error}</div>}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-slate-700 text-sm font-semibold mb-2 ml-1">Username</label>
              <input 
                type="text" 
                name="username" 
                onChange={handleChange} 
                className="w-full p-3 bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 transition" 
                placeholder="Enter username" 
                required 
              />
            </div>
            
            <div>
              <label className="block text-slate-700 text-sm font-semibold mb-2 ml-1">Password</label>
              <input 
                type="password" 
                name="password" 
                onChange={handleChange} 
                className="w-full p-3 bg-slate-50 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 transition" 
                placeholder="Enter password" 
                required 
              />
            </div>

            <div className="text-right">
                <Link to="/forgot-password" className="text-sm text-blue-600 hover:text-blue-800 font-medium hover:underline">
                    Forgot Password?
                </Link>
            </div>

            <motion.button 
                whileHover={{ scale: 1.01 }} 
                whileTap={{ scale: 0.99 }} 
                type="submit" 
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-lg shadow-md transition-all"
            >
                Sign In
            </motion.button>
          </form>

          <div className="mt-8">
             <div className="relative flex py-2 items-center">
                <div className="flex-grow border-t border-slate-200"></div>
                <span className="flex-shrink mx-4 text-slate-400 text-xs uppercase">Or Continue With</span>
                <div className="flex-grow border-t border-slate-200"></div>
             </div>
             <div className="flex justify-center mt-4">
                <GoogleLogin onSuccess={handleGoogleSuccess} onError={() => setError("Google Login Failed")} theme="outline" shape="pill" text="signin_with" width="250" />
             </div>
          </div>

          <p className="text-center mt-8 text-slate-500 text-sm">
            Don't have an account? <Link to="/signup" className="text-blue-600 font-bold hover:underline">Create Account</Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default LoginPage;