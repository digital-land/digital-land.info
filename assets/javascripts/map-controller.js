class MapController {
    constructor(params) {
        this.setParams(params);

        this.map = this.createMap();

        this.geojsonLayers = [];

        var boundSetup = this.setup.bind(this);
        this.map.on('load', boundSetup);

    }

    setParams(params) {
        params = params || {};
        this.mapId = params.mapId || 'mapid';
        this.mapContainerSelector = params.mapContainerSelector || '.dl-map__wrapper';
        this.vectorTileSources = params.vectorTileSources || [{
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
        this.geojsons = params.geojsons || [];
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
        this.vectorTileSources.forEach(source => {
            this.addVectorTileSource(source.name, source.vectorSource);
        });

        this.geojsons.forEach(geojson => {
          if(geojson.data.type == 'Point')
            this.addPoint(geojson);
          else if(['Polygon', 'MultiPolygon'].includes(geojson.data.type))
            this.addPolygon(geojson);
        });

        if(this.geojsons.length == 1){
          if(this.geojsons[0].data.type == 'Point'){
            this.map.flyTo({
              center: this.geojsons[0].data.coordinates,
              essential: true,
              animate: false
            });
          } else {
            var bbox = turf.extent(this.geojsons[0].data);
            let padding = this.geojsons[0].data.type == 'Point' ? 500 : 20;
            this.map.fitBounds(bbox, {padding, animate: false});
          }
        }

        this.addControls()

        var boundClickHandler = this.clickHandler.bind(this);
        this.map.on('click', boundClickHandler);
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

    addPolygon(geometry) {
      this.map.addSource(geometry.name, {
        'type': 'geojson',
        'data': {
          'type': 'Feature',
          'geometry': geometry.data,
          'properties': {
            'entity': geometry.entity,
            'name': geometry.name,
          }
        },
      });
      let layer = this.map.addLayer({
        'id': geometry.name,
        'type': 'fill',
        'source': geometry.name,
        'layout': {},
        'paint': {
          'fill-color': '#088',
          'fill-opacity': 0.5
        }
      });
      this.geojsonLayers.push(geometry.name);
    }

    addPoint(geometry, imageSrc='https://maplibre.org/maplibre-gl-js/docs/assets/osgeo-logo.png') {
      this.map.loadImage(
        imageSrc,
        (error, image) => {
          if (error) throw error;
          this.map.addImage('custom-marker', image);
          this.map.addSource(geometry.name, {
            'type': 'geojson',
            'data': {
              'type': 'Feature',
              'geometry': geometry.data,
              'properties': {
                'entity': geometry.entity,
                'name': geometry.name,
              }
            }
          });
          // Add a symbol layer
          let layer = this.map.addLayer({
            'id': geometry.name,
            'type': 'symbol',
            'source': geometry.name,
            'layout': {
                'icon-image': 'custom-marker',
                // get the year from the source's "year" property
                'text-field': ['get', 'year'],
                'text-font': [
                    'Open Sans Semibold',
                    'Arial Unicode MS Bold'
                ],
                'text-offset': [0, 1.25],
                'text-anchor': 'top'
            }
          });
          this.geojsonLayers.push(geometry.name);
        }
      );
    }

    addVectorTileSource(name, vectorSource) {
      this.map.addSource(name, {
        type: 'vector',
        tiles: [vectorSource],
        minzoom: this.minMapZoom,
        maxzoom: this.maxMapZoom
      });
      this.map.addLayer({
        'id': `${name}-layer-id`,
        'type': 'fill',
        'source': name,
        'source-layer': `${name}-layer`,
        'layout': {},
        'paint': {
          'fill-color': '#088',
          'fill-opacity': 0.5
        }
      });
    }

    clickHandler(e) {
      var map = this.map;
      var bbox = [[e.point.x - 5, e.point.y - 5], [e.point.x + 5, e.point.y + 5]];
      var that = this; // returns a list of layer ids we want to be 'clickable'

      const clickableLayers = this.getClickableLayers();

      var features = map.queryRenderedFeatures(bbox, {
        layers: clickableLayers
      });
      var coordinates = e.lngLat;

      if (features.length) {
        // no need to show popup if not clicking on feature
        var popupHTML = that.createFeaturesPopup(this.removeDuplicates(features));
        var popup = new maplibregl.Popup({
          maxWidth: this.popupWidth
        }).setLngLat(coordinates).setHTML(popupHTML).addTo(map);
      }
    };

    getClickableLayers() {
      var clickableLayers = [];
      if(this.layerControlsComponent){
        var that = this;
        var enabledControls = this.layerControlsComponent.enabledLayers();
        var enabledLayers = enabledControls.map(function ($control) {
          return that.layerControlsComponent.getDatasetName($control);
        });
        var clickableLayers = enabledLayers.map(function (layer) {
          var components = that.layerControlsComponent.availableLayers[layer];

          if (components.includes(layer + 'Fill')) {
            return layer + 'Fill';
          }

          return components[0];
        });
      }
      if (window.DEBUG) console.log('Clickable layers: ', [...clickableLayers, ...this.geojsonLayers]);
      return [...clickableLayers, ...this.geojsonLayers];
    }

    removeDuplicates(features) {
      var uniqueEntities = [];

      return features.filter(function (feature) {
        if (uniqueEntities.indexOf(feature.properties.entity) === -1) {
          uniqueEntities.push(feature.properties.entity);
          return true;
        }

        return false;
      });

    };

    createFeaturesPopup(features) {
      var featureCount = features.length;
      var wrapperOpen = '<div class="app-popup">';
      var wrapperClose = '</div>';
      var featureOrFeatures = featureCount > 1 ? 'features' : 'feature';
      var headingHTML = "<h3 class=\"app-popup-heading\">".concat(featureCount, " ").concat(featureOrFeatures, " selected</h3>");

      if (featureCount > this.popupMaxListLength) {
        headingHTML = '<h3 class="app-popup-heading">Too many features selected</h3>';
        var tooMany = "<p class=\"govuk-body-s\">You clicked on ".concat(featureCount, " features.</p><p class=\"govuk-body-s\">Zoom in or turn off layers to narrow down your choice.</p>");
        return wrapperOpen + headingHTML + tooMany + wrapperClose;
      }

      var itemsHTML = '<ul class="app-popup-list">\n';
      var that = this;
      features.forEach(function (feature) {
        var featureType = capitalizeFirstLetter(feature.sourceLayer || feature.source).replaceAll('-', ' ');
        var fillColour = that.getFillColour(feature);

        var featureName = feature.properties.name
        var featureReference = feature.properties.reference
        if (featureName === ''){
          if (featureReference === ''){
            featureName = 'Not Named'
          } else {
            featureName = featureReference
          }
        }

        var itemHTML = [
          "<li class=\"app-popup-item\" style=\"border-left: 5px solid ".concat(fillColour, "\">"),
          "<p class=\"app-u-secondary-text govuk-!-margin-bottom-0 govuk-!-margin-top-0\">".concat(featureType, "</p>"),
          '<p class="dl-small-text govuk-!-margin-top-0 govuk-!-margin-bottom-0">',
          "<a class='govuk-link' href=\"/entity/".concat(feature.properties.entity, "\">").concat(featureName, "</a>"),
          '</p>',
          '</li>'
        ];
        itemsHTML = itemsHTML + itemHTML.join('\n');
      });
      itemsHTML = headingHTML + itemsHTML + '</ul>';
      return wrapperOpen + itemsHTML + wrapperClose;
    };

    getFillColour(feature) {
      if(this.layerControlsComponent){
        var l = this.layerControlsComponent.getControlByName(feature.sourceLayer || feature.source);
        var styles = this.layerControlsComponent.getStyle(l);
        return styles.colour;
      }
      return '#000000';
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
        this.zoomHandler(); // call at the start to enforce rounding

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
