import { describe, expect, test, vi, beforeEach } from 'vitest'
import {
  setCookie,
  getCookie,
  deleteCookie,
  ConsentCategory,
  getCookieConsent,
  hasCookieConsent,
  showCookieBanner,
  hideCookieBanner,
  showCookieConfirmation,
  hideCookieConfirmation,
  showCookieBannerIfNoChoiceMade,
  syncTrackingWithConsent,
  acceptCookies,
  rejectCookies,
  loadCookiePrefs,
  setCookiePrefsUsage,
  saveCookiePrefs
} from '../../../assets/javascripts/cookies.js'
import { loadGA4 } from '../../../assets/javascripts/analytics/ga4Loader.js'

vi.mock('../../../assets/javascripts/analytics/ga4Loader.js', () => ({
  loadGA4: vi.fn()
}))

describe('cookies.js', () => {
  vi.stubGlobal('window', {
    location: {
      hostname: 'localhost'
    }
  })

  let cookieBannerMock = {
    style: {
      display: 'none'
    },
    ariaHidden: true
  }

  let cookieConfirmationAcceptMock = {
    style: {
      display: 'none'
    },
    ariaHidden: true
  }

  let cookieConfirmationRejectMock = {
    style: {
      display: 'none'
    },
    ariaHidden: true
  }

  let documentCookieMock = {
    cookie: null,
    activeElement: null,
    getElementById: (id) => {
      if (id == 'cookie-banner')
        return cookieBannerMock;
      if (id == 'cookie-confirmation-accept-banner')
        return cookieConfirmationAcceptMock;
      if (id == 'cookie-confirmation-reject-banner')
        return cookieConfirmationRejectMock;
    }
  };
  Object.defineProperty(documentCookieMock, 'cookie', {
    get: function() {
      let cookieString = '';
      Object.keys(this.rawValues || {}).forEach(key => {
        cookieString += `${this.rawValues[key]};`;
      });
      cookieString = cookieString.slice(0, -1);
      return cookieString;
    },
    set: function(value) {
      if(value === null) {
        this.rawValues = {};
        return;
      }
      this.rawValues = this.rawValues || {};
      let key = value.split('=')[0];
      this.rawValues[key] = value;
    }
  })
  vi.stubGlobal('document', documentCookieMock)

  beforeEach(() => {
    documentCookieMock.cookie = null;
    documentCookieMock.activeElement = null;
    delete window.gaMeasurementId;
    loadGA4.mockClear();
    cookieBannerMock.style.display = 'none';
    cookieBannerMock.ariaHidden = true;
  });

  describe('storage', () => {
    test('setCookie', () => {
      let days = 365
      setCookie('test', 'test', days)
      var date = new Date()
      date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
      expect(document.cookie).toBe(`test=test; expires=${date.toUTCString()}; path=/`)

      setCookie('foo', 'bar', days)
      expect(document.cookie).toBe(`test=test; expires=${date.toUTCString()}; path=/;foo=bar; expires=${date.toUTCString()}; path=/`)
    })

    test('deleteCookie', () => {
      let days = 365
      setCookie('test', 'test', days)
      deleteCookie('test')
      expect(document.cookie).toBe(`test=;expires=${new Date};domain=${window.location.hostname};path=/`)
    })

    test('getCookie', () => {
      let days = 365
      setCookie('foo', 'test', days)
      setCookie('bar', 'test2', days)
      setCookie('buzz', 'test3', days)

      expect(getCookie('bar')).toBe('test2')
      expect(getCookie('buzz')).toBe('test3')
      expect(getCookie('foo')).toBe('test')
    })

    test('getCookie returns null when the cookie is not present', () => {
      expect(getCookie('missing')).toBeNull()
    })
  })

  describe('consent decision', () => {
    test('hasCookieConsent returns true when the category is consented to', () => {
      documentCookieMock.cookie = 'cookies_policy={"usage":true}';
      expect(hasCookieConsent('usage')).toBe(true);
    })

    test('hasCookieConsent returns false when the category is not consented to', () => {
      documentCookieMock.cookie = 'cookies_policy={"usage":false}';
      expect(hasCookieConsent('usage')).toBe(false);
    })

    test('hasCookieConsent returns false when no cookie choice has been recorded', () => {
      expect(hasCookieConsent('usage')).toBe(false);
    })

    test('hasCookieConsent returns false and does not throw when the cookie is malformed JSON', () => {
      documentCookieMock.cookie = 'cookies_policy=not-json';
      const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});

      expect(() => hasCookieConsent('usage')).not.toThrow();
      expect(hasCookieConsent('usage')).toBe(false);
      expect(warn).toHaveBeenCalled();

      warn.mockRestore();
    })

    test('hasCookieConsent returns false and does not throw when document is unavailable', () => {
      vi.stubGlobal('document', undefined);

      expect(() => hasCookieConsent('usage')).not.toThrow();
      expect(hasCookieConsent('usage')).toBe(false);

      vi.stubGlobal('document', documentCookieMock);
    })

    test('getCookieConsent returns the parsed cookie policy', () => {
      documentCookieMock.cookie = 'cookies_policy={"essential":true,"usage":true}';
      expect(getCookieConsent()).toEqual({ essential: true, usage: true });
    })

    test('getCookieConsent returns null when no cookie choice has been recorded', () => {
      expect(getCookieConsent()).toBeNull();
    })

    test('ConsentCategory exposes the cookie categories', () => {
      expect(ConsentCategory).toEqual({
        ESSENTIAL: 'essential',
        USAGE: 'usage'
      });
    })
  })

  describe('banner UI', () => {
    test('showCookieBanner', () => {
      showCookieBanner()
      expect(cookieBannerMock.style.display).toBe('block')
      expect(cookieBannerMock.ariaHidden).toBe(false)
    })

    test('hideCookieBanner', () => {
      hideCookieBanner()
      expect(cookieBannerMock.style.display).toBe('none')
      expect(cookieBannerMock.ariaHidden).toBe(true)
    })

    test('hideCookieBanner blurs focused element inside banner', () => {
      const blurMock = vi.fn();
      documentCookieMock.activeElement = {
        blur: blurMock,
        closest: vi.fn(() => cookieBannerMock)
      };

      hideCookieBanner();
      expect(blurMock).toHaveBeenCalled();
    })

    test('showCookieConfirmation', () => {
      showCookieConfirmation(true);
      expect(cookieConfirmationAcceptMock.style.display).toBe('block')
      expect(cookieConfirmationAcceptMock.ariaHidden).toBe(false)
    })

    test('hideCookieConfirmation', () => {
      hideCookieConfirmation();
      expect(cookieConfirmationAcceptMock.style.display).toBe('none')
      expect(cookieConfirmationAcceptMock.ariaHidden).toBe(true)
      expect(cookieConfirmationRejectMock.style.display).toBe('none')
      expect(cookieConfirmationRejectMock.ariaHidden).toBe(true)
    })

    test('hideCookieConfirmation blurs focused element inside confirmation', () => {
      const blurMock = vi.fn();
      documentCookieMock.activeElement = {
        blur: blurMock,
        closest: vi.fn(() => ({}))
      };

      hideCookieConfirmation();
      expect(blurMock).toHaveBeenCalled();
    })
  })

  describe('recording a consent decision', () => {
    describe('showCookieBannerIfNoChoiceMade', () => {
      test('shows the banner when no choice has been recorded', () => {
        showCookieBannerIfNoChoiceMade();
        expect(cookieBannerMock.style.display).toBe('block');
        expect(cookieBannerMock.ariaHidden).toBe(false);
      })

      test('hides the banner when a choice was already recorded', () => {
        documentCookieMock.cookie = 'cookies_preferences_set=true';
        showCookieBannerIfNoChoiceMade();
        expect(cookieBannerMock.style.display).toBe('none');
        expect(cookieBannerMock.ariaHidden).toBe(true);
      })
    })

    describe('syncTrackingWithConsent', () => {
      test('delegates to loadGA4 with usageAllowed=false when no cookie policy is set', () => {
        window.gaMeasurementId = '1234';
        syncTrackingWithConsent();
        expect(loadGA4).toHaveBeenCalledWith('1234', false)
      })

      test('delegates to loadGA4 with usageAllowed=true when usage is allowed', () => {
        window.gaMeasurementId = '1234';
        documentCookieMock.cookie = `cookies_policy=${JSON.stringify({ usage: true })}`;
        syncTrackingWithConsent();
        expect(loadGA4).toHaveBeenCalledWith('1234', true)
      })
    })

    describe('acceptCookies', () => {
      test('records acceptance and enables tracking', () => {
        window.gaMeasurementId = '1234';
        acceptCookies({ essential: true, usage: true });

        expect(JSON.parse(getCookie('cookies_policy'))).toEqual({ essential: true, usage: true })
        expect(loadGA4).toHaveBeenCalledWith('1234', true)
      })
    })

    describe('rejectCookies', () => {
      test('records rejection and disables tracking', () => {
        window.gaMeasurementId = '1234';
        rejectCookies({ essential: true, usage: false });

        expect(JSON.parse(getCookie('cookies_policy'))).toEqual({ essential: true, usage: false })
        expect(loadGA4).toHaveBeenCalledWith('1234', false)
      })
    })
  })

  describe('/cookies settings-page state', () => {
    test('loadCookiePrefs populates state from the cookies_policy cookie, preserved by a later save', () => {
      documentCookieMock.cookie = `cookies_policy=${JSON.stringify({ essential: true, usage: true })}`;
      loadCookiePrefs();
      saveCookiePrefs();

      expect(JSON.parse(getCookie('cookies_policy'))).toEqual({ essential: true, usage: true });
    })

    test('setCookiePrefsUsage changes only the usage field, leaving the other loaded categories untouched', () => {
      documentCookieMock.cookie = `cookies_policy=${JSON.stringify({ essential: true, usage: true })}`;
      loadCookiePrefs();
      setCookiePrefsUsage(false);
      saveCookiePrefs();

      expect(JSON.parse(getCookie('cookies_policy'))).toEqual({ essential: true, usage: false });
    })

    test('saveCookiePrefs deletes usage cookies when usage ends up rejected', () => {
      documentCookieMock.cookie = `cookies_policy=${JSON.stringify({ essential: true, usage: true })}`;
      loadCookiePrefs();
      setCookiePrefsUsage(false);
      saveCookiePrefs();

      expect(document.cookie).toContain(`_ga=;expires=${new Date};domain=${window.location.hostname};path=/`);
    })

    test('saveCookiePrefs does not delete usage cookies when usage remains allowed', () => {
      documentCookieMock.cookie = `cookies_policy=${JSON.stringify({ essential: true, usage: true })}`;
      loadCookiePrefs();
      saveCookiePrefs();

      expect(document.cookie).not.toContain('_ga=;expires=');
    })

    test('saveCookiePrefs syncs tracking with the saved decision', () => {
      window.gaMeasurementId = '1234';
      documentCookieMock.cookie = `cookies_policy=${JSON.stringify({ essential: true, usage: true })}`;
      loadCookiePrefs();
      saveCookiePrefs();

      expect(loadGA4).toHaveBeenCalledWith('1234', true)
    })
  })
})
