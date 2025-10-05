import React from 'react';
import { Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import logger from '../../../utils/logger';

const log = logger('components/Sidebar/SidebarPanels/InfoPanel.jsx');
log.info('InfoPanel module loaded');

export default function InfoPanel(props:any) {
  log.debug('InfoPanel render', { props });
  React.useEffect(() => {
    log.info('InfoPanel mounted');
    return () => log.info('InfoPanel unmounted');
  }, []);

  const { t } = useTranslation('common');
  return (
    <div className="info-panel">
      <section aria-labelledby="info-title" style={{ marginTop: '1rem' }}>
        <Typography id="info-title" variant="h6" sx={{ mb: 1 }}>{t('panel.about')}</Typography>
        <Typography variant="body2">{t('about.text')}</Typography>
      </section>
    </div>
  );
}
