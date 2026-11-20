/**
 * Grows "Select a data layer"'s dataset checkbox list to fill whatever
 * spare room is available in the panel (e.g. once "Find an area" is
 * collapsed), capped at the list's own natural content height, and never
 * shrinking below its 220px design height. Desktop only - mobile keeps
 * its plain CSS-declared height.
 */

import { debounce } from './utils.js';

export default class AdaptiveLayerListHeight {
  constructor() {
    this.layerList = document.getElementById('layer-toggles-list');
    this.panelContent = document.getElementById('dl-map-controls-panel-content');
    this.filterInput = document.getElementById('layer-filter-input');
    this.accordion = document.getElementById('dl-map-controls-accordion');
    this.notePanel = document.getElementById('dl-data-coverage-banner');

    if (!this.layerList || !this.panelContent || !this.accordion) return;

    this.desktopQuery = window.matchMedia('(min-width: 40.0625em)');

    this.update = this.update.bind(this);

    this.watchSectionsAffectingAvailableSpace();

    if (this.filterInput) this.filterInput.addEventListener('input', this.update);
    this.layerList.addEventListener('change', this.update);
    window.addEventListener('resize', debounce(this.update, 150));
    this.desktopQuery.addEventListener('change', this.update);

    this.update();
  }

  /**
   * Recomputes once "Find an area" or "Select a data layer" is
   * expanded/collapsed, since both change how much room is left for the
   * list. Listens on each section's header, not its button - govuk-
   * frontend's own accordion handler (also on the header) must run first
   * so the measurement sees the section's new state, not the stale one.
   */
  watchSectionsAffectingAvailableSpace() {
    const sections = Array.from(this.accordion.children).filter((el) =>
      el.classList.contains('govuk-accordion__section')
    );
    sections.slice(0, 2).forEach((section) => {
      const header = section.querySelector('.govuk-accordion__section-header');
      if (header) header.addEventListener('click', this.update);
    });
  }

  update() {
    if (!this.desktopQuery.matches) {
      this.layerList.style.height = '';
      return;
    }

    const availableHeight = this.panelContent.clientHeight;
    const naturalHeight = this.layerList.scrollHeight;

    // Measured as the actual rendered span between the panel content's
    // top and bottom edges, rather than summed from individual elements'
    // offsetHeight, which excludes margins and would overshoot the target.
    const contentTop = this.panelContent.getBoundingClientRect().top;
    const bottomAnchor = this.notePanel || this.accordion;
    const contentBottom = bottomAnchor.getBoundingClientRect().bottom;
    const othersHeight = contentBottom - contentTop - this.layerList.offsetHeight;
    const maxAvailableForList = availableHeight - othersHeight;

    const target = Math.max(220, Math.min(naturalHeight, maxAvailableForList));

    this.layerList.style.height = target + 'px';
  }
}
