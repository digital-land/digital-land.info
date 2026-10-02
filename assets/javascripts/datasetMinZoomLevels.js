export const datasetMinZoomLevels = {
  'title-boundary': 13,
};

export const getDatasetMinZoom = (dataset) => datasetMinZoomLevels[dataset] ?? null;
