import React, { useState, useEffect } from "react";
import axios from "axios";

const Profile = () => {
  const [activeTab, setActiveTab] = useState("details"); // 'details' or 'security'
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ text: "", type: "" });

  // Profile Data State
  const [profile, setProfile] = useState({
    username: "",
    full_name: "",
    age: "",
    blood_group: "",
    is_vaccinated: "No",
    recent_test_date: ""
  });

  // Password State
  const [passwords, setPasswords] = useState({ new: "", confirm: "" });

  const token = localStorage.getItem("token");

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await axios.post("http://127.0.0.1:8000/api/get-profile/", {}, {
        headers: { Authorization: `Token ${token}` }
      });
      setProfile(res.data);
    } catch (err) { console.error(err); }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post("http://127.0.0.1:8000/api/update-profile/", profile, {
        headers: { Authorization: `Token ${token}` }
      });
      setMsg({ text: "Profile Updated Successfully! ✅", type: "success" });
    } catch (err) {
      setMsg({ text: "Failed to update profile.", type: "error" });
    } finally { setLoading(false); }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (passwords.new !== passwords.confirm) return setMsg({ text: "Passwords do not match ❌", type: "error" });
    
    setLoading(true);
    try {
      await axios.post("http://127.0.0.1:8000/api/change-password/", { new_password: passwords.new }, {
        headers: { Authorization: `Token ${token}` }
      });
      setMsg({ text: "Password Changed! Please login again. 🔒", type: "success" });
      setPasswords({ new: "", confirm: "" });
    } catch (err) {
      setMsg({ text: "Failed to change password.", type: "error" });
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 flex justify-center items-start pt-20">
      <div className="bg-white w-full max-w-2xl rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        
        {/* Header */}
        <div className="bg-indigo-600 p-8 text-center">
            <div className="w-20 h-20 bg-white text-indigo-600 rounded-full flex items-center justify-center text-3xl font-bold mx-auto mb-3 uppercase">
                {profile.username.charAt(0)}
            </div>
            <h2 className="text-2xl font-bold text-white">{profile.full_name || profile.username}</h2>
            <p className="text-indigo-200 text-sm">@{profile.username}</p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-200">
            <button onClick={() => {setActiveTab("details"); setMsg({text:"", type:""})}} className={`flex-1 py-4 font-bold text-sm ${activeTab === "details" ? "text-indigo-600 border-b-2 border-indigo-600" : "text-slate-500 hover:bg-slate-50"}`}>User Details</button>
            <button onClick={() => {setActiveTab("security"); setMsg({text:"", type:""})}} className={`flex-1 py-4 font-bold text-sm ${activeTab === "security" ? "text-indigo-600 border-b-2 border-indigo-600" : "text-slate-500 hover:bg-slate-50"}`}>Security (Password)</button>
        </div>

        {/* Content */}
        <div className="p-8">
            {msg.text && (
                <div className={`mb-6 p-3 rounded-lg text-center font-bold text-sm ${msg.type === "success" ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
                    {msg.text}
                </div>
            )}

            {/* --- TAB 1: DETAILS --- */}
            {activeTab === "details" && (
                <form onSubmit={handleUpdateProfile} className="space-y-5">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-xs font-bold text-slate-500 uppercase">Full Name</label>
                            <input type="text" value={profile.full_name} onChange={(e) => setProfile({...profile, full_name: e.target.value})} className="w-full p-3 mt-1 bg-slate-50 border rounded-xl" />
                        </div>
                        <div>
                            <label className="text-xs font-bold text-slate-500 uppercase">Age</label>
                            <input type="number" value={profile.age} onChange={(e) => setProfile({...profile, age: e.target.value})} className="w-full p-3 mt-1 bg-slate-50 border rounded-xl" />
                        </div>
                    </div>
                    <div>
                        <label className="text-xs font-bold text-slate-500 uppercase">Blood Group</label>
                        <select value={profile.blood_group} onChange={(e) => setProfile({...profile, blood_group: e.target.value})} className="w-full p-3 mt-1 bg-slate-50 border rounded-xl">
                            <option value="">Select Group</option>
                            {["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map(g => <option key={g} value={g}>{g}</option>)}
                        </select>
                    </div>
                    <button disabled={loading} className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 transition">
                        {loading ? "Saving..." : "Update Details"}
                    </button>
                </form>
            )}

            {/* --- TAB 2: SECURITY --- */}
            {activeTab === "security" && (
                <form onSubmit={handleChangePassword} className="space-y-5">
                    <div>
                        <label className="text-xs font-bold text-slate-500 uppercase">New Password</label>
                        <input type="password" value={passwords.new} onChange={(e) => setPasswords({...passwords, new: e.target.value})} className="w-full p-3 mt-1 bg-slate-50 border rounded-xl" placeholder="••••••" />
                    </div>
                    <div>
                        <label className="text-xs font-bold text-slate-500 uppercase">Confirm Password</label>
                        <input type="password" value={passwords.confirm} onChange={(e) => setPasswords({...passwords, confirm: e.target.value})} className="w-full p-3 mt-1 bg-slate-50 border rounded-xl" placeholder="••••••" />
                    </div>
                    <button disabled={loading} className="w-full bg-red-500 text-white font-bold py-3 rounded-xl hover:bg-red-600 transition">
                        {loading ? "Updating..." : "Change Password"}
                    </button>
                </form>
            )}
        </div>
      </div>
    </div>
  );
};

export default Profile;