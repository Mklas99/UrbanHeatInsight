import React from 'react';
import { Box, Button, CircularProgress, LinearProgress, Typography } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useTranslation } from 'react-i18next';

interface UploadSectionProps {
  isUploading: boolean;
  uploadProgress: number;
  handleFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  supportedFormats: string[];
  t: (key: string) => string; // Translation function
}

export default function UploadSection({
  isUploading,
  uploadProgress,
  handleFileUpload,
  supportedFormats
}: UploadSectionProps) {

  const { t } = useTranslation<'data-page'>('data-page');
  return (
    <Box sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadFileIcon />}
          disabled={isUploading}
        >
          {t('uploadButton')}
          <input
            type="file"
            hidden
            accept={supportedFormats.join(',')}
            onChange={handleFileUpload}
          />
        </Button>
        <Typography variant="body2" color="text.secondary">
          {t('supportedFormats', supportedFormats.join(', '))}
        </Typography>
        {isUploading && (
          <Box sx={{ display: 'flex', alignItems: 'center', ml: 'auto', gap: 1 }}>
            <CircularProgress size={20} />
            <Typography variant="body2">{t('uploading', { progress: uploadProgress })}</Typography>
          </Box>
        )}
      </Box>
      {isUploading && <LinearProgress variant="determinate" value={uploadProgress} sx={{ mt: 2 }} />}
    </Box>
  );
}
