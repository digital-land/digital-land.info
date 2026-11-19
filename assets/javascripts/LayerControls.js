/**
 * Wires behaviour onto the "Select a data layer" / "Advanced settings"
 * controls panel markup, which is rendered server-side.
 */
export default class LayerControls {
    constructor (mapController, source, layers, availableLayers, options) {
      this.mapController = mapController;
      this.tileSource = source;
      this.layers = layers;
      this.availableLayers = availableLayers;

      this.layerOptions = [];

      this.layerURLParamName = options.layerURLParamName || 'dataset';
      this.redirectURLParamNames = options.redirectURLParamNames || [];

      var boundSetControls = this.toggleLayersBasedOnUrl.bind(this);
      window.addEventListener('popstate', function (event) {
        boundSetControls();
      });

      this.replaceRedirectParamNames();
    }

    /**
     * Attaches behaviour to the pre-rendered panel markup and sets the
     * initial checkbox state from the URL (or the server-rendered default).
     */
    attach() {
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

      this.layerOptions = this.layers.map((layer) => {
        return new LayerOption(layer, this.availableLayers[layer.dataset], this);
      });

      const urlParams = (new URL(document.location)).searchParams;
      if (!urlParams.has(this.layerURLParamName)) {
        this.updateUrl();
      } else {
        this.toggleLayersBasedOnUrl();
      }
    }

    /** Migrates legacy URL param names (e.g. `layer`) to the current one. */
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

    toggleLayersBasedOnUrl() {
      const enabledLayers = this.getEnabledLayersFromUrl();
      this.showEntitiesForLayers(enabledLayers);
    };

    getEnabledLayersFromUrl() {
      const urlParams = (new URL(document.location)).searchParams;

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

      enabledLayers.forEach(layer => layer.enable());
      disabledLayers.forEach(layer => layer.disable());

      this.mapController.datasetZoomAlerts?.update();
    }

    enabledLayers() {
      return this.layerOptions.filter(option => option.isChecked())
    };

    /** Handles changes to the "Show historical data" checkbox. */
    toggleHistoricalData(event) {
      if (this.enabledLayers().length === 0) {
        event.target.checked = false;
        if (this.$settingsPanelContent) {
          this.$settingsPanelContent.classList.add('govuk-form-group--error');
          this.$settingsPanelContent.prepend(this.$settingsErrorMessage);
        }
        return;
      }

      const showHistorical = event.target.checked;
      this.enabledLayers().forEach(layerOption => {
        layerOption.availableLayers.forEach(layerId => {
          this.mapController.setLayerCurrentEntityFilter(layerId, showHistorical);
        });
      });
    };

    /** Resets "Show historical data" once no dataset layers are checked. */
    updateHistoricalCheckboxState() {
      if (!this.$historicalDataCheckbox) return;

      const anyDatasetChecked = this.enabledLayers().length > 0;

      if (anyDatasetChecked && this.$settingsPanelContent) {
        this.$settingsPanelContent.classList.remove('govuk-form-group--error');
        this.$settingsErrorMessage?.remove();
      }

      if (!anyDatasetChecked && this.$historicalDataCheckbox.checked) {
        this.$historicalDataCheckbox.checked = false;
        this.layerOptions.forEach(layerOption => {
          layerOption.availableLayers.forEach(layerId => {
            this.mapController.setLayerCurrentEntityFilter(layerId, false);
          });
        });
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
      this.layerOptions.forEach(layerOption => layerOption.setLayerCheckboxVisibility(false));
      layerOptions.forEach(layerOption => layerOption.setLayerCheckboxVisibility(true));
      if (cb) {
        cb();
      }
    };

    updateUrl() {
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

      // pushState doesn't fire popstate, so toggleLayersBasedOnUrl is
      // called explicitly.
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

  /** Finds this layer's pre-rendered `<li data-layer-control>` checkbox row. */
  findElement(layer) {
    return document.querySelector('[data-layer-control="' + layer.dataset + '"]');
  }

  clickHandler(e) {
    this.layerControls.updateUrl();
  }

  enable() {
    const $chkbx = this.element.querySelector('input[type="checkbox"]');
    $chkbx.checked = true;
    this.element.dataset.layerControlActive = 'true';
    this.setLayerVisibility(true);
    this.layerControls.updateHistoricalCheckboxState();
  };

  disable() {
    const $chkbx = this.element.querySelector('input[type="checkbox"]');
    $chkbx.checked = false;
    this.element.dataset.layerControlActive = 'false';
    this.setLayerVisibility(false);
    this.layerControls.updateHistoricalCheckboxState();
  };

  isChecked(){
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
    return this.layer.dataset;
  }
}
