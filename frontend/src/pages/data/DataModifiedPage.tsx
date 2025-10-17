import React from 'react';
import logger from '../../utils/logger';
import { Box, Typography } from '@mui/material';

const log = logger('pages/DataModifiedPage.tsx');

export default function DataModifiedPage() {
  
  React.useEffect(() => {
    log.info('DataModifiedPage mounted');
    return () => log.info('DataModifiedPage unmounted');
  }, []);

  return (
    <Box sx={{ p: 3, maxWidth: 960, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Processed Data
      </Typography>
      <Typography variant="body1">
        This page will show the results of any processing steps you run on your
        uploaded dataset. Typical operations could include unit conversions,
        filtering, aggregations or the calculation of heat indices. For the
        purposes of this demonstration the page contains only explanatory text.
      </Typography>
    </Box>
  );
}
