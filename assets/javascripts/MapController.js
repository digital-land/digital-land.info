import BrandImageControl from "./BrandImageControl.js";
import CopyrightControl from "./CopyrightControl.js";
import LayerControls from "./LayerControls.js";
import TiltControl from "./TiltControl.js";
import { capitalizeFirstLetter, preventScroll } from "./utils.js";
import { getApiToken, getFreshApiToken } from "./osApiToken.js";
import {defaultPaintOptions} from "./defaultPaintOptions.js";

export default class MapController {
  constructor(params) {
    // set the params applying default values where none were provided
    this.setParams(params);

    // create an array to store the geojson layers
    this.geojsonLayers = [];

    // create the maplibre map
    this.createMap();
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
    this.customStyleJson = '/static/javascripts/OS_VTS_3857_3D.json';
    this.customStyleLayersToBringToFront = [
      'OS/Names/National/Country',
    ];
    this.useOAuth2 = params.useOAuth2 || false;
    this.layers = params.layers || [];
    this.featuresHoveringOver = 0;
  }

  getViewFromUrl() {
    const urlObj = new URL(document.location)
    const hash = urlObj.hash
    if(hash){
      const [lat, lng, zoom] = hash.substring(1).split(',')
      return {centre: [parseFloat(lng), parseFloat(lat)], zoom: parseFloat(zoom)}
    }
    return {centre: undefined, zoom: undefined}
  }

  async createMap() {
    // Define the custom JSON style.
    // More styles can be found at https://github.com/OrdnanceSurvey/OS-Vector-Tile-API-Stylesheets.

    await getFreshApiToken();

    const viewFromUrl = this.getViewFromUrl()

    var map = new maplibregl.Map({
      container: this.mapId,
      minZoom: 6,
      maxZoom: 18,
      style: this.customStyleJson,
      maxBounds: [
        [ -15, 49 ],
        [ 13, 57 ]
      ],
      center: viewFromUrl.centre || [ -1, 52.9 ],
      zoom: viewFromUrl.zoom || 6,
      transformRequest: (url, resourceType) => {
        if(url.indexOf('api.os.uk') > -1){
          if(! /[?&]key=/.test(url) ) url += '?key=null'

          const requestToMake = {
            url: url + '&srs=3857',
          }

          if(this.useOAuth2){
            const token = getApiToken();
            requestToMake.headers = {
              'Authorization': 'Bearer ' + token,
            }
          }

          return requestToMake;
        }
      }
    });

    map.getCanvas().ariaLabel = `${this.mapId}`;
    this.map = map;

    // once the maplibre map has loaded call the setup function
    var boundSetup = this.setup.bind(this);
    this.map.on('load', boundSetup);

  };

  async setup() {
    console.log('setup')
    try{
      await this.loadImages(this.images);
    }catch(e){
      console.log('error loading images: ' + e)
    }
    console.log('past load images')
    this.availableLayers = this.addVectorTileSources(this.vectorTileSources);
    this.geojsonLayers = this.addGeojsonSources(this.geojsons);
    if(this.geojsonLayers.length == 1){
      this.flyTo(this.geojsons[0]);
    }
    this.addControls()
    this.addClickHandlers();
    this.overwriteWheelEventsForControls();

    const handleMapMove = () => {
      const center = this.map.getCenter()
      const zoom = this.map.getZoom()
      const urlObj = new URL(document.location)
      const newURL = urlObj.origin + urlObj.pathname + urlObj.search + `#${center.lat},${center.lng},${zoom}z`;
      window.history.replaceState({}, '', newURL);
    }
    this.obscureScotland()
    this.obscureWales()
    this.addNeighbours()
    this.map.on('moveend',handleMapMove)
  };

  loadImages(imageSrc=[]) {
    console.log('loading images' + imageSrc.length + ' images')
    return new Promise((resolve, reject) => {
      const promiseArray = imageSrc.map(({src, name}) => {
        return new Promise((resolve, reject) => {
          this.map.loadImage(
            src,
            (error, image) => {
              if (error){
                console.log('error adding image: ' + error)
                reject(error);
              }
              console.log('added image')
              this.map.addImage(name, image, {sdf: true});
              resolve();
            }
          );
        })
      });
      Promise.all(promiseArray).then(() => {
        console.log('resolved')
        resolve();
      }).catch((error) => {
        console.log('rejected')
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

  obscureWales(){
    this.obscure('Wales_simplified', '#FFFFFF', 0.6);
  }

  obscureScotland(){
    this.obscure('Scotland_simplified');
  }

  addNeighbours(){
    this.obscure('UK_neighbours', '#FFFFFF', 0.9);
  }


  obscure(name, colour = '#FFFFFF', opacity = 0.8){
    this.map.addSource(name, {
      type: 'geojson',
      data: `/static/javascripts/geojsons/${name}.json`,
      buffer: 0,
    })
    const layerId = `${name}_Layer`
    this.map.addLayer({
      id: layerId,
      type: 'fill',
      source: name,
      layout: {},
      paint: {
        'fill-color': colour,
        'fill-opacity': opacity,
      }
    })
    this.map.moveLayer(layerId,'OS/Names/National/Country')
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

    if(this.FullscreenControl.enabled){
      this.map.addControl(new maplibregl.FullscreenControl({
        container: document.getElementById(this.mapId)
      }), 'top-left');
    }
    this.map.addControl(new TiltControl(), 'top-left');
    this.map.addControl(new maplibregl.NavigationControl({
      container: document.getElementById(this.mapId)
    }), 'top-left');

    this.map.addControl(new CopyrightControl(), 'bottom-right');

    if(this.LayerControlOptions.enabled){
      this.layerControlsComponent = new LayerControls(this, this.sourceName, this.layers, this.availableLayers, this.LayerControlOptions);
      this.map.addControl(this.layerControlsComponent, 'top-right');
    }
  }

  overwriteWheelEventsForControls() {
    const mapEl = document.getElementById(this.mapId)
    const mapControlsArray = mapEl.querySelectorAll('.maplibregl-control-container')
    mapControlsArray.forEach((mapControls) => mapControls.addEventListener('wheel', preventScroll(['.dl-map__side-panel__content']), {passive: false}));
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

    if(['fill', 'fill-extrusion', 'circle'].includes(layerType)){
      this.map.on('mouseover', layerName, () => {
        this.map.getCanvas().style.cursor = 'pointer'
        this.featuresHoveringOver++;
      })
      this.map.on('mouseout', layerName, () => {
        this.featuresHoveringOver--;
        if(this.featuresHoveringOver == 0)
          this.map.getCanvas().style.cursor = ''
      })
    }

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
        'fill-extrusion-opacity': 0.5,
        'fill-extrusion-height': 1,
        'fill-extrusion-base': 0,
      },
    });

    this.moveLayerBehindBuildings(layer)

    return layer;
  }

  moveLayerBehindBuildings(layer, buildingsLayer = 'OS/TopographicArea_1/Building/1_3D') {
    try{
      this.map.moveLayer(layer, buildingsLayer);
    } catch (e) {
      console.error(`Could not move layer behind ${buildingsLayer}: `, e);
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
          "circle-radius": defaultPaintOptions['circle-radius'],
        }
      })
    }
    return layerName;
  }

  addVectorTileSource(source) {
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
          "circle-radius": defaultPaintOptions['circle-radius']
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

      // create point layer for geometries
      let pointLayerName = this.addLayer({
        sourceName: `${source.name}-source`,
        layerType: 'circle',
        paintOptions: {
          'circle-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
          'circle-opacity': source.styleProps.opacity || defaultPaintOptions['fill-opacity'],
          'circle-stroke-color': source.styleProps.colour || defaultPaintOptions['fill-color'],
          "circle-radius": defaultPaintOptions['circle-radius']
        },
        sourceLayer: `${source.name}`,
        additionalOptions:{
          filter:[ "==", ["geometry-type"], "Point"]
        },
      });
			layers = [fillLayerName, lineLayerName, pointLayerName];
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
      var popupDomElement = this.createFeaturesPopup(this.removeDuplicates(features));
      var popup = new maplibregl.Popup({
        maxWidth: this.popupWidth
      }).setLngLat(coordinates).setDOMContent(popupDomElement).addTo(map);
      popup.getElement().onwheel = preventScroll(['.app-popup-list']);
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

  createFeaturesPopup(features) {
    const wrapper = document.createElement('div');
    wrapper.classList.add('app-popup');

    const featureOrFeatures = features.length > 1 ? 'features' : 'feature';
    const heading = document.createElement('h3');
    heading.classList.add('app-popup-heading');
    heading.textContent = `${features.length} ${featureOrFeatures} selected`;
    wrapper.appendChild(heading);

    if (features.length > this.popupMaxListLength) {
      const tooMany = document.createElement('p');
      tooMany.classList.add('govuk-body-s');
      tooMany.textContent = `You clicked on ${features.length} features.`;
      const tooMany2 = document.createElement('p');
      tooMany2.classList.add('govuk-body-s');
      tooMany2.textContent = 'Zoom in or turn off layers to narrow down your choice.';
      wrapper.appendChild(tooMany);
      wrapper.appendChild(tooMany2);
      return wrapper;
    }

    const list = document.createElement('ul');
    list.classList.add('app-popup-list');
    features.forEach((feature) => {
      const featureType = capitalizeFirstLetter(feature.sourceLayer || feature.source).replaceAll('-', ' ');
      const fillColour = this.getFillColour(feature);

      const featureName = feature.properties.name || feature.properties.reference || 'Not Named';
      const item = document.createElement('li');
      item.classList.add('app-popup-item');
      item.style.borderLeft = `5px solid ${fillColour}`;

      const secondaryText = document.createElement('p');
      secondaryText.classList.add('app-u-secondary-text', 'govuk-!-margin-bottom-0', 'govuk-!-margin-top-0');
      secondaryText.textContent = featureType;
      item.appendChild(secondaryText);

      const link = document.createElement('a');
      link.classList.add('govuk-link');
      link.href = `/entity/${feature.properties.entity}`;
      link.textContent = featureName;
      const smallText = document.createElement('p');
      smallText.classList.add('dl-small-text', 'govuk-!-margin-top-0', 'govuk-!-margin-bottom-0');
      smallText.appendChild(link);
      item.appendChild(smallText);

      list.appendChild(item);
    });

    wrapper.appendChild(list);
    return wrapper;
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
