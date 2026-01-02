import React, { useState, useEffect } from "react";
import axios from "axios";

const Report = () => {
  const [description, setDescription] = useState("");
  const [areaName, setAreaName] = useState(""); // 👈 New Field
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [location, setLocation] = useState({ lat: null, lng: null });
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [reports, setReports] = useState([]);

  const token = localStorage.getItem("token") || localStorage.getItem("access_token");

  useEffect(() => {
    fetchReports();
    getLocation();
  }, []);

  // --- LOCATION & ADDRESS FETCHING ---
  const getLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        setLocation({ lat, lng });

        // Auto-fetch Address (Reverse Geocoding)
        try {
            const res = await axios.get(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
            if (res.data && res.data.address) {
                const city = res.data.address.city || res.data.address.town || res.data.address.village || "";
                const suburb = res.data.address.suburb || res.data.address.neighbourhood || "";
                setAreaName(`${suburb}, ${city}`); // Auto-fill Area Name
            }
        } catch (err) { console.log("Address fetch failed"); }
      });
    }
  };

  const fetchReports = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/get-reports/", { 
          headers: { Authorization: `Token ${token}` } 
      });
      setReports(res.data);
    } catch (err) { console.error(err); }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
        setImage(file);
        setPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) return alert("Please upload an image of the site.");
    if (!areaName) return alert("Please enter the Area Name.");
    
    setLoading(true);
    const formData = new FormData();
    formData.append("description", description);
    formData.append("area_name", areaName); // 👈 Sending Area Name
    formData.append("image", image);
    formData.append("latitude", location.lat || "");
    formData.append("longitude", location.lng || "");

    try {
      await axios.post("http://127.0.0.1:8000/api/submit-report/", formData, {
        headers: { Authorization: `Token ${token}`, "Content-Type": "multipart/form-data" }
      });
      
      setSuccessMsg("Report Submitted Successfully! 🚀");
      fetchReports();
      setDescription("");
      setAreaName("");
      setImage(null);
      setPreview(null);
      setTimeout(() => setSuccessMsg(""), 5000);
    } catch (err) {
      alert("Failed to submit report. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 font-sans pb-20">
      <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* REPORT FORM */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
          <div className="flex items-center gap-3 mb-6">
             <span className="bg-red-100 text-red-600 p-2 rounded-lg">📢</span>
             <div>
                <h2 className="text-2xl font-bold text-slate-800">Report Hazard</h2>
                <p className="text-slate-400 text-xs">Help authorities find breeding sites</p>
             </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Image Upload */}
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:bg-slate-50 relative cursor-pointer transition-colors group">
              <input type="file" onChange={handleImageChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" accept="image/*" />
              {preview ? (
                  <img src={preview} alt="Preview" className="h-48 mx-auto rounded-lg object-cover shadow-sm" />
              ) : (
                  <div className="text-slate-400 group-hover:text-slate-600">
                      <svg className="w-10 h-10 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                      <p className="font-semibold text-sm">Upload Photo</p>
                  </div>
              )}
            </div>

            {/* Inputs */}
            <div>
                <label className="text-xs font-bold text-slate-500 uppercase ml-1">Location / Area</label>
                <input type="text" value={areaName} onChange={(e) => setAreaName(e.target.value)} placeholder="e.g. Gulshan-e-Iqbal Block 4" className="w-full p-4 mt-1 bg-slate-50 border border-slate-200 rounded-xl font-medium outline-none focus:border-indigo-500 transition-colors" />
            </div>

            <div>
                <label className="text-xs font-bold text-slate-500 uppercase ml-1">Details</label>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe the stagnant water or hazard..." className="w-full p-4 mt-1 bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-indigo-500 transition-colors" rows="3"></textarea>
            </div>
            
            <button disabled={loading} className={`w-full py-4 rounded-xl font-bold text-white shadow-lg transition-all ${loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-indigo-200'}`}>
                {loading ? "Submitting..." : "Submit Report 🚀"}
            </button>
          </form>

          {successMsg && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-xl text-center font-bold flex items-center justify-center gap-2 animate-pulse">
               <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
               {successMsg}
            </div>
          )}
        </div>

        {/* HISTORY LIST */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 h-fit">
           <div className="flex justify-between items-center mb-6">
               <h2 className="text-xl font-bold text-slate-800">My Reports</h2>
               <span className="bg-slate-100 text-slate-600 px-3 py-1 rounded-full text-xs font-bold">{reports.length}</span>
           </div>
           
           <div className="space-y-4 max-h-[600px] overflow-y-auto custom-scrollbar pr-2">
             {reports.length > 0 ? (
                 reports.map((r) => (
                <div key={r.id} className="p-4 border border-slate-100 rounded-xl hover:bg-slate-50 transition-colors flex gap-4">
                    {/* Thumbnail */}
                    <div className="w-16 h-16 bg-slate-200 rounded-lg flex-shrink-0 overflow-hidden">
                        {r.image ? <img src={`http://127.0.0.1:8000${r.image}`} alt="Report" className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-slate-400 text-xs">No Img</div>}
                    </div>
                    
                    <div className="flex-1">
                        <div className="flex justify-between items-start">
                            <h4 className="font-bold text-slate-800 text-sm truncate w-40">{r.area_name || "Unknown Location"}</h4>
                            <span className={`text-[10px] font-bold px-2 py-1 rounded border ${
                                r.ai_result.includes("Resolved") ? "bg-green-50 text-green-600 border-green-100" :
                                r.ai_result.includes("Fake") ? "bg-red-50 text-red-600 border-red-100" :
                                "bg-yellow-50 text-yellow-600 border-yellow-100"
                            }`}>
                                {r.ai_result || "Pending"}
                            </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-1 line-clamp-2">{r.description}</p>
                        <p className="text-[10px] text-slate-400 mt-2 font-mono">
                            {new Date(r.created_at).toLocaleDateString()} • {new Date(r.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </p>
                    </div>
                </div>
             ))
             ) : (
                 <div className="text-center py-10 text-slate-400">
                     <p>No reports submitted yet.</p>
                 </div>
             )}
           </div>
        </div>

      </div>
    </div>
  );
};

export default Report;