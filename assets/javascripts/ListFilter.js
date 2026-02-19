import { convertNodeListToArray } from './utils.js';

export class ListFilter{
    constructor($form) {
        if(!$form){
          throw new Error('ListFilter requires a form element');
        }
        this.$form = $form;
        this.filterTimeout = null;
        this.$noMatches = document.querySelector('.dl-list-filter__no-filter-match');
        this.$booleanFilterCheckbox = null;
        this.booleanFilterConfig = null;
        this.init();
    }

    init(params){
        this.setupOptions(params);
        const $form = this.$form;
        // Form should only appear if the JS is working
        $form.classList.add('list-filter__form--active');
        // We don't want the form to submit/refresh the page on enter key
        $form.addEventListener('submit', function () { return false });

        const $input = $form.querySelector('input[type="text"]');
        const boundFilterViaTimeout = this.filterViaTimeout.bind(this);
        $input.addEventListener('input', boundFilterViaTimeout);

        // Set up boolean filter if configured
        this.setupBooleanFilter();

        // make sure no matches message is initially hidden
        this.$noMatches.classList.add('js-hidden');
    }

    filterViaTimeout(e){
        clearTimeout(this.filterTimeout);

        const boundListFilter = this.filterListItems.bind(this);
        this.filterTimeout = setTimeout(function () {
          boundListFilter(e);
        }, 200);
    }

    filterListItems(e){
        const itemsToFilter = convertNodeListToArray(document.querySelectorAll('[data-filter="item"]'));
        const listsToFilter = convertNodeListToArray(document.querySelectorAll('[data-filter="list"]'));
        const searchTerm = e.target.value;

        const boundMatchSearchTerm = this.matchSearchTerm.bind(this);

        // Only filter items not already hidden by boolean filter
        itemsToFilter
          .filter(function ($item) {
            // Skip items hidden by boolean filter
            return !$item._hiddenByBooleanFilter;
          })
          .filter(function ($item) {
            return !boundMatchSearchTerm($item, searchTerm)
          })
          .forEach(function (item) {
            item.classList.add('js-hidden');
          });

        this.updateListCounts(listsToFilter, searchTerm);
    }

    termToMatchOn(item){
        const toConsider = item.querySelectorAll('[data-filter="match-content"]');
        if (toConsider.length) {
          const toConsiderArr = convertNodeListToArray(toConsider);
          const toConsiderStrs = toConsiderArr.map(function (el) {
            return el.textContent
          });
          return toConsiderStrs.join(';')
        }
        return item.querySelector('a').textContent
    }

    matchSearchTerm(item, term){
        // const itemLabels = item.dataset.filterItemLabels
        const contentToMatchOn = this.termToMatchOn(item);
        // Only remove js-hidden if item is not hidden by boolean filter
        if (!item._hiddenByBooleanFilter) {
            item.classList.remove('js-hidden');
        }
        var searchTermRegexp = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
        if (searchTermRegexp.exec(contentToMatchOn) !== null) {
          return true
        }
        return false
    }

    updateListCounts(lists, searchTerm = ''){
        let totalMatches = 0;
        const list_section_selector = this.list_section_selector;
        const count_wrapper_selector = this.count_wrapper_selector;

        lists.forEach(function (list) {
          let matchingCount = list.querySelectorAll('[data-filter="item"]:not(.js-hidden)').length;
          let listSection = list.closest(list_section_selector);
          let countWrapper = listSection.querySelector(count_wrapper_selector);
          let listCount = countWrapper.querySelector('.js-list-filter__count');
          let accessibleListCount = countWrapper.querySelector('.js-accessible-list-filter__count');

          // show/hide sections with matching items
          if (matchingCount > 0) {
            listSection.classList.remove('js-hidden');
            listCount.textContent = matchingCount;
            accessibleListCount.textContent = matchingCount;
          } else {
            listSection.classList.add('js-hidden');
          }

          totalMatches += matchingCount;
        });

        // if no results show message
        if (this.$noMatches) {
          const $searchTermDisplay = this.$noMatches.querySelector('.js-search-term-display');
          if (totalMatches === 0) {
            this.$noMatches.classList.remove('js-hidden');
            // Update the search term display
            if ($searchTermDisplay && searchTerm.trim()) {
              $searchTermDisplay.textContent = `'${searchTerm}'`;
            } else if ($searchTermDisplay) {
              $searchTermDisplay.textContent = '';
            }
          } else {
            this.$noMatches.classList.add('js-hidden');
          }
        }
    }

    setupOptions(params){
        params = params || {};
        this.list_section_selector = params.list_section_selector || '.dl-list-filter__count';
        this.count_wrapper_selector = params.count_wrapper_selector || '.dl-list-filter__count__wrapper';
    }

    setupBooleanFilter(){
        const $form = this.$form;
        const booleanAttribute = $form.dataset.booleanFilterAttribute;
        const booleanValue = $form.dataset.booleanFilterValue;
        const booleanDefault = $form.dataset.booleanFilterDefault;

        // If no boolean filter config, skip setup
        if (!booleanAttribute || !booleanValue) {
            return;
        }

        // Find checkbox with data-filter="boolean-input"
        this.$booleanFilterCheckbox = $form.querySelector('input[data-filter="boolean-input"]');

        if (!this.$booleanFilterCheckbox) {
            console.warn('Boolean filter configured but no checkbox found with data-filter="boolean-input"');
            return;
        }

        // Store configuration
        this.booleanFilterConfig = {
            attribute: booleanAttribute,
            value: booleanValue,
            defaultEnabled: booleanDefault === 'true'
        };

        // Set initial checkbox state
        this.$booleanFilterCheckbox.checked = this.booleanFilterConfig.defaultEnabled;

        // Apply initial filter if default is enabled
        if (this.booleanFilterConfig.defaultEnabled) {
            this.applyBooleanFilter();
            // Update counts after applying initial filter
            const listsToFilter = convertNodeListToArray(document.querySelectorAll('[data-filter="list"]'));
            this.updateListCounts(listsToFilter);
        }

        // Add change event listener
        const boundApplyAllFilters = this.applyAllFilters.bind(this);
        this.$booleanFilterCheckbox.addEventListener('change', boundApplyAllFilters);
    }

    applyBooleanFilter(){
        // If no boolean filter configured, skip
        if (!this.booleanFilterConfig || !this.$booleanFilterCheckbox) {
            return;
        }

        const itemsToFilter = convertNodeListToArray(document.querySelectorAll('[data-filter="item"]'));
        const isChecked = this.$booleanFilterCheckbox.checked;
        const config = this.booleanFilterConfig;

        itemsToFilter.forEach(function(item) {
            if (isChecked) {
                // Get the attribute value (case-insensitive comparison)
                const itemValue = item.getAttribute(config.attribute);
                if (itemValue && itemValue.toLowerCase() === config.value.toLowerCase()) {
                    item.classList.add('js-hidden');
                    item._hiddenByBooleanFilter = true;
                } else {
                    // Clear the flag if item doesn't match
                    delete item._hiddenByBooleanFilter;
                }
            } else {
                // When unchecked, remove js-hidden if it was added by boolean filter
                if (item._hiddenByBooleanFilter) {
                    item.classList.remove('js-hidden');
                    delete item._hiddenByBooleanFilter;
                }
            }
        });
    }

    applyAllFilters(){
        // Apply boolean filter first
        this.applyBooleanFilter();

        // Then apply text filter (if there's a search term)
        const $form = this.$form;
        const $input = $form.querySelector('input[type="text"]');
        if ($input && $input.value) {
            this.filterListItems({ target: $input });
        } else {
            // If no search term, just update counts
            const listsToFilter = convertNodeListToArray(document.querySelectorAll('[data-filter="list"]'));
            this.updateListCounts(listsToFilter);
        }
    }
}
