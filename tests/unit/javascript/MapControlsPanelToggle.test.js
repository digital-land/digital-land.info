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
    closest: vi.fn(() => null),
    getBoundingClientRect: vi.fn(() => ({ top: 0, bottom: 0 })),
    style: { setProperty: vi.fn() },
})

describe('MapControlsPanelToggle', () => {
    afterEach(() => {
        vi.unstubAllGlobals()
    })

    test('does nothing if the expected elements are not present', () => {
        vi.stubGlobal('document', { getElementById: vi.fn(() => null) })
        expect(() => new MapControlsPanelToggle()).not.toThrow()
    })

    const setUp = () => {
        // Real setTimeout/clearTimeout passed through (rather than
        // mockUtils' stubGlobalWindow, whose setTimeout mock invokes
        // callbacks immediately) so vi.useFakeTimers()/advanceTimersByTime
        // can control the post-toggle resync delay precisely where a test
        // needs that.
        vi.stubGlobal('window', {
            addEventListener: vi.fn(),
            setTimeout: (...args) => setTimeout(...args),
            clearTimeout: (...args) => clearTimeout(...args),
        })

        const panel = makeElement()
        const content = makeElement()
        const labelText = { textContent: '' }
        const button = { ...makeElement(), querySelector: vi.fn(() => labelText) }

        const mapWrapper = { ...makeElement(), getBoundingClientRect: vi.fn(() => ({ top: 100, bottom: 800 })) }
        const sourcesPanel = { ...makeElement(), getBoundingClientRect: vi.fn(() => ({ top: 800, bottom: 872 })) }
        const container = {
            style: { setProperty: vi.fn() },
            querySelector: vi.fn((selector) => ({
                '.dl-map__wrapper': mapWrapper,
                '.app-c-sources-panel': sourcesPanel,
            })[selector]),
        }
        panel.closest = vi.fn(() => container)

        vi.stubGlobal('document', {
            getElementById: vi.fn((id) => ({
                'dl-map-controls-panel': panel,
                'dl-map-controls-panel-content': content,
                'dl-map-controls-panel-toggle': button,
            })[id]),
        })

        return { panel, content, button, labelText, mapWrapper, sourcesPanel, container }
    }

    test('collapsing hides the content, updates aria-expanded, and swaps the label', () => {
        const { panel, content, button, labelText } = setUp()

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

    describe('syncContainerHeight()', () => {
        test('sets --dl-map-height to span from the map wrapper top to the footer bottom, on construction', () => {
            const { container } = setUp()

            new MapControlsPanelToggle()

            // footer.bottom (872) - wrapper.top (100) = 772
            expect(container.style.setProperty).toHaveBeenCalledWith('--dl-map-height', '772px')
        })

        test('falls back to the map wrapper alone when there is no footer', () => {
            const { container, mapWrapper } = setUp()
            container.querySelector = vi.fn((selector) => (selector === '.dl-map__wrapper' ? mapWrapper : null))
            mapWrapper.getBoundingClientRect = vi.fn(() => ({ top: 100, bottom: 800 }))

            new MapControlsPanelToggle()

            expect(container.style.setProperty).toHaveBeenCalledWith('--dl-map-height', '700px')
        })

        test('re-syncs after a toggle, once the width transition has finished', () => {
            vi.useFakeTimers()
            const { button, container, sourcesPanel } = setUp()

            new MapControlsPanelToggle()
            container.style.setProperty.mockClear()

            // footer wraps to an extra line once the panel opens and its
            // available width shrinks
            sourcesPanel.getBoundingClientRect = vi.fn(() => ({ top: 800, bottom: 900 }))

            const clickHandler = button.addEventListener.mock.calls.find(call => call[0] === 'click')[1]
            clickHandler()

            expect(container.style.setProperty).not.toHaveBeenCalled()
            vi.advanceTimersByTime(250)

            expect(container.style.setProperty).toHaveBeenCalledWith('--dl-map-height', '800px')
            vi.useRealTimers()
        })

        test('does nothing when there is no .dl-map-with-controls ancestor', () => {
            const { panel } = setUp()
            panel.closest = vi.fn(() => null)

            expect(() => new MapControlsPanelToggle()).not.toThrow()
        })
    })
})
