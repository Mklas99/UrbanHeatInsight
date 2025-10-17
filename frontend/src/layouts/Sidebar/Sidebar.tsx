import React from 'react';
import { useLocation } from 'react-router-dom';
import MapViewSidebar from './MapViewSidebar';
import DataSidebar from './DataSidebar';
import AboutSidebar from './AboutSidebar';
import './Sidebar.css';
import logger from '../../utils/logger';

const log = logger('Sidebar');

const Sidebar: React.FC = () => {
  const location = useLocation();
  const path = location.pathname;
  
  log.debug(`Rendering sidebar for path: ${path}`);
  
  const renderSidebarContent = () => {
    if (path === '/' || path.startsWith('/map')) {
      return <MapViewSidebar />;
    } else if (path === '/data' || path.startsWith('/data/')) {
      return <DataSidebar />;
    } else if (path === '/about' || path.startsWith('/about/')) {
      return <AboutSidebar />;
    }
    
    return null;
  };

  return (
    <div className="sidebar-container">
      {renderSidebarContent()}
    </div>
  );
};

export default Sidebar;