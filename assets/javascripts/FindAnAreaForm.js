class FindAnAreaForm {
  constructor(searchResult) {
    this.searchResult = searchResult;
    this.form = document.querySelector('#dl-find-an-area-form')

    this.initFormListener()
    this.flyToSearchResult()
  }

  flyToSearchResult() {
      setTimeout(() => {
        if (this.searchResult && this.searchResult.geometry && window.mapControllers.map) {
          window.mapControllers.map.addPoint(searchResult.geometry)
          window.mapControllers.map.flyTo(searchResult.geometry)
        }
      }, 1000)
  }

  initFormListener() {
    this.form.addEventListener('submit', function (e) {
      e.preventDefault()

      const input = this.form.querySelector('input[name="q"]')
      const url = new URL(window.location.href)
      const params = new URLSearchParams(url.search)

      // Update or append the 'q' parameter from the form input
      params.set('q', input.value);

      // Build final query string
      const queryString = params.toString();

      // Redirect with merged query parameters
      window.location.href = `${url.pathname}?${queryString}`;
    }.bind(this));
  }
}
