import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, List, ListItem, ListItemIcon, ListItemText, Typography, Divider } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import TableViewIcon from '@mui/icons-material/TableView';
import EqualizerIcon from '@mui/icons-material/Equalizer';
import DownloadIcon from '@mui/icons-material/Download';

const DataSidebar: React.FC = () => {
  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        Data Navigation
      </Typography>
      <Divider />
      <List>
        <ListItem component={RouterLink} to="/data/upload">
          <ListItemIcon>
            <CloudUploadIcon />
          </ListItemIcon>
          <ListItemText primary="Upload Data" />
        </ListItem>
        <ListItem component={RouterLink} to="/data/raw">
          <ListItemIcon>
            <TableViewIcon />
          </ListItemIcon>
          <ListItemText primary="Raw Data" />
        </ListItem>
        <ListItem component={RouterLink} to="/data/processed">
          <ListItemIcon>
            <EqualizerIcon />
          </ListItemIcon>
          <ListItemText primary="Processed Data" />
        </ListItem>
        <ListItem component={RouterLink} to="/data/export">
          <ListItemIcon>
            <DownloadIcon />
          </ListItemIcon>
          <ListItemText primary="Export Data" />
        </ListItem>
      </List>
    </Box>
  );
};

export default DataSidebar;