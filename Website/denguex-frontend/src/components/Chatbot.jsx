import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom"; 
import ReactMarkdown from 'react-markdown'; 

// --- SVG ICONS ---
const PlusIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>;
const MessageIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2-2h14a2 2 0 0 1 2-2h14a2 2 0 0 1 2-2z"/></svg>;
const SendIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>;
const BotIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/><line x1="8" y1="16" x2="8" y2="16"/><line x1="16" y1="16" x2="16" y2="16"/></svg>;
const UserIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
const MenuIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>;
const CloseIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>;
// ✅ NEW TRASH ICON
const TrashIcon = () => <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="gray" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="hover:stroke-red-500 transition-colors"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>;

const Chatbot = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  
  const [userProfile, setUserProfile] = useState({ full_name: "Loading...", age: "" });
  const [showProfileCard, setShowProfileCard] = useState(false);

  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  
  const token = localStorage.getItem('token') || localStorage.getItem('access_token'); 

  useEffect(() => {
    if (!token) {
        console.warn("No Token Found.");
    } else {
        fetchSessions();
        fetchUserProfile();
    }
  }, [token]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const getAuthHeaders = () => {
      return { 
          'Authorization': `Token ${token}`, 
          'Content-Type': 'application/json'
      };
  };

  const fetchUserProfile = async () => {
    if(!token) return;
    try {
      const res = await axios.post("http://127.0.0.1:8000/api/get-profile/", {}, {
        headers: getAuthHeaders()
      });
      const name = res.data.full_name || res.data.username || "User";
      setUserProfile({ 
          full_name: name, 
          age: res.data.age || "N/A" 
      });
    } catch (err) { console.error("Profile Fetch Error:", err); }
  };

  const fetchSessions = async () => {
    if(!token) return;
    try {
      const res = await axios.get("http://127.0.0.1:8000/api/chat-sessions/", {
        headers: getAuthHeaders()
      });
      setSessions(res.data);
    } catch (err) { console.error("Session Fetch Error:", err); }
  };

  const loadSession = async (id) => {
    setCurrentSessionId(id);
    setLoading(true);
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/chat-messages/${id}/`, {
        headers: getAuthHeaders()
      });
      setMessages(res.data);
    } catch (err) { console.error("Message Load Error:", err); }
    setLoading(false);
  };

  // ✅ DELETE FUNCTION
  const deleteSession = async (e, id) => {
    e.stopPropagation(); // Chat load hone se roko
    
    if(!window.confirm("Are you sure you want to delete this chat?")) return;

    try {
        await axios.delete(`http://127.0.0.1:8000/api/delete-chat/${id}/`, {
            headers: getAuthHeaders()
        });
        
        // Remove from list
        setSessions(prev => prev.filter(s => s.id !== id));
        
        // Agar wohi chat khuli thi, to screen saaf kardo
        if (currentSessionId === id) {
            handleNewChat();
        }

    } catch (err) {
        alert("Failed to delete chat.");
        console.error(err);
    }
  };

  const handleNewChat = () => {
    setCurrentSessionId(null);
    setMessages([]);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/chat/", {
        message: input,
        session_id: currentSessionId
      }, {
        headers: getAuthHeaders()
      });

      const botMsg = { text: res.data.response, sender: "bot" };
      setMessages((prev) => [...prev, botMsg]);

      if (!currentSessionId) {
        setCurrentSessionId(res.data.session_id);
        fetchSessions();
      }
    } catch (error) {
      console.error("Chat Error:", error);
      let errorText = "Error: Unable to connect to AI.";
      if(error.response && error.response.status === 401) {
          errorText = "Error: Session Expired. Please Logout & Login again.";
      }
      setMessages((prev) => [...prev, { text: errorText, sender: "bot" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex w-full h-[85vh] bg-white overflow-hidden font-sans border-b border-slate-200 shadow-sm relative">
      
      {/* SIDEBAR */}
      <div className={`${isSidebarOpen ? 'w-[260px]' : 'w-0'} bg-[#202123] text-gray-100 flex flex-col transition-all duration-300 ease-in-out border-r border-gray-700 relative`}>
        <div className="p-3">
          <button onClick={handleNewChat} className="w-full flex items-center gap-3 border border-gray-600 rounded-md px-3 py-3 text-sm hover:bg-gray-700 transition-colors text-white">
            <PlusIcon /> New chat
          </button>
        </div>
        
        {/* ✅ CHAT HISTORY WITH DELETE BUTTON */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1 custom-scrollbar">
            <h4 className="text-xs font-semibold text-gray-500 px-3 py-2 mt-2">History</h4>
            {sessions.map((session) => (
              <div 
                key={session.id} 
                onClick={() => loadSession(session.id)} 
                className={`group flex items-center justify-between w-full px-3 py-3 rounded-md text-sm cursor-pointer transition-colors ${currentSessionId === session.id ? 'bg-[#343541]' : 'hover:bg-[#2A2B32]'}`}
              >
                <div className="flex items-center gap-3 overflow-hidden">
                    <MessageIcon />
                    <span className="truncate flex-1">{session.title}</span>
                </div>
                {/* Delete Button (Sirf Hover par dikhega) */}
                <button 
                    onClick={(e) => deleteSession(e, session.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-700 rounded transition-opacity"
                    title="Delete Chat"
                >
                    <TrashIcon />
                </button>
              </div>
            ))}
        </div>

        {/* PROFILE CARD */}
        {showProfileCard && (
            <div className="absolute bottom-[110px] left-4 w-[230px] bg-[#343541] border border-gray-600 rounded-lg shadow-xl p-4 z-50 text-white animate-fade-in-up">
                <div className="flex justify-between items-start mb-2">
                    <h3 className="text-sm font-bold text-gray-300">User Profile</h3>
                    <button onClick={() => setShowProfileCard(false)} className="text-gray-400 hover:text-white">
                        <CloseIcon />
                    </button>
                </div>
                <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center font-bold text-lg">
                        {userProfile.full_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <p className="font-semibold text-sm truncate w-[140px]">{userProfile.full_name}</p>
                        <p className="text-xs text-green-400">Online</p>
                    </div>
                </div>
                <div className="bg-[#444654] p-2 rounded text-xs space-y-1">
                    <div className="flex justify-between">
                        <span className="text-gray-400">Age:</span>
                        <span className="font-medium">{userProfile.age ? userProfile.age + " Years" : "Not Set"}</span>
                    </div>
                </div>
            </div>
        )}

        {/* SIDEBAR FOOTER */}
        <div className="h-[100px] flex items-center px-4 border-t border-gray-600 bg-[#202123]">
           <div 
             onClick={() => setShowProfileCard(!showProfileCard)}
             className="flex items-center gap-3 w-full hover:bg-gray-700 p-2 rounded-md cursor-pointer transition-colors"
           >
              <div className="w-8 h-8 rounded-sm bg-green-600 flex items-center justify-center font-bold text-white">
                {userProfile.full_name.charAt(0).toUpperCase()}
              </div>
              <div className="text-sm font-medium truncate">
                {userProfile.full_name}
              </div>
           </div>
        </div>
      </div>

      {/* MAIN CHAT */}
      <div className="flex-1 flex flex-col bg-white">
        <div className="h-12 border-b border-gray-200 flex items-center px-4 bg-white md:hidden">
             <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="text-gray-500 hover:text-gray-700"><MenuIcon /></button>
             <span className="ml-4 font-semibold text-gray-700">DengueX Assistant</span>
        </div>
        
        <div className="flex-1 overflow-y-auto w-full">
            {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-4">
                    <div className="bg-white p-4 rounded-full shadow-sm mb-6 border border-gray-100"><div className="w-12 h-12 text-blue-600"><BotIcon /></div></div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">How can I help you today?</h2>
                    <p className="text-gray-500 mb-8 max-w-md">Ask about Dengue stats, prevention tips, or check risk levels in your city.</p>
                </div>
            ) : (
                <div className="flex flex-col pb-4 pt-6">
                    {messages.map((msg, index) => (
                        <div key={index} className={`w-full border-b border-black/5 ${msg.sender === 'bot' ? 'bg-[#F7F7F8]' : 'bg-white'}`}>
                            <div className="max-w-3xl mx-auto flex gap-4 p-4 md:p-6 text-base">
                                <div className={`w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-sm ${msg.sender === 'bot' ? 'bg-[#19c37d]' : 'bg-[#5436DA]'} text-white`}>{msg.sender === 'bot' ? <BotIcon /> : <UserIcon />}</div>
                                
                                <div className="prose prose-slate max-w-none flex-1 leading-7 text-gray-800">
                                    <ReactMarkdown>{msg.text}</ReactMarkdown>
                                </div>
                            </div>
                        </div>
                    ))}
                    {loading && (<div className="w-full bg-[#F7F7F8] border-b border-black/5"><div className="max-w-3xl mx-auto flex gap-4 p-4 md:p-6"><div className="w-8 h-8 bg-[#19c37d] rounded-sm flex items-center justify-center text-white"><BotIcon /></div><div className="text-sm text-gray-500">Thinking...</div></div></div>)}
                    <div ref={messagesEndRef} />
                </div>
            )}
        </div>

        <div className="h-[100px] flex flex-col justify-center border-t border-gray-200 bg-white px-4 md:px-6">
            <div className="max-w-3xl mx-auto w-full">
                <div className="flex items-center bg-white border border-gray-300 shadow-sm rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-blue-400/50 focus-within:border-blue-400">
                    <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendMessage()} placeholder="Send a message..." className="flex-1 p-3 px-4 bg-transparent outline-none text-gray-700" autoFocus />
                    <button onClick={sendMessage} disabled={loading || !input.trim()} className={`p-2 mr-2 rounded-md transition-colors ${input.trim() ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'text-gray-400'}`}><SendIcon /></button>
                </div>
                <div className="w-full text-center mt-2"><p className="text-[10px] text-gray-400">DengueX AI can make mistakes. Verify info.</p></div>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;