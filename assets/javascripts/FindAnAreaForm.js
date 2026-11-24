/** Handles the "Find an area" postcode/UPRN/LPA search form on the map page. */

import { debounce } from './utils.js';

export default class FindAnAreaForm {
  constructor(searchResult) {
    this.searchResult = searchResult
    this.form = document.querySelector('#dl-find-an-area-form')
    this.methodRadios = this.form ? Array.prototype.slice.call(this.form.querySelectorAll('input[name="type"]')) : []

    this.postcodeInput = this.form ? this.form.querySelector('#postcode-input') : null
    this.uprnSearchInput = this.form ? this.form.querySelector('#uprn-search-input') : null

    this.lpaAutocompleteInput = this.form ? this.form.querySelector('#lpa-autocomplete-input') : null
    this.lpaAutocompleteSuggestions = this.form ? this.form.querySelector('#lpa-autocomplete-suggestions') : null
    this.lpaSuggestionsContainer = this.form ? this.form.querySelector('#lpa-suggestions') : null
    this.lpaSelected = false

    // Ignores out-of-order fetchLpaSuggestions() responses.
    this._lpaFetchId = 0

    this.selectMethodFromUrlParam()

    this.initFormListener()
    this.bindMethodChangeListener()
    this.flyToSearchResult()
  }

  /**
   * Selects the radio matching the URL's `type` param, unless the search
   * already succeeded - the server leaves it deselected in that case, even
   * though the URL's `type` param is still present.
   */
  selectMethodFromUrlParam() {
    try {
      const hasSuccessfulResult = !!(this.searchResult && this.searchResult.result)
      const params = new URLSearchParams(window.location.search)
      const sortVal = params.get('type')
      if (sortVal && !hasSuccessfulResult) {
        const target = this.methodRadios.find((radio) => radio.value === sortVal)
        if (target && !target.checked) target.click()
      }
    } catch (e) {
      // Ignore URL parsing errors in older browsers
    }
  }

  getSelectedMethod() {
    const checked = this.methodRadios.find((radio) => radio.checked)
    return checked ? checked.value : ''
  }

  flyToSearchResult() {
      setTimeout(() => {
        if (this.searchResult && this.searchResult.geometry && window.mapControllers.map) {
          window.mapControllers.map.flyTo(this.searchResult.geometry)
        }
      }, 1000)
  }

  initFormListener() {
    this.form.addEventListener('submit', function (e) {
      e.preventDefault()
      const url = new URL(window.location.href)
      const params = new URLSearchParams(url.search)

      let inputValue = ''
      const sel = this.getSelectedMethod()
      if (sel === 'postcode' && this.postcodeInput) {
        inputValue = this.postcodeInput.value
      } else if (sel === 'uprn' && this.uprnSearchInput) {
        inputValue = this.uprnSearchInput.value
      } else if (sel === 'lpa' && this.lpaAutocompleteInput) {
        inputValue = this.lpaSelected ? this.lpaAutocompleteInput.value : ''
      } else if (this.postcodeInput) {
        inputValue = this.postcodeInput.value
      }

      params.set('q', inputValue);
      if (sel) {
        params.set('type', sel);
      }

      window.location.href = `${url.pathname}?${params.toString()}`;
    }.bind(this));
  }

  bindMethodChangeListener() {
    if (!this.methodRadios.length) return

    this.methodRadios.forEach((radio) => {
      radio.addEventListener('change', function () {
        try {
          if (this.postcodeInput) this.postcodeInput.value = ''
          if (this.uprnSearchInput) this.uprnSearchInput.value = ''
          if (this.lpaAutocompleteInput) this.lpaAutocompleteInput.value = ''
          if (this.lpaAutocompleteSuggestions) {
            this.lpaAutocompleteSuggestions.style.display = 'none'
            this.lpaAutocompleteSuggestions.innerHTML = ''
          }
          this.lpaSelected = false
        } catch (err) {
          // Ignore
        }
      }.bind(this))
    })

    if (this.lpaAutocompleteInput) {
      const doFetch = debounce(this.fetchLpaSuggestions.bind(this), 250)
      this.lpaAutocompleteInput.addEventListener('input', function (e) {
        const val = e.target.value
        this.lpaSelected = false
        if (val && val.length > 1 && this.getSelectedMethod() === 'lpa') {
          doFetch(val)
        } else if (this.lpaAutocompleteSuggestions) {
          this.lpaAutocompleteSuggestions.style.display = 'none'
          if (this.lpaSuggestionsContainer) this.lpaSuggestionsContainer.classList.add('js-hidden')
        }
      }.bind(this))

      if (this.lpaAutocompleteSuggestions) {
        this.lpaAutocompleteSuggestions.addEventListener('click', function (e) {
          const item = e.target.closest('li[data-name]')
            if (item) {
              const name = item.getAttribute('data-name')
              if (this.lpaAutocompleteInput) this.lpaAutocompleteInput.value = name
              this.lpaSelected = true
              if (this.postcodeInput) this.postcodeInput.value = name
              if (this.uprnSearchInput) this.uprnSearchInput.value = name
              this.lpaAutocompleteSuggestions.style.display = 'none'
              if (this.lpaSuggestionsContainer) this.lpaSuggestionsContainer.classList.add('js-hidden')
            }
        }.bind(this))
      }
    }
  }

  async fetchLpaSuggestions(term) {
    const fetchId = ++this._lpaFetchId

    try {
      const url = new URL('/entity/dataset-name-search.json', window.location.origin)
      url.searchParams.set('dataset', 'local-planning-authority')
      url.searchParams.set('search', term)
      url.searchParams.set('limit', '10')

      const resp = await fetch(url.toString())
      if (!resp.ok) return

      const data = await resp.json()
      if (fetchId !== this._lpaFetchId) return

      const entities = data.entities || []
      this.renderLpaSuggestions(entities, term)
    } catch (e) {
      // Ignore errors silently
    }
  }

  renderLpaSuggestions(entities, term) {
    if (!this.lpaAutocompleteSuggestions) return
    if (!entities || entities.length === 0) {
      this.lpaAutocompleteSuggestions.style.display = 'none'
      this.lpaAutocompleteSuggestions.innerHTML = ''
      if (this.lpaSuggestionsContainer) this.lpaSuggestionsContainer.classList.add('js-hidden')
      return
    }
    this.lpaAutocompleteSuggestions.innerHTML = ''

    const seen = new Set()

    entities.forEach(entity => {
      const name = entity.name || (entity.properties && entity.properties.name) || ''

      if (!name) return
      if (seen.has(name)) return

      seen.add(name)
      const li = document.createElement('li')
      li.className = "govuk-label"
      li.setAttribute('data-name', name)
      li.setAttribute('role', 'option')
      li.style.padding = '6px 8px'
      li.style.cursor = 'pointer'
      li.textContent = name
      this.lpaAutocompleteSuggestions.appendChild(li)
    })
    if (this.lpaSuggestionsContainer) this.lpaSuggestionsContainer.classList.remove('js-hidden')
    this.lpaAutocompleteSuggestions.style.display = 'block'
  }
}
