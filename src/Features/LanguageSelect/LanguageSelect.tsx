import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppContext } from '../../hooks/AppContext';

const LANGUAGES = [
  { code: "hi", label: "Hindi", native: "हिन्दी" },
  { code: "kn", label: "Kannada", native: "ಕನ್ನಡ" },
  { code: "en", label: "English", native: "English" },
  { code: "bn", label: "Bengali", native: "বাংলা" },
  { code: "te", label: "Telugu", native: "తెలుగు" },
  { code: "mr", label: "Marathi", native: "मराठी" },
  { code: "ta", label: "Tamil", native: "தமிழ்" },
  { code: "gu", label: "Gujarati", native: "ગુજરાતી" },
  { code: "ml", label: "Malayalam", native: "മലയാളം" },
  { code: "pa", label: "Punjabi", native: "ਪੰਜਾਬੀ" },
];

interface LanguageSelectProps {
    onLanguageSelect: () => void;
}

const LanguageSelect: React.FC<LanguageSelectProps> = ({ onLanguageSelect }) => {
  const { setLanguage } = useContext(AppContext);
  const navigate = useNavigate();

  const handleSelect = (lang: string) => {
    setLanguage(lang);
    onLanguageSelect();
    // Navigation will be handled automatically by RequireLanguage component
  };

  return (
    <div className="flex flex-col h-screen items-center justify-center bg-gray-50">
      <img src="/assets/kisan-g-logo.jpg" alt="KisanG Logo" className="mb-8 w-32" />
      <h2 className="text-lg font-bold mb-4">Select your language</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {LANGUAGES.map(l => (
          <button
            key={l.code}
            className="bg-primary text-white rounded-lg px-6 py-3 text-md font-semibold hover:bg-green-700 transition"
            onClick={() => handleSelect(l.code)}
          >
            {l.label} <span className="block text-xs">{l.native}</span>
          </button>
        ))}
      </div>
      <p className="mt-6 text-gray-500">You can change your language anytime.</p>
    </div>
  );
};
export default LanguageSelect;
