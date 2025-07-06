import {describe, expect, test, vi, beforeEach} from 'vitest'


import {
    setCookie,
    deleteCookie,
    getCookie,
    showCookieBanner,
    hideCookieBanner,
    showCookieConfirmation,
    hideCookieConfirmation,
    setTrackingCookies,
    cookiePrefs
} from '../../../assets/javascripts/cookies'

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

    let cookieConfirmationMock = {
        style: {
            display: 'none'
        },
        ariaHidden: true
    }

    let documentCookieMock = {
        cookie: null,
        getElementById: (id) => {
            if(id == 'cookie-banner')
                return cookieBannerMock;
            if(id == 'cookie-confirmation')
                return cookieConfirmationMock;
        }
    };
    Object.defineProperty(documentCookieMock, 'cookie', {
        get: function() {
            let cookieString = '';
            Object.keys(this.rawValues).forEach(key => {
                cookieString += `${this.rawValues[key]};`;
            });
            cookieString = cookieString.slice(0, -1); // remove trailing ;
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
    });

    test('setCookie', () => {
        let days = 365;
        setCookie('test', 'test', days)
        var date = new Date()
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
        expect(document.cookie).toBe(`test=test; expires=${date.toUTCString()}; path=/`);

        setCookie('foo', 'bar', days)
        expect(document.cookie).toBe(`test=test; expires=${date.toUTCString()}; path=/;foo=bar; expires=${date.toUTCString()}; path=/`);
    })

    test('deleteCookie', () => {
        let days = 365;
        setCookie('test', 'test', days)
        deleteCookie('test')
        expect(document.cookie).toBe(`test=;expires=${new Date};domain=${window.location.hostname};path=/`);
    })

    test('getCookie', () => {
        let days = 365;
        setCookie('foo', 'test', days)
        setCookie('bar', 'test2', days)
        setCookie('buzz', 'test3', days)

        const cookie = getCookie('bar')
        expect(cookie).toBe('test2')

        const cookie2 = getCookie('buzz')
        expect(cookie2).toBe('test3')

        const cookie3 = getCookie('foo')
        expect(cookie3).toBe('test')
    })

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

    test('showCookieConfirmation', () => {
        showCookieConfirmation();
        expect(cookieConfirmationMock.style.display).toBe('block')
        expect(cookieConfirmationMock.ariaHidden).toBe(false)
    })

    test('hideCookieConfirmation', () => {
        hideCookieConfirmation();
        expect(cookieConfirmationMock.style.display).toBe('none')
        expect(cookieConfirmationMock.ariaHidden).toBe(true)
    })

    describe('setTrackingCookies', () => {
        test('disables ga when cookie tracking policy isn\'t set and we previously have a measurement id', () => {
            let fakeMeasurementId = '1234';
            window.gaMeasurementId = fakeMeasurementId;
            setTrackingCookies();
            expect(window[`ga-disable-${fakeMeasurementId}`]).toBe(true);
        })

        test('sets up ga when cookie tracking policy is set and we have a measurement id', () => {
            vi.stubGlobal('dataLayer', [])
            let fakeMeasurementId = '1234';
            window.gaMeasurementId = fakeMeasurementId;

            setCookie('cookies_policy', JSON.stringify({usage: true}));
            setTrackingCookies();

            expect(window[`ga-disable-${fakeMeasurementId}`]).toBe(false);
            expect(Array.from(dataLayer[0])).toEqual(['js', new Date()]);
            expect(Array.from(dataLayer[1])).toEqual(['config', fakeMeasurementId]);
        })
    })

    describe('class cookiePrefs', () => {
        test('get', () => {
            setCookie('cookies_policy', JSON.stringify({essential: true, settings: true, campaigns: true, usage: true}));
            cookiePrefs.get();
            expect(cookiePrefs.essential).toBe(true);
            expect(cookiePrefs.settings).toBe(true);
            expect(cookiePrefs.campaigns).toBe(true);
            expect(cookiePrefs.usage).toBe(true);
        })

        const cookieTypes = {
            cookies_policy: "essential",
            cookies_preferences_set: "essential",
            _ga: "usage",
            _gid: "usage",
            _gat: "usage",
          };

        test('invalidateRejectedCookies', () => {
            cookiePrefs.setEssential(true);
            cookiePrefs.setSettings(false);
            cookiePrefs.setCampaigns(false);
            cookiePrefs.setUsage(false);

            cookiePrefs.invalidateRejectedCookies();

            expect(document.cookie).toBe(`_ga=;expires=${new Date};domain=${window.location.hostname};path=/;_gid=;expires=${new Date};domain=${window.location.hostname};path=/;_gat=;expires=${new Date};domain=${window.location.hostname};path=/`);
        })

        test('save', () => {
            cookiePrefs.setEssential(true);
            cookiePrefs.setSettings(false);
            cookiePrefs.setCampaigns(false);
            cookiePrefs.setUsage(false);
            cookiePrefs.save();
            expect(JSON.parse(getCookie('cookies_policy'))).toEqual({essential: true, settings: false, campaigns: false, usage: false});
        })

    })
})
