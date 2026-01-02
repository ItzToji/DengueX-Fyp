import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"; 
import { AnimatePresence } from "framer-motion"; 

// --- IMPORTS ---
import Navbar from "./pages/NavBar"; // 👈 Navbar yahan se aayega
import Chatbot from "./components/Chatbot";
import Dashboard from "./components/Dashboard";
import Signup from "./components/Signup";
import Report from "./components/Report";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminDashboard from "./components/AdminDashboard";
import MosquitoLab from "./components/MosquitoLab";
import LoginPage from "./pages/LoginPage";
import ProfilePage from "./pages/ProfilePage";
import ForgotPassword from "./pages/ForgotPassword";
import NewsPage from "./pages/NewsPage";

// --- ROUTES LOGIC ---
const AdminRoute = ({ children }) => {
  const isAdmin = localStorage.getItem("is_admin") === "true";
  if (!isAdmin) return <Navigate to="/" replace />; 
  return children;
};

const UserRoute = ({ children }) => {
  const isAdmin = localStorage.getItem("is_admin") === "true";
  if (isAdmin) return <Navigate to="/admin" replace />; 
  return children;
};

// --- APP COMPONENT ---
export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem("username");
    if (storedUser) setUser(storedUser);
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
  };

  if (loading) return null;

  return (
    <BrowserRouter>
      <div className="bg-slate-50 min-h-screen flex flex-col font-sans text-slate-800">
        {/* ✅ Clean Navbar Usage */}
        <Navbar user={user} onLogout={handleLogout} />
        
        <main className="flex-grow">
          <AnimatePresence mode="wait">
            <Routes>
              {/* PUBLIC */}
              <Route path="/login" element={<LoginPage setUser={setUser} />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              
              {/* ADMIN */}
              <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />

              {/* USER */}
              <Route path="/" element={<UserRoute><Dashboard /></UserRoute>} />
              <Route path="/news" element={<UserRoute><NewsPage /></UserRoute>} />
              <Route path="/lab" element={<UserRoute><ProtectedRoute user={user}><MosquitoLab /></ProtectedRoute></UserRoute>} />
              <Route path="/report" element={<UserRoute><ProtectedRoute user={user}><Report /></ProtectedRoute></UserRoute>} />
              <Route path="/chat" element={<UserRoute><ProtectedRoute user={user}><div className="container mx-auto p-6 flex justify-center"><Chatbot /></div></ProtectedRoute></UserRoute>} />
              <Route path="/profile" element={<UserRoute><ProtectedRoute user={user}><ProfilePage /></ProtectedRoute></UserRoute>} />
            </Routes>
          </AnimatePresence>
        </main>
      </div>
    </BrowserRouter>
  );
}