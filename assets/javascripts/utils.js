import MapController from './MapController.js';

export const newMapController = (params) => {

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
