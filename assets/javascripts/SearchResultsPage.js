class SearchResultsPage {
  constructor(formElements) {
    this.forms = (formElements || []).filter(Boolean);
    this.resultsSection = document.getElementById('search-results');

    if (this.forms.length) this.initFormListener();
  }

  initFormListener() {
    this.forms.forEach(form => {
      this.addSubmitListener(form);
    })
  }

  addSubmitListener(form) {
    form.addEventListener('submit', function (e) {
      // Respect validation; show messages if invalid
      const formEl = e.currentTarget;
      if (formEl.reportValidity && !formEl.reportValidity()) {
        return;
      }

      e.preventDefault();
      try {
        this.disableForms();
        if (this.resultsSection) {
          this.resultsSection.classList.add('app-search--loading');
          this.resultsSection.setAttribute('aria-busy', 'true');
        }
      } finally {
        HTMLFormElement.prototype.submit.call(formEl);
      }
    }.bind(this))
  }

  disableForms() {
    this.forms.forEach(form => {
      const submitButton = form.querySelector('[type="submit"]');

      form.classList.add('app-search--loading');
      form.setAttribute('aria-disabled', 'true');

      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Searching...';
      }
    });
  }
}
