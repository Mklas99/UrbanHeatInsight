import React from 'react';
import LayerTogglePanel from './SidebarPanels/LayerTogglePanel';
import SettingsPanel from './SidebarPanels/SettingsPanel';
import InfoPanel from './SidebarPanels/InfoPanel';
import './Sidebar.css';

function Sidebar({ sidebarOpen, cityCenterMarkerRef, setcityCenterMarkerRef, heatRadius, setHeatRadius }) {
  return (
    <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`} aria-label="Sidebar controls">
      <div className="sidebar-content">
        <LayerTogglePanel cityCenterMarkerRef={cityCenterMarkerRef} setcityCenterMarkerRef={setcityCenterMarkerRef} />
        <SettingsPanel heatRadius={heatRadius} setHeatRadius={setHeatRadius} />
        <InfoPanel />
      </div>
    </aside>
  );
}

export default Sidebar;
