import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import logger from './utils/logger';
import 'leaflet/dist/leaflet.css';

const log = logger('index.tsx');

log.info("Application initialization started");

const container = document.getElementById('root');
if (!container) {
  log.error("Root container not found");
} else {
  const root = createRoot(container);
  root.render(
    React.createElement(
      React.StrictMode,
      null,
      React.createElement(App, null)
    )
  );
  log.info("React app rendered successfully");
}