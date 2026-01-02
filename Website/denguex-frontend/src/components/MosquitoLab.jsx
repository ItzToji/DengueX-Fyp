import React, { useState } from "react";
import axios from "axios";

const MosquitoLab = () => {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const token = localStorage.getItem("token") || localStorage.getItem("access_token");

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResult(null); // Reset result on new image
  };

  const handleIdentify = async () => {
    if (!image) return alert("Please upload an image first.");
    setLoading(true);

    const formData = new FormData();
    formData.append("image", image);

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/identify-mosquito/", formData, {
        headers: { 
            Authorization: `Token ${token}`,
            "Content-Type": "multipart/form-data" 
        }
      });
      setResult(res.data);
    } catch (err) {
      alert("Identification Failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 font-sans flex justify-center items-center">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-xl overflow-hidden">
        
        {/* Header */}
        <div className="bg-purple-700 p-6 text-white text-center">
            <h2 className="text-3xl font-bold">🧬 Mosquito Lab</h2>
            <p className="opacity-90">Upload a photo to identify species (3,500+ types database)</p>
        </div>

        <div className="p-8">
            {/* Upload Section */}
            <div className="border-2 border-dashed border-purple-200 rounded-xl p-8 text-center hover:bg-purple-50 transition cursor-pointer relative bg-slate-50">
                <input type="file" onChange={handleImageChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" accept="image/*" />
                {preview ? (
                    <img src={preview} alt="Preview" className="h-64 mx-auto rounded-lg object-contain shadow-sm" />
                ) : (
                    <div className="text-purple-400">
                        <div className="text-5xl mb-3">🔬</div>
                        <p className="font-semibold">Tap to Upload Mosquito Image</p>
                    </div>
                )}
            </div>

            {/* Identify Button */}
            <button 
                onClick={handleIdentify} 
                disabled={loading}
                className="w-full mt-6 bg-purple-600 hover:bg-purple-800 text-white font-bold py-4 rounded-xl shadow-lg transition transform hover:scale-[1.01]"
            >
                {loading ? "Scanning DNA Sequence..." : "Identify Species 🦟"}
            </button>

            {/* Result Section */}
            {result && (
                <div className="mt-8 animate-fade-in-up">
                    <div className="bg-green-50 border border-green-200 rounded-xl p-6 relative overflow-hidden">
                        <div className="absolute top-0 right-0 bg-green-200 text-green-800 px-3 py-1 text-xs font-bold rounded-bl-lg">
                            {result.confidence}% Match
                        </div>
                        
                        <h3 className="text-2xl font-extrabold text-slate-800 mb-1">{result.species}</h3>
                        <p className={`text-sm font-bold mb-4 ${result.risk.includes("High") ? "text-red-600" : "text-yellow-600"}`}>
                            ⚠️ Risk Level: {result.risk}
                        </p>

                        <div className="space-y-3">
                            <div className="bg-white p-3 rounded-lg border border-green-100">
                                <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">Identification</span>
                                <p className="text-gray-700 text-sm mt-1">{result.details}</p>
                            </div>
                            <div className="bg-white p-3 rounded-lg border border-green-100">
                                <span className="text-xs font-bold text-gray-500 uppercase tracking-wide">Typical Habitat</span>
                                <p className="text-gray-700 text-sm mt-1">{result.habitat}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default MosquitoLab;