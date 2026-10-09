function usageCookiesAllowed() {
  try {
    return !!(window.cookiePrefs && window.cookiePrefs.usage);
  } catch (e) {
    return false;
  }
}

export function trackEvent(eventName, params = {}) {
  if (!usageCookiesAllowed()) return;
  if (!window.gtag) return;

  window.gtag('event', eventName, params);
}
