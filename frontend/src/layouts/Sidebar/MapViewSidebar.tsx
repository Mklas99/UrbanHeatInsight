import React from 'react';
import { Box, List, ListItem, ListItemIcon, ListItemText, Typography, Divider, Switch, Slider, FormControlLabel } from '@mui/material';
import LayersIcon from '@mui/icons-material/Layers';
import MapIcon from '@mui/icons-material/Map';
import SettingsIcon from '@mui/icons-material/Settings';
import TerrainIcon from '@mui/icons-material/Terrain';
import ZoomInMapIcon from '@mui/icons-material/ZoomInMap';

const MapViewSidebar: React.FC = () => {
  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        Map Settings
      </Typography>
      <Divider />
      <List>
        <ListItem>
          <ListItemIcon>
            <LayersIcon />
          </ListItemIcon>
          <ListItemText primary="Show Layers" />
          <Switch defaultChecked />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <TerrainIcon />
          </ListItemIcon>
          <ListItemText primary="3D Terrain" />
          <Switch />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <ZoomInMapIcon />
          </ListItemIcon>
          <ListItemText primary="Zoom Level" />
        </ListItem>
        <ListItem>
          <Box sx={{ width: '100%', pl: 2, pr: 2 }}>
            <Slider
              defaultValue={8}
              step={1}
              marks
              min={1}
              max={18}
              valueLabelDisplay="auto"
            />
          </Box>
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <MapIcon />
          </ListItemIcon>
          <ListItemText primary="Map Type" secondary="Standard" />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Advanced Settings" />
        </ListItem>
      </List>
    </Box>
  );
};

export default MapViewSidebar;