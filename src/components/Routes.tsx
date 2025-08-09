import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '../Features/Dashboard/DashBoard';
import CropDoctor from '../Features/CropDoctor/CropDoctor';
import MarketAnalyst from '../Features/MarketAnalyst/MarketAnalyst';
import SchemeNavigator from '../Features/SchemeNavigator/SchemeNavigator';
import SoilAnalysis from '../Features/SoilAnalysis/SoilAnalysis';
import VoiceAssistant from './VoiceAssistant';
import Login from '../Features/Auth/Login';
import Signup from '../Features/Auth/Signup';
import LanguageSelect from '../Features/LanguageSelect/LanguageSelect';
import Profile from '../Features/Profile/Profile';
import { useAuth } from '../hooks/useAuth';

const AppRoutes: React.FC = () => {
    const { user } = useAuth();
    const [languageSelected, setLanguageSelected] = useState(false);

    const handleLanguageSelect = () => {
        setLanguageSelected(true);
    };

    return (
        <Router>
            <Routes>
                {!user ? (
                    <>
                        <Route path="/login" element={<Login />} />
                        <Route path="/signup" element={<Signup />} />
                        <Route path="*" element={<Navigate to="/login" />} />
                    </>
                ) : !languageSelected ? (
                    <Route path="*" element={<LanguageSelect onLanguageSelect={handleLanguageSelect} />} />
                ) : (
                    <>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/crop-doctor" element={<CropDoctor />} />
                        <Route path="/market-analyst" element={<MarketAnalyst />} />
                        <Route path="/scheme-navigator" element={<SchemeNavigator />} />
                        <Route path="/soil-analysis" element={<SoilAnalysis />} />
                        <Route path="/profile" element={<Profile />} />
                    </>
                )}
            </Routes>
            {user && languageSelected && <VoiceAssistant />}
        </Router>
    );
};

export default AppRoutes;