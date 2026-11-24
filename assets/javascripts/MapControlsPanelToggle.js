/**
 * Collapses the "Find an area" / "Select a data layer" overlay panel
 * horizontally into a small tab, similar to Google Maps. Desktop only -
 * the toggle button is hidden on mobile, where this class still runs but
 * has nothing reachable to do.
 */

import { debounce } from './utils.js';

export default class MapControlsPanelToggle {
  constructor() {
    this.panel = document.getElementById('dl-map-controls-panel');
    this.content = document.getElementById('dl-map-controls-panel-content');
    this.button = document.getElementById('dl-map-controls-panel-toggle');

    if (!this.panel || !this.content || !this.button) return;

    this.labelText = this.button.querySelector('.dl-map-controls-panel__toggle-text');

    this.container = this.panel.closest('.dl-map-with-controls');
    this.mapWrapper = this.container ? this.container.querySelector('.dl-map__wrapper') : null;
    this.sourcesPanel = this.container ? this.container.querySelector('.app-c-sources-panel') : null;

    this.button.addEventListener('click', this.toggle.bind(this));

    this.syncContainerHeight = this.syncContainerHeight.bind(this);
    window.addEventListener('resize', debounce(this.syncContainerHeight, 150));
    this.syncContainerHeight();
  }

  toggle() {
    const collapsed = !this.panel.classList.contains('dl-map-controls-panel--collapsed');
    this.setCollapsed(collapsed);
  }

  setCollapsed(collapsed) {
    this.panel.classList.toggle('dl-map-controls-panel--collapsed', collapsed);
    this.button.classList.toggle('dl-map-controls-panel__toggle--collapsed', collapsed);
    this.button.setAttribute('aria-expanded', (!collapsed).toString());

    if (collapsed) {
      this.content.setAttribute('hidden', '');
    } else {
      this.content.removeAttribute('hidden');
    }

    if (this.labelText) {
      this.labelText.textContent = collapsed ? 'Show map controls' : 'Hide map controls';
    }

    // Re-measure once the width transition has finished, not mid-animation.
    window.setTimeout(this.syncContainerHeight, 250);
  }

  /**
   * Sets --dl-map-height to span from the map wrapper's top to the
   * footer's bottom, so the panel caps to the map and footer combined.
   */
  syncContainerHeight() {
    if (!this.container || !this.mapWrapper) return;

    const wrapperRect = this.mapWrapper.getBoundingClientRect();
    const footerBottom = this.sourcesPanel
      ? this.sourcesPanel.getBoundingClientRect().bottom
      : wrapperRect.bottom;

    const height = footerBottom - wrapperRect.top;
    if (height > 0) {
      this.container.style.setProperty('--dl-map-height', height + 'px');
    }
  }
}
