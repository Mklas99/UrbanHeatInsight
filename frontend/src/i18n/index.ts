import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import logger from '../utils/logger';
import en from './locales/en/common.json';
import de from './locales/de/common.json';

const log = logger('i18n/index.js');
log.info('i18n module loaded');

void i18n
  .use(initReactI18next)
  .init({
    resources: { en: { common: en }, de: { common: de } },
    lng: localStorage.getItem('uhi-lang') || 'en',
    fallbackLng: 'en',
    ns: ['common'],
    defaultNS: 'common',
    interpolation: { escapeValue: false },
  })
  .then(() => log.info('i18n initialized'))
  .catch((err) => log.error('i18n initialization error', err));

export default i18n;
