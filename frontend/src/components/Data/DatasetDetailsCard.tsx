import React from 'react';
import { Card, CardContent, CardActions, Typography, Box, Chip, Divider, Button, CircularProgress } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import SettingsIcon from '@mui/icons-material/Settings';
import { useTranslation } from 'react-i18next';

export default function DatasetDetailsCard({ uploadedData, processingData, processingComplete, handleProcessData }: any) {

  const { t } = useTranslation<'data-page'>('data-page');
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6">{t('datasetTitle', { fileName: uploadedData?.fileName })}</Typography>
          <Chip label={uploadedData?.format} color="primary" size="small" variant="outlined" />
        </Box>
        <Divider sx={{ my: 2 }} />
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 2 }}>
          {/* ...existing code for dataset details... */}
        </Box>
      </CardContent>
      <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={processingComplete ? <CheckCircleIcon /> : <SettingsIcon />}
          onClick={handleProcessData}
          disabled={processingData || processingComplete}
        >
          {processingData ? (
            <>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              {t('processing')}
            </>
          ) : processingComplete ? (
            t('processed')
          ) : (
            t('processData')
          )}
        </Button>
      </CardActions>
    </Card>
  );
}
