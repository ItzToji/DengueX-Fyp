import React, { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";

const NewsPage = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/news/");
      setNews(res.data);
    } catch (err) {
      console.error("Error fetching news");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 font-sans">
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-10">
            <h1 className="text-4xl font-extrabold text-slate-800 mb-2">📢 Dengue Updates</h1>
            <p className="text-slate-500">Official announcements & city-wise alerts</p>
        </div>

        {loading ? (
           <p className="text-center text-slate-400">Loading Updates...</p>
        ) : news.length === 0 ? (
           <div className="text-center p-10 bg-white rounded-2xl shadow-sm border border-slate-200">
               <p className="text-xl text-slate-400">No news updates yet.</p>
           </div>
        ) : (
           <div className="space-y-6">
             {news.map((item, index) => (
               <motion.div 
                 key={item.id}
                 initial={{ opacity: 0, y: 20 }}
                 animate={{ opacity: 1, y: 0 }}
                 transition={{ delay: index * 0.1 }}
                 className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 hover:shadow-md transition relative overflow-hidden"
               >
                 {/* City Badge */}
                 <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold px-4 py-2 rounded-bl-xl">
                    📍 {item.city}
                 </div>

                 <div className="mb-2">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">{item.date}</span>
                    <h2 className="text-xl font-bold text-slate-800 mt-1">{item.title}</h2>
                 </div>
                 
                 <p className="text-slate-600 leading-relaxed text-sm">
                    {item.content}
                 </p>
               </motion.div>
             ))}
           </div>
        )}
      </div>
    </div>
  );
};

export default NewsPage;