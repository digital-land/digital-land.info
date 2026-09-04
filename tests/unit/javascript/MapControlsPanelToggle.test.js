import {describe, expect, test, vi, beforeEach, afterEach} from 'vitest'
import MapControlsPanelToggle from '../../../assets/javascripts/MapControlsPanelToggle.js'

const makeElement = () => ({
    classList: {
        _collapsed: false,
        contains: vi.fn(function (cls) { return cls === 'dl-map-controls-panel--collapsed' && this._collapsed }),
        toggle: vi.fn(function (cls, force) {
            this._collapsed = force
        }),
    },
    setAttribute: vi.fn(),
    removeAttribute: vi.fn(),
    addEventListener: vi.fn(),
    querySelector: vi.fn(),
})

describe('MapControlsPanelToggle', () => {
    afterEach(() => {
        vi.unstubAllGlobals()
    })

    test('does nothing if the expected elements are not present', () => {
        vi.stubGlobal('document', { getElementById: vi.fn(() => null) })
        expect(() => new MapControlsPanelToggle()).not.toThrow()
    })

    test('collapsing hides the content, updates aria-expanded, and swaps the label', () => {
        const panel = makeElement()
        const content = makeElement()
        const labelText = { textContent: '' }
        const button = { ...makeElement(), querySelector: vi.fn(() => labelText) }

        vi.stubGlobal('document', {
            getElementById: vi.fn((id) => ({
                'dl-map-controls-panel': panel,
                'dl-map-controls-panel-content': content,
                'dl-map-controls-panel-toggle': button,
            })[id]),
        })

        const toggle = new MapControlsPanelToggle()
        const clickHandler = button.addEventListener.mock.calls.find(call => call[0] === 'click')[1]

        clickHandler()

        expect(panel.classList.toggle).toHaveBeenCalledWith('dl-map-controls-panel--collapsed', true)
        expect(button.classList.toggle).toHaveBeenCalledWith('dl-map-controls-panel__toggle--collapsed', true)
        expect(button.setAttribute).toHaveBeenCalledWith('aria-expanded', 'false')
        expect(content.setAttribute).toHaveBeenCalledWith('hidden', '')
        expect(labelText.textContent).toEqual('Show map controls')

        // toggling again re-expands it
        clickHandler()

        expect(panel.classList.toggle).toHaveBeenCalledWith('dl-map-controls-panel--collapsed', false)
        expect(button.classList.toggle).toHaveBeenCalledWith('dl-map-controls-panel__toggle--collapsed', false)
        expect(button.setAttribute).toHaveBeenCalledWith('aria-expanded', 'true')
        expect(content.removeAttribute).toHaveBeenCalledWith('hidden')
        expect(labelText.textContent).toEqual('Hide map controls')
    })
})
