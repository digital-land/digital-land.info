/**
 * "Advanced settings" is a separate accordion section from "Select a data
 * layer" with its own heading/toggle hidden and always expanded, which
 * reads oddly once "Select a data layer" itself is closed. This makes
 * "Advanced settings" follow "Select a data layer"'s open/closed state.
 */
export default class AdvancedSettingsSync {
  constructor() {
    const accordion = document.getElementById('dl-map-controls-accordion');
    if (!accordion) return;

    const { dataLayerButton, settingsButton, dataLayerHeader } = this.findAccordionElements(accordion);
    if (!dataLayerButton || !settingsButton || !dataLayerHeader) return;

    this.dataLayerButton = dataLayerButton;
    this.settingsButton = settingsButton;

    this.sync = this.sync.bind(this);
    dataLayerHeader.addEventListener('click', this.sync);

    // Also covers page load - the accordion persists each section's
    // expanded state independently across visits, so the two could
    // already disagree before either is clicked this time.
    this.sync();
  }

  /**
   * Relies on the fixed section order/count (0: Find an area, 1: Select
   * a data layer, 2: Advanced settings) rather than exact ids, which the
   * accordion's own JS moves around. Listens on the header div, not the
   * button - the accordion's click handler is also on the header and must
   * run first to update aria-expanded, or this would read a stale value.
   */
  findAccordionElements(accordion) {
    const sections = Array.from(accordion.children).filter((el) =>
      el.classList.contains('govuk-accordion__section')
    );

    return {
      dataLayerButton: sections[1] && sections[1].querySelector('.govuk-accordion__section-button'),
      settingsButton: sections[2] && sections[2].querySelector('.govuk-accordion__section-button'),
      dataLayerHeader: sections[1] && sections[1].querySelector('.govuk-accordion__section-header'),
    };
  }

  sync() {
    const dataLayerExpanded = this.dataLayerButton.getAttribute('aria-expanded') === 'true';
    const settingsExpanded = this.settingsButton.getAttribute('aria-expanded') === 'true';

    // Clicking (rather than setting attributes/classes directly) lets the
    // accordion handle visibility/persistence exactly as a real click
    // would; only done when the states actually differ.
    if (dataLayerExpanded !== settingsExpanded) {
      this.settingsButton.click();
    }
  }
}
