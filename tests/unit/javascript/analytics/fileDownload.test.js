import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest';
import { trackEvent } from '../../../../assets/javascripts/analytics/trackEvent.js';

vi.mock('../../../../assets/javascripts/analytics/trackEvent.js', () => ({
  trackEvent: vi.fn()
}));

const expectedTrackedExtensions = ['.geojson', '.json', '.xml', '.gml', '.kml', '.gpkg', '.shp', '.parquet'];

describe('Tracking file downloads', () => {
  let clickHandler;

  beforeEach(async () => {
    trackEvent.mockClear();
    vi.stubGlobal('document', {
      addEventListener: (event, handler) => {
        if (event === 'click') clickHandler = handler;
      }
    });
    vi.resetModules();
    await import('../../../../assets/javascripts/analytics/fileDownload.js');
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function clickOn(href, innerText = '') {
    const link = { href, innerText };
    link.closest = () => link;
    clickHandler({ target: link });
  }

  test.each(expectedTrackedExtensions)('tracks a file_download event for the %s extension', (extension) => {
    const bareExtension = extension.substring(1);
    const href = `https://example.com/data${extension}`;

    clickOn(href, `Download ${bareExtension}`);

    expect(trackEvent).toHaveBeenCalledWith('file_download', {
      link_url: href,
      link_text: `Download ${bareExtension}`,
      file_extension: bareExtension
    });
  });

  test('does not track an extension outside the tracked list (already covered by GA4 enhanced measurement)', () => {
    clickOn('https://example.com/data.csv');

    expect(trackEvent).not.toHaveBeenCalled();
  });

  test('does not track a click that is not on a link', () => {
    clickHandler({ target: { closest: () => null } });

    expect(trackEvent).not.toHaveBeenCalled();
  });

  test('does not throw for an unparsable href', () => {
    const link = { href: 'not a url' };
    link.closest = () => link;

    expect(() => clickHandler({ target: link })).not.toThrow();
    expect(trackEvent).not.toHaveBeenCalled();
  });

  test('strips a parameter that is not on the allow-list from link_url', () => {
    clickOn('https://example.com/data.json?q=whitehall', 'Download json');

    expect(trackEvent).toHaveBeenCalledWith('file_download', {
      link_url: 'https://example.com/data.json',
      link_text: 'Download json',
      file_extension: 'json'
    });
  });

  test('retains an allow-listed parameter in link_url', () => {
    clickOn('https://example.com/data.json?dataset=conservation-area&q=whitehall', 'Download json');

    expect(trackEvent).toHaveBeenCalledWith('file_download', {
      link_url: 'https://example.com/data.json?dataset=conservation-area',
      link_text: 'Download json',
      file_extension: 'json'
    });
  });
});
