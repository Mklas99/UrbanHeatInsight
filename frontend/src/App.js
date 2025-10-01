import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar/Sidebar';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [cityCenterMarkerRef, setcityCenterMarkerRef] = useState(true);
  const [heatRadius, setHeatRadius] = useState(25);

  return (
    <Router>
      <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <Routes>
        <Route path="/" element={
          <HomePage
            sidebarOpen={sidebarOpen}
            cityCenterMarkerRef={cityCenterMarkerRef}
            setcityCenterMarkerRef={setcityCenterMarkerRef}
            heatRadius={heatRadius}
            setHeatRadius={setHeatRadius}
          />
        } />
        <Route path="/about" element={<AboutPage />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
