import { createTheme } from '@mui/material/styles';
import logger from '../utils/logger';

const log = logger('theme/index.js');

export function getTheme(mode: 'light' | 'dark' = 'light') {
  log.debug('getTheme called', { mode });
  const theme = createTheme({
    palette: {
      mode,
      primary: { main: mode === 'light' ? '#7ac94cff' : '#519b26ff' },
      secondary: { main: mode === 'light' ? '#37474f' : '#90a4ae' },
      background: {
        default: mode === 'light' ? '#f5f5f5' : '#212121',
        paper: mode === 'light' ? '#ffffff' : '#424242',
      },
      text: {
        primary: mode === 'light' ? '#212121' : '#ffffff',
        secondary: mode === 'light' ? '#757575' : '#bdbdbd',
      },
    },
    });
  
    const typography = {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h1: { fontWeight: 700, fontSize: '1.5rem', color: theme.palette.text.primary },
      h2: { fontWeight: 700, fontSize: '1.25rem', color: theme.palette.text.primary },
      h3: { fontWeight: 600, fontSize: '1.25rem', color: theme.palette.text.primary },
      h4: { fontWeight: 600, fontSize: '1.125rem', color: theme.palette.text.primary },
      h5: { fontWeight: 500, fontSize: '1.125rem', color: theme.palette.text.primary },
      h6: { fontWeight: 500, fontSize: '1rem', color: theme.palette.text.primary },
      body1: { fontWeight: 400, fontSize: '0.9rem', lineHeight: 1.5, color: theme.palette.text.primary },
      body2: { fontWeight: 400, fontSize: '0.8rem', lineHeight: 1.5, color: theme.palette.text.primary },
    };
  
    const finalTheme = createTheme({
      ...theme,
      typography,
    shape: { borderRadius: 8 }, // Slightly smaller border radius for a modern look
    components: {
      MuiDrawer: { styleOverrides: { paper: { width: 300 } } }, // Adjusted drawer width
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none', // Remove uppercase text for buttons
            borderRadius: 8, // Match theme border radius
          },
        },
      },
    },
  });
  log.debug('theme created');
  return finalTheme;
}
