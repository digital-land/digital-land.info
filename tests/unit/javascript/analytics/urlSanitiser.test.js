import { describe, expect, test, vi, afterEach } from 'vitest';
import {
  sanitiseUrl,
  sanitiseReferrer,
  ALLOWED_QUERY_PARAMS
} from '../../../../assets/javascripts/analytics/urlSanitiser.js';

describe('sanitiseUrl', () => {
  test('retains allow-listed parameters unchanged', () => {
    const url = 'https://www.planning.data.gov.uk/dataset?dataset=conservation-area&utm_source=newsletter';
    expect(sanitiseUrl(url)).toBe(url);
  });

  test('strips a parameter that is not on the allow-list', () => {
    const url = 'https://www.planning.data.gov.uk/search?q=whitehall';
    expect(sanitiseUrl(url)).toBe('https://www.planning.data.gov.uk/search');
  });

  test('keeps only the allow-listed parameter when allowed and disallowed params are mixed', () => {
    const url = 'https://www.planning.data.gov.uk/search?dataset=conservation-area&q=whitehall&page=2';
    expect(sanitiseUrl(url)).toBe('https://www.planning.data.gov.uk/search?dataset=conservation-area');
  });

  test('is unchanged when the URL has no query string', () => {
    const url = 'https://www.planning.data.gov.uk/dataset';
    expect(sanitiseUrl(url)).toBe(url);
  });

  test('returns an empty string for an unparsable URL rather than the raw value', () => {
    expect(sanitiseUrl('not a url')).toBe('');
  });

  test('retains every value of a repeated allow-listed parameter, as submitted by the dataset filter checkboxes', () => {
    const url = 'https://www.planning.data.gov.uk/search?dataset=conservation-area&dataset=listed-building';
    expect(sanitiseUrl(url)).toBe(url);
  });
});

describe('sanitiseReferrer', () => {
  test('applies the allow-list to a same-hostname referrer', () => {
    const referrer = 'https://www.planning.data.gov.uk/search?dataset=conservation-area&q=whitehall';

    expect(sanitiseReferrer(referrer, 'www.planning.data.gov.uk'))
      .toBe('https://www.planning.data.gov.uk/search?dataset=conservation-area');
  });

  test('strips the entire query string from a different-hostname referrer', () => {
    const referrer =
      'https://www.google.com/search?q=planning+data&dataset=conservation-area&user-included-personally-identifiable-info';

    expect(sanitiseReferrer(referrer, 'www.planning.data.gov.uk')).toBe('https://www.google.com/search');
  });

  test('returns an empty string when there is no referrer', () => {
    expect(sanitiseReferrer('', 'www.planning.data.gov.uk')).toBe('');
  });

  test('returns an empty string for an unparsable referrer rather than the raw value', () => {
    expect(sanitiseReferrer('not a url', 'www.planning.data.gov.uk')).toBe('');
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test('defaults the current hostname to window.location.hostname', () => {
    vi.stubGlobal('window', { location: { hostname: 'www.planning.data.gov.uk' } });

    const referrer = 'https://www.planning.data.gov.uk/search?q=whitehall';
    expect(sanitiseReferrer(referrer)).toBe('https://www.planning.data.gov.uk/search');
  });
});

describe('ALLOWED_QUERY_PARAMS', () => {
  test('exposes the agreed allow-list', () => {
    expect(ALLOWED_QUERY_PARAMS).toEqual([
      'dataset',
      'utm_source'
    ]);
  });
});
