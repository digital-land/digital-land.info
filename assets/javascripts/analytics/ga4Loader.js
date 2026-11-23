import { sanitiseUrl, sanitiseReferrer } from './urlSanitiser.js';

function gtagScriptSrc(measurementId) {
  return `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
}

function gtagScriptSelector(measurementId) {
  return `script[src="${gtagScriptSrc(measurementId)}"]`;
}

function injectGtagScriptTag(measurementId) {
  if (document.querySelector(gtagScriptSelector(measurementId))) return;

  const scriptElement = document.createElement('script');
  scriptElement.src = gtagScriptSrc(measurementId);
  document.head.appendChild(scriptElement);
}

function removeGtagScriptTag(measurementId) {
  const scriptElement = document.querySelector(gtagScriptSelector(measurementId));
  if (scriptElement) scriptElement.remove();
}

function pageViewParams() {
  return {
    page_location: sanitiseUrl(window.location.href),
    page_referrer: sanitiseReferrer(document.referrer)
  };
}

/**
 * - injects the gtag.js script tag and initialises the dataLayer
 * - subject to cookie consent.
 */
export function loadGA4(measurementId, usageAllowed = true) {
  if (!usageAllowed) {
    if (measurementId) {
      window[`ga-disable-${measurementId}`] = true;
    }
    removeGtagScriptTag(measurementId);
    return;
  }

  if (!measurementId) {
    console.warn('Google Analytics: No measurement ID specified');
    return;
  }

  const alreadyEnabled = window[`ga-disable-${measurementId}`] === false &&
    document.querySelector(gtagScriptSelector(measurementId));
  if (alreadyEnabled) return;

  injectGtagScriptTag(measurementId);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId, pageViewParams());
  window[`ga-disable-${measurementId}`] = false;
}
