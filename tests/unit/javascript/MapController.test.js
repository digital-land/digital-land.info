import {describe, expect, test, vi, beforeEach} from 'vitest'
import MapController from '../../../assets/javascripts/MapController'
import {
    stubGlobalMapLibre, stubGlobalTurf
} from '../../utils/mockUtils.js';

describe('Map Controller - Unit', () => {

    stubGlobalMapLibre();

    let mapController;

    beforeEach(() => {
        mapController = new MapController()
    })

    test('loadImages() correctly loads images', () => {
        mapController.loadImages(
            [
                {
                    src: 'test',
                    name: 'test'
                },
                {
                    src: 'test2',
                    name: 'test2'
                }
            ]
        )
        expect(mapController.map.loadImage).toHaveBeenCalledTimes(2)
        expect(mapController.map.addImage).toHaveBeenCalledTimes(2)

        expect(mapController.map.loadImage).toHaveBeenCalledWith('test', expect.any(Function))
        expect(mapController.map.loadImage).toHaveBeenCalledWith('test2', expect.any(Function))

        expect(mapController.map.addImage).toHaveBeenCalledWith('test', 'the Image', {sdf: true})
        expect(mapController.map.addImage).toHaveBeenCalledWith('test2', 'the Image', {sdf: true})
    })

    test('addVectorTileSources() correctly executes', () => {
        mapController.addVectorTileSource = vi.fn().mockImplementation((mockSource) => {
            return mockSource.name + '-layer'
        })
        const layers = mapController.addVectorTileSources([
            {
                name: 'testName',
                vectorSource: 'testVectorSource',
            },
            {
                name: 'testName2',
                vectorSource: 'testVectorSource2',
            }
        ])
        expect(mapController.addVectorTileSource).toHaveBeenCalledTimes(2)
        expect(mapController.addVectorTileSource).toHaveBeenCalledWith({
            name: 'testName',
            vectorSource: 'testVectorSource',
        })
        expect(mapController.addVectorTileSource).toHaveBeenCalledWith({
            name: 'testName2',
            vectorSource: 'testVectorSource2',
        })
        expect(layers).toEqual({
            'testName': 'testName-layer',
            'testName2': 'testName2-layer'
        })
    })

    test('addVectorTileSource() correctly executes when adding a point', () => {
        mapController.addLayer = vi.fn().mockImplementation((layerOptions) => {
            return `${layerOptions.sourceName}-${layerOptions.layerType}`
        })

        const minMapZoom = 10;
        const maxMapZoom = 20;

        mapController.minMapZoom = minMapZoom;
        mapController.maxMapZoom = maxMapZoom;


        const layers1 = mapController.addVectorTileSource({
            name: 'testName',
            vectorSource: 'testVectorSource',
            dataType: 'point',
            styleProps: {
                colour: 'red',
                opacity: 0.8,
                weight: 5,
            }
        })
        const layers2 = mapController.addVectorTileSource({
            name: 'testName2',
            vectorSource: 'testVectorSource2',
            dataType: 'point',
            styleProps: {
                colour: 'blue',
                opacity: 0.8,
                weight: 5,
            }
        })
        expect(mapController.addLayer).toHaveBeenCalledTimes(2)

        expect(mapController.map.addSource).toHaveBeenCalledTimes(2)

        expect(mapController.map.addSource).toHaveBeenCalledWith('testName-source', {
			type: 'vector',
			tiles: ['testVectorSource'],
			minzoom: minMapZoom,
			maxzoom: maxMapZoom,
		})

        expect(mapController.map.addSource).toHaveBeenCalledWith('testName2-source', {
            type: 'vector',
            tiles: ['testVectorSource2'],
            minzoom: minMapZoom,
            maxzoom: maxMapZoom,
        })

        expect(mapController.addLayer).toHaveBeenCalledWith({
            sourceName: 'testName-source',
            layerType: 'circle',
            paintOptions: {
                'circle-color': 'red',
                'circle-opacity': 0.8,
                'circle-stroke-color': 'red',
                'circle-radius': 8,
            },
            sourceLayer: `testName`,
        })

        expect(mapController.addLayer).toHaveBeenCalledWith({
            sourceName: 'testName2-source',
            layerType: 'circle',
            paintOptions: {
                'circle-color': 'blue',
                'circle-opacity': 0.8,
                'circle-stroke-color': 'blue',
                'circle-radius': 8,
            },
            sourceLayer: `testName2`,
        })

        expect(layers1).toEqual(['testName-source-circle']);
        expect(layers2).toEqual(['testName2-source-circle']);

    })

    test('addGeojsonSources() correctly executes', () => {
        mapController.addPoint = vi.fn();
        mapController.addPolygon = vi.fn();

        mapController.addGeojsonSources([
            {
                name: 'testName',
                data: {
                    type: 'Point',
                }
            },
            {
                name: 'testName1',
                data: {
                    type: 'Polygon',
                }
            },
            {
                name: 'testName2',
                data: {
                    type: 'MultiPolygon',
                }
            }
        ])

        expect(mapController.addPoint).toHaveBeenCalledTimes(1)
        expect(mapController.addPolygon).toHaveBeenCalledTimes(2)
    })

    describe('addPoint()', () => {
        test('addPoint() correctly executes without layer controls or an image', () => {
            mapController.map.addSource = vi.fn()
            mapController.addLayer = vi.fn().mockImplementation((layerOptions) => {
                return `${layerOptions.sourceName}-${layerOptions.layerType}`
            })

            const layerName = mapController.addPoint({
                name: 'testName-source',
                data: {
                    type: 'Point',
                }
            })

            expect(mapController.map.addSource).toHaveBeenCalledTimes(1)
            expect(mapController.addLayer).toHaveBeenCalledTimes(1)

            expect(layerName).toEqual('testName-source-circle')

        })

        test('addPoint() correctly executes with layer controls and no image', () => {
            mapController.map.addSource = vi.fn()
            mapController.addLayer = vi.fn().mockImplementation((layerOptions) => {
                return `${layerOptions.sourceName}-${layerOptions.layerType}`
            })
            mapController.paint_options = {
                colour: 'red'
            }

            const layerName = mapController.addPoint({
                name: 'testName-source',
                data: {
                    type: 'Point',
                }
            })

            expect(mapController.map.addSource).toHaveBeenCalledTimes(1)
            expect(mapController.addLayer).toHaveBeenCalledTimes(1)

            expect(mapController.addLayer.mock.calls[0][0].paintOptions['circle-color']).toEqual('red')

            expect(layerName).toEqual('testName-source-circle')

        })

        test('addPoint() correctly executes with an image', () => {
            mapController.map.addSource = vi.fn()
            mapController.map.hasImage = vi.fn().mockImplementation((imageId) => {
                return imageId == 'myTestImageId'
            })
            mapController.addLayer = vi.fn().mockImplementation((layerOptions) => {
                return `${layerOptions.sourceName}-${layerOptions.layerType}`
            })
            mapController.$layerControlsList = [1,2,3]
            mapController.$layerControlsList.getFillColour = vi.fn().mockImplementation(() => {
                return 'red'
            })

            const layerName = mapController.addPoint({
                name: 'testName-source',
                data: {
                    type: 'Point',
                }
            }, 'myTestImageId')

            expect(mapController.map.addSource).toHaveBeenCalledTimes(1)
            expect(mapController.addLayer).toHaveBeenCalledTimes(1)

            expect(layerName).toEqual('testName-source-symbol')

        })
    })


    test('addPolygon() correctly adds controls', () => {
        mapController.map.addSource = vi.fn()
        mapController.addLayer = vi.fn().mockImplementation((layerOptions) => {
            return `${layerOptions.sourceName}-${layerOptions.layerType}`
        })
        mapController.paint_options = {
            colour: '#088'
        }

        let geometry = {
            name: 'testName-source',
            data: {
                type: 'Polygon',
            },
            entity: 'testEntity',
        };

        mapController.addPolygon(geometry)

        expect(mapController.addLayer).toHaveBeenCalledTimes(1)
        expect(mapController.map.addSource).toHaveBeenCalledTimes(1)

        expect(mapController.addLayer).toHaveBeenCalledWith({
            sourceName: geometry.name,
            layerType: 'fill',
            paintOptions: {
              'fill-color': '#088',
              'fill-opacity': 0.5
            },
        })

        expect(mapController.map.addSource).toHaveBeenCalledWith(geometry.name, {
            'type': 'geojson',
            'data': {
              'type': 'Feature',
              'geometry': geometry.data,
              'properties': {
                'entity': geometry.entity,
                'name': geometry.name,
              }
            },
        })
    })

    test('addLayer() correctly adds a layer', () => {
        mapController.map.addLayer = vi.fn()

        const testParams = {
            sourceName: 'testSourceName',
            layerType: 'testLayerType',
            paintOptions: {
                'testPaintOption': 'testPaintOptionValue'
            },
            layoutOptions: {
                'testLayoutOption': 'testLayoutOptionValue'
            },
            sourceLayer: 'testSourceLayer',
            additionalOptions: {
                'testAdditionalOption': 'testAdditionalOptionValue'
            },
        }

        mapController.addLayer(testParams)

        expect(mapController.map.addLayer).toHaveBeenCalledTimes(1)
        expect(mapController.map.addLayer).toHaveBeenCalledWith({
            id: `${testParams.sourceName}-${testParams.layerType}`,
            type: testParams.layerType,
            source: testParams.sourceName,
            'source-layer': testParams.sourceLayer,
            paint: testParams.paintOptions,
            layout: testParams.layoutOptions,
            ...testParams.additionalOptions
        })
    })

    describe('flyTo()', () => {
        test('correctly executes flying to a point', () => {
            mapController.map.flyTo = vi.fn()
            mapController.map.fitBounds = vi.fn()
            stubGlobalTurf();

            const fakeGeometry = {
                data: {
                    type: 'Point',
                    coordinates: [1,2]
                }
            }

            mapController.flyTo(fakeGeometry)

            expect(mapController.map.flyTo).toHaveBeenCalledTimes(1)
            expect(mapController.map.flyTo).toHaveBeenCalledWith({
                center: fakeGeometry.data.coordinates,
                essential: true,
                animate: false,
                zoom: 15,
            })

            expect(mapController.map.fitBounds).toHaveBeenCalledTimes(0)
        })

        test('correctly executes flying to a polygon', () => {
            mapController.map.flyTo = vi.fn()
            mapController.map.fitBounds = vi.fn()


            const mockBoundingBox = [1,2,3,4]
            stubGlobalTurf(mockBoundingBox);

            const fakeGeometry = {
                data: {
                    type: 'polygon',
                    coordinates: [1,2]
                }
            }

            mapController.flyTo(fakeGeometry)

            expect(mapController.map.flyTo).toHaveBeenCalledTimes(0)
            expect(mapController.map.fitBounds).toHaveBeenCalledTimes(1)
            expect(mapController.map.fitBounds).toHaveBeenCalledWith(mockBoundingBox, {padding: 20, animate: false})

        })

    })

    test('removeDuplicates() correctly removes duplicate features', () => {

        const mockFeatures = [
            { properties: { entity: 'testEntity1' } },
            { properties: { entity: 'testEntity2' } },
            { properties: { entity: 'testEntity1' } },
            { properties: { entity: 'testEntity2' } },
            { properties: { entity: 'testEntity3' } },
            { properties: { entity: 'testEntity3' } },
            { properties: { entity: 'testEntity4' } },
            { properties: { entity: 'testEntity1' } },
        ]

        const uniqueFeatures = mapController.removeDuplicates(mockFeatures)

        expect(uniqueFeatures).toEqual([
            { properties: { entity: 'testEntity1' } },
            { properties: { entity: 'testEntity2' } },
            { properties: { entity: 'testEntity3' } },
            { properties: { entity: 'testEntity4' } },
        ])
    })

    describe('createFeaturesPopupHtml()', () => {
        test('correctly creates a popup', () => {
            mapController.getFillColour = vi.fn().mockImplementation(() => {
                return 'red'
            })

            const mockFeatures = [
                {
                    sourceLayer: 'testSourceLayer1',
                    properties: {
                        name: 'testName1',
                        reference: 'testReference1',
                        entity: 'testEntity1'
                    }
                },
            ]

            const html = mapController.createFeaturesPopupHtml(mockFeatures)

            expect(html).toContain('testName1')
            expect(html).toContain(`href="/entity/${mockFeatures[0].properties.entity}`)
        })

        test('correctly creates a popup for a feature without a name', () => {
            mapController.getFillColour = vi.fn().mockImplementation(() => {
                return 'red'
            })

            const mockFeatures = [
                {
                    sourceLayer: 'testSourceLayer1',
                    properties: {
                        name: '',
                        reference: 'testReference1',
                        entity: 'testEntity1'
                    }
                },
            ]

            const html = mapController.createFeaturesPopupHtml(mockFeatures)

            expect(html).toContain('testReference1')
            expect(html).toContain(`href="/entity/${mockFeatures[0].properties.entity}`)
            expect(html).toContain('border-left: 5px solid red')
        })

        test('correctly creates a popup for a feature without a name or reference', () => {
            mapController.getFillColour = vi.fn().mockImplementation(() => {
                return 'red'
            })

            const mockFeatures = [
                {
                    sourceLayer: 'testSourceLayer1',
                    properties: {
                        name: '',
                        reference: '',
                        entity: 'testEntity1'
                    }
                },
            ]

            const html = mapController.createFeaturesPopupHtml(mockFeatures)

            expect(html).toContain('Not Named')
            expect(html).toContain(`href="/entity/${mockFeatures[0].properties.entity}`)
        })

    })

    describe('getFillColour()', () => {
        test('getFillColour() correctly queries for a fill colour', () => {
            const getPaintMock = vi.fn()
            mapController.map.getLayer = vi.fn().mockImplementation(() => {
                return {
                    getPaintProperty: getPaintMock
                }
            })
            mapController.getFillColour({ layer: { type: 'fill' } })
            expect(getPaintMock).toHaveBeenCalledTimes(1)
            expect(getPaintMock).toHaveBeenCalledWith('fill-color')
        })

        test('getFillColour() correctly queries for a symbol colour', () => {
            const getPaintMock = vi.fn()
            mapController.map.getLayer = vi.fn().mockImplementation(() => {
                return {
                    getPaintProperty: getPaintMock
                }
            })
            mapController.getFillColour({ layer: { type: 'symbol' } })
            expect(getPaintMock).toHaveBeenCalledTimes(1)
            expect(getPaintMock).toHaveBeenCalledWith('icon-color')
        })

        test('getFillColour() correctly queries for a circle colour', () => {
            const getPaintMock = vi.fn()
            mapController.map.getLayer = vi.fn().mockImplementation(() => {
                return {
                    getPaintProperty: getPaintMock
                }
            })
            mapController.getFillColour({ layer: { type: 'circle' } })
            expect(getPaintMock).toHaveBeenCalledTimes(1)
            expect(getPaintMock).toHaveBeenCalledWith('circle-color')
        })
    })

    test('setLayerVisibility() correctly forwards the request onto the map', () => {
        mapController.map.setLayoutProperty = vi.fn()
        mapController.setLayerVisibility('testLayer', true)
        expect(mapController.map.setLayoutProperty).toHaveBeenCalledTimes(1)
        expect(mapController.map.setLayoutProperty).toHaveBeenCalledWith('testLayer', 'visibility', true)
    })
})
