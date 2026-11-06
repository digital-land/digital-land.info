export const ALLOWED_QUERY_PARAMS = [
  'dataset',
  'utm_source'
];

export function sanitiseUrl (url) {
  try {
    const parsed = new URL(url);
    const filtered = new URLSearchParams();
    for (const key of ALLOWED_QUERY_PARAMS) {
      for (const value of parsed.searchParams.getAll(key)) {
        filtered.append(key, value);
      }
    }
    parsed.search = filtered.toString();
    return parsed.toString();
  } catch (e) {
    return '';
  }
}

export function sanitiseReferrer (referrer, currentHostname = window.location.hostname) {
  if (!referrer) return '';

  try {
    const parsed = new URL(referrer);
    if (parsed.hostname !== currentHostname) {
      parsed.search = '';
      return parsed.toString();
    }
  } catch (e) {
    return '';
  }

  return sanitiseUrl(referrer);
}
