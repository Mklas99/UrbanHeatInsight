import React from 'react';
import logger from '../utils/logger';
import './Header.css';
import { AppBar, Toolbar, Typography, IconButton, Box, Select, MenuItem, Tooltip, ButtonBase } from '@mui/material';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import MenuIcon from '@mui/icons-material/Menu';
import LanguageIcon from '@mui/icons-material/Language';
import { useTranslation } from 'react-i18next';
import { useUIStore } from '../state/uiStore';

const log = logger('components/Header.jsx');

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
    <AppBar position="fixed" color="primary" enableColorOnDark>
      <Toolbar>
        {/* Toggle Sidebar */}
        <Tooltip title={t('header.toggleSidebar')}>
          <IconButton edge="start" onClick={toggleSidebar} aria-label={t('header.toggleSidebar')}>
            <MenuIcon />
          </IconButton>
        </Tooltip>
        <Typography variant="h1" sx={{ ml: 1 }}>{t('appTitle')}</Typography>
        {/* Page links */}
        <Box sx={{ mr: 3, flexGrow: 1, display: 'flex', justifyContent: 'right', gap: 3 }}>
          <Typography variant="h2">
            <a href="/" className='header-link'>{t('header.home')}</a>
          </Typography>
          <Typography variant="h2">
            <a href="/data" className='header-link'>{t('header.data')}</a>
          </Typography>
          <Typography variant="h2">
            <a href="/about" className='header-link'>{t('header.about')}</a>
          </Typography>
        </Box>
        {/* Settings */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box className='language-select' sx={
              { display: 'flex', alignItems: 'center', 
                border: '4px solid var(--color-primary)',
                borderRadius: '4px', padding: '2px 8px' }}>
              <LanguageIcon aria-hidden style={{ color: 'var(--color-primary)', marginRight: '4px' }}/>
              <Select className='language-dropdown' size="small" value={language} onChange={(e) => setLanguage(e.target.value)} aria-label={t('header.language')} disableUnderline>
                <MenuItem value="en">EN</MenuItem>
                <MenuItem value="de">DE</MenuItem>
              </Select>
            </Box>
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
