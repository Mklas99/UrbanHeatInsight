import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Providers from './Providers';
import Header from './components/Header';
import Sidebar from './components/Sidebar/Sidebar';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import logger from './utils/logger';

const log = logger('App.jsx');
log.info('App module loaded');

export default function App() {
  React.useEffect(() => {
    log.info('App mounted');
    return () => log.info('App unmounted');
  }, []);

  log.debug('render App');
  return (
    <BrowserRouter>
      <Providers>
        <Header />
        <Sidebar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Providers>
    </BrowserRouter>
  );
}
