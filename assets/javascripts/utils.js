import MapController from './MapController.js';

export const newMapController = (params = { layers: []}) => {

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
      mapId: params.mapId || 'map',
    };
    return new MapController(mapParams);
  }

export const capitalizeFirstLetter = (string) => {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

export const convertNodeListToArray = (nl) => {
  return Array.prototype.slice.call(nl)
}

export const makePreventScrollFn = (scrollDivClass = []) => {
  return (e) => {
    const closestClassName = scrollDivClass.find((c) => {
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
