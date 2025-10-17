import React from 'react';
import logger from '../utils/logger';
import MapView from '../components/MapView';
import './HomePage.css';
import { Box } from '@mui/material';

const log = logger('pages/HomePage.jsx');

export default function HomePage(props: any) {
  log.debug('HomePage render', { props });
  
  React.useEffect(() => {
    log.info('HomePage mounted');
    return () => log.info('HomePage unmounted');
  }, []);

  return (
    <Box className="home-page">
      {/* The MapView component takes care of its own sizing. Wrapping it in a Box
          allows the RouteLayout to control margins while the map fills the
          available space. */}
      <MapView />
    </Box>
  );
}
