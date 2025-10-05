import React from 'react';
import logger from '../utils/logger';
import './AboutPage.css';
import PageLayout from '../layouts/PageLayout';

const log = logger('pages/AboutPage.jsx');
log.info('AboutPage module loaded');

export default function AboutPage(props: any) {
  log.debug('AboutPage render', { props });
  
  React.useEffect(() => {
    log.info('AboutPage mounted');
    return () => log.info('AboutPage unmounted');
  }, []);

  return (
    <PageLayout className="about-page" style={{ padding: '80px 24px' }}>
      UrbanHeatInsight – About
    </PageLayout>
  );
}
