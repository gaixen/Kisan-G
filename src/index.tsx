import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';              // <- Tailwind CSS
import App from './APP';
import '../remote/src/i18n';                   // <- Localization setup

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);



