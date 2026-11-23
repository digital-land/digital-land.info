import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest'
import SearchResultsPage from '../../../assets/javascripts/SearchResultsPage.js'

function mockButton() {
  const listeners = {}
  return {
    listeners,
    addEventListener: vi.fn((event, cb) => { listeners[event] = cb }),
    click() { listeners.click?.() },
    disabled: false,
    textContent: '',
  }
}

function mockInput(value = '') {
  return { value, focus: vi.fn() }
}

function mockRadio(checked = false) {
  return { checked }
}

function mockStatus() {
  return { textContent: '' }
}

describe('SearchResultsPage', () => {
  let elements

  beforeEach(() => {
    elements = {
      'search-results': null,
      'entry-date-clear': mockButton(),
      'entry-date-clear-status': mockStatus(),
    }

    vi.stubGlobal('document', {
      getElementById: vi.fn((id) => elements[id] ?? null),
      querySelectorAll: vi.fn((selector) => {
        if (selector === '#entry-date .govuk-date-input__input') {
          return elements.entryDateInputs ?? []
        }
        if (selector === 'input[name="entry_date_match"]') {
          return elements.entryDateMatchRadios ?? []
        }
        return []
      }),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  describe('entry date filter', () => {
    test('clicking the clear button empties the date fields, unchecks radios, announces change and focuses day field', () => {
      elements.entryDateInputs = [mockInput('27'), mockInput('3'), mockInput('2021')]
      elements.entryDateMatchRadios = [mockRadio(true), mockRadio(false)]

      new SearchResultsPage([], [])
      elements['entry-date-clear'].click()

      elements.entryDateInputs.forEach((input) => {
        expect(input.value).toBe('')
      })
      elements.entryDateMatchRadios.forEach((radio) => {
        expect(radio.checked).toBe(false)
      })
      expect(elements['entry-date-clear-status'].textContent).toBe('Entry date cleared')
      expect(elements.entryDateInputs[0].focus).toHaveBeenCalledOnce()
    })
  })
})
