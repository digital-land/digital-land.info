import InteractiveMap from '@defra/interactive-map'
import maplibreProvider from '@defra/interactive-map/providers/maplibre'
import createDatasetsPlugin from '@defra/interactive-map/plugins/datasets'
import createInteractPlugin from '@defra/interactive-map/plugins/interact'
import '@defra/interactive-map/css'
import '@defra/interactive-map/plugins/datasets/css'
import { getApiToken, getFreshApiToken } from './osApiToken.js'

const config = window.__DEFRA_MAP_PROTOTYPE_CONFIG__

// Diagnostic: point/symbol datasets (e.g. "tree") temporarily excluded to
// isolate a MapLibre GL internal crash in the icon/symbol placement code
// (bucket.icon.opacityVertexArray mismatch) to the symbol layer.
const polygonAndLineDatasets = config.datasets.filter((d) => d.type !== 'point')

const datasetConfigs = polygonAndLineDatasets.map((d) => ({
  id: d.dataset,
  label: d.name,
  tiles: [d.tileUrl],
  sourceLayer: d.dataset,
  minZoom: 0,
  maxZoom: 24,
  showInKey: true,
  showInMenu: true,
  visible: false,
  style:
    d.type === 'point'
      ? {
          symbol: 'pin',
          symbolBackgroundColor: d.colour || '#003078'
        }
      : {
          stroke: d.colour || '#003078',
          strokeWidth: 2,
          fill: d.colour || '#003078',
          opacity: d.opacity ? Number(d.opacity) : 0.5
        }
}))

// Search result (postcode / UPRN / LPA), equivalent to the current map's
// `geojsons`/`paint_options` params passed to the MapController macro.
if (config.searchResult && config.searchResult.geometry) {
  datasetConfigs.push({
    id: 'search-result',
    label: config.searchResult.name || 'Search result',
    geojson: {
      type: 'FeatureCollection',
      features: [{ type: 'Feature', properties: {}, geometry: config.searchResult.geometry }]
    },
    generateIds: true,
    showInKey: true,
    showInMenu: true,
    style:
      config.searchResult.type === 'point'
        ? { symbol: 'pin', symbolBackgroundColor: config.searchResult.colour || '#d4351c' }
        : {
            stroke: config.searchResult.colour || '#d4351c',
            strokeWidth: 3,
            fill: config.searchResult.colour || '#d4351c',
            opacity: 0.3
          }
  })
}

const datasetsPlugin = createDatasetsPlugin({
  datasets: datasetConfigs
})

const interactPlugin = createInteractPlugin({
  interactionModes: ['selectFeature'],
  multiSelect: false,
  layers: polygonAndLineDatasets.map((d) => ({
    layerId: d.dataset,
    labelProperty: 'reference'
  }))
})

// MapLibre's transformRequest must be synchronous, so the token has to be
// fetched and cached *before* the map is constructed (mirrors MapController.js).
await getFreshApiToken()

// Reuses the same /os/getToken proxy and OAuth2 token cache as the
// existing MapController, so the OS vector tile basemap renders
// authenticated exactly as it does today.
function transformRequest(url, resourceType) {
  if (url.indexOf('api.os.uk') === -1) {
    return { url }
  }

  if (!/[?&]key=/.test(url)) url += '?key=null'

  return {
    url: url + '&srs=3857',
    headers: { Authorization: `Bearer ${getApiToken()}` }
  }
}

const interactiveMap = new InteractiveMap('map', {
  mapProvider: maplibreProvider(),
  behaviour: 'inline',
  ...(config.bounds ? { bounds: config.bounds } : { zoom: config.zoom, center: config.center }),
  containerHeight: config.containerHeight || '700px',
  transformRequest,
  mapStyle: {
    url: config.osStyleUrl,
    attribution: 'Contains OS data © Crown copyright and database rights'
  },
  plugins: [datasetsPlugin, interactPlugin]
})

// Open the Layers panel by default, rather than requiring the user to find
// and click the "Layers" button first, matching current map's layer list
// being visible immediately.
interactiveMap.on('datasets:ready', () => {
  interactiveMap.showPanel('datasetsLayers', { focus: false })
})

interactiveMap.on('interact:select', (event) => {
  const selected = event?.selectedFeatures || event?.detail?.selectedFeatures
  // eslint-disable-next-line no-console
  console.log('[defra-map-prototype] selected feature(s)', selected)
})

window.__defraInteractiveMap = interactiveMap
