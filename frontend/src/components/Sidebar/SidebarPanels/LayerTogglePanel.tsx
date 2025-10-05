import React from 'react';
import { FormControlLabel, Checkbox, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useUIStore } from '../../../state/uiStore';
import logger from '../../../utils/logger';

const log = logger('components/Sidebar/SidebarPanels/LayerTogglePanel.jsx');
log.info('LayerTogglePanel module loaded');

export default function LayerTogglePanel(props:any) {
  log.debug('LayerTogglePanel render', { props });
  React.useEffect(() => {
    log.info('LayerTogglePanel mounted');
    return () => log.info('LayerTogglePanel unmounted');
  }, []);

  const { t } = useTranslation('common');
  const showHeatmap = useUIStore((s) => s.showHeatmap);
  const setShowHeatmap = useUIStore((s) => s.setShowHeatmap);
  return (
    <section aria-labelledby="layer-toggle-title" className="layer-toggle-panel">
      <Typography id="layer-toggle-title" variant="h6" sx={{ mb: 1 }}>{t('panel.layers')}</Typography>
      <FormControlLabel control={<Checkbox checked={showHeatmap} onChange={(e) => setShowHeatmap(e.target.checked)} />} label={t('panel.showHeatmap')} />
    </section>
  );
}
