// "Advanced settings" (just "Show historical data" today) is a separate
// accordion section from "Select a data layer" - deliberately kept that
// way in the markup, but its heading/toggle is hidden on every
// breakpoint (_controls-panel.scss) and it's always expanded, with no
// way to close it on its own - which reads oddly once the user closes
// "Select a data layer" itself, since a setting for data layers stays
// visibly open with nothing selected. This makes "Advanced settings"
// follow "Select a data layer"'s own open/closed state instead.
export default class AdvancedSettingsSync {
  constructor() {
    const accordion = document.getElementById('dl-map-controls-accordion');
    if (!accordion) return;

    // [0] Find an area, [1] Select a data layer, [2] Advanced settings -
    // relying on the fixed section order/count rather than exact ids,
    // which govuk-frontend's own JS moves around (see LayerControls.js's
    // notes on this elsewhere).
    const sections = Array.from(accordion.children).filter((el) =>
      el.classList.contains('govuk-accordion__section')
    );

    this.dataLayerButton = sections[1] && sections[1].querySelector('.govuk-accordion__section-button');
    this.settingsButton = sections[2] && sections[2].querySelector('.govuk-accordion__section-button');
    // govuk-frontend's own Accordion listens for clicks on this header
    // div (accordion.mjs's $header), not the button itself - a click on
    // the button bubbles up through this element, so a listener attached
    // directly to the button instead would fire *before* govuk-frontend's
    // own handler updates aria-expanded, always reading the stale value.
    const dataLayerHeader = sections[1] && sections[1].querySelector('.govuk-accordion__section-header');

    if (!this.dataLayerButton || !this.settingsButton || !dataLayerHeader) return;

    this.sync = this.sync.bind(this);
    dataLayerHeader.addEventListener('click', this.sync);

    // Also covers page load itself - govuk-frontend's Accordion persists
    // each section's expanded state independently across page loads
    // (sessionStorage), so the two could disagree from a previous visit
    // even before either is clicked this time.
    this.sync();
  }

  sync() {
    const dataLayerExpanded = this.dataLayerButton.getAttribute('aria-expanded') === 'true';
    const settingsExpanded = this.settingsButton.getAttribute('aria-expanded') === 'true';

    // Click rather than set attributes/classes directly, so govuk-
    // frontend's own Accordion handles content visibility/sessionStorage
    // exactly as it would for a real user click - only actually clicking
    // when the states genuinely differ, to avoid re-triggering this same
    // listener pointlessly (govuk's own click handler on this same
    // button doesn't call back into here, so there's no risk of a loop,
    // but there's no reason to dispatch a click at all when unneeded).
    if (dataLayerExpanded !== settingsExpanded) {
      this.settingsButton.click();
    }
  }
}
