import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FaHome, FaStethoscope, FaChartBar, FaGift, FaLanguage, FaUser, FaFlask } from 'react-icons/fa';

const tabs = [
  { path: "/", label: "Home", icon: <FaHome /> },
  { path: "/crop-doctor", label: "Crop Doctor", icon: <FaStethoscope /> },
  { path: "/market", label: "Market", icon: <FaChartBar /> },
  { path: "/schemes", label: "Schemes", icon: <FaGift /> },
  { path: "/soil-analysis", label: "Soil", icon: <FaFlask /> },
  { path: "/language-select", label : "language", icon: <FaLanguage /> },
  { path: "/profile", label: "Profile", icon: <FaUser /> },
];

const NavBar = () => {
  const location = useLocation();
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white shadow-lg flex justify-around py-2 z-50">
      {tabs.map(tab => (
        <Link to={tab.path} key={tab.label}>
          <div className={`flex flex-col items-center ${
            location.pathname === tab.path ? 'text-primary' : 'text-gray-500'
          }`}>
            {tab.icon}
            <span className="text-xs">{tab.label}</span>
          </div>
        </Link>
      ))}
    </nav>
  );
};
export default NavBar;
