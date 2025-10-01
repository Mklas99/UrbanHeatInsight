import React from 'react';
import Sidebar from '../components/Sidebar/Sidebar';
import MapView from '../components/MapView';
import './HomePage.css';

function HomePage({ sidebarOpen, cityCenterMarkerRef, setcityCenterMarkerRef, heatRadius, setHeatRadius }) {
  return (
    <div className="home-container">
      <Sidebar
        sidebarOpen={sidebarOpen}
        cityCenterMarkerRef={cityCenterMarkerRef}
        setcityCenterMarkerRef={setcityCenterMarkerRef}
        heatRadius={heatRadius}
        setHeatRadius={setHeatRadius}
      />
      <main className={`map-container ${sidebarOpen ? 'with-sidebar' : 'full-width'}`}>
        <MapView cityCenterMarkerRef={cityCenterMarkerRef} heatRadius={heatRadius} />
      </main>
    </div>
  );
}

export default HomePage;
