import { describe, expect, test } from 'vitest'
import { datasetMinZoomLevels, getDatasetMinZoom } from '../../../assets/javascripts/datasetMinZoomLevels.js'

describe('datasetMinZoomLevels', () => {
  test('getDatasetMinZoom() returns the configured zoom for a restricted dataset', () => {
    expect(getDatasetMinZoom('title-boundary')).toEqual(13)
  })

  test('getDatasetMinZoom() returns null for an unrestricted dataset', () => {
    expect(getDatasetMinZoom('area-of-outstanding-natural-beauty')).toBeNull()
  })

  test('getDatasetMinZoom() returns null for an unknown dataset', () => {
    expect(getDatasetMinZoom(undefined)).toBeNull()
  })
})
