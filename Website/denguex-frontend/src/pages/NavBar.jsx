import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

// --- 🟦 PRO ICONS ---
const Icons = {
  Home: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>,
  News: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>,
  Lab: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>,
  Report: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>,
  Chat: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>,
  Bell: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>,
  Logout: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
};

const Navbar = ({ user, onLogout }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const isAdmin = localStorage.getItem("is_admin") === "true";
  
  if (["/login", "/signup", "/forgot-password"].includes(location.pathname)) return null;

  const handleLogoutClick = () => {
    onLogout();
    localStorage.clear();
    navigate("/login");
  };

  const NavItem = ({ to, label, icon: Icon }) => {
    const isActive = location.pathname === to;
    return (
      <Link 
        to={to} 
        className={`relative px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-semibold transition-all duration-200 
        ${isActive 
            ? "bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-200" 
            : "text-slate-500 hover:text-slate-900 hover:bg-slate-50"
        }`}
      >
        <Icon />
        {label}
      </Link>
    );
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-white border-b border-slate-200 shadow-sm">
      <div className="container mx-auto px-6 h-16 flex justify-between items-center">
        
        {/* 1. BRAND LOGO - Clean & Corporate */}
        <Link to={isAdmin ? "/admin" : "/"} className="flex items-center gap-2 group">
          <div className="bg-blue-600 text-white w-8 h-8 rounded-lg flex items-center justify-center font-black text-sm tracking-tighter shadow-sm group-hover:bg-blue-700 transition-colors">
            DX
          </div>
          <div className="flex flex-col">
            <h1 className="font-bold text-lg leading-none text-slate-800 tracking-tight group-hover:text-blue-600 transition-colors">
              DengueX
            </h1>
            {isAdmin && <span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Admin Console</span>}
          </div>
        </Link>

        {/* 2. NAVIGATION - Center Aligned */}
        {!isAdmin && (
          <nav className="hidden md:flex items-center gap-1">
            <NavItem to="/" label="Dashboard" icon={Icons.Home} />
            <NavItem to="/news" label="News" icon={Icons.News} />
            <NavItem to="/report" label="Report" icon={Icons.Report} />
            <NavItem to="/chat" label="Assistant" icon={Icons.Chat} />
            <NavItem to="/lab" label="Lab" icon={Icons.Lab} />
          </nav>
        )}

        {/* 3. USER PROFILE - Professional */}
        <div className="flex items-center gap-4">
          
          {/* Notifications */}
          <button className="relative p-2 text-slate-400 hover:text-blue-600 transition-colors rounded-full hover:bg-slate-50">
             <Icons.Bell />
             <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
          </button>

          {/* Vertical Divider */}
          <div className="h-6 w-px bg-slate-200"></div>

          {user ? (
            <div className="flex items-center gap-3">
               {/* User Info & Avatar */}
               <Link to="/profile" className="flex items-center gap-3 group">
                  <div className="text-right hidden sm:block">
                    <p className="text-sm font-bold text-slate-700 leading-none group-hover:text-blue-600 transition-colors">{user}</p>
                    <p className="text-[10px] text-emerald-600 font-medium mt-0.5">Online</p>
                  </div>
                  <div className="w-9 h-9 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 font-bold text-sm uppercase group-hover:ring-2 ring-blue-100 transition-all">
                    {user.charAt(0)}
                  </div>
               </Link>
               
               {/* Logout */}
               <button 
                 onClick={handleLogoutClick} 
                 className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-all" 
                 title="Secure Logout"
               >
                 <Icons.Logout />
               </button>
            </div>
          ) : (
            <div className="flex gap-3">
              <Link to="/login" className="px-4 py-2 text-sm font-semibold text-slate-600 hover:text-blue-600 transition-colors">Log In</Link>
              <Link to="/signup" className="px-5 py-2 text-sm font-bold text-white bg-slate-900 rounded-lg hover:bg-slate-800 shadow-sm transition-all transform hover:-translate-y-0.5">Get Started</Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;