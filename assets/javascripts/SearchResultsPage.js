class SearchResultsPage {
  constructor(formElements) {
    this.forms = formElements;
    this.resultsSection = document.getElementById('search-results');

    this.initFormListener();
  }

  initFormListener() {
    this.forms.forEach(form => {
      this.addSubmitListener(form);
    })
  }

  addSubmitListener(form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      try {
        // Defensive UI updates; avoid throwing if elements are missing
        this.disableForms();

        if (this.resultsSection) {
          this.resultsSection.classList.add('app-search--loading');
        }
      } finally {
        // Always submit even if UI updates throw
        HTMLFormElement.prototype.submit.call(e.currentTarget);
      }
    }.bind(this))
  }

  disableForms() {
    this.forms.forEach(form => {
      form.classList.add('app-search--loading');
      const submitButton = form.querySelector('[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Searching...';
      }
    });
  }
}
