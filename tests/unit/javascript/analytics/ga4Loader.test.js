import { describe, expect, test, vi, afterEach } from 'vitest';
import { loadGA4 } from '../../../../assets/javascripts/analytics/ga4Loader.js';

function stubDocument (existingScriptSrcs = []) {
  const appended = [];
  const removeSpies = {};

  vi.stubGlobal('document', {
    querySelector: (selector) => {
      const match = existingScriptSrcs.find(src => selector === `script[src="${src}"]`);
      if (!match) return null;
      removeSpies[match] = removeSpies[match] || vi.fn();
      return { src: match, remove: removeSpies[match] };
    },
    createElement: () => ({}),
    head: { appendChild: (el) => appended.push(el) }
  });

  return { appended, removeSpies };
}

describe('loadGA4', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test('injects the gtag script tag and configures gtag when usage is allowed', () => {
    const { appended } = stubDocument();
    vi.stubGlobal('window', {});

    loadGA4('G-123', true);

    expect(appended).toHaveLength(1);
    expect(appended[0].src).toBe('https://www.googletagmanager.com/gtag/js?id=G-123');
    expect(window.dataLayer[0][0]).toBe('js');
    expect(window.dataLayer[1][0]).toBe('config');
    expect(window.dataLayer[1][1]).toBe('G-123');
    expect(window['ga-disable-G-123']).toBe(false);
  });

  test('does not inject the script tag when usage is not allowed', () => {
    const { appended } = stubDocument();
    vi.stubGlobal('window', {});

    loadGA4('G-123', false);

    expect(appended).toHaveLength(0);
    expect(window['ga-disable-G-123']).toBe(true);
    expect(window.gtag).toBeUndefined();
  });

  test('removes an already-injected script tag when usage is withdrawn', () => {
    const src = 'https://www.googletagmanager.com/gtag/js?id=G-123';
    const { removeSpies } = stubDocument([src]);
    vi.stubGlobal('window', {});

    loadGA4('G-123', false);

    expect(removeSpies[src]).toHaveBeenCalled();
  });

  test('does not throw when usage is withdrawn and no script tag was ever injected', () => {
    stubDocument();
    vi.stubGlobal('window', {});

    expect(() => loadGA4('G-123', false)).not.toThrow();
  });

  test('does not inject the script tag again once it is already present', () => {
    const { appended } = stubDocument(['https://www.googletagmanager.com/gtag/js?id=G-123']);
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

  test('does not attempt to inject a script tag when usage is allowed but no measurement ID is given', () => {
    const { appended } = stubDocument();
    vi.stubGlobal('window', {});
    vi.spyOn(console, 'warn').mockImplementation(() => { });

    loadGA4(undefined, true);

    expect(appended).toHaveLength(0);
  });
});
