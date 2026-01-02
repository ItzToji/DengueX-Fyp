import React, { useState, useEffect } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

const Analytics = () => {
  // --- STATE ---
  const [data, setData] = useState([]);
  const [filters, setFilters] = useState({
    city: "All",
    startDate: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().split('T')[0], // 30 days ago
    endDate: new Date().toISOString().split('T')[0] // Today
  });
  const [loading, setLoading] = useState(false);

  // --- FETCH DATA ---
  useEffect(() => {
    fetchAnalytics();
  }, []); // Initial load

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      // Query Params bana rahe hain
      const query = `?city=${filters.city}&start_date=${filters.startDate}&end_date=${filters.endDate}`;
      const res = await axios.get(`http://127.0.0.1:8000/api/analytics/${query}`);
      setData(res.data);
    } catch (err) {
      console.error("Error fetching analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  // --- HANDLERS ---
  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const applyFilters = (e) => {
    e.preventDefault();
    fetchAnalytics();
  };

  // ✅ EXPORT TO CSV FUNCTION
  const downloadCSV = () => {
    if (data.length === 0) return alert("No data to export!");

    // CSV Header
    const headers = ["Date", "Active Cases", "Moving Average", "Previous Year"];
    
    // CSV Rows
    const rows = data.map(row => [
      row.date, 
      row.cases, 
      row.moving_avg, 
      row.prev_year
    ]);

    // Combine
    let csvContent = "data:text/csv;charset=utf-8," 
      + headers.join(",") + "\n" 
      + rows.map(e => e.join(",")).join("\n");

    // Download Link Logic
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `dengue_report_${filters.city}_${filters.startDate}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-center mb-8">
        <div>
           <h1 className="text-3xl font-bold text-slate-800">📊 Advanced Analytics</h1>
           <p className="text-slate-500">Analyze Dengue trends with real-time filtering.</p>
        </div>
        <button 
           onClick={downloadCSV}
           className="mt-4 md:mt-0 flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-lg font-medium transition shadow-sm"
        >
           <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
           Export Data
        </button>
      </div>

      {/* FILTER BAR */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 mb-8">
         <form onSubmit={applyFilters} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            
            {/* City Filter */}
            <div>
               <label className="block text-sm font-semibold text-gray-700 mb-1">Select Region</label>
               <select 
                 name="city" 
                 value={filters.city} 
                 onChange={handleFilterChange} 
                 className="w-full p-2.5 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
               >
                 <option value="All">All Cities</option>
                 <option value="Lahore">Lahore</option>
                 <option value="Karachi">Karachi</option>
                 <option value="Islamabad">Islamabad</option>
                 <option value="Rawalpindi">Rawalpindi</option>
               </select>
            </div>

            {/* Start Date */}
            <div>
               <label className="block text-sm font-semibold text-gray-700 mb-1">From Date</label>
               <input 
                 type="date" 
                 name="startDate" 
                 value={filters.startDate} 
                 onChange={handleFilterChange} 
                 className="w-full p-2.5 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
               />
            </div>

            {/* End Date */}
            <div>
               <label className="block text-sm font-semibold text-gray-700 mb-1">To Date</label>
               <input 
                 type="date" 
                 name="endDate" 
                 value={filters.endDate} 
                 onChange={handleFilterChange} 
                 className="w-full p-2.5 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
               />
            </div>

            {/* Apply Button */}
            <button 
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 rounded-lg transition"
            >
              {loading ? "Loading..." : "Apply Filters"}
            </button>
         </form>
      </div>

      {/* CHARTS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
         
         {/* Chart 1: Daily Cases Trend */}
         <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">📈 Daily Infection Trend</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="colorCases" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" tick={{fontSize: 12}} />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="cases" stroke="#ef4444" fillOpacity={1} fill="url(#colorCases)" name="Active Cases" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
         </div>

         {/* Chart 2: Comparison with Last Year */}
         <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="text-lg font-bold text-gray-800 mb-4">📅 Year-over-Year Comparison</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" tick={{fontSize: 12}} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="cases" stroke="#3b82f6" strokeWidth={2} dot={false} name="Current Year" />
                  <Line type="monotone" dataKey="prev_year" stroke="#9ca3af" strokeDasharray="5 5" name="Previous Year" />
                </LineChart>
              </ResponsiveContainer>
            </div>
         </div>

      </div>

      {/* DATA TABLE (Exportable) */}
      <div className="mt-8 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 border-b border-gray-100">
             <h3 className="text-lg font-bold text-gray-800">📋 Detailed Data Report</h3>
          </div>
          <div className="overflow-x-auto">
             <table className="w-full text-left text-sm text-gray-600">
                <thead className="bg-gray-50 text-gray-800 font-semibold uppercase">
                   <tr>
                      <th className="px-6 py-3">Date</th>
                      <th className="px-6 py-3 text-red-600">Active Cases</th>
                      <th className="px-6 py-3">Moving Avg (7-Day)</th>
                      <th className="px-6 py-3">Vs Last Year</th>
                   </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                   {data.slice(0, 10).map((row, index) => (
                      <tr key={index} className="hover:bg-gray-50 transition">
                         <td className="px-6 py-3 font-medium">{row.date}</td>
                         <td className="px-6 py-3 font-bold text-red-600">{row.cases}</td>
                         <td className="px-6 py-3">{row.moving_avg}</td>
                         <td className="px-6 py-3">
                            <span className={`px-2 py-1 rounded text-xs font-bold ${row.cases > row.prev_year ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                                {row.cases > row.prev_year ? `+${row.cases - row.prev_year}` : `${row.cases - row.prev_year}`}
                            </span>
                         </td>
                      </tr>
                   ))}
                </tbody>
             </table>
             <div className="p-4 text-center text-xs text-gray-400 bg-gray-50">
                Showing recent 10 records. Use "Export Data" to see all.
             </div>
          </div>
      </div>

    </div>
  );
};

export default Analytics;