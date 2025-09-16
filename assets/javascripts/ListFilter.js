import { convertNodeListToArray } from './utils.js';

export class ListFilter{
    constructor($form) {
        if(!$form){
          throw new Error('ListFilter requires a form element');
        }
        this.$form = $form;
        this.filterTimeout = null;
        this.$noMatches = document.querySelector('.dl-list-filter__no-filter-match');
        this.init();
    }

    init(params){
        this.setupOptions(params);
        const $form = this.$form;
        // Form should only appear if the JS is working
        $form.classList.add('list-filter__form--active');
        // We don't want the form to submit/refresh the page on enter key
        $form.addEventListener('submit', function () { return false });

        const $input = $form.querySelector('input');
        const boundFilterViaTimeout = this.filterViaTimeout.bind(this);
        $input.addEventListener('input', boundFilterViaTimeout);

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
        itemsToFilter
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
        item.classList.remove('js-hidden');
        var searchTermRegexp = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
        if (searchTermRegexp.exec(contentToMatchOn) !== null) {
          return true
        }
        return false
    }

    updateListCounts(lists, searchTerm = ''){
        var totalMatches = 0;
        const list_section_selector = this.list_section_selector;
        const count_wrapper_selector = this.count_wrapper_selector;

        lists.forEach(function (list) {
          var matchingCount = list.querySelectorAll('[data-filter="item"]:not(.js-hidden)').length;
          var listSection = list.closest(list_section_selector);
          var countWrapper = listSection.querySelector(count_wrapper_selector);
          var listCount = countWrapper.querySelector('.js-list-filter__count');
          var accessibleListCount = countWrapper.querySelector('.js-accessible-list-filter__count');

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
}
