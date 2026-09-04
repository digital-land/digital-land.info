import {describe, expect, test, vi, afterEach} from 'vitest'
import AdaptiveLayerListHeight from '../../../assets/javascripts/AdaptiveLayerListHeight.js'

// govuk-frontend's own click listener lives on .govuk-accordion__section-
// header, not the button, so a section mock only needs to hand back a
// header element here - nothing in this class reads the button itself.
const makeSection = () => {
    const header = { addEventListener: vi.fn() }
    return {
        classList: { contains: (cls) => cls === 'govuk-accordion__section' },
        querySelector: vi.fn((selector) => (selector === '.govuk-accordion__section-header' ? header : null)),
        header,
    }
}

const makeMediaQuery = (matches) => ({
    matches,
    addEventListener: vi.fn(),
})

const setUp = ({ desktop = true } = {}) => {
    const layerList = {
        style: { height: '' },
        scrollHeight: 500,
        offsetHeight: 220,
    }
    // Measured as an actual rendered span (panelContent's top to the note
    // panel's bottom) rather than summed from individual elements'
    // offsetHeight - offsetHeight excludes margins, and govuk-frontend's
    // own .govuk-accordion carries a real 30px margin-bottom that a
    // plain "accordion height + note height" sum would silently miss.
    // _top/_bottom are plain mutable fields a test can reassign directly;
    // getBoundingClientRect() (called as a method, so `this` binds
    // correctly) just reads whatever they currently hold.
    const panelContent = {
        clientHeight: 700,
        _top: 100,
        getBoundingClientRect() {
            return { top: this._top }
        },
    }
    // top 100 to bottom 580 = a 480px natural span, 220px of which is the
    // list itself - 260px of "everything else" (matching a real
    // accordion+30px-margin+note total, not just each element's own box).
    const notePanel = {
        _bottom: 580,
        getBoundingClientRect() {
            return { bottom: this._bottom }
        },
    }
    const accordion = { children: [] }
    const filterInput = { addEventListener: vi.fn() }

    const findAnAreaSection = makeSection()
    const dataLayerSection = makeSection()
    const settingsSection = makeSection()
    accordion.children = [findAnAreaSection, dataLayerSection, settingsSection]

    const mediaQuery = makeMediaQuery(desktop)
    const windowMock = {
        matchMedia: vi.fn(() => mediaQuery),
        addEventListener: vi.fn(),
        setTimeout: (...args) => setTimeout(...args),
        clearTimeout: (...args) => clearTimeout(...args),
    }

    vi.stubGlobal('document', {
        getElementById: vi.fn((id) => ({
            'layer-toggles-list': layerList,
            'dl-map-controls-panel-content': panelContent,
            'layer-filter-input': filterInput,
            'dl-map-controls-accordion': accordion,
            'dl-data-coverage-banner': notePanel,
        })[id]),
    })
    vi.stubGlobal('window', windowMock)

    return {
        layerList,
        panelContent,
        accordion,
        notePanel,
        filterInput,
        mediaQuery,
        windowMock,
        findAnAreaHeader: findAnAreaSection.header,
        dataLayerHeader: dataLayerSection.header,
    }
}

describe('AdaptiveLayerListHeight', () => {
    afterEach(() => {
        vi.unstubAllGlobals()
    })

    test('does nothing if the expected elements are not present', () => {
        vi.stubGlobal('document', { getElementById: vi.fn(() => null) })
        expect(() => new AdaptiveLayerListHeight()).not.toThrow()
    })

    test('stays at 440px when "Find an area" is open and that\'s all the spare room there is, on construction', () => {
        const { layerList } = setUp()

        new AdaptiveLayerListHeight()

        // available (700) - othersHeight (span 480 - list 220 = 260) =
        // 440, capped by naturalHeight (500) -> min(500, 440) = 440.
        expect(layerList.style.height).toEqual('440px')
    })

    test('grows past the baseline once there is spare room (e.g. "Find an area" collapsed)', () => {
        const { layerList, notePanel, findAnAreaHeader } = setUp()

        new AdaptiveLayerListHeight()

        // "Find an area" collapsing shrinks the natural span from 480 to
        // 330 - everything else drops from 260 to 110, so the list could
        // grow to 590, but is capped by its natural 500.
        notePanel._bottom = 100 + 330
        const handler = findAnAreaHeader.addEventListener.mock.calls.find(call => call[0] === 'click')[1]
        handler()

        expect(layerList.style.height).toEqual('500px')
    })

    test('caps growth at the list\'s own natural content height, rather than stretching past what its items need', () => {
        const { layerList, notePanel, findAnAreaHeader } = setUp()
        layerList.scrollHeight = 300 // only enough datasets to need 300px

        new AdaptiveLayerListHeight()

        notePanel._bottom = 100 + 330 // up to 590px would otherwise fit
        const handler = findAnAreaHeader.addEventListener.mock.calls.find(call => call[0] === 'click')[1]
        handler()

        expect(layerList.style.height).toEqual('300px')
    })

    test('accounts for gaps/margins between elements, not just their own offsetHeight', () => {
        const { layerList, panelContent } = setUp()
        // an extra 30px gap between panelContent's top and the accordion's
        // real start - e.g. govuk-frontend's own .govuk-accordion margin-
        // bottom, which never shows up in any element's own offsetHeight
        panelContent._top = 70 // widens the measured span from 480 to 510

        new AdaptiveLayerListHeight()

        // available (700) - othersHeight (510 - 220 = 290) = 410
        expect(layerList.style.height).toEqual('410px')
    })

    test('falls back to the accordion\'s own bottom edge if the note panel is missing', () => {
        const layerList = { style: { height: '' }, scrollHeight: 500, offsetHeight: 220 }
        const panelContent = { clientHeight: 700, getBoundingClientRect: () => ({ top: 100 }) }
        const accordion = { children: [], getBoundingClientRect: () => ({ bottom: 580 }) }
        const elements = {
            'layer-toggles-list': layerList,
            'dl-map-controls-panel-content': panelContent,
            'dl-map-controls-accordion': accordion,
            'dl-data-coverage-banner': null,
        }

        vi.stubGlobal('document', { getElementById: vi.fn((id) => elements[id]) })
        vi.stubGlobal('window', { matchMedia: vi.fn(() => makeMediaQuery(true)), addEventListener: vi.fn() })

        expect(() => new AdaptiveLayerListHeight()).not.toThrow()
        expect(layerList.style.height).toEqual('440px')
    })

    test('never shrinks below the original 220px design height', () => {
        const { layerList, notePanel } = setUp()
        // a pathologically wide "everything else" span that would
        // otherwise squeeze the list below its floor
        notePanel._bottom = 100 + 900

        new AdaptiveLayerListHeight()

        expect(layerList.style.height).toEqual('220px')
    })

    test('recomputes when "Select a data layer" is clicked (it may have been hidden, going stale)', () => {
        const { layerList, notePanel, dataLayerHeader } = setUp()

        new AdaptiveLayerListHeight()
        notePanel._bottom = 100 + 330

        const handler = dataLayerHeader.addEventListener.mock.calls.find(call => call[0] === 'click')[1]
        handler()

        expect(layerList.style.height).toEqual('500px')
    })

    test('recomputes when the dataset filter input is typed into', () => {
        const { layerList, notePanel, filterInput } = setUp()

        new AdaptiveLayerListHeight()
        notePanel._bottom = 100 + 330
        layerList.scrollHeight = 450 // filtering hid some items

        const handler = filterInput.addEventListener.mock.calls.find(call => call[0] === 'input')[1]
        handler()

        expect(layerList.style.height).toEqual('450px')
    })

    test('falls back to the plain CSS-declared height on mobile', () => {
        const { layerList } = setUp({ desktop: false })

        new AdaptiveLayerListHeight()

        expect(layerList.style.height).toEqual('')
    })

    test('resyncs to the CSS default when the viewport crosses down below the desktop breakpoint', () => {
        const { layerList, mediaQuery } = setUp({ desktop: true })

        new AdaptiveLayerListHeight()
        expect(layerList.style.height).toEqual('440px')

        mediaQuery.matches = false
        const changeHandler = mediaQuery.addEventListener.mock.calls.find(call => call[0] === 'change')[1]
        changeHandler()

        expect(layerList.style.height).toEqual('')
    })

    test('recomputes on window resize, debounced', () => {
        vi.useFakeTimers()
        const { layerList, notePanel, windowMock } = setUp()

        new AdaptiveLayerListHeight()
        const resizeHandler = windowMock.addEventListener.mock.calls.find(call => call[0] === 'resize')[1]

        notePanel._bottom = 100 + 330
        resizeHandler()

        expect(layerList.style.height).toEqual('440px') // not yet - debounced
        vi.advanceTimersByTime(150)

        expect(layerList.style.height).toEqual('500px')
        vi.useRealTimers()
    })
})
