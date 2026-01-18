class FindAnAreaForm {
  constructor(searchResult) {
    this.searchResult = searchResult;
    this.form = document.querySelector('#dl-find-an-area-form')
    this.selectMethod = this.form ? this.form.querySelector('#select-method') : null

    this.postcodeUPRNContainer = this.form ? this.form.querySelector('#postcode-uprn-container') : null
    this.postcodeUPRNInput = this.form ? this.form.querySelector('#postcode-uprn-input') : null

    this.lpaContainer = this.form ? this.form.querySelector('#lpa-container') : null
    this.lpaAutocompleteInput = this.form ? this.form.querySelector('#lpa-autocomplete-input') : null
    this.lpaAutocompleteSuggestions = this.form ? this.form.querySelector('#lpa-autocomplete-suggestions') : null

    this.submitButton = this.form ? this.form.querySelector('#find-an-area-submit') : null

    // ID to track latest fetch so we can ignore out-of-order responses
    this._lpaFetchId = 0

    // If a type parameter is present in the URL, set the select to that value
    try {
      const params = new URLSearchParams(window.location.search)
      const sortVal = params.get('type')
      if (sortVal && this.selectMethod) {
        this.selectMethod.value = sortVal
      }
    } catch (e) {
      // Ignore URL parsing errors in older browsers
    }

    this.initFormListener()
    this.bindSelectListener()
    this.updateControlsVisibility()
    this.flyToSearchResult()
  }

  flyToSearchResult() {
      setTimeout(() => {
        if (this.searchResult && this.searchResult.geometry && window.mapControllers.map) {
          // Don't add the geometry again - it's already added
          // via geojsons param in map initialization
          window.mapControllers.map.flyTo(searchResult.geometry)
        }
      }, 1000)
  }

  initFormListener() {
    this.form.addEventListener('submit', function (e) {
      e.preventDefault()
      const input = this.postcodeUPRNInput
      const url = new URL(window.location.href)
      const params = new URLSearchParams(url.search)

      // Update or append the 'q' parameter from the form input
      params.set('q', input.value);
      // Ensure the selected type option is preserved in the URL
      if (this.selectMethod) {
        params.set('type', this.selectMethod.value);
      }

      // Build final query string
      const queryString = params.toString();

      this.sendAnalyticsEvent('search_term', {
        'event_category': 'Search',
        'event_label': 'Find an area form',
        'value': input.value
      });

      // Redirect with merged query parameters
      window.location.href = `${url.pathname}?${queryString}`;
    }.bind(this));
  }

  bindSelectListener() {
    if (!this.selectMethod) return

    // Clear inputs and autocomplete suggestions,
    // toggle between input visibility,
    // when the select method changes
    this.selectMethod.addEventListener('change', function (e) {
      try {
        if (this.postcodeUPRNInput) this.postcodeUPRNInput.value = ''
        if (this.lpaAutocompleteInput) this.lpaAutocompleteInput.value = ''
        if (this.lpaAutocompleteSuggestions) {
          this.lpaAutocompleteSuggestions.style.display = 'none'
          this.lpaAutocompleteSuggestions.innerHTML = ''
        }
      } catch (err) {
        // Ignore URL parsing errors in older browsers
      }
      this.updateControlsVisibility()
    }.bind(this))

    // If LPA input, bind autocomplete behaviour
    if (this.lpaAutocompleteInput) {
      const doFetch = this.debounce(this.fetchLpaSuggestions.bind(this), 250)
      this.lpaAutocompleteInput.addEventListener('input', function (e) {
        const val = e.target.value
        if (val && val.length > 1 && this.selectMethod && this.selectMethod.value === 'lpa') {
          doFetch(val)
        } else if (this.lpaAutocompleteSuggestions) {
          this.lpaAutocompleteSuggestions.style.display = 'none'
        }
      }.bind(this))

      // Autocomplete suggestion click handler
      if (this.lpaAutocompleteSuggestions) {
        this.lpaAutocompleteSuggestions.addEventListener('click', function (e) {
          const item = e.target.closest('li[data-name]')
          if (item) {
            const name = item.getAttribute('data-name')
            if (this.lpaAutocompleteInput) this.lpaAutocompleteInput.value = name
            // Ensure the main input (non-lpa-search) is updated too
            if (this.postcodeUPRNInput) this.postcodeUPRNInput.value = name
            this.lpaAutocompleteSuggestions.style.display = 'none'
          }
        }.bind(this))
      }
    }
  }

  updateControlsVisibility() {
    // Toggle input visibility

    const val = this.selectMethod ? this.selectMethod.value : ''
    const visible = val === 'postcode' || val === 'uprn'
    const lpaVisible = val === 'lpa'

    // Postcode or UPRN options are selected then LPA
    // input field will be hidden
    if (this.postcodeUPRNContainer) {
      if (visible) {
        this.postcodeUPRNContainer.classList.remove('js-hidden')
        this.postcodeUPRNContainer.setAttribute('aria-hidden', 'false')
      } else {
        this.postcodeUPRNContainer.classList.add('js-hidden')
        this.postcodeUPRNContainer.setAttribute('aria-hidden', 'true')
      }
    }

    // LPA input field is hidden if Postcode or UPRN options
    // are selected and vice-versa
    if (this.lpaContainer) {
      if (lpaVisible) {
        this.lpaContainer.classList.remove('js-hidden')
        this.lpaContainer.setAttribute('aria-hidden', 'false')
        if (this.lpaAutocompleteSuggestions) this.lpaAutocompleteSuggestions.style.display = 'none'
      } else {
        this.lpaContainer.classList.add('js-hidden')
        this.lpaContainer.setAttribute('aria-hidden', 'true')
      }
    }

    // Enable/disable appropriate inputs
    if (this.postcodeUPRNInput) this.postcodeUPRNInput.disabled = !visible
    if (this.lpaAutocompleteInput) this.lpaAutocompleteInput.disabled = !lpaVisible
    if (this.submitButton) this.submitButton.disabled = !(visible || lpaVisible)
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
      // Backend expects `q` for the query term
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
