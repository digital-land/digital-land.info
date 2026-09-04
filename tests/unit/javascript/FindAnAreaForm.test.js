import {describe, expect, test, vi, beforeEach, afterEach} from 'vitest'
import FindAnAreaForm from '../../../assets/javascripts/FindAnAreaForm.js'

const makeRadio = (value, checked = false) => ({
    value,
    checked,
    click: vi.fn(function () {
        this.checked = true
    }),
    addEventListener: vi.fn(),
})

const makeForm = ({ radios, postcodeInput, uprnInput, lpaInput, lpaSuggestions, lpaSuggestionsContainer }) => {
    const elements = {
        '#postcode-input': postcodeInput,
        '#uprn-search-input': uprnInput,
        '#lpa-autocomplete-input': lpaInput,
        '#lpa-autocomplete-suggestions': lpaSuggestions,
        '#lpa-suggestions': lpaSuggestionsContainer,
    }

    return {
        querySelectorAll: vi.fn((selector) => {
            if (selector === 'input[name="type"]') return radios
            return []
        }),
        querySelector: vi.fn((selector) => elements[selector] || null),
        addEventListener: vi.fn(),
    }
}

const makeInput = (value = '') => ({ value, addEventListener: vi.fn() })

const stubDocumentAndWindow = ({ form, search = '', href = 'http://localhost:3000/map/' }) => {
    vi.stubGlobal('document', {
        querySelector: vi.fn((selector) => (selector === '#dl-find-an-area-form' ? form : null)),
    })
    vi.stubGlobal('window', {
        location: { search, href, pathname: '/map/' },
        mapControllers: {},
        gtag: vi.fn(),
    })
}

describe('FindAnAreaForm', () => {
    afterEach(() => {
        vi.unstubAllGlobals()
        vi.restoreAllMocks()
    })

    describe('getSelectedMethod()', () => {
        test('returns the value of whichever radio is checked', () => {
            const radios = [makeRadio('postcode', false), makeRadio('uprn', true), makeRadio('lpa', false)]
            const form = makeForm({ radios })
            stubDocumentAndWindow({ form })

            const findAnAreaForm = new FindAnAreaForm(null)

            expect(findAnAreaForm.getSelectedMethod()).toEqual('uprn')
        })
    })

    describe('constructor', () => {
        test('clicks the radio matching the `type` URL param when it is not already checked', () => {
            const radios = [makeRadio('postcode', true), makeRadio('uprn', false), makeRadio('lpa', false)]
            const form = makeForm({ radios })
            stubDocumentAndWindow({ form, search: '?q=123&type=uprn' })

            new FindAnAreaForm(null)

            expect(radios[1].click).toHaveBeenCalledTimes(1)
            expect(radios[0].click).not.toHaveBeenCalled()
        })

        test('does not click the radio if it is already the checked one', () => {
            const radios = [makeRadio('postcode', true), makeRadio('uprn', false)]
            const form = makeForm({ radios })
            stubDocumentAndWindow({ form, search: '?type=postcode' })

            new FindAnAreaForm(null)

            expect(radios[0].click).not.toHaveBeenCalled()
            expect(radios[1].click).not.toHaveBeenCalled()
        })

        test('does not click the radio matching `type` once the search has already succeeded', () => {
            const radios = [makeRadio('postcode', false), makeRadio('uprn', false)]
            const form = makeForm({ radios })
            stubDocumentAndWindow({ form, search: '?q=123&type=uprn' })

            new FindAnAreaForm({ type: 'uprn', result: { UPRN: '123' } })

            expect(radios[0].click).not.toHaveBeenCalled()
            expect(radios[1].click).not.toHaveBeenCalled()
        })
    })

    describe('submit handling', () => {
        test('redirects with the active method\'s value and preserves other query params', () => {
            const postcodeInput = makeInput('SW1A 1AA')
            const radios = [makeRadio('postcode', true), makeRadio('uprn', false)]
            const form = makeForm({ radios, postcodeInput })
            stubDocumentAndWindow({ form, href: 'http://localhost:3000/map/?foo=bar' })

            const findAnAreaForm = new FindAnAreaForm(null)
            const submitHandler = form.addEventListener.mock.calls.find(call => call[0] === 'submit')[1]

            const preventDefault = vi.fn()
            submitHandler({ preventDefault })

            expect(preventDefault).toHaveBeenCalled()
            expect(window.location.href).toEqual('/map/?foo=bar&q=SW1A+1AA&type=postcode')
        })

        test('LPA method only submits a value when a suggestion was explicitly selected', () => {
            const lpaInput = makeInput('Some Council')
            const radios = [makeRadio('postcode', false), makeRadio('lpa', true)]
            const form = makeForm({ radios, lpaInput })
            stubDocumentAndWindow({ form, href: 'http://localhost:3000/map/' })

            const findAnAreaForm = new FindAnAreaForm(null)
            const submitHandler = form.addEventListener.mock.calls.find(call => call[0] === 'submit')[1]

            // typed but not selected from the suggestions list
            findAnAreaForm.lpaSelected = false
            submitHandler({ preventDefault: vi.fn() })
            expect(window.location.href).toEqual('/map/?q=&type=lpa')

            // explicitly selected from the suggestions list
            window.location.href = 'http://localhost:3000/map/'
            findAnAreaForm.lpaSelected = true
            submitHandler({ preventDefault: vi.fn() })
            expect(window.location.href).toEqual('/map/?q=Some+Council&type=lpa')
        })
    })

    describe('flyToSearchResult()', () => {
        beforeEach(() => {
            vi.useFakeTimers()
        })

        afterEach(() => {
            vi.useRealTimers()
        })

        test('flies to the search result geometry once the map controller is available', () => {
            const radios = [makeRadio('postcode', true)]
            const form = makeForm({ radios })
            stubDocumentAndWindow({ form })
            window.mapControllers.map = { flyTo: vi.fn() }

            const geometry = { data: { type: 'Point', coordinates: [0, 0] } }
            new FindAnAreaForm({ geometry })

            vi.advanceTimersByTime(1000)

            expect(window.mapControllers.map.flyTo).toHaveBeenCalledWith(geometry)
        })

        test('does nothing when there is no search result', () => {
            const radios = [makeRadio('postcode', true)]
            const form = makeForm({ radios })
            stubDocumentAndWindow({ form })
            window.mapControllers.map = { flyTo: vi.fn() }

            new FindAnAreaForm(null)

            vi.advanceTimersByTime(1000)

            expect(window.mapControllers.map.flyTo).not.toHaveBeenCalled()
        })
    })
})
