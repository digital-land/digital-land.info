// @vitest-environment jsdom
// Parses the map's generated markup with a real DOM to check that dataset
// values cannot create elements or event-handler attributes.

import { describe, expect, test, vi, beforeEach } from 'vitest'
import DatasetZoomAlerts from '../../../assets/javascripts/DatasetZoomAlerts.js'

vi.mock('../../../assets/javascripts/analytics/trackEvent.js', () => ({
  trackEvent: vi.fn(),
}))

const NAME_PAYLOAD = '<img src=x onerror="window.__xss=1">'

function eventHandlerAttributes(root) {
  return [...root.querySelectorAll('*')].flatMap((el) =>
    [...el.attributes].filter((attr) => attr.name.startsWith('on')).map((attr) => attr.name)
  )
}

describe('map markup built from dataset values', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    delete window.__xss
  })

  test('zoom alert shows the layer name as text only', () => {
    const fakeAlerts = {
      alertElements: {},
      shown: {},
      _container: document.body,
      dismiss: vi.fn(),
    }
    DatasetZoomAlerts.prototype.showAlert.call(fakeAlerts, 'greenspace', NAME_PAYLOAD)

    const alert = fakeAlerts.alertElements.greenspace
    expect(alert.querySelector('img')).toBeNull()
    expect(eventHandlerAttributes(alert)).toEqual([])
    expect(alert.querySelector('.dl-zoom-alert__content').textContent)
      .toBe(`Zoom in to view ${NAME_PAYLOAD} data layer.`)
  })
})
