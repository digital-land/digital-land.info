export default class FindAnAreaForm {
  constructor(searchResult) {
    this.searchResult = searchResult
    this.form = document.querySelector('#dl-find-an-area-form')
    this.methodRadios = this.form ? Array.prototype.slice.call(this.form.querySelectorAll('input[name="type"]')) : []

    // Postcode controls
    this.postcodeInput = this.form ? this.form.querySelector('#postcode-input') : null

    // UPRN controls
    this.uprnSearchInput = this.form ? this.form.querySelector('#uprn-search-input') : null

    // LPA controls
    this.lpaAutocompleteInput = this.form ? this.form.querySelector('#lpa-autocomplete-input') : null
    this.lpaAutocompleteSuggestions = this.form ? this.form.querySelector('#lpa-autocomplete-suggestions') : null
    this.lpaSuggestionsContainer = this.form ? this.form.querySelector('#lpa-suggestions') : null
    // Track whether the user has selected an LPA suggestion (not just typed)
    this.lpaSelected = false

    // ID to track latest fetch so we can ignore out-of-order responses
    this._lpaFetchId = 0

    // If a `type` parameter is present in the URL, select the matching
    // radio. The GOV.UK Radios component (already initialised via initAll()
    // by the time this runs) shows/hides each conditional block based on a
    // radio's checked state and syncs that from its own click handler, so
    // we click the radio - rather than just setting `.checked` - to keep
    // the conditional reveal in sync with it.
    //
    // Skipped when the search actually succeeded (searchResult.result is
    // populated) - the server already leaves the radio deselected in that
    // case (its job is done, the result is shown below instead), and
    // without this check we'd immediately re-select it here since the
    // URL's `type` param is still present after a successful search.
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

    this.initFormListener()
    this.bindMethodChangeListener()
    this.flyToSearchResult()
  }

  getSelectedMethod() {
    const checked = this.methodRadios.find((radio) => radio.checked)
    return checked ? checked.value : ''
  }

  flyToSearchResult() {
      setTimeout(() => {
        if (this.searchResult && this.searchResult.geometry && window.mapControllers.map) {
          // Don't add the geometry again - it's already added
          // via geojsons param in map initialization
          window.mapControllers.map.flyTo(this.searchResult.geometry)
        }
      }, 1000)
  }

  initFormListener() {
    this.form.addEventListener('submit', function (e) {
      e.preventDefault()
      const url = new URL(window.location.href)
      const params = new URLSearchParams(url.search)

      // Determine which input is currently active based on the checked radio
      let inputValue = ''
      const sel = this.getSelectedMethod()
      if (sel === 'postcode' && this.postcodeInput) {
        inputValue = this.postcodeInput.value
      } else if (sel === 'uprn' && this.uprnSearchInput) {
        inputValue = this.uprnSearchInput.value
      } else if (sel === 'lpa' && this.lpaAutocompleteInput) {
        // Only use LPA value if a suggestion was explicitly selected
        if (this.lpaSelected) {
          inputValue = this.lpaAutocompleteInput.value
        } else {
          inputValue = ''
        }
      } else if (this.postcodeInput) {
        // Fallback to the main input
        inputValue = this.postcodeInput.value
      }

      // Update or append the 'q' parameter from the form input
      params.set('q', inputValue);
      // Ensure the selected type option is preserved in the URL
      if (sel) {
        params.set('type', sel);
      }

      // Build final query string
      const queryString = params.toString();

      this.sendAnalyticsEvent('search_term', {
        'event_category': 'Search',
        'event_label': 'Find an area form',
        'value': inputValue
      });

      // Redirect with merged query parameters
      window.location.href = `${url.pathname}?${queryString}`;
    }.bind(this));
  }

  bindMethodChangeListener() {
    if (!this.methodRadios.length) return

    // Clear inputs and autocomplete suggestions when the search method
    // changes. Showing/hiding each method's conditional content is handled
    // by GOV.UK's own Radios component.
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

    // If LPA input, bind autocomplete behaviour
    if (this.lpaAutocompleteInput) {
      const doFetch = this.debounce(this.fetchLpaSuggestions.bind(this), 250)
      this.lpaAutocompleteInput.addEventListener('input', function (e) {
        const val = e.target.value
        // Any manual input invalidates previous selection
        this.lpaSelected = false
        if (val && val.length > 1 && this.getSelectedMethod() === 'lpa') {
          doFetch(val)
        } else if (this.lpaAutocompleteSuggestions) {
          // hide the suggestions list and its container
          this.lpaAutocompleteSuggestions.style.display = 'none'
          if (this.lpaSuggestionsContainer) this.lpaSuggestionsContainer.classList.add('js-hidden')
        }
      }.bind(this))

      // Autocomplete suggestion click handler
      if (this.lpaAutocompleteSuggestions) {
        this.lpaAutocompleteSuggestions.addEventListener('click', function (e) {
          const item = e.target.closest('li[data-name]')
            if (item) {
              const name = item.getAttribute('data-name')
              if (this.lpaAutocompleteInput) this.lpaAutocompleteInput.value = name
              // Mark that a suggestion was explicitly selected
              this.lpaSelected = true
              // Ensure the main inputs are also updated so a redirect built from them contains the value
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
    // Mark this fetch with an id; only the latest fetch's response
    // will be rendered.
    //
    // This will avoid duplicate suggestions being displayed
    const fetchId = ++this._lpaFetchId

    try {
      const url = new URL('/entity/dataset-name-search.json', window.location.origin)
      url.searchParams.set('dataset', 'local-planning-authority')
      // Backend expects `search` for the query term
      url.searchParams.set('search', term)
      url.searchParams.set('limit', '10')

      const resp = await fetch(url.toString())
      if (!resp.ok) return

      const data = await resp.json()
      // Ignore responses from earlier fetches
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
    // Clear existing suggestions
    this.lpaAutocompleteSuggestions.innerHTML = ''

    // Deduplicate by name in case backend returns duplicates or
    // multiple matching rows
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
    this.lpaAutocompleteSuggestions.style.display = 'inline'
    // Ensure the parent container is visible and the list uses block layout
    if (this.lpaSuggestionsContainer) this.lpaSuggestionsContainer.classList.remove('js-hidden')
    this.lpaAutocompleteSuggestions.style.display = 'block'
  }

  // Debounce helper
  debounce(fn, wait) {
    let timeout
    return function (...args) {
      clearTimeout(timeout)
      timeout = setTimeout(() => fn.apply(this, args), wait)
    }
  }

  sendAnalyticsEvent(action, params) {
    if (window.gtag) {
      window.gtag('event', action, params);
    }
  }
}
