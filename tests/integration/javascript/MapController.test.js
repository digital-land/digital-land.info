// integration tests for the map controller

import {describe, expect, test, vi, beforeEach} from 'vitest'
import MapController from '../../../assets/javascripts/MapController'
import TiltControl from '../../../assets/javascripts/TiltControl';

vi.stubGlobal('window', {
    addEventListener: vi.fn(),
    location: {
        pathname: '/test',
        hash: 'testHash',
    },
    history: {
        pushState: vi.fn(),
    },
})

const urlDeleteMock = vi.fn();
    const urlAppendMock = vi.fn().mockImplementation(() => {
        console.log('run');
    })
    vi.stubGlobal('URL', vi.fn(() => {
        return {
            searchParams: {
                params: [],
                toString: vi.fn().mockImplementation(() => {
                    return 'layer=Layer1-domElement&layer=Layer2-domElement'
                }),
                has: vi.fn().mockImplementation(() => {
                    return false
                }),
                delete: vi.fn(),
                getAll: vi.fn().mockImplementation(() => {
                    return ['testLayer1', 'testLayer2']
                }),
                append: vi.fn(),
            },
        }
    }))

let domElementMock = {
    querySelector: vi.fn(),
    querySelectorAll: vi.fn().mockImplementation(() => {
        return []
    }),
    closest: vi.fn().mockImplementation(() => {
        return domElementMock;
    }),
    classList: {
        remove: vi.fn(),
        add: vi.fn(),
    },
    dataset: {
        layerControl: 'testLayer1',
    },
    appendChild: vi.fn(),
    addEventListener: vi.fn(),
    setAttribute: vi.fn(),
    focus: vi.fn(),
}

const mapMock = {
    events: {},
    on: vi.fn().mockImplementation((event, callback) => {
        mapMock.events[event] = callback;
    }),
    loadImage: vi.fn().mockImplementation(vi.fn().mockImplementation((src, callback) => {
        callback(false, 'the Image');
    })),
    addImage: vi.fn(),
    hasImage: vi.fn().mockImplementation(() => {
        return true;
    }),
    addSource: vi.fn(),
    addLayer: vi.fn(),
    addControl: vi.fn(),
    flyTo: vi.fn(),
    getContainer: vi.fn().mockImplementation(() => {
        return domElementMock;
    }),
    queryRenderedFeatures: vi.fn().mockImplementation(() => {
        return [
            {
                sourceLayer: 'testSourceLayer',
                source: 'testSource',
                properties: {
                    name: 'testName',
                    entity: 'testEntity',
                    reference: 'testReference',
                },
                layer: {
                    type: 'symbol',
                }
            },
            {
                sourceLayer: 'testSourceLayer',
                source: 'testSource2',
                properties: {
                    name: 'testName2',
                    entity: 'testEntity2',
                    reference: 'testReference2',
                },
                layer: {
                    type: 'fill',
                }
            },
        ];
    }),
    getLayer: vi.fn().mockImplementation(() => {
        return {
            getPaintProperty: vi.fn().mockImplementation(() => {
                return 'red'
            })
        }
    }),
}

const popupMock = {
    setLngLat: vi.fn().mockImplementation(() => popupMock),
    setHTML: vi.fn().mockImplementation(() => popupMock),
    addTo: vi.fn().mockImplementation(() => popupMock),
}

vi.stubGlobal('maplibregl', {
    Map: vi.fn().mockImplementation(() => {
        return mapMock
    }),
    ScaleControl: vi.fn(),
    NavigationControl: vi.fn(),
    FullscreenControl: vi.fn(),
    Popup: vi.fn().mockImplementation(() => {
        return popupMock
    }),
})

vi.stubGlobal('document', {
    createElement: vi.fn().mockImplementation(() => {
        return domElementMock
    }),
    querySelector: vi.fn().mockImplementation(() => {
        return domElementMock
    })
})

beforeEach(() => {
    vi.clearAllMocks()
})


describe('Map Controller', () => {

    describe('Constructor', () => {
        test('Works as expected, applying default params', async () => {
            const mapController = new MapController()

            expect(mapController.map.events.load).toBeDefined()

            await mapController.map.events.load() // initiate the load event

            expect(mapController).toBeDefined()
            expect(mapController.map).toBeDefined()

            expect(mapController.mapId).toEqual('mapid');
            expect(mapController.mapContainerSelector).toEqual('.dl-map__wrapper');
            expect(mapController.vectorTileSources).toEqual([]);
            expect(mapController.datasetVectorUrl).toEqual(null);
            expect(mapController.datasets).toEqual(null);
            expect(mapController.minMapZoom).toEqual(5);
            expect(mapController.maxMapZoom).toEqual(15);
            expect(mapController.baseURL).toEqual('https://digital-land.github.io');
            expect(mapController.baseTileStyleFilePath).toEqual('./base-tiles-2.json');
            expect(mapController.popupWidth).toEqual('260px');
            expect(mapController.popupMaxListLength).toEqual(10);
            expect(mapController.LayerControlOptions).toEqual({enabled: false});
            expect(mapController.ZoomControlsOptions).toEqual({enabled: false});
            expect(mapController.FullscreenControl).toEqual({enabled: false});
            expect(mapController.geojsons).toEqual([]);
            expect(mapController.images).toEqual([{src: '/static/images/location-pointer-sdf.png', name: 'custom-marker'}]);
            expect(mapController.paint_options).toEqual(null);

            expect(mapController.map.loadImage).toHaveBeenCalledOnce();
            expect(mapController.map.addImage).toHaveBeenCalledOnce();
            expect(mapController.map.loadImage).toHaveBeenCalledWith('/static/images/location-pointer-sdf.png', expect.any(Function));
            expect(mapController.map.addImage).toHaveBeenCalledWith('custom-marker', 'the Image', {sdf: true});

            expect(mapController.map.addControl).toHaveBeenCalledTimes(3);
            expect(mapController.map.addControl).toHaveBeenCalledWith(new maplibregl.ScaleControl, 'top-left');
            expect(mapController.map.addControl).toHaveBeenCalledWith(new maplibregl.NavigationControl, 'top-left');
            expect(mapController.map.addControl).toHaveBeenCalledWith(new TiltControl, 'top-left');
        })

        test('Works as expected, enabling full screen', async () => {
            const mapController = new MapController({
                FullscreenControl: {
                    enabled: true,
                }
            })

            expect(mapController.map.events.load).toBeDefined()

            await mapController.map.events.load() // initiate the load event

            expect(mapController).toBeDefined()
            expect(mapController.map).toBeDefined()

            expect(mapController.mapId).toEqual('mapid');
            expect(mapController.mapContainerSelector).toEqual('.dl-map__wrapper');
            expect(mapController.vectorTileSources).toEqual([]);
            expect(mapController.datasetVectorUrl).toEqual(null);
            expect(mapController.datasets).toEqual(null);
            expect(mapController.minMapZoom).toEqual(5);
            expect(mapController.maxMapZoom).toEqual(15);
            expect(mapController.baseURL).toEqual('https://digital-land.github.io');
            expect(mapController.baseTileStyleFilePath).toEqual('./base-tiles-2.json');
            expect(mapController.popupWidth).toEqual('260px');
            expect(mapController.popupMaxListLength).toEqual(10);
            expect(mapController.LayerControlOptions).toEqual({enabled: false});
            expect(mapController.ZoomControlsOptions).toEqual({enabled: false});
            expect(mapController.FullscreenControl).toEqual({enabled: true});
            expect(mapController.geojsons).toEqual([]);
            expect(mapController.images).toEqual([{src: '/static/images/location-pointer-sdf.png', name: 'custom-marker'}]);
            expect(mapController.paint_options).toEqual(null);

            expect(mapController.map.loadImage).toHaveBeenCalledOnce();
            expect(mapController.map.addImage).toHaveBeenCalledOnce();
            expect(mapController.map.loadImage).toHaveBeenCalledWith('/static/images/location-pointer-sdf.png', expect.any(Function));
            expect(mapController.map.addImage).toHaveBeenCalledWith('custom-marker', 'the Image', {sdf: true});

            expect(mapController.map.addControl).toHaveBeenCalledTimes(4);
            expect(mapController.map.addControl).toHaveBeenCalledWith(new maplibregl.ScaleControl, 'top-left');
            expect(mapController.map.addControl).toHaveBeenCalledWith(new maplibregl.NavigationControl, 'top-left');
            expect(mapController.map.addControl).toHaveBeenCalledWith(new maplibregl.FullscreenControl, 'bottom-left');
            expect(mapController.map.addControl).toHaveBeenCalledWith(new TiltControl, 'top-left');
        })

        test('Works with one geojson feature of type point', async () => {
            const params = {
                geojsons: [
                    {
                        name: 'testName',
                        data: {
                            type: 'Point',
                        },
                        entity: 'testEntity',
                    }
                ],
                paint_options: {
                    colour: '#0000ff',
                }
            }

            const mapController = new MapController(params)
            await mapController.map.events.load() // initiate the load event

            expect(mapController.map.addSource).toHaveBeenCalledOnce();
            expect(mapController.map.addLayer).toHaveBeenCalledOnce();
            expect(mapController.map.addSource).toHaveBeenCalledWith(params.geojsons[0].name, {
                'type': 'geojson',
                'data': {
                  'type': 'Feature',
                  'geometry': params.geojsons[0].data,
                  'properties': {
                    'entity': params.geojsons[0].entity,
                    'name': params.geojsons[0].name,
                  }
                }
            });
            const layerName = `${params.geojsons[0].name}-symbol`;
            expect(mapController.map.addLayer).toHaveBeenCalledWith({
                id: layerName,
                type: 'symbol',
                source: params.geojsons[0].name,
                'source-layer': '',
                paint: {
                    'icon-color': params.paint_options.colour,
                },
                layout: {
                    'icon-image': 'custom-marker',
                    'icon-anchor': 'bottom',
                    // get the year from the source's "year" property
                    'text-field': ['get', 'year'],
                    'text-font': [
                        'Open Sans Semibold',
                        'Arial Unicode MS Bold'
                    ],
                    'text-offset': [0, 1.25],
                    'text-anchor': 'top'
                }
            })

        })

        test('Works with many geojson features of type point', async () => {
            const params = {
                geojsons: [
                    {
                        name: 'testName',
                        data: {
                            type: 'Point',
                        }
                    },
                    {
                        name: 'testName1',
                        data: {
                            type: 'Point',
                        }
                    },
                    {
                        name: 'testName2',
                        data: {
                            type: 'Point',
                        }
                    }
                ]
            }

            const mapController = new MapController(params)
            await mapController.map.events.load() // initiate the load event

            expect(mapController.map.addSource).toHaveBeenCalledTimes(3);
            expect(mapController.map.addLayer).toHaveBeenCalledTimes(3);

            params.geojsons.forEach((geojson, index) => {
                expect(mapController.map.addSource).toHaveBeenCalledWith(params.geojsons[index].name, {
                    'type': 'geojson',
                    'data': {
                      'type': 'Feature',
                      'geometry': params.geojsons[index].data,
                      'properties': {
                        'entity': params.geojsons[index].entity,
                        'name': params.geojsons[index].name,
                      }
                    }
                });
                const layerName = `${params.geojsons[index].name}-symbol`;
                expect(mapController.map.addLayer).toHaveBeenCalledWith({
                    id: layerName,
                    type: 'symbol',
                    source: params.geojsons[index].name,
                    'source-layer': '',
                    paint: {
                        'icon-color': 'blue',
                    },
                    layout: {
                        'icon-image': 'custom-marker',
                        'icon-anchor': 'bottom',
                        // get the year from the source's "year" property
                        'text-field': ['get', 'year'],
                        'text-font': [
                            'Open Sans Semibold',
                            'Arial Unicode MS Bold'
                        ],
                        'text-offset': [0, 1.25],
                        'text-anchor': 'top'
                    }
                })
            })
        })

        test('Works with many geojson features of type polygon/MultiPolygon', async () => {
            const params = {
                geojsons: [
                    {
                        name: 'testName',
                        data: {
                            type: 'Polygon',
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
                ]
            }

            const mapController = new MapController(params)
            await mapController.map.events.load() // initiate the load event

            expect(mapController.map.addSource).toHaveBeenCalledTimes(3);
            expect(mapController.map.addLayer).toHaveBeenCalledTimes(3);

            params.geojsons.forEach((geojson, index) => {
                expect(mapController.map.addSource).toHaveBeenCalledWith(params.geojsons[index].name, {
                    'type': 'geojson',
                    'data': {
                      'type': 'Feature',
                      'geometry': params.geojsons[index].data,
                      'properties': {
                        'entity': params.geojsons[index].entity,
                        'name': params.geojsons[index].name,
                      }
                    }
                });
                const layerName = `${params.geojsons[index].name}-fill`;
                expect(mapController.map.addLayer).toHaveBeenCalledWith({
                    id: layerName,
                    type: 'fill',
                    source: params.geojsons[index].name,
                    'source-layer': '',
                    paint: {
                        'fill-color': 'blue',
                        'fill-opacity': 0.5
                    },
                    layout: {}
                })
            })
        })

        test('Works with many geojson features of type polygon with layer controls enabled', async () => {
            const params = {
                geojsons: [
                    {
                        name: 'testName',
                        data: {
                            type: 'Polygon',
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
                ],
                LayerControlOptions: {
                    enabled: true,
                },
            }

            const mapController = new MapController(params)
            await mapController.map.events.load() // initiate the load event

            expect(mapController.layerControlsComponent).toBeDefined();
        })

        test('Works with a point vectorSource layer', async () => {
            const minMapZoom = 10;
            const maxMapZoom = 20;
            const params = {
                vectorTileSources: [
                    {
                        name: 'testName',
                        vectorSource: 'testUrl',
                        dataType: 'point',
                        styleProps: {
                            colour: '#0000ff',
                            opacity: 0.5,
                        }
                    }
                ],
                LayerControlOptions: {
                    enabled: true,
                },
                minMapZoom: minMapZoom,
                maxMapZoom: maxMapZoom,
            }

            const mapController = new MapController(params)
            await mapController.map.events.load() // initiate the load event

            expect(mapController.map.addSource).toHaveBeenCalledOnce();
            expect(mapController.map.addLayer).toHaveBeenCalledOnce();
            expect(mapController.map.addSource).toHaveBeenCalledWith(params.vectorTileSources[0].name + '-source', {
                type: 'vector',
                tiles: [params.vectorTileSources[0].vectorSource],
                minzoom: minMapZoom,
                maxzoom: maxMapZoom
            });
            expect(mapController.map.addLayer).toHaveBeenCalledWith({
                id: `${params.vectorTileSources[0].name}-source-circle`,
                type: 'circle',
                source: `${params.vectorTileSources[0].name}-source`,
                'source-layer': `${params.vectorTileSources[0].name}`,
                paint: {
                    'circle-color': params.vectorTileSources[0].styleProps.colour,
                    'circle-opacity': params.vectorTileSources[0].styleProps.opacity,
                    'circle-stroke-color': params.vectorTileSources[0].styleProps.colour,
                    'circle-radius': 8,
                  },
                layout: {}
            });
            expect(mapController.availableLayers).toEqual({
                [params.vectorTileSources[0].name]: [`${params.vectorTileSources[0].name}-source-circle`]
            })
        })

        test('Works with a polygon vectorSource layer', async () => {
            const minMapZoom = 10;
            const maxMapZoom = 20;
            const params = {
                vectorTileSources: [
                    {
                        name: 'testName',
                        vectorSource: 'testUrl',
                        dataType: 'polygon',
                        styleProps: {
                            colour: '#0000ff',
                            opacity: 0.5,
                        },
                    },
                ],
                minMapZoom,
                maxMapZoom,
                LayerControlOptions: {
                    enabled: true,
                }
            }

            const mapController = new MapController(params)
            await mapController.map.events.load() // initiate the load event

            expect(mapController.map.addSource).toHaveBeenCalledOnce();
            expect(mapController.map.addLayer).toHaveBeenCalledTimes(2);
            expect(mapController.map.addSource).toHaveBeenCalledWith(params.vectorTileSources[0].name + '-source', {
                type: 'vector',
                tiles: [params.vectorTileSources[0].vectorSource],
                minzoom: minMapZoom,
                maxzoom: maxMapZoom
            });
            expect(mapController.map.addLayer).toHaveBeenCalledWith({
                id: `${params.vectorTileSources[0].name}-source-fill`,
                type: 'fill',
                source: `${params.vectorTileSources[0].name}-source`,
                'source-layer': `${params.vectorTileSources[0].name}`,
                paint: {
                    'fill-color': params.vectorTileSources[0].styleProps.colour,
                    'fill-opacity': params.vectorTileSources[0].styleProps.opacity,
                },
                layout: {}
            });
            expect(mapController.map.addLayer).toHaveBeenCalledWith({
                id: `${params.vectorTileSources[0].name}-source-line`,
                type: 'line',
                source: `${params.vectorTileSources[0].name}-source`,
                'source-layer': `${params.vectorTileSources[0].name}`,
                paint: {
                    'line-color': params.vectorTileSources[0].styleProps.colour,
                    'line-width': 1,
                },
                layout: {}
            });
            expect(mapController.availableLayers).toEqual({
                [params.vectorTileSources[0].name]: [`${params.vectorTileSources[0].name}-source-fill`, `${params.vectorTileSources[0].name}-source-line`]
            })
        })
    })

    test('clickHandler works as expected', async () => {
        const mapController = new MapController({
            LayerControlOptions: {
                enabled: true,
            },
        })
        await mapController.map.events.load() // initiate the load event

        const mockClickEvent = {
            point: {
                x: 100,
                y: 100,
            },
            lngLat: {
                lng: 100,
                lat: 100,
            },
        }

        mapController.clickHandler(mockClickEvent);

        expect(maplibregl.Popup).toHaveBeenCalledOnce();
        expect(popupMock.setLngLat).toHaveBeenCalledOnce();
        expect(popupMock.setHTML).toHaveBeenCalledOnce();
        expect(popupMock.addTo).toHaveBeenCalledOnce();
        expect(popupMock.setLngLat).toHaveBeenCalledWith(mockClickEvent.lngLat);

        const expectedHTML = `<div class=\"app-popup\"><h3 class=\"app-popup-heading\">2 features selected</h3><ul class=\"app-popup-list\">
<li class=\"app-popup-item\" style=\"border-left: 5px solid red\">
<p class=\"app-u-secondary-text govuk-!-margin-bottom-0 govuk-!-margin-top-0\">TestSourceLayer</p>
<p class=\"dl-small-text govuk-!-margin-top-0 govuk-!-margin-bottom-0\">
<a class='govuk-link' href=\"/entity/testEntity\">testName</a>
</p>
</li><li class=\"app-popup-item\" style=\"border-left: 5px solid red\">
<p class=\"app-u-secondary-text govuk-!-margin-bottom-0 govuk-!-margin-top-0\">TestSourceLayer</p>
<p class=\"dl-small-text govuk-!-margin-top-0 govuk-!-margin-bottom-0\">
<a class='govuk-link' href=\"/entity/testEntity2\">testName2</a>
</p>
</li></ul></div>`;

        expect(popupMock.setHTML).toHaveBeenCalledWith(expectedHTML);
        expect(popupMock.addTo).toHaveBeenCalledWith(mapController.map);
    })
})
