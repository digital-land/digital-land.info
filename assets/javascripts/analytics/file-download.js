// Track downloads when the user has allowed analytics cookies only
// cookiePrefs is exposed globally in `application/templates/layouts/base.html`
//
// Example:
//
// Page loads
//   └─ addEventListener registered (once)
//   └─ cookiePrefs.usage = false

// User clicks download .geojson
//   └─ Handler: usageCookiesAllowed() → false → return (no tracking)

// User accepts analytics cookies
//   └─ cookiePrefs.usage = true (same page session)

// User clicks download .json (or other extension)
//   └─ Handler: usageCookiesAllowed() → true → gtag() fires
function usageCookiesAllowed() {
  try {
		return !!(window.cookiePrefs && window.cookiePrefs.usage);
  } catch (e) {
		return false;
  }
}


// Runs once when the script is first executed (on page load)
document.addEventListener('click', function (event) {
  // Runs every time the user clicks anywhere on the site/page
  if (!usageCookiesAllowed()) return;

  // If GA is blocked/disabled, don't error.
  if (!window.gtag) return;

  // Gets hit every time the user clicks anywhere on the site/page
  // when analytics cookies have been accepted
  const link = event.target.closest('a');
  if (!link || !link.href) return;

  const fileExtensions = ['.geojson', '.json', '.xml', '.gml', '.kml', '.gpkg', '.shp'];

  let url;
  try {
		url = new URL(link.href);
  } catch (e) {
		return;
  }

  const extension = url.pathname.substring(url.pathname.lastIndexOf('.'));
  if (!fileExtensions.includes(extension.toLowerCase())) return;

  // Send to GA4 the:
  // link url
  // link text
  // file extension
  window.gtag('event', 'file_download', {
		link_url: link.href,
		link_text: link.innerText || link.href,
		file_extension: extension.toLowerCase().substring(1),
  });
});
