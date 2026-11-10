import MapController from './MapController.js';

// Shown in place of the map when the browser can't run it. Mirrors the
// <noscript> message in components/map/macro.jinja.
export const MAP_UNSUPPORTED_MESSAGE = 'To view this map, you need to use a more up-to-date browser.';

// MapLibre needs WebGL2, and its script won't load at all in older browsers
// (leaving `maplibregl` undefined), so check both before creating a map.
export const isMapSupported = () => {
  if (typeof maplibregl === 'undefined') {
    return false;
  }
  try {
    const canvas = document.createElement('canvas');
    return !!(canvas.getContext && canvas.getContext('webgl2'));
  } catch (e) {
    return false;
  }
}

export const showMapUnsupportedMessage = (mapId) => {
  const mapElement = document.getElementById(mapId);
  if (!mapElement) {
    return;
  }
  mapElement.textContent = MAP_UNSUPPORTED_MESSAGE;

  // Hide the loading overlay, if this map has one, so the message is visible.
  const wrapper = mapElement.closest && mapElement.closest('.dl-map__wrapper');
  const loader = wrapper && wrapper.querySelector('.dl-map__loader');
  if (loader) {
    loader.remove();
  }
}

export const newMapController = (params = { layers: []}) => {

  const mapId = params.mapId || 'map';
  if (!isMapSupported()) {
    showMapUnsupportedMessage(mapId);
    return null;
  }

  const datasetUrl = params.DATASETTE_TILES_URL || '';

  let mapParams = {
    ...params,
    vectorSource: `${datasetUrl}/-/tiles/dataset_tiles/{z}/{x}/{y}.vector.pbf`,
    datasetVectorUrl: `${datasetUrl}/-/tiles/`,
    datasets: params.layers.map(d => d.dataset),
    sources: params.layers.map(d => {
      return {
        name: d.dataset + '-source',
        vectorSource: `${datasetUrl}/-/tiles/"${d.dataset}/{z}/{x}/{y}.vector.pbf`,
      }
    }),
    mapId: mapId,
  };
  return new MapController(mapParams);
}

export const capitalizeFirstLetter = (string) => {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export const convertNodeListToArray = (nl) => {
  return Array.prototype.slice.call(nl)
}

// Prevents scrolling of the page when the user triggers the wheel event on a div
// while still allowing scrolling of any specified scrollable child elements.
// Params:
//  scrollableChildElements: an array of class names of potential scrollable elements
export const preventScroll = (scrollableChildElements = []) => {
  return (e) => {
    const closestClassName = scrollableChildElements.find((c) => {
      return e.target.closest(c) != null;
    });

    if(!closestClassName){
      e.preventDefault();
      return false
    }

    const list = e.target.closest(closestClassName);

    if(!list){
      e.preventDefault();
      return false
    }

    var verticalScroll = list.scrollHeight > list.clientHeight;
    if(!verticalScroll)
      e.preventDefault();

    return false;
  }
}
