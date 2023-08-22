
import {vi} from 'vitest'

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
};

const mapControllerMock = {
    map: mapMock,
    setLayerVisibility: vi.fn(),
}

const domElementMock = {
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
    removeEventListener: vi.fn(),
    setAttribute: vi.fn(),
    focus: vi.fn(),
}

const popupMock = {
    setLngLat: vi.fn().mockImplementation(() => popupMock),
    setHTML: vi.fn().mockImplementation(() => popupMock),
    addTo: vi.fn().mockImplementation(() => popupMock),
}


export const getMapMock = () => {
    return mapMock;
}

export const getMapControllerMock = () => {
    return mapControllerMock;
}

export const getDomElementMock = () => {
    return domElementMock;
}

export const getPopupMock = () => {
    return popupMock;
}

export const stubGlobalMapLibre = () => {
    return vi.stubGlobal('maplibregl', {
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
}

export const stubGlobalWindow = (pathname = 'http://localhost', hash = '') => {
    vi.stubGlobal('window', {
        addEventListener: vi.fn(),
        location: {
            pathname: pathname,
            hash: hash,
        },
        history: {
            pushState: vi.fn(),
        },
    })
}

let urlParams = [];

export const stubGlobalUrl = (urlParams = []) => {
    urlParams = urlParams || [];
    const deleteMock = vi.fn().mockImplementation((key) => {
        urlParams = urlParams.filter((param) => {
            return param.name !== key
        })
    })
    const appendMock = vi.fn().mockImplementation((name, value) => {
        urlParams.push({name, value})
    })
    vi.stubGlobal('URL', vi.fn(() => {
        return {
            searchParams: {
                has: vi.fn().mockImplementation((key) => {
                    return urlParams.some((param) => {
                        return param.name === key
                    })
                }),
                getAll: vi.fn().mockImplementation((key) => {
                    return urlParams.filter((param) => {
                        return param.name === key
                    }).map((param) => {
                        return param.value
                    })
                }),
                delete: deleteMock,
                append: appendMock,
                toString: vi.fn().mockImplementation(() => {
                    let toReturn = ''
                    urlParams.forEach((param, index) => {
                        toReturn += `${index > 0 ? '&' : ''}${param.name}=${param.value}`
                    })
                    return toReturn;
                })
            }
        }
    }))
    return [deleteMock, appendMock]
}

export const stubGlobalDocument = (location = 'http://localhost:3000/?layers=layer1&layers=layer2') => {
    vi.stubGlobal('document', {
        createElement: vi.fn().mockImplementation(() => {
            return domElementMock
        }),
        querySelector: vi.fn().mockImplementation(() => {
            return domElementMock
        }),
        location: location
    })
}

export const stubGlobalTurf = (boundingBox) => {
    vi.stubGlobal('turf', {
        extent: vi.fn().mockReturnValue(boundingBox || [1,2,3,4])
    })
}
