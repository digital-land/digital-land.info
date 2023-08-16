import {describe, expect, test, vi} from 'vitest'
import MapController from '../../../assets/javascripts/MapController'

describe('Map Controller', () => {

    const mockSuccessCallback = vi.fn().mockImplementation((src, callback) => {
        callback(false, 'the Image');
    });

    vi.stubGlobal('maplibregl', {
            Map: vi.fn().mockImplementation(() => {
                return {
                    on: vi.fn(),
                    loadImage: vi.fn().mockImplementation(mockSuccessCallback),
                    addImage: vi.fn(),
                }
            })
        }
    )

    const mapController = new MapController()

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

    test('addVectorTileSource() correctly executes', () => {
        mapController.addVectorTileSource()
    })

    test('addGeojsonSources() correctly executes', () => {

    })

    test('addPoint() correctly executes', () => {

    })

    test('addPolygon() correctly adds controls', () => {

    })

    test('addLayer() correctly adds a layer', () => {

    })

    test('flyTo() correctly executes', () => {

    })

    test('removeDuplicates() correctly removes duplicate features', () => {

    })

    test('createFeaturesPopupHtml() correctly creates a popup', () => {

    })

    test('getFillColour() correctly returns a fill colour', () => {

    })
})
