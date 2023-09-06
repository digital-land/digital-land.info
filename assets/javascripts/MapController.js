import BrandImageControl from "./BrandImageControl.js";
import CopyrightControl from "./CopyrightControl.js";
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
    this.vectorTileSources = params.vectorTileSources || [];
    this.datasetVectorUrl = params.datasetVectorUrl || null;
    this.datasets = params.datasets || null;
    this.minMapZoom = params.minMapZoom || 5;
    this.maxMapZoom = params.maxMapZoom || 15;
    this.baseURL = params.baseURL || 'https://digital-land.github.io';
    this.baseTileStyleFilePath = params.baseTileStyleFilePath || '/static/javascripts/base-tile.json';
    this.popupWidth = params.popupWidth || '260px';
    this.popupMaxListLength = params.popupMaxListLength || 10;
    this.LayerControlOptions = params.LayerControlOptions || {enabled: false};
    this.ZoomControlsOptions = params.ZoomControlsOptions || {enabled: false};
    this.FullscreenControl = params.FullscreenControl || {enabled: false};
    this.geojsons = params.geojsons || [];
    this.images = params.images || [{src: '/static/images/location-pointer-sdf-256.png', name: 'custom-marker-256', size: 256}];
    this.paint_options = params.paint_options || null;
    this.apiToken = params.apiToken || null;
  }



  createMap() {
    // Define the custom JSON style.
    // More styles can be found at https://github.com/OrdnanceSurvey/OS-Vector-Tile-API-Stylesheets.
    const customStyleJson = '/static/javascripts/OS_VTS_3857_3D.json';

    var map = new maplibregl.Map({
      container: this.mapId,
      minZoom: 4,
      maxZoom: 18,
      style: customStyleJson,
      maxBounds: [
        [ -11, 49 ],
        [ 8, 57 ]
      ],
      center: [ -1.5, 53.1 ],
      zoom: 4,
      transformRequest: (url, resourceType) => {
        if((resourceType === 'Source' || resourceType === 'Tile' || resourceType === 'Glyphs') && url.indexOf('api.os.uk') > -1){
          if(! /[?&]key=/.test(url) ) url += '?key=null'
          return {
              url: url + '&srs=3857',
              headers: {
                'Authorization': 'Bearer ' + this.apiToken,
              }
          }
        }
      }
    });
    return map;
  };

  async setup() {
    await this.loadImages(this.images);
    this.availableLayers = this.addVectorTileSources(this.vectorTileSources);
    this.geojsonLayers = this.addGeojsonSources(this.geojsons);
    if(this.geojsonLayers.length == 1){
      this.flyTo(this.geojsons[0]);
    }
    this.addControls()
    this.addClickHandlers();
  };

  loadImages(imageSrc=[]) {
    return new Promise((resolve, reject) => {
      const promiseArray = imageSrc.map(({src, name}) => {
        return new Promise((resolve, reject) => {
          this.map.loadImage(
            src,
            (error, image) => {
              if (error){
                reject(error);
              }
              this.map.addImage(name, image, {sdf: true});
              resolve();
            }
          );
        })
      });
      Promise.all(promiseArray).then(() => {
        resolve();
      }).catch((error) => {
        reject(error);
      });
    })
  }

	addVectorTileSources(vectorTileSources = []) {
    let availableLayers = {};
		// add vector tile sources to map
    vectorTileSources.forEach(source => {
      let layers = this.addVectorTileSource(source);
      availableLayers[source.name] = layers;
    });
		return availableLayers;
	}

  addGeojsonSources(geojsons = []) {
    // add geojsons sources to map
    const addedLayers = [];
    geojsons.forEach(geojson => {
      if(geojson.data.type == 'Point')
        addedLayers.push(this.addPoint(geojson, this.images[0]));
      else if(['Polygon', 'MultiPolygon'].includes(geojson.data.type))
        addedLayers.push(this.addPolygon(geojson));
      else
        throw new Error('Unsupported geometry type');
    });
    return addedLayers;
  }

  addControls() {



    this.map.addControl(new maplibregl.ScaleControl({
      container: document.getElementById(this.mapId)
    }), 'bottom-left');
    this.map.addControl(new BrandImageControl({
      imageSrc: '/static/images/os-logo-maps.png'
    }), 'bottom-left');

    if(this.FullscreenControl.enabled){
      this.map.addControl(new maplibregl.FullscreenControl({
        container: document.getElementById(this.mapId)
      }), 'top-left');
    }
    this.map.addControl(new TiltControl(), 'top-left');
    this.map.addControl(new maplibregl.NavigationControl({
      container: document.getElementById(this.mapId)
    }), 'top-left');

		// add layer controls
		if(this.LayerControlOptions.enabled){
			const layerControlsList = document.querySelector(`[data-module="layer-controls-${this.mapId}"]`)
			this.layerControlsComponent = new LayerControls(layerControlsList, this, this.sourceName, this.availableLayers,  this.LayerControlOptions);
		}

    this.map.addControl(new CopyrightControl(), 'bottom-right');


  }

  addClickHandlers() {
    if(this.layerControlsComponent){
      this.map.on('click', this.clickHandler.bind(this));
    }
  }


  flyTo(geometry){
    if(geometry.data.type == 'Point'){
      this.map.flyTo({
        center: geometry.data.coordinates,
        essential: true,
        animate: false,
        zoom: 15
      });
    } else {
      var bbox = turf.extent(geometry.data);
      this.map.fitBounds(bbox, {padding: 20, animate: false});
    }
  }

  addLayer({
    sourceName,
    layerType,
    paintOptions={},
    layoutOptions={},
    sourceLayer='',
    additionalOptions={}
  }){
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

    let colour = 'blue';
    if(this.paint_options)
      colour = this.paint_options.colour;

    let layer = this.addLayer({
      sourceName: geometry.name,
      layerType: 'fill-extrusion',
      paintOptions: {
        'fill-extrusion-color': colour,
        'fill-extrusion-opacity': 0.5
      },
    });

    this.moveLayerBehindBuildings(layer)

    return layer;
  }

  moveLayerBehindBuildings(layer, buildingsLayer = 'OS/TopographicArea_1/Building/1_3D') {
    try{
      this.map.moveLayer(layer, buildingsLayer);
    } catch (e) {
      console.log(`Could not move layer behind ${buildingsLayer}: `, e);
    }
  }

  addPoint(geometry, image=undefined){
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
    if(this.paint_options)
      iconColor = this.paint_options.colour;

    let layerName
    // if an image is provided use that otherwise use a circle
    if(image){
      if(!this.map.hasImage(image.name)){
        throw new Error('Image not loaded, imageName: ' + image.name + ' not found');
      }
      layerName = this.addLayer(
        {
          sourceName: geometry.name,
          layerType: 'symbol',
          paintOptions: {
            'icon-color': iconColor,
            'icon-opacity': 1,
          },
          layoutOptions: {
            'icon-image': image.name,
            'icon-size': 256 / image.size * 0.15,
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
			'fill-opacity': 0.6,
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
        layerType: 'fill-extrusion',
        paintOptions: {
          'fill-extrusion-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
          'fill-extrusion-height': 1,
          'fill-extrusion-base': 0,
          'fill-extrusion-opacity': parseFloat(source.styleProps.opacity) || defaultPaintOptions['fill-opacity']
        },
        sourceLayer: `${source.name}`,
      });

      this.moveLayerBehindBuildings(fillLayerName)

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
      var popupHTML = this.createFeaturesPopupHtml(this.removeDuplicates(features));
      var popup = new maplibregl.Popup({
        maxWidth: this.popupWidth
      }).setLngLat(coordinates).setHTML(popupHTML).addTo(map);
    }
  };

  // map.queryRenderedFeatures() can return duplicate features so we need to remove them
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

  createFeaturesPopupHtml(features) {
    var wrapperOpen = '<div class="app-popup">';
    var wrapperClose = '</div>';
    var featureOrFeatures = features.length > 1 ? 'features' : 'feature';
    var headingHTML = `<h3 class=\"app-popup-heading\">${features.length} ${featureOrFeatures} selected</h3>`;

    if (features.length > this.popupMaxListLength) {
      headingHTML = '<h3 class="app-popup-heading">Too many features selected</h3>';
      var tooMany = `<p class=\"govuk-body-s\">You clicked on ${features.length} features.</p><p class="govuk-body-s">Zoom in or turn off layers to narrow down your choice.</p>`;
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
        `<li class=\"app-popup-item\" style=\"border-left: 5px solid ${fillColour}">`,
        `<p class=\"app-u-secondary-text govuk-!-margin-bottom-0 govuk-!-margin-top-0\">${featureType}</p>`,
        '<p class="dl-small-text govuk-!-margin-top-0 govuk-!-margin-bottom-0">',
        `<a class='govuk-link' href="/entity/${feature.properties.entity}">${featureName}</a>`,
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
      else if(feature.layer.type === 'fill-extrusion')
      return this.map.getLayer(feature.layer.id).getPaintProperty('fill-extrusion-color');
    else if(feature.layer.type === 'circle')
      return this.map.getLayer(feature.layer.id).getPaintProperty('circle-color');
    else
      throw new Error("could not get fill colour for feature of type " + feature.layer.type);
  };

  setLayerVisibility(layerName, visibility) {
    this.map.setLayoutProperty(
      layerName,
      'visibility',
      visibility
    );
  };

}
