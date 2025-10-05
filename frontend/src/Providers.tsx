import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n';
import { useUIStore } from './state/uiStore';
import { getTheme } from './theme';
import logger from './utils/logger';

const log = logger('Providers.jsx');

export default function Providers({ children }: React.PropsWithChildren<{}>) {
  log.info('module loaded, Providers component initialized');
  const themeMode = useUIStore((s) => s.themeMode) as 'light' | 'dark';
  const language = useUIStore((s) => s.language);
  React.useEffect(() => {
    log.debug('useEffect - language change detected', { language, i18nLanguage: i18n.language });
    if (i18n.language !== language) {
      log.info('changing i18n language', language);
      i18n.changeLanguage(language).catch((err) => log.error('i18n.changeLanguage error', err));
    }
  }, [language]);
  log.debug('render Providers', { themeMode, language });
  return (
    <I18nextProvider i18n={i18n}>
      <ThemeProvider theme={getTheme(themeMode as 'light' | 'dark')}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </I18nextProvider>
  );
}
