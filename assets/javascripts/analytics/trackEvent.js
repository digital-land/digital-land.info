import { hasCookieConsent, ConsentCategory } from '../cookies.js';

export function trackEvent (eventName, params = {}) {
  if (!hasCookieConsent(ConsentCategory.USAGE)) return;
  if (!window.gtag) return;

  window.gtag('event', eventName, params);
}
