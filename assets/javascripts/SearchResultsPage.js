class SearchResultsPage {
  constructor(formElements, paginationElements) {
    this.forms = (formElements || []).filter(Boolean);
    this.paginationLinks = (paginationElements || []).filter(Boolean);
    this.resultsSection = document.getElementById('search-results');

    if (this.forms.length) this.initFormListener();
    if (this.paginationLinks.length) this.initPaginationListener();
  }

  initFormListener() {
    this.forms.forEach(form => {
      this.addSubmitListener(form);
    })
  }

  initPaginationListener() {
    this.paginationLinks.forEach(link => {
      this.addPaginationListener(link);
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
        this.disableInteractiveElements();
      } finally {
        HTMLFormElement.prototype.submit.call(formEl);
      }
    }.bind(this))
  }

  addPaginationListener(link) {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      try {
        this.disableInteractiveElements();
      } finally {
        window.location = link.href;
      }
    }.bind(this))
  }

  disableInteractiveElements() {
    this.disableForms();
    this.disableResultSection();
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

  disableResultSection() {
    if (this.resultsSection) {
      this.resultsSection.classList.add('app-search--loading');
      this.resultsSection.setAttribute('aria-busy', 'true');
    }
  }
}
