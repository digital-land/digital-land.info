import { loadGA4 } from './analytics/ga4Loader.js';

/* Storage */

export function setCookie (name, value, days) {
  var expires = ''
  if (days) {
    var date = new Date()
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
    expires = '; expires=' + date.toUTCString()
  }
  document.cookie = name + '=' + (value || '') + expires + '; path=/'
}

export function getCookie (name) {
  var nameEQ = name + '='
  var ca = document.cookie.split(';')
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i]
    while (c.charAt(0) === ' ') c = c.substring(1, c.length)
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length)
  }
  return null
}

export function deleteCookie (name) {
  document.cookie = name + "=;expires=" + new Date + ";domain=" + window.location.hostname + ";path=/";
}

/* Consent decision */

export const ConsentCategory = Object.freeze({
  ESSENTIAL: 'essential',
  SETTINGS: 'settings',
  USAGE: 'usage',
  CAMPAIGNS: 'campaigns',
});

export function getCookieConsent () {
  const rawPolicy = getCookie('cookies_policy');
  if (!rawPolicy) return null;

  try {
    return JSON.parse(rawPolicy);
  } catch (error) {
    console.warn('Cookies policy cookie could not be parsed', error);
    return null;
  }
}

export function hasCookieConsent (category) {
  try {
    const consent = getCookieConsent();
    return !!(consent && consent[category]);
  } catch (error) {
    return false;
  }
}

/* Banner UI */

/**
 * Releases focus if the currently active element lives within the provided
 * selector.
 *
 * @param {string} selector - CSS selector used to determine whether the
 * focused element needs blurring.
 */
function activeElementBlurRelease (selector) {
  const activeElement = document.activeElement
  const isInsideBanner = activeElement?.closest?.(selector)

  if (isInsideBanner && typeof activeElement.blur === 'function') {
    activeElement.blur()
  }
}

export function hideCookieBanner () {
  var cookieBanner = document.getElementById('cookie-banner')
  if(cookieBanner){
    activeElementBlurRelease('#cookie-banner')
    cookieBanner.style.display = 'none'
    cookieBanner.ariaHidden = true
  }
}

export function showCookieBanner () {
  var cookieBanner = document.getElementById('cookie-banner')
  if(cookieBanner){
    cookieBanner.style.display = 'block'
    cookieBanner.ariaHidden = false
  }
}

/**
 * Hides cookies banner and any confirmation banners already rendered.
 */
export function hideCookieConfirmation () {
  hideCookieBanner ()

  let acceptBanner = document.getElementById('cookie-confirmation-accept-banner')
  let rejectBanner = document.getElementById('cookie-confirmation-reject-banner')

  activeElementBlurRelease('#cookie-confirmation-accept-banner, #cookie-confirmation-reject-banner')
  const updateBanner = (el) => {
    if (!el) return
    el.style.display = 'none'
    el.ariaHidden = true
  }

  updateBanner(acceptBanner)
  updateBanner(rejectBanner)
}

/**
 * Shows the confirmation banner that corresponds to the user's
 * latest choice.
 *
 * @param {boolean} cookiesAccepted - Indicates whether the user
 * accepted (true) or rejected (false) additional cookies.
 */
export function showCookieConfirmation (cookiesAccepted = true) {
  const acceptBanner = document.getElementById('cookie-confirmation-accept-banner')
  const rejectBanner = document.getElementById('cookie-confirmation-reject-banner')

  const updateBanner = (el, show) => {
    // If the element doesn't exist, return
    if (!el) return
    el.style.display = show ? 'block' : 'none'
    el.ariaHidden = !show
  }

  updateBanner(acceptBanner, cookiesAccepted)
  updateBanner(rejectBanner, !cookiesAccepted)
}

/* Recording a consent decision */

export const cookieTypes = {
  cookies_policy: "essential",
  cookies_preferences_set: "essential",
  _ga: "usage",
};

export function showCookieBannerIfNoChoiceMade () {
  if (window.gaMeasurementId) {
    cookieTypes[`_ga_${window.gaMeasurementId}`] = 'usage';
  }

  showCookieBanner()
  if (getCookie('cookies_preferences_set')) {
    hideCookieBanner()
  }
}

/**
 * Brings tracking scripts in line with the current cookie choice.
 */
export function syncTrackingWithConsent () {
  const consent = getCookieConsent();
  const usageAllowed = !!(consent && consent.usage);

  loadGA4(window.gaMeasurementId, usageAllowed);
}

/**
 * Records the acceptance of additional analytical cookies,
 * hides the banner, and enables tracking scripts.
 *
 * @param {{ essential: boolean, settings: boolean, usage: boolean, campaigns: boolean }} [cookiePrefs] - Object
 * describing which categories of cookies are permitted.
 */
export function acceptCookies (cookiePrefs = { essential: true, settings: true, usage: true, campaigns: true }) { // eslint-disable-line no-unused-vars
  let cookiesAccepted = true
  setCookie('cookies_preferences_set', true, 365)
  setCookie('cookies_policy', JSON.stringify(cookiePrefs), 365)
  hideCookieBanner()
  // explicitly show acceptance confirmation
  showCookieConfirmation(cookiesAccepted)
  syncTrackingWithConsent()
}

/**
 * Records the rejection of additional analytical cookies,
 * hides the banner, and keeps only essential cookies.
 *
 * @param {{ essential: boolean, settings: boolean, usage: boolean, campaigns: boolean }} [cookiePrefs] - Object
 * describing which categories of cookies are permitted.
 */
export function rejectCookies (cookiePrefs = { essential: true, settings: false, usage: false, campaigns: false }) { // eslint-disable-line no-unused-vars
  let cookiesAccepted = false
  setCookie('cookies_preferences_set', true, 365)
  setCookie('cookies_policy', JSON.stringify(cookiePrefs), 365)
  hideCookieBanner()
  // explicitly show rejection confirmation
  showCookieConfirmation(cookiesAccepted)
  syncTrackingWithConsent()
}

/* /cookies settings-page state */

let essential = true;
let settings = false;
let usage = false;
let campaigns = false;

export function loadCookiePrefs () {
  const consent = getCookieConsent();
  if (consent) {
    essential = consent.essential;
    settings = consent.settings;
    usage = consent.usage;
    campaigns = consent.campaigns;
  }
}

export function setCookiePrefsUsage (value) {
  usage = value;
}

export function saveCookiePrefs (expires = 365) {
  setCookie('cookies_preferences_set', true, expires);
  setCookie('cookies_policy', JSON.stringify({ essential, settings, usage, campaigns }), expires);
  hideCookieBanner();
  invalidateRejectedCookiePrefs();
  syncTrackingWithConsent();
}

function invalidateRejectedCookiePrefs () {
  for (const name in cookieTypes) {
    if (!essential && cookieTypes[name] == 'essential') {
      deleteCookie(name);
    }
    if (!settings && cookieTypes[name] == 'settings') {
      deleteCookie(name);
    }
    if (!usage && cookieTypes[name] == 'usage') {
      deleteCookie(name);
    }
    if (!campaigns && cookieTypes[name] == 'campaigns') {
      deleteCookie(name);
    }
  }
}
