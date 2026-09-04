export default class LayerControls {
    constructor (mapController, source, layers, availableLayers, options) {
      this.mapController = mapController;
      this.tileSource = source;
      this.layers = layers;
      this.availableLayers = availableLayers;

      this.layerOptions = [];

      this.layerURLParamName = options.layerURLParamName || 'dataset';
      this.redirectURLParamNames = options.redirectURLParamNames || [];

      // listen for changes to URL
      var boundSetControls = this.toggleLayersBasedOnUrl.bind(this);
      window.addEventListener('popstate', function (event) {
        boundSetControls();
      });

      this.replaceRedirectParamNames();
    }

    // Wires behaviour onto the "Select a data layer"/"Advanced settings"
    // markup rendered server-side by components/map-controls-panel/macro.jinja
    // (rather than building that markup here, as this used to).
    attach() {
      this.$layerList = document.getElementById('layer-toggles-list');
      this.$settingsPanelContent = document.getElementById('dl-map-settings-content');

      this.$settingsErrorMessage = document.createElement('p');
      this.$settingsErrorMessage.classList.add('govuk-error-message');
      this.$settingsErrorMessage.textContent = 'Select a data layer first';

      this.$historicalDataCheckbox = document.getElementById('show-historical-data');
      if (this.$historicalDataCheckbox) {
        this.$historicalDataCheckbox.addEventListener('change', this.toggleHistoricalData.bind(this));
      }

      this.$textbox = document.getElementById('layer-filter-input');
      if (this.$textbox) {
        this.$textbox.addEventListener('input', this.filterCheckboxes.bind(this));
      }

      this.$keyPanel = document.getElementById('dl-map-key-panel');
      this.$keyPanelToggle = document.getElementById('dl-map-key-panel-toggle');
      this.$keyPanelClose = document.getElementById('dl-map-key-panel-close');

      // The toggle always flips whatever the current state is (click while
      // collapsed -> expand, click while expanded -> collapse); the close
      // button only ever collapses. Either way, the next checkbox change
      // re-syncs to "expanded if anything's selected, collapsed if not" via
      // updateKeyPanel() - a manual open/close doesn't stick past that.
      if (this.$keyPanelToggle) {
        this.$keyPanelToggle.addEventListener('click', () => {
          this.setKeyPanelExpanded(!!(this.$keyPanel && this.$keyPanel.classList.contains('dl-map-key-panel--collapsed')));
        });
      }
      if (this.$keyPanelClose) {
        this.$keyPanelClose.addEventListener('click', () => this.setKeyPanelExpanded(false));
      }

      this.layerOptions = this.layers.map((layer) => {
        return new LayerOption(layer, this.availableLayers[layer.dataset], this);
      });

      // initial set up of controls (default or urlParams)
      const urlParams = (new URL(document.location)).searchParams;
      if (!urlParams.has(this.layerURLParamName)) {
        // if not set then use default checked controls
        this.updateUrl();
      } else {
        // use URL params if available
        this.toggleLayersBasedOnUrl();
      }
    }

    replaceRedirectParamNames() {
      const urlParams = (new URL(document.location)).searchParams;
      this.redirectURLParamNames.forEach(param => {
        if (urlParams.has(param)) {
          let values = urlParams.getAll(param);
          urlParams.delete(param);
          values.forEach(value => {
            urlParams.append(this.layerURLParamName, value);
          });
        }
      });
      let newURL = window.location.pathname
      if(urlParams.size > 0)
        newURL = newURL + '?' + urlParams.toString() + window.location.hash;
      window.history.replaceState({}, '', newURL);
    }

    // toggles visibility of elements/entities based on URL params
    toggleLayersBasedOnUrl() {
      const enabledLayers = this.getEnabledLayersFromUrl();
      this.showEntitiesForLayers(enabledLayers);
    };

    getEnabledLayersFromUrl() {
      // Get the URL parameters
      const urlParams = (new URL(document.location)).searchParams;

      // Get the names of the enabled and disabled layers
      // Only care about layers that exist
      let enabledLayerNames = [];
      if (urlParams.has(this.layerURLParamName)) {
          enabledLayerNames = urlParams
            .getAll(this.layerURLParamName)
            .filter(name => this.layerOptions.find((option) => option.getDatasetName() == name) != undefined)
            .map(name => this.layerOptions.find((option) => option.getDatasetName() == name));
      }

      return enabledLayerNames;
    }

    showEntitiesForLayers(enabledLayers) {

      const layerOptionsClone = [].concat(this.layerOptions);
      const disabledLayers = layerOptionsClone.filter(layer => enabledLayers.indexOf(layer) === -1);

      // pass correct this arg
      enabledLayers.forEach(layer => layer.enable());
      disabledLayers.forEach(layer => layer.disable());

      this.reorderLayerList();
      this.updateKeyPanel();
    }

    // Shows/hides each pre-rendered key row (components/map-key-panel/
    // macro.jinja renders one per layer, plus one for "Show historical
    // data", all hidden except any that are checked at initial page
    // load) to match which layers/settings are currently selected, and
    // syncs the panel's expanded/collapsed state to whether there's
    // anything to show. Called after every dataset checkbox change
    // (via showEntitiesForLayers) and every "Show historical data"
    // change (toggleHistoricalData/updateHistoricalCheckboxState), so
    // it's the single place both keep the key panel in sync from.
    updateKeyPanel() {
      if (!this.$keyPanel) return;

      let anyChecked = false;
      this.layerOptions.forEach(option => {
        const checked = option.isChecked();
        if (checked) anyChecked = true;

        const row = this.$keyPanel.querySelector('[data-layer-key="' + option.getDatasetName() + '"]');
        if (row) row.style.display = checked ? 'flex' : 'none';
      });

      // Not a regular data layer (no LayerOption of its own), so handled
      // separately - always the first row in the markup already (see the
      // macro), so it doesn't need any reordering to stay at the top.
      const historicalChecked = !!(this.$historicalDataCheckbox && this.$historicalDataCheckbox.checked);
      if (historicalChecked) anyChecked = true;
      const historicalRow = this.$keyPanel.querySelector('[data-layer-key="show-historical-data"]');
      if (historicalRow) historicalRow.style.display = historicalChecked ? 'flex' : 'none';

      this.setKeyPanelExpanded(anyChecked);
    }

    setKeyPanelExpanded(expanded) {
      if (!this.$keyPanel) return;

      this.$keyPanel.classList.toggle('dl-map-key-panel--collapsed', !expanded);
      if (this.$keyPanelToggle) {
        this.$keyPanelToggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
      }
    }

    // Design wants checked layers "sticky" at the top of the list, above
    // any unchecked ones - selected first, then everything else, each
    // group keeping the same relative order it always had (this.layerOptions
    // is built once from the server-rendered order in attach() and never
    // itself reshuffled, so re-partitioning it here on every change is
    // enough to keep that order stable rather than drifting on repeated
    // toggles).
    //
    // This runs after every checkbox change and URL-driven update (both
    // funnel through showEntitiesForLayers above), so the list re-sorts
    // itself immediately regardless of whether the change came from a
    // click or a page-load/back-button URL restore.
    reorderLayerList() {
      if (!this.$layerList) return;

      const checked = [];
      const unchecked = [];
      this.layerOptions.forEach(option => {
        (option.isChecked() ? checked : unchecked).push(option);
      });

      // Appending an already-attached element moves it rather than
      // duplicating it, so this reorders in place without touching
      // display/visibility (relevant while the filter box has some items
      // hidden) or any listeners already bound to these elements.
      checked.concat(unchecked).forEach(option => {
        this.$layerList.appendChild(option.element);
      });
    }

    enabledLayers() {
      return this.layerOptions.filter(option => option.isChecked())
    };

    // Checkbox handler for "Show historical data"
    toggleHistoricalData(event) {
      if (this.enabledLayers().length === 0) {
        event.target.checked = false;
        if (this.$settingsPanelContent) {
          this.$settingsPanelContent.classList.add('govuk-form-group--error');
          this.$settingsPanelContent.prepend(this.$settingsErrorMessage);
        }
        this.updateKeyPanel();
        return;
      }

      const showHistorical = event.target.checked;
      this.enabledLayers().forEach(layerOption => {
        layerOption.availableLayers.forEach(layerId => {
          this.mapController.setLayerCurrentEntityFilter(layerId, showHistorical);
        });
      });
      this.updateKeyPanel();
    };

    // Resets the "Show historical data" checkbox when no dataset checkboxes
    // are checked, and clears the error state when a dataset becomes checked.
    updateHistoricalCheckboxState() {
      if (!this.$historicalDataCheckbox) return;

      const anyDatasetChecked = this.enabledLayers().length > 0;

      if (anyDatasetChecked && this.$settingsPanelContent) {
        this.$settingsPanelContent.classList.remove('govuk-form-group--error');
        this.$settingsErrorMessage?.remove();
      }

      // If no datasets are checked, uncheck and reset the historical filter
      if (!anyDatasetChecked && this.$historicalDataCheckbox.checked) {
        this.$historicalDataCheckbox.checked = false;
        this.layerOptions.forEach(layerOption => {
          layerOption.availableLayers.forEach(layerId => {
            this.mapController.setLayerCurrentEntityFilter(layerId, false);
          });
        });
        this.updateKeyPanel();
      }
    };

    filterCheckboxes(e) {
      var query = e.target.value;
      var filteredCheckboxes = this.filterCheckboxesArr(query);
      this.displayMatchingCheckboxes(filteredCheckboxes)
    };

    filterCheckboxesArr(query) {
      return this.layerOptions.filter(layerOption => layerOption.getDatasetName().toLowerCase().indexOf(query.toLowerCase()) !== -1)
    };

    displayMatchingCheckboxes(layerOptions, cb) {
      // hide all
      this.layerOptions.forEach(layerOption => layerOption.setLayerCheckboxVisibility(false));
      // re show those in filtered array
      layerOptions.forEach(layerOption => layerOption.setLayerCheckboxVisibility(true));
      if (cb) {
        cb();
      }
    };

    updateUrl() {
      // set the url params based on the enabled layers
      const urlParams = (new URL(document.location)).searchParams;
      urlParams.delete(this.layerURLParamName);

      this.enabledLayers().forEach((layer) =>
        urlParams.append(this.layerURLParamName, layer.getDatasetName())
      );

      let newURL =
        window.location.pathname +
        "?" +
        urlParams.toString() +
        window.location.hash;

      // add entry to history, does not fire event so need to call toggleLayersBasedOnUrl
      window.history.pushState({}, '', newURL);
      this.toggleLayersBasedOnUrl();
    }

    getClickableLayers() {
      var clickableLayers = [];
      var enabledLayers = this.enabledLayers().map(layer => layer.getDatasetName());

      return enabledLayers.map((layer) => {
        var components = this.availableLayers[layer];

        if (components.includes(layer + 'Fill')) {
          return layer + 'Fill';
        }

        return components[0];
      });
    }
}

export class LayerOption {
  constructor(layer, availableLayers, layerControls){
    this.layer = layer;
    this.element = this.findElement(layer);
    this.layerControls = layerControls;
    this.availableLayers = availableLayers;

    const $chkbx = this.element && this.element.querySelector('input[type="checkbox"]');
    if ($chkbx) {
      $chkbx.addEventListener('change', this.clickHandler.bind(this));
    }
  }

  // Finds the pre-rendered <li data-layer-control="{dataset}"> for this
  // dataset, rendered server-side by components/map/macro.jinja's
  // layerControlItem macro.
  findElement(layer) {
    return document.querySelector('[data-layer-control="' + layer.dataset + '"]');
  }

  clickHandler(e) {
    this.layerControls.updateUrl();
  }

  enable() {
    // Check the input, update UI classes, and set the map layer visibility to true
    const $chkbx = this.element.querySelector('input[type="checkbox"]');
    $chkbx.checked = true;
    this.element.dataset.layerControlActive = 'true';
    this.element.classList.remove(this.layerControlDeactivatedClass);
    this.setLayerVisibility(true);
    this.layerControls.updateHistoricalCheckboxState();
  };

  disable() {
    // Uncheck the input, update UI classes, and set the map layer visibility to false
    const $chkbx = this.element.querySelector('input[type="checkbox"]');
    $chkbx.checked = false;
    this.element.dataset.layerControlActive = 'false';
    this.element.classList.add(this.layerControlDeactivatedClass);
    this.setLayerVisibility(false);
    this.layerControls.updateHistoricalCheckboxState();
  };

  isChecked(){
    // Return the checked status of the layer's checkbox
    return this.element.querySelector('input[type="checkbox"]').checked
  }

  setLayerVisibility(visible) {
    const visibility = (visible) ? 'visible' : 'none';
    const showHistorical = !!(this.layerControls.$historicalDataCheckbox && this.layerControls.$historicalDataCheckbox.checked);

    this.availableLayers.forEach(layerId => {
      this.layerControls.mapController.setLayerVisibility(layerId, visibility);
      this.layerControls.mapController.setLayerCurrentEntityFilter(layerId, visible && showHistorical);
    });
  }

  setLayerCheckboxVisibility(display) {
    const displayString = display ? 'block' : 'none';
    this.element.style.display = displayString;
  }

  getDatasetName(){
    // Return the dataset identifier for this layer
    return this.layer.dataset;
  }
}
