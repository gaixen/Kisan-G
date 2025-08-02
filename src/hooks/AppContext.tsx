import React, { createContext, useState, useEffect, ReactNode } from "react";

type User = {
  name: string;
  phone: string;
  language: string;
  location: string;
};

type Crop = { name: string; stage: string};
//...other props };

type AppContextType = {
  user: User | null;
  crops: Crop[];
  highlights: string[];
  language: string;
  hasSelectedLanguage: boolean;
  setLanguage: (lang: string) => void;
  logout: () => void;
  // ...other state
};

export const AppContext = createContext<AppContextType>({} as AppContextType);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Dummy data for brevity
  const [user, setUser] = useState<User | null>({ name: "Rohan", phone: "+91 922XXXXXXX", language: "en", location: "Bengaluru, Karnataka" });
  const [language, setLanguage] = useState<string>('');
  const [hasSelectedLanguage, setHasSelectedLanguage] = useState<boolean>(false);
  const [crops, setCrops] = useState<Crop[]>([
    { name: "Wheat", stage: "Tillering" },
    { name: "Maize", stage: "Vegetative" },
    { name: "paddy", stage: "tilling"},

    //...
  ]);
  const [highlights, setHighlights] = useState<string[]>([
    "Cloudy weather expected this week, avoid spraying pesticides in Tomato till sunshine returns.",
    "With upcoming rainfall, delay urea top dressing for Maize to avoid nutrient washout.",
  ]);

  useEffect(() => {
    const savedLanguage = localStorage.getItem('selectedLanguage');
    if (savedLanguage) {
      setLanguage(savedLanguage);
      setHasSelectedLanguage(true);
    }
  }, []);

  const handleSetLanguage = (lng: string) => {
    setLanguage(lng);
    setHasSelectedLanguage(true);
    // Persist language selection in localStorage
    localStorage.setItem('selectedLanguage', lng);
  };

  const logout = () => {
    setUser(null);
    setHasSelectedLanguage(false);
    localStorage.removeItem('selectedLanguage');
    window.location.href = '/login';
  };

  return (
    <AppContext.Provider value={{
      user, crops, highlights, language, hasSelectedLanguage,
      setLanguage: handleSetLanguage,
      logout
    }}>
      {children}
    </AppContext.Provider>
  );
};
