
import React, { useState } from 'react';
import { Typography, Box, Snackbar, Alert, Collapse } from '@mui/material';
import logger from '../../utils/logger';
import UploadSection from '../../components/Data/UploadSection';
import { SUPPORTED_FILE_FORMATS } from '../../constants/fileFormats';
import { useTranslation } from 'react-i18next';
import DatasetDetailsCard from '@/components/Data/DatasetDetailsCard';

const log = logger('pages/DataUploadPage.tsx');

export default function DataUploadPage(props: any) {
  const { t } = useTranslation<'data-page'>('data-page');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({ open: false, message: '', severity: 'success' });
  const [uploadedData, setUploadedData] = useState<UploadedData | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Only allow GML files for this upload
  const supportedFormats = ['.gml', '.gml32'];

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setError(null);
    setIsUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/gml/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText);
      }

      setUploadProgress(100);
      setUploadedData(await response.json());
      setShowDetails(true);
      setSnackbar({ open: true, message: t('uploadSuccess'), severity: 'success' });
    } catch (error: any) {
      setSnackbar({ open: true, message: error.message || t('uploadError'), severity: 'error' });
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcessData = () => {
    if (!uploadedData) return;
  
    // Mock data processing
    setTimeout(() => {
      log.info('Data processing complete');
    }, 2000);
  };
  
  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        {t('uploadDataTitle', 'Upload Data')}
      </Typography>
      <UploadSection
        isUploading={isUploading}
        uploadProgress={uploadProgress}
        handleFileUpload={handleFileUpload}
        supportedFormats={supportedFormats}
        t={t}
      />
      {error && <Alert severity="error" sx={{ mb: 3 }}>{t(error)}</Alert>}
      <Collapse in={showDetails && uploadedData !== null}>
        <DatasetDetailsCard
          uploadedData={uploadedData}
          handleProcessData={handleProcessData}
        />
      </Collapse>
      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}