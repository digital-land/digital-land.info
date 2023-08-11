class MapController {
    constructor(params) {
        this.setParams(params);

        this.map = this.createMap();

        this.geojsonLayers = [];

        var boundSetup = this.setup.bind(this);
        this.map.on('load', boundSetup);

    }

	testEarchquake() {
		// Add a new source from our GeoJSON data and
	// set the 'cluster' option to true. GL-JS will
	// add the point_count property to your source data.
		this.map.addSource('earthquakes', {
			type: 'geojson',
			// Point to GeoJSON data. This example visualizes all M1.0+ earthquakes
			// from 12/22/15 to 1/21/16 as logged by USGS' Earthquake hazards program.
			data: 'https://docs.mapbox.com/mapbox-gl-js/assets/earthquakes.geojson',
			cluster: true,
			clusterMaxZoom: 14, // Max zoom to cluster points on
			clusterRadius: 50 // Radius of each cluster when clustering points (defaults to 50)
		});

		this.map.addLayer({
			id: 'clusters',
			type: 'circle',
			source: 'earthquakes',
			filter: ['has', 'point_count'],
			paint: {
			// Use step expressions (https://docs.mapbox.com/mapbox-gl-js/style-spec/#expressions-step)
			// with three steps to implement three types of circles:
			//   * Blue, 20px circles when point count is less than 100
			//   * Yellow, 30px circles when point count is between 100 and 750
			//   * Pink, 40px circles when point count is greater than or equal to 750
			'circle-color': [
			'step',
			['get', 'point_count'],
			'#51bbd6',
			100,
			'#f1f075',
			750,
			'#f28cb1'
			],
			'circle-radius': [
			'step',
			['get', 'point_count'],
			20,
			100,
			30,
			750,
			40
			]
			}
		});

		this.map.addLayer({
			id: 'cluster-count',
			type: 'symbol',
			source: 'earthquakes',
			filter: ['has', 'point_count'],
			layout: {
			'text-field': ['get', 'point_count_abbreviated'],
			'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
			'text-size': 12
			}
		});

		const paintOptions = {
			'icon-color': '#ff0000',
		  };
		  const layoutOptions = {
			  'icon-image': 'custom-marker',
			  'icon-anchor': 'bottom',
			  'symbol-placement': 'point',
			  'icon-allow-overlap': true,
			  'icon-ignore-placement': true,
		  };

		this.map.addLayer({
			id: 'unclustered-point',
			type: 'symbol',
			source: 'earthquakes',
			filter: ['!', ['has', 'point_count']],
			paint: paintOptions,
			layout: layoutOptions,
		});
	}

    testAddTrees() {
      // add the source
      this.map.addSource('treeTest', {
        type: 'vector',
        tiles: ['https://datasette-tiles.planning.data.gov.uk/-/tiles/tree/{z}/{x}/{y}.vector.pbf'],
        minzoom: this.minMapZoom,
        maxzoom: this.maxMapZoom,
		cluster: true,
		clusterMaxZoom: 14, // Max zoom to cluster points on
		clusterRadius: 50
      });

      // add the layer
      const paintOptions = {
        'icon-color': '#ff0000',
      };
      const layoutOptions = {
          'icon-image': 'custom-marker',
          'icon-anchor': 'bottom',
          'symbol-placement': 'point',
          'icon-allow-overlap': true,
          'icon-ignore-placement': true,
      };

	  this.map.addLayer({
		id: 'clusters',
		type: 'circle',
		source: 'treeTest',
		'source-layer': 'tree',
		filter: ['has', 'point_count'],
		paint: {
			// Use step expressions (https://maplibre.org/maplibre-style-spec/#expressions-step)
			// with three steps to implement three types of circles:
			//   * Blue, 20px circles when point count is less than 100
			//   * Yellow, 30px circles when point count is between 100 and 750
			//   * Pink, 40px circles when point count is greater than or equal to 750
			'circle-color': [
				'step',
				['get', 'point_count'],
				'#51bbd6',
				100,
				'#f1f075',
				750,
				'#f28cb1'
			],
			'circle-radius': [
				'step',
				['get', 'point_count'],
				20,
				100,
				30,
				750,
				40
			]
		}
	});

	this.map.addLayer({
		id: 'cluster-count',
		type: 'symbol',
		source: 'treeTest',
		'source-layer': 'tree',
		filter: ['has', 'point_count'],
		layout: {
			'text-field': '{point_count_abbreviated}',
			'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
			'text-size': 12
		}
	});


      this.map.addLayer({
        id: 'treeTest-layer',
        type: 'symbol',
        source: 'treeTest',
        'source-layer': 'tree',
        paint: paintOptions,
        layout: layoutOptions,
      });

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
        var map = new maplibregl.Map({
          container: this.mapId,
          // container id
          style: this.baseTileStyleFilePath,
          // open source tiles?
          center: [-0.5, 52.6],
          // // starting position [lng, lat]
          zoom: 5.5
          // // starting zoom

        });

        if(this.FullscreenControl.enabled){
            map.addControl(new maplibregl.ScaleControl({
              container: document.querySelector(this.mapContainerSelector)
            }), 'bottom-left');
            map.addControl(new maplibregl.FullscreenControl({
              container: document.querySelector(this.mapContainerSelector)
            }), 'bottom-left');

            map.addControl(new maplibregl.NavigationControl({
              container: document.querySelector(this.mapContainerSelector)
            }), 'top-left');

        }

        return map;
    };

    setup() {
		const that = this;
        this.addPinImage(() => {
			that.addSources();
			that.addControls()

			var boundClickHandler = that.clickHandler.bind(that);
			that.map.on('click', boundClickHandler);
		});
    };

	addSources() {
		// add sources to map
        let availableLayers = {};
        this.vectorTileSources.forEach(source => {
          let layers = this.addVectorTileSourceAndLayer(source);
          availableLayers[source.name] = layers;
        });
		this.availableLayers = availableLayers;

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
	}

    addControls() {
		// add layer controls
		if(this.LayerControlOptions.enabled){
			this.$layerControlsList = document.querySelector(`[data-module="layer-controls-${this.mapId}"]`)
			this.layerControlsComponent = new LayerControls(this.$layerControlsList, this.map, this.sourceName, this.availableLayers,  this.LayerControlOptions);
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

    addPoint(geometry, imageSrc='/static/images/location-pointer-sdf.png') {
      this.map.loadImage(
        imageSrc,
        (error, image) => {
          if (error) throw error;
          this.map.addImage('custom-marker', image, {sdf: true});
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
          let iconColor = 'blue';
          if(this.$layerControlsList)
            iconColor = this.$layerControlsList.getFillColour(geometry.name) || 'blue';
          let layer = this.map.addLayer({
            'id': geometry.name,
            'type': 'symbol',
            'source': geometry.name,
            'layout': {
                'icon-image': 'custom-marker',
                'icon-anchor': 'bottom',
                // get the year from the source's "year" property
                'text-field': ['get', 'year'],
                'text-font': [
                    'Open Sans Semibold',
                    'Arial Unicode MS Bold'
                ],
                'text-offset': [0, 1.25],
                'text-anchor': 'top'
            },
            'paint': {
              'icon-color': iconColor,
            },
          });
          this.geojsonLayers.push(geometry.name);
        }
      );
    }

    addPinImage(callback, imageSrc='/static/images/location-pointer-sdf.png') {
      this.map.loadImage(
        imageSrc,
        (error, image) => {
          if (error) throw error;
          this.map.addImage('custom-marker', image, {sdf: true});
		  console.log('Image added');
		  if(callback)
			callback();
        }
      );
    }

    createVectorLayer(layerId, datasetName, _type, paintOptions = {}, layoutOptions = {}, additionalOptions = {}) {
      // if there is a tileSource for the layer use that or default to the group one
      const tileSource = this.map.getSource(datasetName + '-source') ? datasetName + '-source' : this.tileSource;
      console.log('TileSource:', tileSource);
      this.map.addLayer({
        id: layerId,
        type: _type,
        source: tileSource,
        'source-layer': datasetName,
        paint: paintOptions,
		layout: layoutOptions,
		...additionalOptions
      });
    };

    addVectorTileSourceAndLayer(source) {

		const defaultPaintOptions = {
			'fill-color': '#003078',
			'fill-opacity': 0.5,
			'weight': 1,
		};


		// add source
		this.map.addSource(`${source.name}-source`, {
			type: 'vector',
			tiles: [source.vectorSource],
			minzoom: this.minMapZoom,
			maxzoom: this.maxMapZoom
		});

		// add layer
		let layers;
		if (source.dataType === 'point') {
      minPinZoom = 11;
			// set options for points as circle markers
			const paintOptions = {
				'icon-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
				'icon-opacity': 0.8,
			};
			const layoutOptions = {
				'icon-image': 'custom-marker',
				'icon-anchor': 'bottom',
				'symbol-placement': 'point',
				'icon-allow-overlap': true,
				'icon-size': 0.7,
			};

			this.createVectorLayer(source.name+'-symbol', source.name, 'symbol', paintOptions, layoutOptions, {minzoom: minPinZoom});

			// set options for points as circle markers
			const paintOptionsCircle = {
				'circle-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
				'circle-opacity': source.styleProps.opacity || defaultPaintOptions['fill-opacity'],
				'circle-radius': 5,
				'circle-stroke-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
				'circle-stroke-width': source.styleProps.weight || defaultPaintOptions['weight']
			};
			// create the layer
			this.createVectorLayer(source.name+'-circle', source.name, 'circle', paintOptionsCircle, {}, {maxzoom: minPinZoom});
			layers = [source.name+'-symbol', source.name+'-circle'];
		} else {
			const fillName = `${source.name}-Fill`;
			const lineName = `${source.name}-Line`;
			// create fill layer
			this.createVectorLayer(fillName, source.name, 'fill', {
				'fill-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
				'fill-opacity': source.styleProps.opacity || defaultPaintOptions['fill-opacity']
			},{});
			// create line layer
			this.createVectorLayer(lineName, source.name, 'line', {
				'line-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
				'line-width': source.styleProps.weight || defaultPaintOptions['weight']
			},{});
			layers = [fillName, lineName];
		}
		return layers;
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
      if(feature.layer.type === 'symbol')
        return this.map.getLayer(feature.layer.id).getPaintProperty('icon-color');
      else if(feature.layer.type === 'fill')
        return this.map.getLayer(feature.layer.id).getPaintProperty('fill-color');
      else
        throw new Error("could not get fill colour for feature of type " + feature.layer.type);
    };

}

class LayerControls {
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

class HelloWorldControl {
  onAdd(map) {
      this._map = map;
      this._container = document.createElement('div');
      this._container.className = 'maplibregl-ctrl';
      this._container.textContent = 'Hello, world';
      return this._container;
  }

  onRemove() {
      this._container.parentNode.removeChild(this._container);
      this._map = undefined;
  }
}
