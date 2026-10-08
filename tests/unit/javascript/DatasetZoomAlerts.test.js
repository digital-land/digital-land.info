import { describe, expect, test, vi, beforeEach } from 'vitest'
import DatasetZoomAlerts from '../../../assets/javascripts/DatasetZoomAlerts.js'

vi.mock('../../../assets/javascripts/datasetMinZoomLevels.js', () => ({
  getDatasetMinZoom: (dataset) => {
    const levels = { 'restricted-dataset': 13, 'another-restricted-dataset': 10 }
    return levels[dataset] ?? null
  },
}))

function mockElement() {
  const children = []
  const dismissButton = {
    listeners: {},
    addEventListener(event, cb) { this.listeners[event] = cb },
    click() { this.listeners.click?.() },
  }

  return {
    classList: { add: vi.fn() },
    attributes: {},
    setAttribute(name, value) { this.attributes[name] = value },
    innerHTML: '',
    children,
    appendChild: vi.fn((child) => children.push(child)),
    remove: vi.fn(),
    querySelector: vi.fn(() => dismissButton),
    dismissButton,
  }
}

function mockMapController(zoom) {
  return {
    map: {
      on: vi.fn(),
      getZoom: vi.fn(() => zoom),
      getContainer: vi.fn(() => mockElement()),
    },
  }
}

function mockLayerOption(dataset, name, checked) {
  return {
    getDatasetName: () => dataset,
    isChecked: () => checked,
    layer: { name },
  }
}

describe('DatasetZoomAlerts', () => {
  beforeEach(() => {
    vi.stubGlobal('document', { createElement: vi.fn(() => mockElement()) })
  })

  describe('visibility', () => {
    test('shows alert message for a checked dataset below zoom level at which dataset displays', () => {
      const layerControls = {
        layerOptions: [mockLayerOption('restricted-dataset', 'Restricted dataset', true)],
      }
      const alerts = new DatasetZoomAlerts(mockMapController(6), layerControls)

      expect(Object.keys(alerts.alertElements)).toEqual(['restricted-dataset'])
    })

    test('does not show alert for a dataset with no configured minzoom', () => {
      const layerControls = {
        layerOptions: [mockLayerOption('unrestricted-dataset', 'Unrestricted dataset', true)],
      }
      const alerts = new DatasetZoomAlerts(mockMapController(6), layerControls)

      expect(alerts.alertElements).toEqual({})
    })

    test('does not show alert for a dataset that is not checked', () => {
      const layerControls = {
        layerOptions: [mockLayerOption('restricted-dataset', 'Restricted dataset', false)],
      }
      const alerts = new DatasetZoomAlerts(mockMapController(6), layerControls)

      expect(alerts.alertElements).toEqual({})
    })

    test('hides alert once zoom reaches the dataset minzoom and dataset becomes visible', () => {
      const option = mockLayerOption('restricted-dataset', 'Restricted dataset', true)
      const mapController = mockMapController(6)
      const layerControls = { layerOptions: [option] }
      const alerts = new DatasetZoomAlerts(mapController, layerControls)
      expect(alerts.alertElements['restricted-dataset']).toBeDefined()

      mapController.map.getZoom = vi.fn(() => 13)
      alerts.update()

      expect(alerts.alertElements).toEqual({})
    })

    test('unchecking and rechecking a dataset shows the message again', () => {
      const option = mockLayerOption('restricted-dataset', 'Restricted dataset', true)
      const mapController = mockMapController(6)
      const layerControls = { layerOptions: [option] }
      const alerts = new DatasetZoomAlerts(mapController, layerControls)
      alerts.dismiss('restricted-dataset')

      option.isChecked = () => false
      alerts.update()
      expect(alerts.alertElements).toEqual({})

      option.isChecked = () => true
      alerts.update()
      expect(alerts.alertElements['restricted-dataset']).toBeDefined()
    })

    test('registers a zoom listener on the map so alerts respond to zoom level changes', () => {
      const mapController = mockMapController(6)
      const layerControls = { layerOptions: [] }
      new DatasetZoomAlerts(mapController, layerControls)

      expect(mapController.map.on).toHaveBeenCalledWith('zoom', expect.any(Function))
    })
  })

  describe('dismissal', () => {
    test('once manually dismissed, the alert is hidden, and stays hidden even after zooming in and back out again', () => {
      const option = mockLayerOption('restricted-dataset', 'Restricted dataset', true)
      const mapController = mockMapController(6)
      const layerControls = { layerOptions: [option] }
      const alerts = new DatasetZoomAlerts(mapController, layerControls)

      const alertElement = alerts.alertElements['restricted-dataset']
      alertElement.dismissButton.click()

      // Zoom in - tiles become visible, alert hides automatically either way
      mapController.map.getZoom = vi.fn(() => 13)
      alerts.update()
      expect(alerts.alertElements).toEqual({})

      // Zoom back out - a dismissal should not be forgotten
      mapController.map.getZoom = vi.fn(() => 6)
      alerts.update()
      expect(alerts.alertElements).toEqual({})
    })

    test('an automatic hide while zoomed in is not treated as a dismissal - the alert reappears once zoom drops back below minzoom', () => {
      const option = mockLayerOption('restricted-dataset', 'Restricted dataset', true)
      const mapController = mockMapController(6)
      const layerControls = { layerOptions: [option] }
      const alerts = new DatasetZoomAlerts(mapController, layerControls)
      expect(alerts.alertElements['restricted-dataset']).toBeDefined()

      // Zoom in - tiles become visible, alert hides automatically (never dismissed)
      mapController.map.getZoom = vi.fn(() => 13)
      alerts.update()
      expect(alerts.alertElements).toEqual({})

      // Zoom back out - nothing was ever dismissed, so it should reappear
      mapController.map.getZoom = vi.fn(() => 6)
      alerts.update()
      expect(alerts.alertElements['restricted-dataset']).toBeDefined()
    })
  })

  describe('multiple datasets', () => {
    test('stacks alerts for multiple restricted datasets independently', () => {
      const layerControls = {
        layerOptions: [
          mockLayerOption('restricted-dataset', 'Restricted dataset', true),
          mockLayerOption('another-restricted-dataset', 'Another restricted dataset', true),
        ],
      }
      const alerts = new DatasetZoomAlerts(mockMapController(6), layerControls)

      expect(Object.keys(alerts.alertElements).sort()).toEqual(
        ['another-restricted-dataset', 'restricted-dataset'].sort()
      )
      expect(alerts._container.children).toHaveLength(2)

      // Dismissing one leaves the other showing
      alerts.dismiss('restricted-dataset')
      expect(alerts.alertElements['another-restricted-dataset']).toBeDefined()
      expect(alerts.alertElements['restricted-dataset']).toBeUndefined()
    })
  })
})
