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
    this.applyFiltersButton = document.getElementById('dl-map-apply-filters-button');

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

    // Mobile-only "Apply filters" button (hidden entirely on desktop via
    // CSS) - everything in the panel already applies live as it's
    // changed, so this doesn't apply anything itself, it just closes the
    // overlay once the user's happy with their selection. Always a plain
    // collapse, never a toggle - it only makes sense while the panel is
    // already open (it isn't visible otherwise).
    if (this.applyFiltersButton) {
      this.applyFiltersButton.addEventListener('click', () => this.setCollapsed(true));
    }

    this.syncContainerHeight = this.syncContainerHeight.bind(this);
    window.addEventListener('resize', this.debounce(this.syncContainerHeight, 150));
    // Both the map wrapper's and footer's heights are already stable as
    // soon as CSS has applied - no need to wait for the map's own async
    // load event, which only affects tile rendering, not layout.
    this.syncContainerHeight();

    // On mobile, the panel slides down from the top instead of in from
    // the left (see _controls-panel.scss), content-hugging up to its own
    // max-height cap rather than being fixed to the map's height - so
    // its bottom edge (where the collapse tab sits) moves not only when
    // the whole panel is toggled, but whenever an individual accordion
    // section inside it opens or closes too. A ResizeObserver catches
    // every one of those cases generically, rather than having to hook
    // each possible cause individually. Harmless on desktop - nothing
    // there reads --dl-panel-height, since that toggle is positioned by
    // width, not height.
    if (this.container && typeof ResizeObserver !== 'undefined') {
      this.panelResizeObserver = new ResizeObserver(() => {
        this.container.style.setProperty('--dl-panel-height', this.panel.getBoundingClientRect().height + 'px');
      });
      this.panelResizeObserver.observe(this.panel);
    }
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

    const wrapperRect = this.mapWrapper.getBoundingClientRect();
    const footerBottom = this.sourcesPanel
      ? this.sourcesPanel.getBoundingClientRect().bottom
      : wrapperRect.bottom;

    const height = footerBottom - wrapperRect.top;
    if (height > 0) {
      this.container.style.setProperty('--dl-map-height', height + 'px');
    }

    // The map canvas's own height specifically, not map+footer combined -
    // used by the mobile panel's max-height cap (_controls-panel.scss),
    // which needs to leave part of the *map* visible below it. The
    // footer's own height is highly variable on narrow viewports (its
    // text can wrap across several more lines there than on desktop), so
    // --dl-map-height alone would make that cap leave room for whatever
    // mix of map-and-footer-overflow happened to be tallest that time,
    // not reliably "some of the map".
    if (wrapperRect.height > 0) {
      this.container.style.setProperty('--dl-wrapper-height', wrapperRect.height + 'px');
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
