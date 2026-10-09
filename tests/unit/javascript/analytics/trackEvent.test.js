import { describe, expect, test, vi, afterEach } from 'vitest'
import { trackEvent } from '../../../../assets/javascripts/analytics/trackEvent.js'

describe('trackEvent', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('sends the event via gtag when usage cookies are accepted', () => {
    const gtag = vi.fn()
    vi.stubGlobal('window', { cookiePrefs: { usage: true }, gtag })

    trackEvent('zoom_alert_shown', { dataset: 'restricted-dataset' })

    expect(gtag).toHaveBeenCalledWith('event', 'zoom_alert_shown', {
      dataset: 'restricted-dataset',
    })
  })

  test('does not call gtag when usage cookies are not accepted', () => {
    const gtag = vi.fn()
    vi.stubGlobal('window', { cookiePrefs: { usage: false }, gtag })

    trackEvent('zoom_alert_shown', { dataset: 'restricted-dataset' })

    expect(gtag).not.toHaveBeenCalled()
  })

  test('does not call gtag when no cookie preferences have been set at all', () => {
    const gtag = vi.fn()
    vi.stubGlobal('window', { gtag })

    trackEvent('zoom_alert_shown', { dataset: 'restricted-dataset' })

    expect(gtag).not.toHaveBeenCalled()
  })

  test('does not throw when gtag is unavailable (not yet loaded or blocked)', () => {
    vi.stubGlobal('window', { cookiePrefs: { usage: true } })

    expect(() => trackEvent('zoom_alert_shown', { dataset: 'restricted-dataset' })).not.toThrow()
  })

  test('does not throw when window itself is unavailable', () => {
    vi.stubGlobal('window', undefined)

    expect(() => trackEvent('zoom_alert_shown', { dataset: 'restricted-dataset' })).not.toThrow()
  })

  test('defaults params to an empty object when none are given', () => {
    const gtag = vi.fn()
    vi.stubGlobal('window', { cookiePrefs: { usage: true }, gtag })

    trackEvent('zoom_alert_shown')

    expect(gtag).toHaveBeenCalledWith('event', 'zoom_alert_shown', {})
  })
})
