import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Providers from './Providers';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import logger from './utils/logger';
import DataPage from './pages/data/DataPage';
import DataRawPage from './pages/data/DataRawPage';
import DataModifiedPage from './pages/data/DataModifiedPage';
import DataUploadPage from './pages/data/DataUploadPage';
import RouteLayout from './layouts/RouteLayout';
import MapViewSidebar from './layouts/Sidebar/MapViewSidebar';
import DataSidebar from './layouts/Sidebar/DataSidebar';
import AboutSidebar from './layouts/Sidebar/AboutSidebar';

const log = logger('App.jsx');

export default function App() {
  React.useEffect(() => {
    log.info('App mounted');
    return () => log.info('App unmounted');
  }, []);

  return (
    <BrowserRouter>
      <Providers>
        <Routes>
          {/* Home route uses the map sidebar */}
          <Route
            path="/"
            element={
              <RouteLayout sidebar={<MapViewSidebar />}>
                <HomePage />
              </RouteLayout>
            }
          />
          {/* Data routes share the data sidebar */}
          <Route
            path="/data"
            element={
              <RouteLayout sidebar={<DataSidebar />}>
                <DataPage />
              </RouteLayout>
            }
          />
          <Route
            path="/data/upload"
            element={
              <RouteLayout sidebar={<DataSidebar />}>
                <DataUploadPage />
              </RouteLayout>
            }
          />
          <Route
            path="/data/raw"
            element={
              <RouteLayout sidebar={<DataSidebar />}>
                <DataRawPage />
              </RouteLayout>
            }
          />
          <Route
            path="/data/processed"
            element={
              <RouteLayout sidebar={<DataSidebar />}>
                <DataModifiedPage />
              </RouteLayout>
            }
          />
          {/* Alias for an export page, reusing the processed data view for now */}
          <Route
            path="/data/export"
            element={
              <RouteLayout sidebar={<DataSidebar />}>
                <DataModifiedPage />
              </RouteLayout>
            }
          />
          {/* About route uses the about sidebar */}
          <Route
            path="/about"
            element={
              <RouteLayout sidebar={<AboutSidebar />}>
                <AboutPage />
              </RouteLayout>
            }
          />
          {/* Catch-all redirects unknown routes to home */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Providers>
    </BrowserRouter>
  );
}
