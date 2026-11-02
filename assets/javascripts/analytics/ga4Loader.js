function gtagScriptSrc(measurementId) {
  return `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
}

function injectGtagScriptTag(measurementId) {
  const src = gtagScriptSrc(measurementId);
  if (document.querySelector(`script[src="${src}"]`)) return;

  const scriptElement = document.createElement('script');
  scriptElement.src = src;
  document.head.appendChild(scriptElement);
}

/**
 * Loads GA4
 * - injects the gtag.js script tag and initialises the dataLayer
 * - subject to cookie consent.
 */
export function loadGA4(measurementId, usageAllowed = true) {
  injectGtagScriptTag(measurementId);

  if (!usageAllowed) {
    if (measurementId) {
      window[`ga-disable-${measurementId}`] = true;
    }
    return;
  }

  if (!measurementId) {
    console.warn('Google Analytics: No measurement ID specified');
    return;
  }

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments) };
  window.gtag('js', new Date());
  window.gtag('config', measurementId);
  window[`ga-disable-${measurementId}`] = false;
}
