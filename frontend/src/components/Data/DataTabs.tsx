import React from 'react';
import { Box, Paper, Tabs, Tab, Typography, TableContainer, Table, TableHead, TableRow, TableCell, TableBody, Chip } from '@mui/material';
import TableChartIcon from '@mui/icons-material/TableChart';
import SettingsIcon from '@mui/icons-material/Settings';
import TabPanel from './TabPanel';
import type { UploadedData } from '@/models/UploadData';
import { useTranslation } from 'react-i18next';

interface DataTabsProps {
  tabValue: number;
  setTabValue: (value: number) => void;
  uploadedData: UploadedData | null;
  processingComplete: boolean;
}

export default function DataTabs({
  tabValue,
  setTabValue,
  uploadedData,
  processingComplete,
}: DataTabsProps) {
  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const { t } = useTranslation<'data-page'>('data-page');
  return (
    <Paper sx={{ mb: 4 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="data tabs">
          <Tab
            label="Raw Data"
            icon={<TableChartIcon />}
            iconPosition="start"
            id="data-tab-0"
            aria-controls="data-tabpanel-0"
          />
          <Tab
            label="Processed Data"
            icon={<SettingsIcon />}
            iconPosition="start"
            id="data-tab-1"
            aria-controls="data-tabpanel-1"
            disabled={!processingComplete}
          />
        </Tabs>
      </Box>
      <TabPanel value={tabValue} index={0}>
        <Typography variant="subtitle1" gutterBottom>
          Raw Data Preview (20 rows)
        </Typography>
        <TableContainer>
          <Table size="small" aria-label="raw data table">
            <TableHead>
              <TableRow>
                {uploadedData?.data && uploadedData.data.length > 0 &&
                  Object.keys(uploadedData?.data?.[0] || {}).map((key) => (
                    <TableCell key={key}>{key}</TableCell>
                  ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {uploadedData?.data?.map((row, index) => (
                <TableRow key={index}>
                  {Object.values(row).map((value, i) => (
                    <TableCell key={i}>{String(value)}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        <Typography variant="subtitle1" gutterBottom>
          Processed Data Preview with Added Features
        </Typography>
        <TableContainer>
          <Table size="small" aria-label="processed data table">
            <TableHead>
              <TableRow>
                {uploadedData?.processedData && uploadedData.processedData.length > 0 &&
                  Object.keys(uploadedData?.processedData?.[0] || {}).map((key) => (
                    <TableCell
                      key={key}
                      sx={{
                        backgroundColor: !uploadedData?.data?.[0]?.hasOwnProperty(key)
                          ? 'rgba(76, 175, 80, 0.1)'
                          : undefined,
                      }}
                    >
                      {key}
                      {!uploadedData?.data?.[0]?.hasOwnProperty(key) && (
                        <Chip
                          size="small"
                          label="new"
                          color="success"
                          sx={{ ml: 1, height: 16, fontSize: '0.6rem' }}
                        />
                      )}
                    </TableCell>
                  ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {uploadedData?.processedData?.map((row, index) => (
                <TableRow key={index}>
                  {Object.values(row).map((value, i) => (
                    <TableCell key={i}>{String(value)}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>
    </Paper>
  );
}
