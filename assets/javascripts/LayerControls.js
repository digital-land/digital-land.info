export default class LayerControls {
    constructor ($module, map, source, availableLayers, options) {
      this.$module = $module;
      this.map = map;
      this.tileSource = source;
          this.availableLayers = availableLayers;
        // if the element is loaded then init, otherwise wait for load event
        if(this.$module){
            this.init(options);
        }else{
            this.$module.addEventListener('load', this.init.bind(this, options));
        }
      }

    init(params) {
      this.setupOptions(params);
      this._initialLoadWithLayers = false;

      // returns a node list so convert to array
      var $controls = this.$module.querySelectorAll(this.layerControlSelector);
      this.$controls = Array.prototype.slice.call($controls);

      // find parent
      this.$container = this.$module.closest('.' + this.controlsContainerClass);
      this.$container.classList.remove('js-hidden');

      // add buttons to open and close panel
      this.$closeBtn = this.createCloseButton();
      this.$openBtn = this.createOpenButton();

      // list all datasets names
      this.datasetNames = this.$controls.map($control => $control.dataset.layerControl);

      // listen for changes to URL
      var boundSetControls = this.toggleLayersBasedOnUrl.bind(this);
      window.addEventListener('popstate', function (event) {
        console.log('URL has changed - back button');
        boundSetControls();
      });

      // initial set up of controls (default or urlParams)
      const urlParams = (new URL(document.location)).searchParams;
      console.log('PARAMS', urlParams);
      if (!urlParams.has(this.layerURLParamName)) {
        // if not set then use default checked controls
        console.log('NO layer params exist');
        this.updateUrl();
      } else {
        // use URL params if available
        console.log('layer params exist');
        this.toggleLayersBasedOnUrl();
        this._initialLoadWithLayers = true;
      }

      // listen for changes on each checkbox and change the URL
      const boundControlChkbxChangeHandler = this.onControlChkbxChange.bind(this);
      this.$controls.forEach(function ($control) {
        $control.addEventListener('change', boundControlChkbxChangeHandler, true);
      }, this);

      return this
    };

    setupOptions(params) {
      params = params || {};
      this.layerControlSelector = params.layerControlSelector || '[data-layer-control]';
      this.layerControlDeactivatedClass = params.layerControlDeactivatedClass || 'deactivated-control';
      this.onEachFeature = params.onEachFeature || this.defaultOnEachFeature;
      this.baseUrl = params.baseUrl || 'http://digital-land.github.io';
      this.controlsContainerClass = params.controlsContainerClass || 'dl-map__side-panel',
      this.layerURLParamName = params.layerURLParamName || 'layer';
    };

    createCloseButton() {
      const button = document.createElement('button');
      button.classList.add('dl-map__close-btn');
      button.dataset.action = 'close';
      const label = document.createElement('span');
      label.textContent = 'Close layer panel';
      label.classList.add('govuk-visually-hidden');
      button.appendChild(label);
      this.$container.appendChild(button);

      const boundTogglePanel = this.togglePanel.bind(this);
      button.addEventListener('click', boundTogglePanel);
      return button
    };

    createOpenButton() {
      const button = document.createElement('button');
      button.classList.add('dl-map__open-btn', 'dl-map__overlay', 'js-hidden');
      button.dataset.action = 'open';
      const label = document.createElement('span');
      label.textContent = 'Open layer panel';
      label.classList.add('govuk-visually-hidden');
      button.appendChild(label);
      this.map.getContainer().appendChild(button);

      const boundTogglePanel = this.togglePanel.bind(this);
      button.addEventListener('click', boundTogglePanel);
      return button
    };

    togglePanel(e) {
      const action = e.target.dataset.action;
      const opening = (action === 'open');
      // set aria attributes
      this.$container.setAttribute('aria-hidden', !opening);
      this.$container.setAttribute('open', opening);
      if (opening) {
        this.$container.classList.remove('dl-map__side-panel--collapsed');
        this.$openBtn.classList.add('js-hidden');
        // focus on the panel when opening
        this.$container.focus();
      } else {
        this.$container.classList.add('dl-map__side-panel--collapsed');
        this.$openBtn.classList.remove('js-hidden');
        // focus on open btn when closing panel
        this.$openBtn.focus();
      }
    };


      // toggles visibility of elements/entities based on URL params
    toggleLayersBasedOnUrl() {
      // Get the URL parameters
      const urlParams = (new URL(document.location)).searchParams;

      // Get the names of the enabled and disabled layers
      // Only care about layers that exist
      let enabledLayerNames = [];
      if (urlParams.has(this.layerURLParamName)) {
          enabledLayerNames = urlParams.getAll(this.layerURLParamName).filter(name => this.datasetNames.indexOf(name) > -1);
      }

      this.showEntitiesForLayers(enabledLayerNames);
    };

    showEntitiesForLayers(enabledLayerNames) {
      console.log('Enable:', enabledLayerNames);

      const datasetNamesClone = [].concat(this.datasetNames);
      const disabledLayerNames = datasetNamesClone.filter(name => enabledLayerNames.indexOf(name) === -1);
      console.log('Disable:', disabledLayerNames);

      // map the names to the controls
      const toEnable = enabledLayerNames.map(name => this.getControlByName(name));
      const toDisable = disabledLayerNames.map(name => this.getControlByName(name));
      console.log(toEnable, toDisable);

      // pass correct this arg
      toEnable.forEach(this.enable, this);
      toDisable.forEach(this.disable, this);
    }

    updateUrl() {
      // set the url params based on the enabled layers
      const urlParams = (new URL(document.location)).searchParams;
      const enabledLayers = this.enabledLayers().map($control => this.getDatasetName($control));
      urlParams.delete(this.layerURLParamName);
      enabledLayers.forEach(name => urlParams.append(this.layerURLParamName, name));
      const newURL = window.location.pathname + '?' + urlParams.toString() + window.location.hash;

      // add entry to history, does not fire event so need to call toggleLayersBasedOnUrl
      window.history.pushState({}, '', newURL);
      this.toggleLayersBasedOnUrl();
    };

    enabledLayers() {
      return this.$controls.filter($control => this.getCheckbox($control).checked)
    };

    disabledLayers() {
      return this.$controls.filter($control => !this.getCheckbox($control).checked)
    };

    getCheckbox($control) {
      return $control.querySelector('input[type="checkbox"]')
    };

    getControlByName(dataset) {
      for (let i = 0; i < this.$controls.length; i++) {
        const $control = this.$controls[i];
        if ($control.dataset.layerControl === dataset) {
          return $control
        }
      }
      return undefined
    };

    enable($control) {
      console.log('enable', this.getDatasetName($control));
      const $chkbx = $control.querySelector('input[type="checkbox"]');
      $chkbx.checked = true;
      $control.dataset.layerControlActive = 'true';
      $control.classList.remove(this.layerControlDeactivatedClass);
      this.toggleLayerVisibility(this.map, this.getDatasetName($control), true);
    };

    disable($control) {
      console.log('disable', this.getDatasetName($control));
      const $chkbx = $control.querySelector('input[type="checkbox"]');
      $chkbx.checked = false;
      $control.dataset.layerControlActive = 'false';
      $control.classList.add(this.layerControlDeactivatedClass);
      this.toggleLayerVisibility(this.map, this.getDatasetName($control), false);
    };

    getDatasetName($control) {
      return $control.dataset.layerControl
    };

    toggleLayerVisibility(map, datasetName, toEnable) {
      console.log('toggle layer', datasetName);
      const visibility = (toEnable) ? 'visible' : 'none';
      const layers = this.availableLayers[datasetName];
      layers.forEach(layerId => this._toggleLayer(layerId, visibility));
    };

    _toggleLayer(layerId, visibility) {
      this.map.setLayoutProperty(
        layerId,
        'visibility',
        visibility
      );
    };

    onControlChkbxChange = function (e) {
      console.log('Has been toggled', e.target, this);
      // when a control is changed update the URL params
      this.updateUrl();
    };

  }
