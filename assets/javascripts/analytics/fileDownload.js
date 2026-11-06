import { trackEvent } from './trackEvent.js';
import { sanitiseUrl } from './urlSanitiser.js';

// This event is ALSO fired by GA4's "File downloads" enhanced measurement
// setting, which covers a fixed list of extensions Google maintains and we
// can't edit (csv, pdf, xlsx, zip, etc). The list below deliberately holds
// only the formats that setting misses, so reporting sees one event per
// download. csv is absent because GA already tracks it - adding it here, or
// any other extension Google covers, would double count.
const fileExtensions = [
  '.geojson',
  '.json',
  '.xml',
  '.gml',
  '.kml',
  '.gpkg',
  '.shp',
  '.parquet',
];

document.addEventListener('click', handleDownloadClick);

function handleDownloadClick(event) {
  const link = getClickedLink(event);
  if (!link) return;

  const extension = getFileExtension(link.href);
  if (!shouldTrackFileDownload(extension)) return;

  trackEvent('file_download', {
    link_url: sanitiseUrl(link.href),
    link_text: link.innerText || link.href,
    file_extension: extension.substring(1),
  });
}

function getClickedLink(event) {
  const link = event.target.closest('a');
  return link && link.href ? link : null;
}

function getFileExtension(href) {
  try {
    const url = new URL(href);
    return url.pathname.substring(url.pathname.lastIndexOf('.')).toLowerCase();
  } catch (e) {
    return null;
  }
}

function shouldTrackFileDownload(extension) {
  return fileExtensions.includes(extension);
}
