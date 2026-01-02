import React, { useState, useEffect } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";

// --- 🛠️ ICONS ---
const Icons = {
  Home: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>,
  Chart: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>,
  News: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" /></svg>,
  Bulb: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>,
  ArrowLeft: () => <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>,
  Users: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>,
  Trash: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>,
  Eye: () => <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>,
  Close: () => <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
};

const getFullUrl = (path) => {
  if (!path) return null;
  if (path.startsWith("http")) return path;
  return `http://127.0.0.1:8000${path}`;
};

const CITIES = ["All Pakistan", "Lahore", "Karachi", "Islamabad", "Rawalpindi", "Multan", "Peshawar", "Quetta", "Faisalabad"];

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [reports, setReports] = useState([]);
  const [allCityStats, setAllCityStats] = useState([]); 
  const [users, setUsers] = useState([]); 
  const [newsList, setNewsList] = useState([]); 
  const [tipsList, setTipsList] = useState([]); 
  const [selectedReport, setSelectedReport] = useState(null);

  // Forms
  const [statsData, setStatsData] = useState({ city_name: "", active_cases: "", recovered: "", deaths: "", latitude: "", longitude: "" });
  const [newsData, setNewsData] = useState({ title: "", content: "", city: "All Pakistan" });
  const [tipData, setTipData] = useState({ title: "", description: "" });

  const token = localStorage.getItem("token");

  useEffect(() => {
    fetchStats(); fetchReports(); fetchUsers(); fetchNews(); fetchTips(); 
  }, []);

  const fetchReports = async () => { try { const res = await axios.get("http://127.0.0.1:8000/api/admin/all-reports/", { headers: { Authorization: `Token ${token}` }}); setReports(res.data); } catch (err) {} };
  const fetchStats = async () => { try { const res = await axios.get("http://127.0.0.1:8000/api/dashboard-data/"); const data = res.data.stats || res.data.city_stats || res.data; setAllCityStats(Array.isArray(data) ? data : []); } catch(err) {} }
  const fetchUsers = async () => { try { const res = await axios.get("http://127.0.0.1:8000/api/admin/users/", { headers: { Authorization: `Token ${token}` }}); setUsers(res.data); } catch (err) {} };
  const fetchNews = async () => { try { const res = await axios.get("http://127.0.0.1:8000/api/news/", { headers: { Authorization: `Token ${token}` }}); setNewsList(res.data); } catch (err) {} };
  const fetchTips = async () => { try { const res = await axios.get("http://127.0.0.1:8000/api/health-tips/", { headers: { Authorization: `Token ${token}` }}); setTipsList(res.data); } catch (err) {} };

  // --- DELETE CITY ---
  const handleDeleteCity = async (id, name) => {
      if(!window.confirm(`⚠️ Are you sure you want to DELETE ${name}?`)) return;
      try {
          await axios.post("http://127.0.0.1:8000/api/admin/delete-city/", { id: id }, { headers: { Authorization: `Token ${token}` } });
          alert(`🗑️ ${name} Deleted!`);
          fetchStats(); 
      } catch (err) { alert("Delete failed!"); }
  };

  // --- ✅ DELETE NEWS / TIPS (New Function) ---
  const handleDeleteItem = async (id, type) => {
      const endpoint = type === 'news' ? "delete-news/" : "delete-tip/";
      if(!window.confirm(`⚠️ Are you sure you want to DELETE this ${type === 'news' ? 'Alert' : 'Health Tip'}?`)) return;
      
      try {
          await axios.post(`http://127.0.0.1:8000/api/admin/${endpoint}`, { id: id }, { headers: { Authorization: `Token ${token}` } });
          alert(`🗑️ Deleted Successfully!`);
          if(type === 'news') fetchNews(); else fetchTips(); // Refresh List
      } catch (err) { 
          alert("Delete failed! Check backend logs."); 
      }
  };

  const handleAddOrUpdateCity = async () => {
    if (!statsData.city_name) return alert("City Name Required");
    const payload = { 
        city_name: statsData.city_name.trim(), 
        active_cases: parseInt(statsData.active_cases) || 0, 
        recovered: parseInt(statsData.recovered) || 0, 
        deaths: parseInt(statsData.deaths) || 0,
        latitude: statsData.latitude ? parseFloat(statsData.latitude) : null,
        longitude: statsData.longitude ? parseFloat(statsData.longitude) : null
    };
    try { await axios.post("http://127.0.0.1:8000/api/admin/update-stats/", payload, { headers: { Authorization: `Token ${token}` } }); alert(`✅ City Updated`); setStatsData({ city_name: "", active_cases: "", recovered: "", deaths: "", latitude: "", longitude: "" }); fetchStats(); } catch (err) { alert("Update Failed!"); }
  };

  const handleStatusUpdate = async (id, newStatus) => {
    setReports(prev => prev.map(r => r.id === id ? { ...r, ai_result: newStatus } : r));
    if(selectedReport && selectedReport.id === id) setSelectedReport({...selectedReport, ai_result: newStatus});
    try { await axios.post("http://127.0.0.1:8000/api/admin/update-status/", { id, status: newStatus }, { headers: { Authorization: `Token ${token}` } }); } catch (err) {}
  };

  const handlePost = async (type) => {
     try {
       const endpoint = type === 'news' ? "post-news/" : "add-tip/";
       const payload = type === 'news' ? newsData : tipData;
       await axios.post(`http://127.0.0.1:8000/api/admin/${endpoint}`, payload, { headers: { Authorization: `Token ${token}` } });
       alert("Posted!");
       if(type === 'news') { setNewsData({ title: "", content: "", city: "All Pakistan" }); fetchNews(); } 
       else { setTipData({ title: "", description: "" }); fetchTips(); }
     } catch (err) { alert("Failed to publish"); }
  };

  const handleBlockToggle = async (userId, currentStatus) => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/api/admin/toggle-block-user/", { user_id: userId }, { headers: { Authorization: `Token ${token}` } });
      setUsers(users.map(u => u.id === userId ? { ...u, is_active: res.data.is_active } : u));
      alert("User Status Updated");
    } catch (err) { alert("Failed"); }
  };

  return (
    <div className="flex h-screen bg-[#F1F5F9] font-sans text-slate-800 overflow-hidden relative">
      
      {/* SIDEBAR */}
      <aside className="w-72 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col shadow-2xl z-20 border-r border-slate-700/50">
        <div className="h-24 flex items-center px-8 border-b border-slate-700/50">
           <div className="w-10 h-10 bg-gradient-to-tr from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-lg mr-4 shadow-lg shadow-indigo-500/30">DX</div>
           <div>
             <span className="text-white font-black text-xl tracking-tight block">Dengue<span className="text-indigo-400">X</span></span>
             <span className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">Admin Console</span>
           </div>
        </div>
        <nav className="flex-1 p-6 space-y-3 mt-4 overflow-y-auto custom-scrollbar">
           {[{ id: 'overview', label: 'Reports', icon: Icons.Home }, 
             { id: 'analytics', label: 'Analytics', icon: Icons.Chart }, 
             { id: 'users', label: 'Users', icon: Icons.Users }, 
             { id: 'broadcast', label: 'News Alert', icon: Icons.News },  // ✅ Renamed
             { id: 'tips', label: 'Health Tips', icon: Icons.Bulb }]      // ✅ Renamed
           .map((item) => (
             <button key={item.id} onClick={() => setActiveTab(item.id)} className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl text-sm font-bold transition-all duration-300 group ${activeTab === item.id ? "bg-indigo-600/10 text-indigo-400 border border-indigo-600/20 shadow-inner" : "text-slate-400 hover:bg-white/5 hover:text-white"}`}>
               <span className={`transition-transform duration-300 ${activeTab === item.id ? "scale-110" : "group-hover:scale-110"}`}><item.icon /></span> 
               {item.label}
               {activeTab === item.id && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400 shadow-[0_0_10px_rgba(129,140,248,0.8)]"></div>}
             </button>
           ))}
        </nav>
        <div className="p-6 border-t border-slate-700/50 bg-slate-900/50">
           <Link to="/"><button className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-xl text-xs font-bold text-slate-300 bg-slate-800 hover:bg-slate-700 hover:text-white transition-all border border-slate-700"><Icons.ArrowLeft /> Return to Website</button></Link>
        </div>
      </aside>

      {/* MAIN */}
      <main className="flex-1 flex flex-col overflow-hidden relative z-10 bg-[#F8FAFC]">
        <header className="h-24 bg-white/80 backdrop-blur-md border-b border-slate-200/60 flex items-center justify-between px-10 sticky top-0 z-30 shadow-sm/50">
           <div>
             {/* ✅ Dynamic Title */}
             <h2 className="text-3xl font-black text-slate-800 capitalize tracking-tight">
                {activeTab === 'broadcast' ? 'News Alerts' : activeTab === 'tips' ? 'Health Tips' : activeTab}
             </h2>
             <p className="text-xs text-slate-500 font-medium mt-1">Manage and monitor your system in real-time</p>
           </div>
           <div className="flex items-center gap-4">
             <div className="bg-white border border-slate-200 px-4 py-2 rounded-full shadow-sm text-xs font-bold text-slate-600 flex items-center gap-2">
               <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Server Online
             </div>
             <div className="w-10 h-10 bg-gradient-to-r from-slate-200 to-slate-300 rounded-full border-2 border-white shadow-md"></div>
           </div>
        </header>

        <div className="flex-1 overflow-y-auto p-10 custom-scrollbar">
          <div className="max-w-7xl mx-auto space-y-10">
            
            {/* --- TAB 1: OVERVIEW (REPORTS) --- */}
            {activeTab === "overview" && (
              <div className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[{t:"Total Incidents",v:reports.length, c:"from-blue-500 to-indigo-600"},{t:"Pending Review",v:reports.filter(r=>!r.ai_result.includes('Resolved')).length, c:"from-amber-400 to-orange-500"},{t:"Resolved Cases",v:reports.filter(r=>r.ai_result.includes('Resolved')).length, c:"from-emerald-400 to-green-600"}].map((c,i)=>(
                    <motion.div initial={{opacity:0, y:20}} animate={{opacity:1, y:0}} transition={{delay:i*0.1}} key={i} className={`relative overflow-hidden bg-gradient-to-br ${c.c} p-6 rounded-3xl shadow-lg shadow-slate-200 text-white`}>
                      <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-white/20 rounded-full blur-2xl"></div>
                      <h4 className="text-white/80 text-xs font-bold uppercase tracking-wider">{c.t}</h4>
                      <div className="text-5xl font-black mt-3 tracking-tighter">{c.v}</div>
                    </motion.div>
                  ))}
                </div>
                
                <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
                  <div className="px-8 py-6 border-b border-slate-50 flex justify-between items-center">
                    <h3 className="font-bold text-lg text-slate-800">Recent Reports</h3>
                    <button onClick={fetchReports} className="text-indigo-600 text-xs font-bold hover:underline">Refresh List</button>
                  </div>
                  <table className="w-full text-sm text-left">
                      <thead className="bg-slate-50/50 text-slate-400 font-bold uppercase text-[10px] tracking-wider">
                          <tr><th className="p-6">User Identity</th><th className="p-6">Current Status</th><th className="p-6">Date</th><th className="p-6 text-center">Action</th></tr>
                      </thead>
                      <tbody className="divide-y divide-slate-50">
                          {reports.map((r, idx)=>(
                              <tr key={r.id} className="hover:bg-slate-50/80 transition-colors group">
                                  <td className="p-6">
                                    <div className="flex items-center gap-3">
                                      <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 font-bold text-xs">{r.username.charAt(0)}</div>
                                      <span className="font-bold text-slate-700">{r.username}</span>
                                    </div>
                                  </td>
                                  <td className="p-6"><span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide border ${r.ai_result.includes("Resolved") ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-amber-50 text-amber-600 border-amber-100'}`}>{r.ai_result}</span></td>
                                  <td className="p-6 text-slate-400 text-xs font-mono">{r.date}</td>
                                  <td className="p-6 text-center">
                                      <button onClick={() => setSelectedReport(r)} className="px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-xl text-xs font-bold hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm">Review Details</button>
                                  </td>
                              </tr>
                          ))}
                      </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* --- TAB 2: ANALYTICS --- */}
            {activeTab === "analytics" && (
              <div className="space-y-8">
                 <div className="relative rounded-3xl overflow-hidden shadow-2xl shadow-indigo-500/20 bg-slate-900 border border-slate-800">
                    <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
                    <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-purple-600/10 rounded-full blur-[80px] translate-y-1/2 -translate-x-1/2 pointer-events-none"></div>
                    
                    <div className="relative z-10 p-10">
                        <div className="flex items-center gap-4 mb-8">
                          <div className="p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 text-indigo-400"><Icons.Chart /></div>
                          <div>
                            <h3 className="font-black text-2xl text-white tracking-tight">Data Management Center</h3>
                            <p className="text-slate-400 text-sm">Update statistics and geolocation for regional tracking</p>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-6">
                            <div className="lg:col-span-3 space-y-2">
                                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">City / Region</label>
                                <input type="text" value={statsData.city_name} onChange={(e)=>setStatsData({...statsData, city_name: e.target.value})} className="w-full h-12 px-4 bg-slate-800/50 border border-slate-700 rounded-xl focus:border-indigo-500 focus:bg-slate-800 focus:ring-1 focus:ring-indigo-500/50 outline-none text-white font-bold placeholder-slate-600 transition-all" placeholder="Enter city name..." />
                            </div>
                            <div className="lg:col-span-5 grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Latitude</label>
                                    <input type="number" value={statsData.latitude || ""} onChange={(e)=>setStatsData({...statsData, latitude: e.target.value})} className="w-full h-12 px-4 bg-slate-800/50 border border-slate-700 rounded-xl focus:border-indigo-500 outline-none text-slate-300 font-mono text-sm placeholder-slate-700" placeholder="00.0000" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pl-1">Longitude</label>
                                    <div className="flex gap-2">
                                      <input type="number" value={statsData.longitude || ""} onChange={(e)=>setStatsData({...statsData, longitude: e.target.value})} className="w-full h-12 px-4 bg-slate-800/50 border border-slate-700 rounded-xl focus:border-indigo-500 outline-none text-slate-300 font-mono text-sm placeholder-slate-700" placeholder="00.0000" />
                                      <button onClick={async () => {
                                            if(!statsData.city_name) return alert("Enter City Name first!");
                                            try {
                                                const res = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${statsData.city_name}`);
                                                if(res.data && res.data[0]) { setStatsData({ ...statsData, latitude: res.data[0].lat, longitude: res.data[0].lon }); } 
                                                else { alert("Location not found!"); }
                                            } catch(e) { alert("Failed to fetch location"); }
                                        }} className="h-12 w-12 flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl flex items-center justify-center transition-all shadow-lg shadow-indigo-500/20" title="Auto-Locate">📍</button>
                                    </div>
                                </div>
                            </div>
                            <div className="lg:col-span-4 grid grid-cols-3 gap-2 pt-6 lg:pt-0">
                                <div className="space-y-1">
                                  <label className="text-[9px] font-bold text-blue-400 uppercase text-center block">Active</label>
                                  <input type="number" value={statsData.active_cases} onChange={(e)=>setStatsData({...statsData, active_cases: e.target.value})} className="w-full h-10 text-center bg-blue-500/10 border border-blue-500/30 rounded-lg text-blue-400 font-bold outline-none focus:bg-blue-500/20" placeholder="0" />
                                </div>
                                <div className="space-y-1">
                                  <label className="text-[9px] font-bold text-emerald-400 uppercase text-center block">Recov</label>
                                  <input type="number" value={statsData.recovered} onChange={(e)=>setStatsData({...statsData, recovered: e.target.value})} className="w-full h-10 text-center bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 font-bold outline-none focus:bg-emerald-500/20" placeholder="0" />
                                </div>
                                <div className="space-y-1">
                                  <label className="text-[9px] font-bold text-red-400 uppercase text-center block">Fatal</label>
                                  <input type="number" value={statsData.deaths} onChange={(e)=>setStatsData({...statsData, deaths: e.target.value})} className="w-full h-10 text-center bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 font-bold outline-none focus:bg-red-500/20" placeholder="0" />
                                </div>
                            </div>
                        </div>
                        
                        <div className="mt-8 flex justify-end">
                            <button onClick={handleAddOrUpdateCity} className="px-8 py-3 bg-white text-slate-900 font-black rounded-xl hover:bg-indigo-50 hover:text-indigo-900 hover:shadow-[0_0_20px_rgba(255,255,255,0.3)] transition-all transform active:scale-95 flex items-center gap-2">
                                UPDATE DATABASE <span className="text-indigo-600">⚡</span>
                            </button>
                        </div>
                    </div>
                 </div>

                 <div>
                    <div className="flex justify-between items-end mb-6 px-2">
                        <div>
                          <h3 className="font-black text-2xl text-slate-800">Live Database</h3>
                          <p className="text-slate-500 text-sm">Real-time statistics per region</p>
                        </div>
                        <span className="bg-slate-200 text-slate-600 px-4 py-1.5 rounded-full text-xs font-bold">{allCityStats.length} Records Found</span>
                    </div>
                    
                    {allCityStats.length > 0 ? (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {allCityStats.map((item, i) => (
                                <motion.div initial={{opacity:0, scale:0.9}} animate={{opacity:1, scale:1}} transition={{delay:i*0.05}} key={i} className="group relative bg-white border border-slate-100 rounded-[2rem] p-1 shadow-sm hover:shadow-xl hover:shadow-indigo-100 hover:-translate-y-1 transition-all duration-300">
                                    <div className="absolute top-4 right-4 z-20 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                        <button 
                                            onClick={(e) => { e.stopPropagation(); handleDeleteCity(item.id, item.city || item.city_name); }}
                                            className="h-8 w-8 bg-white text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-full shadow-md flex items-center justify-center transition-all transform hover:scale-110"
                                            title="Delete Record"
                                        >
                                            <Icons.Trash />
                                        </button>
                                    </div>

                                    <div className="bg-slate-50/50 rounded-[1.7rem] p-5 h-full flex flex-col cursor-pointer" 
                                         onClick={() => setStatsData({ city_name: item.city || item.city_name, active_cases: item.cases || item.active || item.active_cases, recovered: item.recovered, deaths: item.deaths, latitude: item.latitude || item.lat, longitude: item.longitude || item.lon })}>
                                        
                                        <div className="flex justify-between items-start mb-4">
                                            <div>
                                              <h4 className="font-black text-lg text-slate-800 leading-tight">{item.city || item.city_name}</h4>
                                              <div className="flex items-center gap-1.5 mt-1">
                                                <span className={`w-2 h-2 rounded-full ${item.latitude ? 'bg-emerald-500' : 'bg-red-400 animate-pulse'}`}></span>
                                                <span className="text-[10px] font-bold text-slate-400 uppercase">{item.latitude ? 'Live on Map' : 'Loc Missing'}</span>
                                              </div>
                                            </div>
                                        </div>
                                        
                                        <div className="mt-auto space-y-3">
                                            <div className="flex justify-between items-center bg-white p-3 rounded-2xl shadow-sm border border-slate-100">
                                                <span className="text-xs font-bold text-slate-400 uppercase">Active</span>
                                                <span className="font-black text-blue-600 text-lg">{item.cases || item.active || item.active_cases || 0}</span>
                                            </div>
                                            <div className="grid grid-cols-2 gap-2">
                                              <div className="bg-emerald-50 border border-emerald-100 p-2 rounded-xl text-center">
                                                <span className="text-[9px] font-bold text-emerald-400 uppercase block">Recovered</span>
                                                <span className="font-bold text-emerald-700">{item.recovered || 0}</span>
                                              </div>
                                              <div className="bg-red-50 border border-red-100 p-2 rounded-xl text-center">
                                                <span className="text-[9px] font-bold text-red-400 uppercase block">Fatal</span>
                                                <span className="font-bold text-red-700">{item.deaths || 0}</span>
                                              </div>
                                            </div>
                                        </div>
                                        
                                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity">
                                          <span className="bg-indigo-600 text-white text-xs font-bold px-4 py-2 rounded-full shadow-lg transform translate-y-4 group-hover:translate-y-0 transition-transform">Click to Edit</span>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-20 bg-white border-2 border-dashed border-slate-200 rounded-3xl">
                            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center text-slate-300 mb-4"><Icons.Chart /></div>
                            <p className="text-slate-500 font-medium">Database is empty.</p>
                            <p className="text-xs text-slate-400">Add a new city above to get started.</p>
                        </div>
                    )}
                 </div>
              </div>
            )}

            {/* --- USERS TAB --- */}
            {activeTab === "users" && (
                <div className="bg-white rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden">
                    <div className="p-8 border-b border-slate-50 flex justify-between items-center">
                        <h3 className="font-black text-xl text-slate-800">User Directory</h3>
                        <span className="bg-indigo-50 text-indigo-600 px-4 py-1.5 rounded-full text-xs font-bold">{users.length} Total Users</span>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-slate-50 text-slate-400 font-bold uppercase text-[10px] tracking-wider">
                                <tr><th className="p-6">User Profile</th><th className="p-6">Role</th><th className="p-6">Status</th><th className="p-6 text-right">Access Control</th></tr>
                            </thead>
                            <tbody className="divide-y divide-slate-50">
                                {users.map(u => (
                                    <tr key={u.id} className="hover:bg-slate-50/50 transition-colors">
                                        <td className="p-6">
                                            <div className="flex items-center gap-4">
                                                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold shadow-md ${u.is_active ? 'bg-gradient-to-br from-indigo-500 to-purple-600' : 'bg-slate-400'}`}>
                                                    {u.username.charAt(0).toUpperCase()}
                                                </div>
                                                <div><p className={`font-bold text-base ${u.is_active ? 'text-slate-700' : 'text-slate-400'}`}>{u.username}</p><p className="text-xs text-slate-400 font-medium">{u.email || "No Email Provided"}</p></div>
                                            </div>
                                        </td>
                                        <td className="p-6"><span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wide border ${u.role === 'Admin' || u.is_superuser ? 'bg-purple-50 text-purple-600 border-purple-100' : 'bg-slate-100 text-slate-500 border-slate-200'}`}>{u.role || (u.is_superuser ? "Admin" : "Standard User")}</span></td>
                                        <td className="p-6"><span className={`flex items-center gap-2 text-xs font-bold ${u.is_active ? 'text-emerald-600' : 'text-red-500'}`}><span className={`w-2 h-2 rounded-full ${u.is_active ? 'bg-emerald-500' : 'bg-red-500'}`}></span>{u.is_active ? "Active" : "Suspended"}</span></td>
                                        <td className="p-6 text-right">
                                            {(u.role === 'Admin' || u.is_superuser) ? (
                                                <span className="text-xs font-bold text-slate-300 italic pr-4">Immutable</span>
                                            ) : (
                                                <button onClick={() => handleBlockToggle(u.id, u.is_active)} className={`px-5 py-2 rounded-xl text-xs font-bold transition-all shadow-sm ${u.is_active ? "bg-white border border-red-200 text-red-600 hover:bg-red-50" : "bg-emerald-600 text-white hover:bg-emerald-700 shadow-emerald-200"}`}>
                                                    {u.is_active ? "Block User" : "Activate User"}
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
            
            {/* --- BROADCAST & TIPS --- */}
            {(activeTab === "broadcast" || activeTab === "tips") && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Editor Card */}
                    <div className="lg:col-span-1">
                      <div className="bg-white p-8 rounded-[2rem] shadow-xl shadow-slate-200/50 border border-slate-100 h-fit sticky top-28">
                        <div className="mb-6">
                          <span className="text-[10px] font-bold text-indigo-500 uppercase tracking-widest bg-indigo-50 px-3 py-1 rounded-full">{activeTab === "broadcast" ? "Public Alert" : "Health Advice"}</span>
                          <h3 className="text-3xl font-black text-slate-800 mt-3">Compose New</h3>
                        </div>
                        <div className="space-y-5">
                            {activeTab === 'broadcast' && (<div><label className="text-xs font-bold text-slate-400 uppercase pl-1">Audience</label><select value={newsData.city} onChange={(e) => setNewsData({...newsData, city: e.target.value})} className="w-full p-4 mt-1 bg-slate-50 border-none rounded-xl font-bold text-slate-700 focus:ring-2 focus:ring-indigo-500 transition-all">{CITIES.map(c => <option key={c} value={c}>{c}</option>)}</select></div>)}
                            <input type="text" value={activeTab === 'broadcast' ? newsData.title : tipData.title} onChange={(e) => activeTab === 'broadcast' ? setNewsData({...newsData, title: e.target.value}) : setTipData({...tipData, title: e.target.value})} className="w-full p-4 bg-slate-50 border-none rounded-xl font-bold text-slate-800 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 transition-all" placeholder="Enter headline..." />
                            <textarea rows="6" value={activeTab === 'broadcast' ? newsData.content : tipData.description} onChange={(e) => activeTab === 'broadcast' ? setNewsData({...newsData, content: e.target.value}) : setTipData({...tipData, description: e.target.value})} className="w-full p-4 bg-slate-50 border-none rounded-xl text-slate-600 placeholder-slate-400 focus:ring-2 focus:ring-indigo-500 transition-all resize-none" placeholder="Write your message here..."></textarea>
                            <button onClick={() => handlePost(activeTab === 'broadcast' ? 'news' : 'tip')} className="w-full py-4 bg-slate-900 text-white font-black rounded-xl shadow-lg hover:bg-indigo-600 hover:shadow-indigo-500/30 transition-all transform active:scale-95">PUBLISH NOW</button>
                        </div>
                      </div>
                    </div>
                    {/* Feed with DELETE BUTTON */}
                    <div className="lg:col-span-2 space-y-6">
                        <h3 className="text-2xl font-black text-slate-800 pl-2">Live Feed History</h3>
                        {(activeTab === 'broadcast' ? newsList : tipsList).map((item, idx) => (
                            <motion.div initial={{opacity:0, y:20}} animate={{opacity:1, y:0}} transition={{delay:idx*0.05}} key={item.id} className="relative bg-white p-8 rounded-[2rem] shadow-sm border border-slate-100 hover:shadow-lg transition-all group">
                                {/* DELETE BUTTON FOR FEED ITEMS */}
                                <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button 
                                        onClick={() => handleDeleteItem(item.id, activeTab === 'broadcast' ? 'news' : 'tip')}
                                        className="p-2 bg-slate-100 text-slate-400 hover:bg-red-50 hover:text-red-500 rounded-full transition-all"
                                        title="Delete Post"
                                    >
                                        <Icons.Trash />
                                    </button>
                                </div>

                                <div className="flex justify-between items-start mb-4 pr-10">
                                  <h4 className="font-bold text-xl text-slate-800 group-hover:text-indigo-600 transition-colors">{item.title}</h4>
                                  {activeTab === 'broadcast' && <span className="bg-slate-100 text-slate-600 px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider">{item.city || "All Pakistan"}</span>}
                                </div>
                                <p className="text-slate-500 leading-relaxed">{item.content || item.description}</p>
                                <div className="mt-6 flex items-center gap-2 text-xs font-bold text-slate-300">
                                  <span>Published {item.date || "Just Now"}</span>
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

          </div>
        </div>
      </main>

      {/* --- MODAL --- */}
      {selectedReport && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-md flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0, scale: 0.9, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} className="bg-white w-full max-w-2xl rounded-[2.5rem] shadow-2xl overflow-hidden border border-white/50">
                <div className="p-8 pb-0 flex justify-between items-start">
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Incident Report #{selectedReport.id}</span>
                    <h3 className="font-black text-2xl text-slate-800 mt-1">Detailed Analysis</h3>
                  </div>
                  <button onClick={() => setSelectedReport(null)} className="p-3 bg-slate-50 hover:bg-slate-100 rounded-full transition-colors"><Icons.Close /></button>
                </div>
                <div className="p-8 space-y-8">
                    <div className="flex items-center gap-5 p-4 bg-slate-50 rounded-2xl border border-slate-100">
                      <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center text-indigo-600 font-black text-xl shadow-sm">{selectedReport.username.charAt(0)}</div>
                      <div>
                        <p className="font-bold text-slate-800 text-lg">{selectedReport.username}</p>
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-wide">Reported on {selectedReport.date}</p>
                      </div>
                      <span className={`ml-auto px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide ${selectedReport.ai_result.includes("Resolved") ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>{selectedReport.ai_result}</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-slate-900 rounded-2xl overflow-hidden flex items-center justify-center aspect-square md:aspect-auto">
                        {selectedReport.image ? (<img src={getFullUrl(selectedReport.image)} alt="Evidence" className="w-full h-full object-cover opacity-90" />) : (<span className="text-slate-500 font-medium">No Image Evidence</span>)}
                      </div>
                      <div className="space-y-6">
                        <div>
                          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Location Data</p>
                          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 text-slate-700 font-medium">{selectedReport.location || "Coordinates not available"}</div>
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">AI Assessment</p>
                          <div className="p-4 bg-indigo-50 rounded-2xl border border-indigo-100 text-indigo-800 font-bold flex justify-between items-center"><span>Dengue Larva Detected</span> <span>88% Conf.</span></div>
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">User Remarks</p>
                          <p className="text-slate-600 text-sm leading-relaxed">{selectedReport.description}</p>
                        </div>
                      </div>
                    </div>
                </div>
                <div className="p-6 bg-slate-50 border-t border-slate-100 flex gap-4 justify-end">
                  <button onClick={() => handleStatusUpdate(selectedReport.id, "Rejected ❌")} className="px-6 py-3 rounded-xl font-bold text-slate-500 hover:text-red-600 hover:bg-red-50 transition-all">Dismiss Report</button>
                  <button onClick={() => handleStatusUpdate(selectedReport.id, "Resolved ✅")} className="px-8 py-3 bg-slate-900 text-white font-bold rounded-xl hover:bg-emerald-600 hover:shadow-lg hover:shadow-emerald-500/30 transition-all">Verify & Resolve</button>
                </div>
            </motion.div>
        </div>
      )}

    </div>
  );
};

export default AdminDashboard;