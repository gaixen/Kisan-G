import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';              // <- Tailwind CSS
import App from './App';
import './i18n';                   // <- Localization setup
import { AuthProvider } from './hooks/useAuth';
import { AppProvider } from './hooks/AppContext';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <AuthProvider>
      <AppProvider>
        <App />
      </AppProvider>
    </AuthProvider>
  </React.StrictMode>
);



