import React from 'react';
import logger from '../utils/logger';
import './Header.css';
import { AppBar, Toolbar, Typography, IconButton, Box, Select, MenuItem, Tooltip } from '@mui/material';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import MenuIcon from '@mui/icons-material/Menu';
import LanguageIcon from '@mui/icons-material/Language';
import { useTranslation } from 'react-i18next';
import { useUIStore } from '../state/uiStore';

const log = logger('components/Header.jsx');
log.info('Header module loaded');

interface HeaderProps {}

export default function Header(props: HeaderProps){
  const { t } = useTranslation<'common'>('common');
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);
  const themeMode = useUIStore((s) => s.themeMode);
  const toggleTheme = useUIStore((s) => s.toggleTheme);
  const language = useUIStore((s) => s.language);
  const setLanguage = useUIStore((s) => s.setLanguage);

  log.debug('Header render', { props });
  React.useEffect(() => {
    log.info('Header mounted');
    return () => log.info('Header unmounted');
  }, []);

  return (
    <AppBar position="fixed" color="default">
      <Toolbar>
        <Tooltip title={t('header.toggleSidebar')}>
          <IconButton edge="start" onClick={toggleSidebar} aria-label={t('header.toggleSidebar')}>
            <MenuIcon />
          </IconButton>
        </Tooltip>
        <Typography variant="h6" sx={{ ml: 1, fontWeight: 700 }}>{t('appTitle')}</Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LanguageIcon aria-hidden />
          <Select size="small" value={language} onChange={(e) => setLanguage(e.target.value)} aria-label={t('header.language')}>
            <MenuItem value="en">EN</MenuItem>
            <MenuItem value="de">DE</MenuItem>
          </Select>
          <Tooltip title={t('header.theme')}>
            <IconButton onClick={toggleTheme} aria-label={t('header.theme')}>
              {themeMode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
