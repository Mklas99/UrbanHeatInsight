import React from 'react';
import {
  Box,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import logger from '../../utils/logger';

const log = logger('pages/DataPage.tsx');

export default function DataPage() {

  const { t } = useTranslation<'data-page'>('data-page');
  
  // Effect for logging
  React.useEffect(() => {
    log.info('DataPage mounted');
    return () => log.info('DataPage unmounted');
  }, []);

  return (
    <Box className="data-page">
      View and manage your data uploads. open sidebar for actions.
    </Box>
  );
}