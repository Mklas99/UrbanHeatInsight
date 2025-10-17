import React, { useState } from 'react';
import {
  Typography,
  Box,
  Collapse,
  Alert,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useTranslation } from 'react-i18next';
import logger from '../../utils/logger';
import DatasetDetailsCard from '../../components/Data/DatasetDetailsCard';
import UploadSection from '../../components/Data/UploadSection';
import DataTabs from '../../components/Data/DataTabs';
import { formatFileSize, calculateHeatIndex, generateMockData } from '../../utils/dataUtils';

import { SUPPORTED_FILE_FORMATS } from '../../constants/fileFormats';
import type { UploadedData } from '@/models/UploadData';

const log = logger('pages/DataPage.tsx');

export default function DataPage() {

  const { t } = useTranslation<'data-page'>('data-page');

  // State
  const [uploadedData, setUploadedData] = useState<UploadedData | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showDetails, setShowDetails] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [processingData, setProcessingData] = useState(false);
  const [processingComplete, setProcessingComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Event handlers
  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setError(null);
    setIsUploading(true);
    setUploadProgress(0);
    
    // Mock file upload with progress
    const timer = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(timer);
          handleUploadComplete(file);
          return 100;
        }
        return prev + 10;
      });
    }, 300);
  };
  
  const handleUploadComplete = (file: File) => {
    // Mock successful upload after delay
    setTimeout(() => {
      setIsUploading(false);
      
      // Create mock data stats
      const mockData: UploadedData = {
        fileName: file.name,
        fileSize: formatFileSize(file.size),
        uploadTime: new Date().toLocaleString(),
        format: file.name.split('.').pop()?.toUpperCase() || 'UNKNOWN',
        stats: {
          rowCount: 1250,
          columnCount: 8,
          dataTypes: {
            'latitude': 'float64',
            'longitude': 'float64',
            'temperature': 'float64',
            'humidity': 'float64',
            'timestamp': 'datetime64',
            'sensor_id': 'int64',
            'location_name': 'string',
            'measurement_quality': 'string'
          },
          missingValues: {
            'temperature': 12,
            'humidity': 8,
            'location_name': 3
          },
          memoryUsage: '1.2 MB'
        },
        data: generateMockData(20),
        processedData: null
      };
      
      setUploadedData(mockData);
      setShowDetails(true);
      log.info('File upload complete', { fileName: file.name, fileSize: file.size });
    }, 500);
  };
  
  const handleProcessData = () => {
    if (!uploadedData) return;
    
    setProcessingData(true);
    
    // Mock data processing
    setTimeout(() => {
      setUploadedData(prev => {
        if (!prev) return null;
        
        // Create processed data by transforming the original data
        const processed = prev.data.map(row => {
          // Apply some transformations to the data
          const transformedRow = {...row};
          if (typeof row.temperature === 'number') {
            // Convert to Fahrenheit from Celsius
            transformedRow.temperature_f = (row.temperature * 9/5) + 32;
          }
          if (typeof row.humidity === 'number') {
            // Normalize humidity to 0-1 range
            transformedRow.humidity_normalized = row.humidity / 100;
          }
          // Add heat index calculation
          if (typeof row.temperature === 'number' && typeof row.humidity === 'number') {
            transformedRow.heat_index = calculateHeatIndex(row.temperature, row.humidity);
          }
          return transformedRow;
        });
        
        return {
          ...prev,
          processedData: processed
        };
      });
      
      setProcessingData(false);
      setProcessingComplete(true);
      log.info('Data processing complete');
    }, 2000);
  };
  
  // Effect for logging
  React.useEffect(() => {
    log.info('DataPage mounted');
    return () => log.info('DataPage unmounted');
  }, []);

  return (
    <Box className="data-page">
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        <Typography variant="h4" gutterBottom>
          {t('title')}
        </Typography>
        <UploadSection
          isUploading={isUploading}
          uploadProgress={uploadProgress}
          handleFileUpload={handleFileUpload}
          supportedFormats={SUPPORTED_FILE_FORMATS}
          t={t} // Pass translation function to UploadSection
        />
        {error && <Alert severity="error" sx={{ mb: 3 }}>{t(error)}</Alert>}
        <Collapse in={showDetails && uploadedData !== null}>
          <DatasetDetailsCard
            uploadedData={uploadedData}
            processingData={processingData}
            processingComplete={processingComplete}
            handleProcessData={handleProcessData}
          />
          <DataTabs
            tabValue={tabValue}
            setTabValue={setTabValue}
            uploadedData={uploadedData}
            processingComplete={processingComplete}
          />
        </Collapse>
        {!uploadedData && !isUploading && (
          <Box
            sx={{
              p: 4,
              textAlign: 'center',
              border: '2px dashed',
              borderColor: 'divider',
              borderRadius: 2,
              bgcolor: 'background.paper',
              mt: 2,
            }}
          >
            <UploadFileIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6">{t('emptyState.title')}</Typography>
            <Typography variant="body2" color="text.secondary">
              {t('emptyState.description')}
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}