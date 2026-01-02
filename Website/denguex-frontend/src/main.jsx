import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css' // Agar ye file nahi hai to is line ko hata dein
import { GoogleOAuthProvider } from '@react-oauth/google';
import 'leaflet/dist/leaflet.css';
// 🔴 APNI CLIENT ID YAHAN PASTE KAREIN (Quotes ke andar)
const GOOGLE_CLIENT_ID = "309442616660-a9o27abc4ele1ndu8n4vualb3c4momtv.apps.googleusercontent.com";

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* App ko Google Provider se wrap karna zaroori hai */}
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>,
)
