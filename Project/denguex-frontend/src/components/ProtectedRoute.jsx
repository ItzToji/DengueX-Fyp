import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ user, children }) => {
  // Agar User login nahi hai (null hai), to Login page par bhej do
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  // Agar User hai, to jo page manga hai wo dikhao (Children)
  return children;
};

export default ProtectedRoute;