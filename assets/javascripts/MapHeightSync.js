// Keeps --dl-map-height (used by .dl-map-with-controls, see
// _controls-panel.scss, to give the map+footer construct a genuinely
// explicit height rather than one merely derived from its content) in
// sync with the combined height of the map and its footer note
// (app-c-sources-panel). The footer's rendered height is dynamic - its
// text wraps to a different number of lines depending on the available
// width - so a single value computed once server-side can't capture it;
// it's measured directly and kept in sync here instead.
export default class MapHeightSync {
  constructor() {
    this.container = document.querySelector('.dl-map-with-controls');
    this.mapWrapper = this.container ? this.container.querySelector('.dl-map__wrapper') : null;
    this.sourcesPanel = this.container ? this.container.querySelector('.app-c-sources-panel') : null;

    if (!this.container || !this.mapWrapper) return;

    // Both the map wrapper's and footer's heights are already stable as
    // soon as CSS has applied - no need to wait for the map's own async
    // load event, which only affects tile rendering, not layout.
    this.sync = this.sync.bind(this);
    window.addEventListener('resize', this.debounce(this.sync, 150));
    this.sync();
  }

  // Measures from the top of the map wrapper to the bottom of the
  // footer directly, rather than adding the two elements' own heights
  // together - that's automatically correct regardless of any gap or
  // margin between them.
  sync() {
    const wrapperRect = this.mapWrapper.getBoundingClientRect();
    const footerBottom = this.sourcesPanel
      ? this.sourcesPanel.getBoundingClientRect().bottom
      : wrapperRect.bottom;

    const height = footerBottom - wrapperRect.top;
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
