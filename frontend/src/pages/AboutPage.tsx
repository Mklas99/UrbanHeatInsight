import React from 'react';
import logger from '../utils/logger';
import './AboutPage.css';
import { Typography, Box } from '@mui/material';

const log = logger('pages/AboutPage.tsx');

export default function AboutPage(props: any) {
  log.debug('AboutPage render', { props });
  
  React.useEffect(() => {
    log.info('AboutPage mounted');
    return () => log.info('AboutPage unmounted');
  }, []);

  return (
    <Box className="about-page" sx={{ maxWidth: 960, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        UrbanHeatInsight
      </Typography>
      <Typography variant="body1" paragraph>
        UrbanHeatInsight is an experimental platform for visualising and analysing the
        urban heat island effect in Vienna. It allows you to upload, explore and
        manipulate spatial temperature data to better understand how urban geometry,
        land use and meteorological conditions interact.
      </Typography>
      <Typography variant="body1" paragraph>
        The project is built with React, TypeScript and Material UI. It demonstrates
        how modern web mapping libraries such as Leaflet can be integrated with a
        component based architecture to build interactive data applications. The
        sidebar on this page contains useful links and metadata.
      </Typography>
    </Box>
  );
}
