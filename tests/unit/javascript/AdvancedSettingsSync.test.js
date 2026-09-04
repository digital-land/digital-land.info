import {describe, expect, test, vi, afterEach} from 'vitest'
import AdvancedSettingsSync from '../../../assets/javascripts/AdvancedSettingsSync.js'

const makeButton = (expanded) => ({
    _expanded: expanded,
    getAttribute: vi.fn(function (name) {
        return name === 'aria-expanded' ? String(this._expanded) : null
    }),
    click: vi.fn(function () {
        this._expanded = !this._expanded
    }),
})

// govuk-frontend's own click listener lives on .govuk-accordion__section-
// header, not the button - so the section mock needs to hand back a
// distinct header element (with its own addEventListener) alongside the
// button, not the same element for both selectors.
const makeSection = (button) => {
    const header = { addEventListener: vi.fn() }
    return {
        classList: { contains: (cls) => cls === 'govuk-accordion__section' },
        querySelector: vi.fn((selector) => {
            if (selector === '.govuk-accordion__section-button') return button
            if (selector === '.govuk-accordion__section-header') return header
            return null
        }),
        header,
    }
}

const makeMediaQuery = (matches) => ({
    matches,
    addEventListener: vi.fn(),
})

const setUp = ({ dataLayerExpanded = true, settingsExpanded = true, desktop = true } = {}) => {
    const findAnAreaButton = makeButton(true)
    const dataLayerButton = makeButton(dataLayerExpanded)
    const settingsButton = makeButton(settingsExpanded)

    const findAnAreaSection = makeSection(findAnAreaButton)
    const dataLayerSection = makeSection(dataLayerButton)
    const settingsSection = makeSection(settingsButton)

    const accordion = { children: [findAnAreaSection, dataLayerSection, settingsSection] }
    const mediaQuery = makeMediaQuery(desktop)

    vi.stubGlobal('document', {
        getElementById: vi.fn((id) => (id === 'dl-map-controls-accordion' ? accordion : null)),
    })
    vi.stubGlobal('window', {
        matchMedia: vi.fn(() => mediaQuery),
    })

    return { dataLayerButton, settingsButton, dataLayerHeader: dataLayerSection.header, mediaQuery }
}

describe('AdvancedSettingsSync', () => {
    afterEach(() => {
        vi.unstubAllGlobals()
    })

    test('does nothing if the accordion is not present', () => {
        vi.stubGlobal('document', { getElementById: vi.fn(() => null) })
        expect(() => new AdvancedSettingsSync()).not.toThrow()
    })

    test('closes "Advanced settings" on construction if "Select a data layer" starts closed', () => {
        const { settingsButton } = setUp({ dataLayerExpanded: false, settingsExpanded: true })

        new AdvancedSettingsSync()

        expect(settingsButton.click).toHaveBeenCalledTimes(1)
        expect(settingsButton._expanded).toBe(false)
    })

    test('does not click "Advanced settings" if it already matches on construction', () => {
        const { settingsButton } = setUp({ dataLayerExpanded: true, settingsExpanded: true })

        new AdvancedSettingsSync()

        expect(settingsButton.click).not.toHaveBeenCalled()
    })

    test('closes "Advanced settings" when "Select a data layer" is clicked closed', () => {
        const { dataLayerButton, settingsButton, dataLayerHeader } = setUp({ dataLayerExpanded: true, settingsExpanded: true })

        new AdvancedSettingsSync()
        settingsButton.click.mockClear()

        // The listener is attached to the header div, not the button -
        // govuk-frontend's own handler (also on the header, registered
        // first) already flips aria-expanded by the time a real click
        // bubbles up to it; dataLayerButton.click() mimics that flip
        // directly, then we invoke our own registered listener exactly
        // as the browser would next, on bubbling to the header.
        dataLayerButton.click()
        const syncHandler = dataLayerHeader.addEventListener.mock.calls.find(call => call[0] === 'click')[1]
        syncHandler()

        expect(settingsButton.click).toHaveBeenCalledTimes(1)
        expect(settingsButton._expanded).toBe(false)
    })

    test('re-opens "Advanced settings" when "Select a data layer" is clicked back open', () => {
        const { dataLayerButton, settingsButton, dataLayerHeader } = setUp({ dataLayerExpanded: false, settingsExpanded: false })

        new AdvancedSettingsSync()
        settingsButton.click.mockClear()

        dataLayerButton.click()
        const syncHandler = dataLayerHeader.addEventListener.mock.calls.find(call => call[0] === 'click')[1]
        syncHandler()

        expect(settingsButton.click).toHaveBeenCalledTimes(1)
        expect(settingsButton._expanded).toBe(true)
    })

    test('leaves mobile (below the breakpoint) fully independent', () => {
        const { settingsButton } = setUp({ dataLayerExpanded: false, settingsExpanded: true, desktop: false })

        new AdvancedSettingsSync()

        expect(settingsButton.click).not.toHaveBeenCalled()
    })

    test('re-syncs when the viewport crosses the desktop breakpoint', () => {
        const { settingsButton, mediaQuery } = setUp({ dataLayerExpanded: false, settingsExpanded: true, desktop: false })

        new AdvancedSettingsSync()
        expect(settingsButton.click).not.toHaveBeenCalled()

        mediaQuery.matches = true
        const changeHandler = mediaQuery.addEventListener.mock.calls.find(call => call[0] === 'change')[1]
        changeHandler()

        expect(settingsButton.click).toHaveBeenCalledTimes(1)
    })
})
