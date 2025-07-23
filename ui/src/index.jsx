// File: src/index.jsx

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';
import './viewport.js';

// --- Capacitor StatusBar overlay fix ---
// Only run if Capacitor is available and on a native platform
(async () => {
  if (window.Capacitor && window.Capacitor.isNativePlatform) {
    try {
      const { StatusBar, Style } = await import('@capacitor/status-bar');
      await StatusBar.setOverlaysWebView({ overlay: true });
      await StatusBar.setStyle({ style: Style.Light }); // Optional: set light style for red background
    } catch (e) {
      // Fail silently if plugin is not available
    }
  }
})();
// --- End Capacitor StatusBar overlay fix ---

/**
 * Application entry point that renders the root component
 */
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);