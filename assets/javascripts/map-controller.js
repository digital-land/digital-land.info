class MapController {
    constructor(params) {
        this.setParams(params);

        this.map = this.createMap();

        var boundSetup = this.setup.bind(this);
        this.map.on('load', boundSetup);

    }

    setParams(params) {
        params = params || {};
        this.mapId = params.mapId || 'mapid';
        this.mapContainerSelector = params.mapContainerSelector || '.dl-map__wrapper';
        this.sources = params.sources || [{
            name: 'dl-vectors',
            vectorSource: 'https://datasette-tiles.digital-land.info/-/tiles/dataset_tiles/{z}/{x}/{y}.vector.pbf'
        }];
        this.datasetVectorUrl = params.datasetVectorUrl || null;
        this.datasets = params.datasets || null;
        this.minMapZoom = params.minMapZoom || 5;
        this.maxMapZoom = params.maxMapZoom || 15;
        this.baseURL = params.baseURL || 'https://digital-land.github.io';
        this.baseTileStyleFilePath = params.baseTileStyleFilePath || './base-tile.json';
        this.popupWidth = params.popupWidth || '260px';
        this.popupMaxListLength = params.popupMaxListLength || 10;
        this.LayerControlOptions = params.LayerControlOptions || {enabled: false};
        this.ZoomControlsOptions = params.ZoomControlsOptions || {enabled: false};
        this.FullscreenControl = params.FullscreenControl || {enabled: false};
    }

    createMap() {
        var mappos = DLMaps.Permalink.getMapLocation(6, [0, 52]);
        var map = new maplibregl.Map({
          container: this.mapId,
          // container id
          style: this.baseTileStyleFilePath,
          // open source tiles?
          center: mappos.center,
          // starting position [lng, lat]
          zoom: mappos.zoom // starting zoom

        });
        DLMaps.Permalink.setup(map); // add fullscreen control

        if(this.FullscreenControl.enabled){
            map.addControl(new maplibregl.FullscreenControl({
              container: document.querySelector(this.mapContainerSelector)
            }), 'bottom-left');
        }

        return map;
    };

    setup() {
        // add sources to map
        this.sources.forEach(source => {
            this.addSource(source.name, source.vectorSource);
        });

        // ToDo: this should be done using addSource
        // this.addDatasetVectorSources(this.datasetVectorUrl, this.datasets);

        this.addControls()

        // var boundClickHandler = this.clickHandler.bind(this);
        // this.map.on('click', boundClickHandler);
    };

    addControls() {
        // add zoom controls
        if(this.ZoomControlsOptions.enabled){
            this.$zoomControls = document.querySelector(`[data-module="zoom-controls-${this.mapId}"]`)
            this.zoomControl = new ZoomControls(this.$zoomControls, this.map, this.map.getZoom(), this.ZoomControlsOptions);
        }

        // add layer controls
        if(this.LayerControlOptions.enabled){
            this.$layerControlsList = document.querySelector(`[data-module="layer-controls-${this.mapId}"]`)
            this.layerControlsComponent = new LayerControls(this.$layerControlsList, this.map, this.sourceName, this.LayerControlOptions);

        }
    }

    addSource(name, vectorSource) {
        this.map.addSource(name, {
          type: 'vector',
          tiles: [vectorSource],
          minzoom: this.minMapZoom,
          maxzoom: this.maxMapZoom
        });
    }

    addDatasetVectorSources(sourceUrl,datasets) {
        if (sourceUrl === null || datasets === null){
          console.log("dataset vector sources not added, will default to vectorSource")
        } else {
          console.log("dataset vector sources added")
        // set up source for each dataset on the tiles server
          for (let i = 0; i < datasets.length; i++) {
            var sourceName = datasets[i] + '-source';
            this.map.addSource(sourceName, {
              type: 'vector',
              tiles: [sourceUrl + datasets[i] + '/{z}/{x}/{y}.vector.pbf'],
              minzoom: this.minMapZoom,
              maxzoom: this.maxMapZoom
            });
          }
        }
      };


}


class ZoomControls {
    constructor($module, leafletMap, initialZoom, options) {
        this.$module = $module;
        this.map = leafletMap;
        this.initialZoom = initialZoom;
        // if the element is loaded then init, otherwise wait for load event
        if(this.$module){
            this.init(options);
        }else{
            this.$module.addEventListener('load', this.init.bind(this, options));
        }
    }

    init(params) {
        this.setupOptions(params);

        if (!this.$module) {
            return undefined
        }

        this.$module.classList.remove('js-hidden');

        const $buttons = this.$module.querySelectorAll('.' + this.buttonClass);
        this.$buttons = Array.prototype.slice.call($buttons);

        this.$counter = this.$module.querySelector(this.counterSelector);
        this.$counter.textContent = this.initialZoom;

        const boundClickHandler = this.clickHandler.bind(this);
        this.$buttons.forEach(function ($button) {
            $button.addEventListener('click', boundClickHandler);
        });

        const boundZoomHandler = this.zoomHandler.bind(this);
        // use on() not addEventListener()
        this.map.on('zoomend', boundZoomHandler);

        return this
    }

    setupOptions(params) {
        params = params || {};
        this.buttonClass = params.buttonClass || 'zoom-controls__btn';
        this.counterSelector = params.counterSelector || '.zoom-controls__count';
    };

    clickHandler(e) {
        e.preventDefault();
        const $clickedEl = e.target;
        let $clickedControl = $clickedEl;
        // check if button was pressed
        // if contained span then find button
        if (!$clickedEl.classList.contains(this.buttonClass)) {
          $clickedControl = $clickedEl.closest('.' + this.buttonClass);
        }
        this.zoom($clickedControl.dataset.zoomControl);
    };

    zoom(direction) {
        (direction === 'in') ? this.map.zoomIn(1) : this.map.zoomOut(1);
    };

    zoomHandler(e) {
        const zoomLevel = this.map.getZoom();
        let zl = parseFloat(zoomLevel);
        if (zl % 1 !== 0) {
          zl = parseFloat(zoomLevel).toFixed(2);
        }
        this.$counter.textContent = zl;
      };
}

class LayerControls {
    constructor ($module, map, source, options) {
        this.$module = $module;
        this.map = map;
        this.tileSource = source;
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

        // create mapping between dataset and layer, one per control item
        this.availableLayers = this.createAllFeatureLayers();
        console.log(this.availableLayers);

        // listen for changes to URL
        var boundSetControls = this.setControls.bind(this);
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
          this.updateURL();
        } else {
          // use URL params if available
          console.log('layer params exist');
          this.setControls();
          this._initialLoadWithLayers = true;
        }

        // listen for changes on each checkbox and change the URL
        const boundControlChkbxChangeHandler = this.onControlChkbxChange.bind(this);
        this.$controls.forEach(function ($control) {
          console.log(this);
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

    createAllFeatureLayers() {
        const availableDatasets = [];
        const that = this;

        this.$controls.forEach(function ($control) {
          const datasetName = $control.dataset.layerControl;
          const dataType = $control.dataset.layerType;
          const styleProps = that.getStyle($control);
          let layers;

          if (dataType === 'point') {
            // set options for points as circle markers
            const paintOptions = {
              'circle-color': styleProps.colour,
              'circle-opacity': styleProps.opacity,
              'circle-radius': {
                base: 1.5,
                stops: [
                  [6, 1],
                  [22, 180]
                ]
              },
              'circle-stroke-color': styleProps.colour,
              'circle-stroke-width': styleProps.weight
            };
            // create the layer
            that.createVectorLayer(datasetName, datasetName, 'circle', paintOptions);
            layers = [datasetName];
          } else {
            // create fill layer
            that.createVectorLayer(datasetName + 'Fill', datasetName, 'fill', {
              'fill-color': styleProps.colour,
              'fill-opacity': styleProps.opacity
            });
            // create line layer
            that.createVectorLayer(datasetName + 'Line', datasetName, 'line', {
              'line-color': styleProps.colour,
              'line-width': styleProps.weight
            });
            layers = [datasetName + 'Fill', datasetName + 'Line'];
          }
          availableDatasets[datasetName] = layers;
        });
        return availableDatasets
    };

    createVectorLayer(layerId, datasetName, _type, paintOptions) {
        // if there is a tileSource for the layer use that or default to the group one
        const tileSource = this.map.getSource(datasetName + '-source') ? datasetName + '-source' : this.tileSource;
        console.log('TileSource:', tileSource);
        this.map.addLayer({
          id: layerId,
          type: _type,
          source: tileSource,
          'source-layer': datasetName,
          paint: paintOptions
        });
    };

    getStyle($control) {
        const defaultColour = '#003078';
        const defaultOpacity = 0.5;
        const defaultWeight = 2;
        const s = $control.dataset.styleOptions;
        const parts = s.split(',');
        return {
          colour: parts[0] || defaultColour,
          opacity: parseFloat(parts[1]) || defaultOpacity,
          weight: parseInt(parts[2]) || defaultWeight
        }
    };

    // toggles visibility of elements based on URL params
    setControls() {
        // Get the URL parameters
        const urlParams = (new URL(document.location)).searchParams;

        // Get the names of the enabled and disabled layers
        // Only care about layers that exist
        let enabledLayerNames = [];
        if (urlParams.has(this.layerURLParamName)) {
            enabledLayerNames = urlParams.getAll(this.layerURLParamName).filter(name => this.datasetNames.indexOf(name) > -1);
        }
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
    };

    updateURL() {
        const urlParams = (new URL(document.location)).searchParams;
        const enabledLayers = this.enabledLayers().map($control => this.getDatasetName($control));

        urlParams.delete(this.layerURLParamName);
        enabledLayers.forEach(name => urlParams.append(this.layerURLParamName, name));
        console.log(urlParams.toString());
        const newURL = window.location.pathname + '?' + urlParams.toString() + window.location.hash;
        // add entry to history, does not fire event so need to call setControls
        window.history.pushState({}, '', newURL);
        this.setControls();
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
        // get the control containing changed checkbox
        // var $clickedControl = e.target.closest(this.layerControlSelector)

        // when a control is changed update the URL params
        this.updateURL();
    };

}
