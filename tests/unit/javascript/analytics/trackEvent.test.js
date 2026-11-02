import { describe, expect, test, vi, afterEach } from 'vitest';
import { trackEvent } from '../../../../assets/javascripts/analytics/trackEvent.js';
import { hasCookieConsent } from '../../../../assets/javascripts/cookies.js';

vi.mock('../../../../assets/javascripts/cookies.js', async () => {
  const actual = await vi.importActual('../../../../assets/javascripts/cookies.js');
  return {
    ...actual,
    hasCookieConsent: vi.fn()
  };
});

describe('trackEvent', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    hasCookieConsent.mockReset();
  });

  test('sends the event via gtag when usage is consented to', () => {
    hasCookieConsent.mockReturnValue(true);
    const gtag = vi.fn();
    vi.stubGlobal('window', { gtag });

    trackEvent('some_custom_event', { some_param: 'some_value' });

    expect(hasCookieConsent).toHaveBeenCalledWith('usage');
    expect(gtag).toHaveBeenCalledWith('event', 'some_custom_event', {
      some_param: 'some_value',
    });
  });

  test('does not call gtag when usage is not consented to', () => {
    hasCookieConsent.mockReturnValue(false);
    const gtag = vi.fn();
    vi.stubGlobal('window', { gtag });

    trackEvent('some_custom_event', { some_param: 'some_value' });

    expect(gtag).not.toHaveBeenCalled();
  });

  test('defaults params to an empty object when none are given', () => {
    hasCookieConsent.mockReturnValue(true);
    const gtag = vi.fn();
    vi.stubGlobal('window', { gtag });

    trackEvent('some_custom_event');

    expect(gtag).toHaveBeenCalledWith('event', 'some_custom_event', {});
  });
});
