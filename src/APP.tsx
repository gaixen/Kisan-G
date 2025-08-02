import * as React from 'react';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Dashboard from './Features/Dashboard/DashBoard';
import CropDoctor from './Features/CropDoctor/CropDoctor';
import MarketAnalyst from './Features/MarketAnalyst/MarketAnalyst';
import SchemeNavigator from './Features/SchemeNavigator/SchemeNavigator';
import Profile from './Features/Profile/Profile';
import LanguageSelect from './Features/LanguageSelect/LanguageSelect';
import NavBar from '../remote/src/components/NavBar';
import { AppProvider, AppContext } from '../remote/src/hooks/AppContext';
import { AuthProvider, useAuth } from '../remote/src/hooks/useAuth';
import Login from './Features/Auth/Login';
import Signup from './Features/Auth/Signup';

const RequireAuth: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const { user } = useAuth();
  // Show a loading spinner or fallback while checking auth if needed
  if (!user) return <Login />;
  return <>{children}</>;
};

const RequireLanguage: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const { hasSelectedLanguage } = React.useContext(AppContext);
  if (!hasSelectedLanguage) return <LanguageSelect />;
  return <>{children}</>;
};

const express = require('express');
const cors = require('cors');
const geminiRoute = require('./routes/gemini');
const app = express();

const App: React.FC = () => (
  <AuthProvider>
    <Router>
      <NavBar />
      <Routes> 
        <Route path = "/login" element = {<Login/>} />
        <Route path = "/signup" element = {<Signup/>} />
        <Route path = "/*" element = {
          <RequireAuth>
            <AppProvider>
              <RequireLanguage>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/crop-doctor" element={<CropDoctor />} />
                  <Route path="/market" element={<MarketAnalyst />} />
                  <Route path="/schemes" element={<SchemeNavigator />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/languages" element={<LanguageSelect />} />
                </Routes>
              </RequireLanguage>
            </AppProvider>
          </RequireAuth>
        }/>
      </Routes>
      <NavBar />
    </Router>
  </AuthProvider>
);

export default App;
