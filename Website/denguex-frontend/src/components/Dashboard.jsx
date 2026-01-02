import React, { useState, useEffect } from "react";
import axios from "axios";
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { motion } from "framer-motion";
import DengueMap from "./DengueMap"; 

// --- 🎨 ICONS ---
const Icons = {
    Logo: () => <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="none"><path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="#6366F1" /><path d="M8 12L11 15L16 9" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg>,
    Report: () => <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>,
    Active: () => <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>,
    Recover: () => <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
    Death: () => <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
    Tip: () => <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>,
    Location: () => <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
};

const PROVINCE_MAPPING = {
    Punjab: ["Lahore", "Rawalpindi", "Multan", "Faisalabad", "Sialkot", "Gujranwala", "Bahawalpur", "Sargodha"],
    Sindh: ["Karachi", "Hyderabad", "Sukkur", "Larkana", "Nawabshah"],
    KPK: ["Peshawar", "Abbottabad", "Swat", "Mardan"],
    Balochistan: ["Quetta", "Gwadar", "Turbat"],
    Islamabad: ["Islamabad"]
};

// --- COMPONENTS ---
const MetricCard = ({ title, value, color, icon: Icon, delay }) => (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: delay * 0.1 }} className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 relative overflow-hidden group hover:shadow-lg transition-all">
        <div className={`absolute top-0 right-0 w-24 h-24 rounded-full blur-3xl opacity-10 ${color}`}></div>
        <div className="flex justify-between items-start relative z-10">
            <div><p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">{title}</p><h3 className="text-4xl font-black text-slate-800 tracking-tight">{value.toLocaleString()}</h3></div>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color.replace('bg-', 'bg-opacity-10 text-').replace('500', '600')} ${color.includes('slate') ? 'bg-slate-100 text-slate-600' : ''}`}><Icon /></div>
        </div>
        <div className="mt-4 flex items-center gap-2">
            <span className="text-[10px] font-bold bg-slate-50 px-2 py-1 rounded-md text-slate-500 border border-slate-100">Live Data</span>
            <span className="text-[10px] text-slate-400">Updated just now</span>
        </div>
    </motion.div>
);

const HealthTipItem = ({ tip }) => (
    <motion.div whileHover={{ scale: 1.02 }} className="group p-4 bg-gradient-to-r from-blue-50 to-white border border-blue-100 rounded-xl mb-3 hover:shadow-md transition-all cursor-pointer">
        <div className="flex items-start gap-3">
            <div className="bg-blue-100 p-2 rounded-lg text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors"><Icons.Tip /></div>
            <div>
                {/* Ensure backend sends 'title' and 'description' */}
                <h5 className="font-bold text-slate-800 text-sm group-hover:text-blue-700 transition-colors">{tip.title}</h5>
                <p className="text-xs text-slate-500 leading-relaxed mt-1">{tip.description}</p>
            </div>
        </div>
    </motion.div>
);

const CityCard = ({ data }) => {
    const [isFlipped, setIsFlipped] = useState(false);
    const city = (data.city || data.city_name || "Unknown").trim();
    const active = parseInt(data.active || 0);
    const recovered = parseInt(data.recovered || 0);
    const deaths = parseInt(data.deaths || 0);
    const total = active + recovered + deaths;

    return (
        <div className="relative h-64 w-full cursor-pointer perspective-1000" onClick={() => setIsFlipped(!isFlipped)}>
            <motion.div initial={false} animate={{ rotateY: isFlipped ? 180 : 0 }} transition={{ duration: 0.6 }} style={{ transformStyle: "preserve-3d" }} className="relative w-full h-full">
                <div className={`absolute inset-0 backface-hidden bg-white border border-slate-100 rounded-2xl p-6 shadow-sm overflow-hidden group ${active > 100 ? 'shadow-red-100' : 'shadow-emerald-100'}`} style={{ backfaceVisibility: "hidden" }}>
                    <div className="flex justify-between items-start mb-4 relative z-10">
                        <div className="flex items-center gap-2"><div className={`p-1.5 rounded-lg ${active > 100 ? 'bg-red-100 text-red-600' : 'bg-emerald-100 text-emerald-600'}`}><Icons.Location /></div><h4 className="text-lg font-bold text-slate-800">{city}</h4></div>
                        <span className={`text-[10px] font-bold px-2 py-1 rounded-full border ${active > 100 ? 'bg-red-50 text-red-600 border-red-100' : 'bg-emerald-50 text-emerald-600 border-emerald-100'}`}>{active > 100 ? "Alert" : "Safe"}</span>
                    </div>
                    <div className="mb-4 relative z-10"><p className="text-xs text-slate-400 font-bold uppercase tracking-wider">Total Reports</p><div className="flex items-baseline gap-1"><p className="text-3xl font-black text-slate-800">{total}</p><span className="text-xs font-bold text-slate-400">cases</span></div></div>
                    <div className="flex gap-4 pt-4 border-t border-slate-50 relative z-10"><div className="text-center"><p className="text-[10px] text-slate-400 font-bold uppercase">Active</p><p className="text-sm font-bold text-blue-600">{active}</p></div><div className="text-center px-4 border-l border-slate-100"><p className="text-[10px] text-slate-400 font-bold uppercase">Recovered</p><p className="text-sm font-bold text-emerald-600">{recovered}</p></div></div>
                </div>
                <div className="absolute inset-0 backface-hidden bg-white border border-slate-100 rounded-2xl p-6 shadow-xl flex flex-col justify-center items-center text-center" style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}>
                    <h4 className="text-sm font-bold text-slate-800 uppercase tracking-widest border-b-2 border-slate-100 pb-1 w-full mb-4">{city} Breakdown</h4>
                    <div className="w-full space-y-2"><div className="flex justify-between text-sm bg-slate-100 p-2 rounded-lg"><span className="text-slate-600 font-bold">Total</span><span className="font-black text-slate-900">{total}</span></div><div className="flex justify-between text-sm bg-slate-50 p-2 rounded-lg"><span className="text-slate-500">Active</span><span className="font-bold text-blue-600">{active}</span></div><div className="flex justify-between text-sm bg-slate-50 p-2 rounded-lg"><span className="text-slate-500">Recovered</span><span className="font-bold text-emerald-600">{recovered}</span></div><div className="flex justify-between text-sm bg-red-50 p-2 rounded-lg"><span className="text-red-500">Critical</span><span className="font-bold text-red-600">{deaths}</span></div></div>
                </div>
            </motion.div>
        </div>
    );
};

// --- 📊 MAIN DASHBOARD ---
const Dashboard = () => {
    const [stats, setStats] = useState([]); 
    const [allChartData, setAllChartData] = useState([]); // Stores Full History
    const [displayChartData, setDisplayChartData] = useState([]); // Stores Filtered Data
    const [chartFilter, setChartFilter] = useState("30 Days");
    const [healthTips, setHealthTips] = useState([]);
    const [selectedProvince, setSelectedProvince] = useState("Punjab");
    const [summary, setSummary] = useState({ total_reports: 0, active: 0, recovered: 0, deaths: 0 });

    useEffect(() => {
        const fetchData = async () => {
            try {
                // 1. Dashboard Stats (Active/Recovered Cards + Map)
                const dashboardRes = await axios.get("http://127.0.0.1:8000/api/dashboard-data/");
                const rawCityData = dashboardRes.data.stats || dashboardRes.data.city_stats || [];
                
                const normalizedStats = Array.isArray(rawCityData) ? rawCityData.map(item => {
                    return {
                        ...item,
                        city: (item.city || item.city_name || "Unknown").trim(),
                        active: parseInt(item.active || item.cases || item.active_cases || 0),
                        recovered: parseInt(item.recovered || 0),
                        deaths: parseInt(item.deaths || 0),
                        latitude: parseFloat(item.latitude || item.lat),
                        longitude: parseFloat(item.longitude || item.lon)
                    };
                }) : [];

                setStats(normalizedStats);

                if (normalizedStats.length > 0) {
                    const totals = normalizedStats.reduce((acc, curr) => {
                        acc.active += curr.active;
                        acc.recovered += curr.recovered;
                        acc.deaths += curr.deaths;
                        acc.total_reports += (curr.active + curr.recovered + curr.deaths);
                        return acc;
                    }, { total_reports: 0, active: 0, recovered: 0, deaths: 0 });
                    setSummary(totals); 
                }

                // 2. Chart Data (FROM NEW ANALYTICS API)
                // 👇 This URL matches your urls.py path('analytics/', ...)
                const chartRes = await axios.get("http://127.0.0.1:8000/api/analytics/");
                let rawData = [];
                if (Array.isArray(chartRes.data)) {
                    rawData = chartRes.data; // [{ date: "Dec 24", cases: 5 }, ...]
                }
                
                setAllChartData(rawData);
                setDisplayChartData(rawData.slice(-30)); // Show last 30 entries by default

                // 3. Health Tips (FROM NEW TIPS API)
                // 👇 This URL matches your urls.py path('health-tips/', ...)
                const tipsRes = await axios.get("http://127.0.0.1:8000/api/health-tips/");
                setHealthTips(Array.isArray(tipsRes.data) ? tipsRes.data : []);

            } catch (error) {
                console.error("Dashboard Data Error:", error);
            }
        };
        fetchData();
    }, []);

    // --- 🗓️ FILTER LOGIC ---
    useEffect(() => {
        if (!allChartData || allChartData.length === 0) {
            setDisplayChartData([]);
            return;
        }
        if (chartFilter === "7 Days") {
            setDisplayChartData(allChartData.slice(-7));
        } else {
            setDisplayChartData(allChartData.slice(-30));
        }
    }, [chartFilter, allChartData]);

    const getProvinceData = (prov) => {
        const allMapped = Object.values(PROVINCE_MAPPING).flat().map(c => c.toLowerCase());
        if (prov === "Others") {
            return stats.filter(s => { const name = (s.city || "").toLowerCase(); return name && !allMapped.some(m => name.includes(m)); });
        }
        const targets = (PROVINCE_MAPPING[prov] || []).map(c => c.toLowerCase());
        return stats.filter(s => { const name = (s.city || "").toLowerCase(); return targets.some(t => name.includes(t)); });
    };

    const currentRegionData = getProvinceData(selectedProvince);
    const TABS = [...Object.keys(PROVINCE_MAPPING), "Others"];

    return (
        <div className="min-h-screen bg-[#F8FAFC] font-sans pb-20 selection:bg-indigo-100 selection:text-indigo-700">
            {/* HEADER */}
            <div className="sticky top-0 z-40 bg-white/80 backdrop-blur-xl border-b border-slate-200/60 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                    <div className="flex items-center gap-3"><Icons.Logo /><div><h1 className="text-xl font-black text-slate-800 tracking-tight">Dengue<span className="text-indigo-600">X</span></h1><p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">National Surveillance</p></div></div>
                    <div className="flex items-center gap-4"><div className="hidden md:flex flex-col items-end mr-2"><span className="text-xs font-bold text-slate-700">System Operational</span><span className="text-[10px] text-slate-400">v2.4.0 (Stable)</span></div><span className="relative flex h-3 w-3"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span><span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border-2 border-white"></span></span></div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 pt-10 space-y-8">
                {/* 1. TOP CARDS */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <MetricCard title="Total Reports" value={summary.total_reports} color="bg-slate-500" icon={Icons.Report} delay={1} />
                    <MetricCard title="Active Cases" value={summary.active} color="bg-blue-500" icon={Icons.Active} delay={2} />
                    <MetricCard title="Recovered" value={summary.recovered} color="bg-emerald-500" icon={Icons.Recover} delay={3} />
                    <MetricCard title="Fatalities" value={summary.deaths} color="bg-red-500" icon={Icons.Death} delay={4} />
                </div>

                {/* 2. CHART & HEALTH TIPS */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    
                    {/* --- 📈 GRAPH SECTION --- */}
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }} 
                        animate={{ opacity: 1, scale: 1 }} 
                        transition={{ delay: 0.2 }} 
                        className="lg:col-span-8 bg-white p-8 rounded-3xl border border-slate-100 shadow-sm relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
                        
                        <div className="flex justify-between items-center mb-8 relative z-10">
                            <div>
                                <h3 className="text-xl font-bold text-slate-800">Daily Infection Trends</h3>
                                <p className="text-sm text-slate-500 mt-1">New cases reported per day</p>
                            </div>
                            
                            <div className="flex gap-2">
                                {['7 Days', '30 Days'].map((t) => (
                                    <button 
                                        key={t} 
                                        onClick={() => setChartFilter(t)}
                                        className={`px-4 py-2 text-xs font-bold rounded-full transition-all ${
                                            chartFilter === t 
                                            ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' 
                                            : 'bg-slate-50 text-slate-500 hover:bg-slate-100'
                                        }`}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div style={{ width: '100%', height: 350 }} className="relative z-10">
                            {displayChartData && displayChartData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={displayChartData} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
                                        <defs>
                                            <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#6366F1" stopOpacity={0.5}/>
                                                <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
                                            </linearGradient>
                                        </defs>
                                        
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                                        
                                        <XAxis 
                                            dataKey="date" 
                                            axisLine={false} 
                                            tickLine={false} 
                                            tick={{ fontSize: 11, fill: '#64748B', fontWeight: 600 }} 
                                            dy={10}
                                        />
                                        
                                        <YAxis 
                                            axisLine={false} 
                                            tickLine={false} 
                                            tick={{ fontSize: 11, fill: '#64748B', fontWeight: 600 }} 
                                        />
                                        
                                        <Tooltip 
                                            contentStyle={{ 
                                                backgroundColor: '#1E293B', 
                                                borderRadius: '8px', 
                                                border: 'none', 
                                                color: '#fff' 
                                            }} 
                                            itemStyle={{ color: '#818CF8' }}
                                            labelStyle={{ color: '#94A3B8', marginBottom: '5px' }}
                                            formatter={(value) => [`${value} Cases`, "New Reports"]}
                                        />
                                        
                                        <Area 
                                            type="monotone" 
                                            dataKey="cases"
                                            stroke="#6366F1" 
                                            strokeWidth={3} 
                                            fill="url(#colorCases)" 
                                            activeDot={{ r: 6, strokeWidth: 0 }} 
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-slate-400 bg-slate-50/50 rounded-2xl border-2 border-dashed border-slate-100">
                                    <Icons.Report />
                                    <p className="text-sm font-bold mt-2 text-slate-500">No Daily Data Yet</p>
                                    <p className="text-xs text-slate-400">Add entries via Admin to see graph.</p>
                                </div>
                            )}
                        </div>
                    </motion.div>

                    {/* --- 💡 HEALTH TIPS SECTION --- */}
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="lg:col-span-4 bg-white p-6 rounded-3xl border border-slate-200 shadow-sm flex flex-col h-full overflow-hidden max-h-[480px]">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="font-bold text-lg text-slate-800">Health Tips</h3>
                            <span className="bg-indigo-50 text-indigo-600 text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-wider">{healthTips.length} Active</span>
                        </div>
                        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                            {healthTips.length > 0 ? (
                                healthTips.map((tip, index) => <HealthTipItem key={tip.id || index} tip={tip} />)
                            ) : (
                                <div className="h-full flex flex-col items-center justify-center text-slate-300">
                                    <Icons.Tip />
                                    <p className="text-xs font-bold mt-2">No Tips Added</p>
                                    <p className="text-[10px] text-slate-400">Check Admin Panel</p>
                                </div>
                            )}
                        </div>
                    </motion.div>
                </div>

                {/* 3. MAIN MAP */}
                <motion.div 
                    initial={{ opacity: 0, y: 20 }} 
                    animate={{ opacity: 1, y: 0 }} 
                    transition={{ delay: 0.3 }} 
                    className="w-full h-[650px] bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden"
                >
                    <DengueMap stats={stats} />
                </motion.div>

                {/* 4. CITY BREAKDOWN */}
    <div className="space-y-8">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-6"><div><h3 className="text-2xl font-black text-slate-800">Regional Intelligence</h3><p className="text-sm text-slate-500 font-medium">Detailed breakdown by province and major cities</p></div><div className="bg-white p-1.5 rounded-2xl border border-slate-200 shadow-sm flex overflow-x-auto max-w-full">{TABS.map(prov => (<button key={prov} onClick={() => setSelectedProvince(prov)} className={`px-6 py-2.5 text-xs font-bold rounded-xl transition-all whitespace-nowrap ${selectedProvince === prov ? 'bg-slate-900 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'}`}>{prov}</button>))}</div></div>
                    <motion.div layout className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {currentRegionData.length > 0 ? (currentRegionData.map((item, index) => <CityCard key={index} data={item} />)) : (<div className="col-span-full py-24 text-center bg-white rounded-3xl border-2 border-dashed border-slate-200 flex flex-col items-center"><Icons.Report /><h4 className="text-slate-900 font-bold text-lg mt-4">No Reports Found</h4><p className="text-slate-500 text-sm mt-1">There are no reports for {selectedProvince} at this time.</p></div>)}
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;