// On desktop, "Select a data layer"'s dataset checkbox list has a fixed
// 220px height (see _controls-panel.scss) sized to fit alongside "Find
// an area"'s own content when both are open - the panel's overall
// height is capped to the map's (round 27), so there's a genuine
// ceiling on how much room is available. But once "Find an area" (or
// "Select a data layer" itself, momentarily) is collapsed, that ceiling
// relaxes - there's real spare room in the panel the list could use
// instead of staying stuck at 220px with its own scrollbar while the
// rest of the panel sits empty below it.
//
// This grows the list to fill whatever space is actually available,
// capped at however tall its own content genuinely needs to be (so a
// short list of datasets doesn't get stretched into a mostly-empty
// box), and never shrinks it below the original 220px design height.
export default class AdaptiveLayerListHeight {
  constructor() {
    this.layerList = document.getElementById('layer-toggles-list');
    this.panelContent = document.getElementById('dl-map-controls-panel-content');
    this.filterInput = document.getElementById('layer-filter-input');
    this.accordion = document.getElementById('dl-map-controls-accordion');
    this.notePanel = document.getElementById('dl-data-coverage-banner');

    if (!this.layerList || !this.panelContent || !this.accordion) return;

    // Only on desktop/tablet+ - mobile's panel doesn't have this kind of
    // spare room to give away (see _controls-panel.scss's own mobile
    // block, a content-hugging height capped well short of the map's
    // full height), so the list just keeps its plain CSS-declared
    // height there.
    this.desktopQuery = window.matchMedia('(min-width: 40.0625em)');

    this.update = this.update.bind(this);

    // [0] Find an area, [1] Select a data layer - both affect how much
    // room is left for the list: the first by taking up its own space
    // whenever it's open, the second by hiding the list entirely while
    // it's closed, which could otherwise leave a stale measurement from
    // before it was hidden. govuk-frontend's own Accordion listens for
    // clicks on this header element (not the button itself), and this
    // listener - registered afterwards - runs once that toggle has
    // already happened, so the measurement below sees the new state.
    const sections = Array.from(this.accordion.children).filter((el) =>
      el.classList.contains('govuk-accordion__section')
    );
    sections.slice(0, 2).forEach((section) => {
      const header = section.querySelector('.govuk-accordion__section-header');
      if (header) header.addEventListener('click', this.update);
    });

    if (this.filterInput) this.filterInput.addEventListener('input', this.update);
    window.addEventListener('resize', this.debounce(this.update, 150));
    this.desktopQuery.addEventListener('change', this.update);

    this.update();
  }

  update() {
    if (!this.desktopQuery.matches) {
      // Falls back to the plain CSS-declared 220px on mobile.
      this.layerList.style.height = '';
      return;
    }

    const availableHeight = this.panelContent.clientHeight;
    const naturalHeight = this.layerList.scrollHeight;
    // The height of everything else in the panel, measured as an actual
    // rendered span (contentTop to contentBottom) rather than summed from
    // individual elements' offsetHeight - offsetHeight doesn't include
    // margins, and govuk-frontend's own .govuk-accordion carries a real
    // 30px margin-bottom (its default spacing below the last section)
    // that a plain "accordion height + note height" sum silently missed,
    // consistently overshooting the target by that much and forcing a
    // scrollbar. Measuring the genuine top/bottom edges of the content
    // sidesteps needing to know about every individual margin/padding
    // rule involved. Deliberately NOT panelContent.scrollHeight for this
    // either - that container has a fixed height (100% of the panel)
    // with overflow-y: auto, and an overflowing scroll container's
    // scrollHeight is floored at its own clientHeight, so it can never
    // report less than the space already available.
    const contentTop = this.panelContent.getBoundingClientRect().top;
    const bottomAnchor = this.notePanel || this.accordion;
    const contentBottom = bottomAnchor.getBoundingClientRect().bottom;
    const othersHeight = contentBottom - contentTop - this.layerList.offsetHeight;
    const maxAvailableForList = availableHeight - othersHeight;

    const target = Math.max(220, Math.min(naturalHeight, maxAvailableForList));

    this.layerList.style.height = target + 'px';
  }

  debounce(fn, wait) {
    let timeout;
    return function (...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), wait);
    };
  }
}
