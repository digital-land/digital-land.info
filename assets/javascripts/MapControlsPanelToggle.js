// Lets the whole "Find an area" / "Select a data layer" overlay panel be
// collapsed horizontally into a small tab (similar to Google Maps), rather
// than only collapsing individual accordion sections. Independent of
// LayerControls.js/the accordion itself - this only ever hides/shows the
// panel's content wrapper, it doesn't know or care what's inside it.
export default class MapControlsPanelToggle {
  constructor() {
    this.panel = document.getElementById('dl-map-controls-panel');
    this.content = document.getElementById('dl-map-controls-panel-content');
    this.button = document.getElementById('dl-map-controls-panel-toggle');

    if (!this.panel || !this.content || !this.button) return;

    this.labelText = this.button.querySelector('.dl-map-controls-panel__toggle-text');

    // The panel should stretch/cap to the map *and its footer* combined
    // (see _controls-panel.scss's --dl-map-height), not just the map's
    // own height - the footer (app-c-sources-panel) is meant to read as
    // sitting inside the same bordered box, with the panel's own bottom
    // edge landing level with the footer's, not the map's. The footer's
    // rendered height is dynamic (its text can wrap to a different
    // number of lines depending on how much width it has - which itself
    // changes when the panel opens/closes, see the margin-left toggle
    // below), so this can't be a single static value computed once
    // server-side - it's measured and kept in sync here instead.
    this.container = this.panel.closest('.dl-map-with-controls');
    this.mapWrapper = this.container ? this.container.querySelector('.dl-map__wrapper') : null;
    this.sourcesPanel = this.container ? this.container.querySelector('.app-c-sources-panel') : null;

    this.button.addEventListener('click', this.toggle.bind(this));

    this.syncContainerHeight = this.syncContainerHeight.bind(this);
    window.addEventListener('resize', this.debounce(this.syncContainerHeight, 150));
    // Both the map wrapper's and footer's heights are already stable as
    // soon as CSS has applied - no need to wait for the map's own async
    // load event, which only affects tile rendering, not layout.
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

    // Collapsing/expanding changes the footer's available width, which
    // can change how many lines its text wraps to (and so its height) -
    // re-measure once the width transition has actually finished,
    // rather than mid-animation.
    window.setTimeout(this.syncContainerHeight, 250);
  }

  // Measures from the top of the map wrapper to the bottom of the footer
  // directly, rather than adding the two elements' own heights together -
  // that's automatically correct regardless of any gap/margin between
  // them, and is unaffected by whatever --dl-map-height currently is:
  // the footer's own position in normal document flow depends only on
  // the map wrapper's real height and its own content, never on the
  // container's declared height (overflow only affects how far content
  // visually spills past the container's border, not where it's laid
  // out) - so there's no risk of this feeding back into itself.
  syncContainerHeight() {
    if (!this.container || !this.mapWrapper) return;

    const wrapperTop = this.mapWrapper.getBoundingClientRect().top;
    const footerBottom = this.sourcesPanel
      ? this.sourcesPanel.getBoundingClientRect().bottom
      : this.mapWrapper.getBoundingClientRect().bottom;

    const height = footerBottom - wrapperTop;
    if (height > 0) {
      this.container.style.setProperty('--dl-map-height', height + 'px');
    }
  }

  debounce(fn, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), wait);
    };
  }
}
