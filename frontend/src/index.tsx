import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import logger from './utils/logger';
import 'leaflet/dist/leaflet.css';

const log = logger('index.tsx');

const container = document.getElementById('root');
if (!container) {
    log.error('Root container not found');
} else {
    const root = createRoot(container);
    log.info('mounting React App');
    root.render(
        React.createElement(
            React.StrictMode,
            null,
            React.createElement(App, null)
        )
    );
    log.info('React App mounted');
}