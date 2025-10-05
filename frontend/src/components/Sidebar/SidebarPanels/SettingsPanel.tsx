import React from 'react';
import { Typography, Slider } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useUIStore } from '../../../state/uiStore';
import logger from '../../../utils/logger';

const log = logger('components/Sidebar/SidebarPanels/SettingsPanel.jsx');
log.info('SettingsPanel module loaded');

export default function SettingsPanel(props:any) {
  log.debug('SettingsPanel render', { props });
  React.useEffect(() => {
    log.info('SettingsPanel mounted');
    return () => log.info('SettingsPanel unmounted');
  }, []);

  const { t } = useTranslation('common');
  const heatRadius = useUIStore((s) => s.heatRadius);
  const setHeatRadius = useUIStore((s) => s.setHeatRadius);
  return (
    <section aria-labelledby="settings-title" style={{ marginTop: '1rem' }} className="settings-panel">
      <Typography id="settings-title" variant="h6" sx={{ mb: 1 }}>{t('panel.settings')}</Typography>
      <Typography variant="body2" sx={{ mb: 1 }}>{t('panel.heatRadius')}: {heatRadius}</Typography>
      <Slider value={heatRadius} min={10} max={50} step={1} onChange={(_, v) => setHeatRadius(v as number)} valueLabelDisplay="auto" aria-label={t('panel.heatRadius')} />
    </section>
  );
}
