import React from 'react';
import { Box, List, ListItem, ListItemIcon, ListItemText, Typography, Divider } from '@mui/material';
import EmailIcon from '@mui/icons-material/Email';
import PersonIcon from '@mui/icons-material/Person';
import InfoIcon from '@mui/icons-material/Info';
import GitHubIcon from '@mui/icons-material/GitHub';

const AboutSidebar: React.FC = () => {
  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h6" sx={{ p: 2 }}>
        Contact Information
      </Typography>
      <Divider />
      <List>
        <ListItem>
          <ListItemIcon>
            <PersonIcon />
          </ListItemIcon>
          <ListItemText primary="Team" secondary="Project Contributors" />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <EmailIcon />
          </ListItemIcon>
          <ListItemText primary="Email" secondary="contact@example.com" />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <GitHubIcon />
          </ListItemIcon>
          <ListItemText primary="GitHub" secondary="github.com/project-repo" />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <InfoIcon />
          </ListItemIcon>
          <ListItemText primary="Version" secondary="1.0.0" />
        </ListItem>
      </List>
    </Box>
  );
};

export default AboutSidebar;