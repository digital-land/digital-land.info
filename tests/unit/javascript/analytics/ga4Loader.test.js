import { describe, expect, test, vi, afterEach } from 'vitest';
import { loadGA4 } from '../../../../assets/javascripts/analytics/ga4Loader.js';

function stubDocument(existingScriptSrcs = []) {
  const appended = [];
  vi.stubGlobal('document', {
    querySelector: (selector) => {
      const match = existingScriptSrcs.find(src => selector === `script[src="${src}"]`);
      return match ? { src: match } : null;
    },
    createElement: () => ({}),
    head: { appendChild: (el) => appended.push(el) }
  });
  return appended;
}

describe('loadGA4', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test('injects the gtag script tag and configures gtag when usage is allowed', () => {
    const appended = stubDocument();
    vi.stubGlobal('window', {});

    loadGA4('G-123', true);

    expect(appended).toHaveLength(1);
    expect(appended[0].src).toBe('https://www.googletagmanager.com/gtag/js?id=G-123');
    expect(window.dataLayer[0][0]).toBe('js');
    expect(window.dataLayer[1][0]).toBe('config');
    expect(window.dataLayer[1][1]).toBe('G-123');
    expect(window['ga-disable-G-123']).toBe(false);
  });

  test('disables ga and does not configure gtag when usage is not allowed', () => {
    stubDocument();
    vi.stubGlobal('window', {});

    loadGA4('G-123', false);

    expect(window['ga-disable-G-123']).toBe(true);
    expect(window.gtag).toBeUndefined();
  });

  test('does not inject the script tag again once it is already present', () => {
    const appended = stubDocument(['https://www.googletagmanager.com/gtag/js?id=G-123']);
    vi.stubGlobal('window', {});

    loadGA4('G-123', true);

    expect(appended).toHaveLength(0);
  });

  test('warns and does not configure gtag when usage is allowed but no measurement ID is given', () => {
    stubDocument();
    vi.stubGlobal('window', {});
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => { });

    loadGA4(undefined, true);

    expect(warn).toHaveBeenCalledWith('Google Analytics: No measurement ID specified');
    expect(window.gtag).toBeUndefined();

    warn.mockRestore();
  });
});
