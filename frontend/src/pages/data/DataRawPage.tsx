import React from 'react';
import logger from '../../utils/logger';
import { Box, Typography } from '@mui/material';

const log = logger('pages/DataRawPage.tsx');

export default function DataRawPage(props: any) {
  log.debug('DataRawPage render', { props });
  
  React.useEffect(() => {
    log.info('DataRawPage mounted');
    return () => log.info('DataRawPage unmounted');
  }, []);

  return (
    <Box sx={{ p: 3, maxWidth: 960, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Raw Data
      </Typography>
      <Typography variant="body1">
        This page will display the raw datasets you have uploaded. In a real
        application you might show a table, charts or a map preview of your
        data. For now, this placeholder explains the intent of the raw data view.
      </Typography>
    </Box>
  );
}
