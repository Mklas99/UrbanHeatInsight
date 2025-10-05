import React from 'react';
import logger from '../../utils/logger';
import './Sidebar.css';
import { Drawer, Toolbar, Box, Divider, Typography } from '@mui/material';
import LayerTogglePanel from './SidebarPanels/LayerTogglePanel';
import SettingsPanel from './SidebarPanels/SettingsPanel';
import InfoPanel from './SidebarPanels/InfoPanel';
import { useUIStore } from '../../state/uiStore';

const log = logger('components/Sidebar/Sidebar.jsx');
log.info('Sidebar module loaded');

export default function Sidebar(props:any) {
  const sidebarOpen: boolean = useUIStore((s: { sidebarOpen: boolean }) => s.sidebarOpen);
  log.debug('Sidebar render', { props });
  React.useEffect(() => {
    log.info('Sidebar mounted');
    return () => log.info('Sidebar unmounted');
  }, []);

  return (
      <Drawer variant="persistent" anchor="left" open={sidebarOpen} className="sidebar">
        <Toolbar />
        <Box sx={{ p: 2 }} role="complementary" aria-label="Sidebar controls">
          <Typography variant="overline" color="text.secondary">Controls</Typography>
          <LayerTogglePanel />
          <Divider sx={{ my: 2 }} />
          <SettingsPanel />
          <Divider sx={{ my: 2 }} />
          <InfoPanel />
        </Box>
      </Drawer>
  );
}
