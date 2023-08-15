import LayerControls from "./LayerControls.js";
import TiltControl from "./TiltControl.js";
import { capitalizeFirstLetter } from "./utils.js";

export default class MapController {
  constructor(params) {
    // set the params applying default values where none were provided
    this.setParams(params);

    // create an array to store the geojson layers
    this.geojsonLayers = [];

    // create the maplibre map
    this.map = this.createMap();

    // once the maplibre map has loaded call the setup function
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
    this.baseTileStyleFilePath = params.baseTileStyleFilePath || './base-tiles-2.json';
    this.popupWidth = params.popupWidth || '260px';
    this.popupMaxListLength = params.popupMaxListLength || 10;
    this.LayerControlOptions = params.LayerControlOptions || {enabled: false};
    this.ZoomControlsOptions = params.ZoomControlsOptions || {enabled: false};
    this.FullscreenControl = params.FullscreenControl || {enabled: false};
    this.geojsons = params.geojsons || [];
    this.images = params.images || [{src: '/static/images/location-pointer-sdf.png', name: 'custom-marker'}];
  }

  createMap() {
    var map = new maplibregl.Map({
      container: this.mapId,
      // container id
      style: this.baseTileStyleFilePath,
      // open source tiles?
      center: [-0.61, 53.1],
      // // starting position [lng, lat]
      zoom: 5.5
      // // starting zoom
    });
    return map;
  };

  setup() {
    this.loadImages(this.images);
    this.addVectorTileSources(this.vectorTileSources);
    this.addGeojsonSources(this.geojsons);
    if(this.geojsonLayers.length == 1){
      this.flyTo(this.geojsons[0]);
    }
    this.addControls()
    this.addClickHandlers();
  };

  loadImages(imageSrc=[]) {
    imageSrc.forEach(({src, name}) => {
      this.map.loadImage(
        src,
        (error, image) => {
          if (error) throw error;
          this.map.addImage(name, image, {sdf: true});
          console.log('Image added');
        }
      );
    })
  }

	addVectorTileSources(vectorTileSources = []) {
    let availableLayers = {};
		// add vector tile sources to map
    vectorTileSources.forEach(source => {
      let layers = this.addVectorTileSource(source);
      availableLayers[source.name] = layers;
    });
		this.availableLayers = availableLayers;
	}

  addGeojsonSources(geojsons = []) {
    // add geojsons sources to map
    this.geojsons.forEach(geojson => {
      if(geojson.data.type == 'Point')
        this.geojsonLayers.push(this.addPoint(geojson));
      else if(['Polygon', 'MultiPolygon'].includes(geojson.data.type))
        this.geojsonLayers.push(this.addPolygon(geojson));
    });
  }

  addControls() {
    this.map.addControl(new maplibregl.ScaleControl({
      container: document.querySelector(this.mapContainerSelector)
    }), 'bottom-left');
    this.map.addControl(new TiltControl(), 'top-left');
    this.map.addControl(new maplibregl.NavigationControl({
      container: document.querySelector(this.mapContainerSelector)
    }), 'top-left');

		// add layer controls
		if(this.LayerControlOptions.enabled){
			this.$layerControlsList = document.querySelector(`[data-module="layer-controls-${this.mapId}"]`)
			this.layerControlsComponent = new LayerControls(this.$layerControlsList, this.map, this.sourceName, this.availableLayers,  this.LayerControlOptions);
		}

    if(this.FullscreenControl.enabled){
      this.map.addControl(new maplibregl.FullscreenControl({
        container: document.querySelector(this.mapContainerSelector)
      }), 'bottom-left');

    }
  }

  addClickHandlers() {
    this.map.on('click', this.clickHandler.bind(this));
  }


  flyTo(geometry){
    if(geometry.data.type == 'Point'){
      this.map.flyTo({
        center: geometry.data.coordinates,
        essential: true,
        animate: false
      });
    } else {
      var bbox = turf.extent(geometry.data);
      let padding = geometry.data.type == 'Point' ? 500 : 20;
      this.map.fitBounds(bbox, {padding, animate: false});
    }
  }

  addLayer(params){
    const {
      sourceName,
      layerType,
      paintOptions={},
      layoutOptions={},
      sourceLayer='',
      additionalOptions={}
    } = params;
    const layerName = `${sourceName}-${layerType}`;
    this.map.addLayer({
      id: layerName,
      type: layerType,
      source: sourceName,
      'source-layer': sourceLayer,
      paint: paintOptions,
      layout: layoutOptions,
      ...additionalOptions
    });
    return layerName;
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
    let layer = this.addLayer({
      sourceName: geometry.name,
      layerType: 'fill',
      paintOptions: {
        'fill-color': '#088',
        'fill-opacity': 0.5
      },
    });
    this.geojsonLayers.push(geometry.name);
  }

  addPoint(geometry, imageName=undefined){
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

    let iconColor = 'blue';
    if(this.$layerControlsList)
      iconColor = this.$layerControlsList.getFillColour(geometry.name) || 'blue';

    let layerName
    // if an image is provided use that otherwise use a circle
    if(imageName){
      if(!this.map.hasImage(imageName)){
        throw new Error('Image not loaded');
      }
      layerName = this.addLayer(
        {
          sourceName: geometry.name,
          layerType: 'symbol',
          paintOptions: {
            'icon-color': iconColor,
          },
          layoutOptions: {
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
        })
    }else{
      layerName = this.addLayer({
        sourceName: geometry.name,
        layerType: 'circle',
        paintOptions: {
          'circle-color': iconColor,
          'circle-radius': 5,
        }
      })
    }
    return layerName;
  }

  addVectorTileSource(source) {
		const defaultPaintOptions = {
			'fill-color': '#003078',
			'fill-opacity': 0.8,
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
      let layerName = this.addLayer({
        sourceName: `${source.name}-source`,
        layerType: 'circle',
        paintOptions: {
          'circle-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
          'circle-opacity': source.styleProps.opacity || defaultPaintOptions['fill-opacity'],
          'circle-stroke-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
          'circle-radius': 8,
        },
        sourceLayer: `${source.name}`,
      });

			layers = [layerName];
		} else {
			// create fill layer
      let fillLayerName = this.addLayer({
        sourceName: `${source.name}-source`,
        layerType: 'fill',
        paintOptions: {
          'fill-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
          'fill-opacity': source.styleProps.opacity || defaultPaintOptions['fill-opacity']
        },
        sourceLayer: `${source.name}`,
      });

			// create line layer
      let lineLayerName = this.addLayer({
        sourceName: `${source.name}-source`,
        layerType: 'line',
        paintOptions: {
          'line-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
          'line-width': source.styleProps.weight || defaultPaintOptions['weight']
        },
        sourceLayer: `${source.name}`,
      });
			layers = [fillLayerName, lineLayerName];
		}
		return layers;
  }

  clickHandler(e) {
    var map = this.map;
    var bbox = [[e.point.x - 5, e.point.y - 5], [e.point.x + 5, e.point.y + 5]];

    let clickableLayers = this.layerControlsComponent.getClickableLayers() || [];

    var features = map.queryRenderedFeatures(bbox, {
      layers: clickableLayers
    });
    var coordinates = e.lngLat;

    if (features.length) {
      // no need to show popup if not clicking on feature
      var popupHTML = this.createFeaturesPopup(this.removeDuplicates(features));
      var popup = new maplibregl.Popup({
        maxWidth: this.popupWidth
      }).setLngLat(coordinates).setHTML(popupHTML).addTo(map);
    }
  };

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
    features.forEach((feature) => {
      var featureType = capitalizeFirstLetter(feature.sourceLayer || feature.source).replaceAll('-', ' ');
      var fillColour = this.getFillColour(feature);

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