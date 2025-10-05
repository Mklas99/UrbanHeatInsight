import { createTheme } from '@mui/material/styles';
import logger from '../utils/logger';

const log = logger('theme/index.js');
log.info('theme module loaded');


export function getTheme(mode: 'light' | 'dark' = 'light') {
  log.debug('getTheme called', { mode });
  const theme = createTheme({
    palette: {
      mode,
      primary: { main: '#00796b' },
      secondary: { main: '#8e24aa' },
    },
    shape: { borderRadius: 12 },
    components: {
      MuiDrawer: { styleOverrides: { paper: { width: 320 } } },
    },
  });
  log.debug('theme created');
  return theme;
}
