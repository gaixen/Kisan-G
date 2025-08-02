import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translation JSON files
import en from './json/en.json';
import hi from './json/hi.json';
import kn from './json/kn.json';
import bn from './json/bn.json';
import te from './json/te.json';
import mr from './json/mr.json';
import ta from './json/ta.json';
import gu from './json/gu.json';
import ml from './json/ml.json';
import pa from './json/pa.json';

i18n
  .use(initReactI18next) // passes i18n down to react-i18next
  .init({
    resources: {
      en: { translation: en }, // english
      hi: { translation: hi }, // hindi
      kn: { translation: kn }, // kannada
      bn: { translation: bn }, // bengali
      te: { translation: te }, // telugu
      mr: { translation: mr }, // marathi
      ta: { translation: ta }, // tamil
      gu: { translation: gu }, // gujarati
      ml: { translation: ml }, // malayalam
      pa: { translation: pa }, // panjabi
    },
    lng: 'en',                 // default language
    fallbackLng: 'en',         // fallback language if key is missing
    debug: false,              // set true during development for debugging
    interpolation: {
      escapeValue: false,      // react already escapes by default
    }
  });

export default i18n;

