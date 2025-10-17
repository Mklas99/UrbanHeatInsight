import React from 'react';
import { Typography, Box } from '@mui/material';
import logger from '../../utils/logger';

const log = logger('pages/DataUploadPage.tsx');

/**
 * DataUploadPage – placeholder page to demonstrate routing. In a real
 * application this would host a file upload form that allows users
 * to select and upload CSV/GeoJSON files. To keep this example
 * focused on layout concerns we simply render some explanatory text.
 */
export default function DataUploadPage(props: any) {
  log.debug('DataUploadPage render', { props });

  React.useEffect(() => {
    log.info('DataUploadPage mounted');
    return () => log.info('DataUploadPage unmounted');
  }, []);

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Upload Data
      </Typography>
      <Typography variant="body1">
        This page is a placeholder for a future data upload workflow. Here
        you would present a drag-and-drop area or file picker allowing
        users to upload their urban heat island datasets. Once uploaded the
        dataset could be validated, processed and displayed in the raw
        or processed views using the tabs in the data section.
      </Typography>
    </Box>
  );
}