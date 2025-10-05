import React from 'react';
import logger from '../utils/logger';
import MapView from '../components/MapView';
import './HomePage.css';
import PageLayout from '../layouts/PageLayout';

const log = logger('pages/HomePage.jsx');
log.info('HomePage module loaded');

export default function HomePage(props: any) {
  log.debug('HomePage render', { props });
  
  React.useEffect(() => {
    log.info('HomePage mounted');
    return () => log.info('HomePage unmounted');
  }, []);

  return (
    <PageLayout className="home-page" fullHeight={true}>
      <MapView 
      />
    </PageLayout>
  );
}
