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

    this.button.addEventListener('click', this.toggle.bind(this));
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
  }
}
