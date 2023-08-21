// integration tests for the layer controller

import {describe, expect, test, vi, beforeEach} from 'vitest'
import LayerControls from '../../../assets/javascripts/LayerControls'


/*
    key integration tests for the layer controller
        - toggleLayersBasedOnUrl
        - onControlChkbxChange
            - will need to mock URL and window global objects
        - getClickableLayers
*/

const domElementMock = {
    classList: {
        add: vi.fn(),
        remove: vi.fn()
    },
    dataset: {},
    appendChild: vi.fn(),
    addEventListener: vi.fn(),
}

const mapControllerMock = {
    map: {
        getContainer: vi.fn().mockImplementation(() => domElementMock)
    },
    setLayerVisibility: vi.fn(),
}

vi.stubGlobal('document', {
    createElement: vi.fn().mockImplementation(() => domElementMock),
    location: ''
})

vi.stubGlobal('window', {
    addEventListener: vi.fn(),
    location: {
        pathname: 'http://localhost:3000/',
        hash: ''
    },
    history: {
        pushState: vi.fn()
    }
})

const urlParams = [];

vi.stubGlobal('URL', vi.fn(() => {
    return {
        searchParams: {
            has: vi.fn().mockImplementation(() => true),
            getAll: vi.fn().mockImplementation(() => ['layer1', 'layer2']),
            delete: vi.fn(),
            append: vi.fn().mockImplementation((name, value) => {
                urlParams.push({name, value})
            }),
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

const availableLayers = {
    layer1: ['layer1-fill', 'layer1-line'],
    layer2: ['layer2-fill', 'layer2-line'],
    layer3: ['layer3-fill', 'layer3-line'],
}

let layer1Checkbox = {
    checked: false
};
let layer2Checkbox = {
    checked: false
};
let layer3Checkbox = {
    checked: true
};

const moduleMock = {
    querySelectorAll: vi.fn().mockImplementation(() => {
        return [
            {
                dataset: {
                    layerControl: 'layer1'
                },
                querySelector: vi.fn().mockImplementation(() => {
                    return layer1Checkbox
                }),
                classList: {
                    add: vi.fn(),
                    remove: vi.fn()
                },
                addEventListener: vi.fn()
            },
            {
                dataset: {
                    layerControl: 'layer2'
                },
                querySelector: vi.fn().mockImplementation(() => {
                    return layer2Checkbox
                }),
                classList: {
                    add: vi.fn(),
                    remove: vi.fn()
                },
                addEventListener: vi.fn()
            },
            {
                dataset: {
                    layerControl: 'layer3'
                },
                querySelector: vi.fn().mockImplementation(() => {
                    return layer3Checkbox
                }),
                classList: {
                    add: vi.fn(),
                    remove: vi.fn()
                },
                addEventListener: vi.fn()
            }
        ];
    }),
    closest: vi.fn().mockImplementation(() => domElementMock)
}

vi.stubGlobal('document', {
    createElement: vi.fn().mockImplementation(() => domElementMock),
    location: 'http://localhost:3000/?layers=layer1&layers=layer2'
})

describe('LayerControls', () => {
    test('toggleLayersBasedOnUrl', () => {

        const layerControls = new LayerControls(moduleMock, mapControllerMock, undefined, availableLayers, {});
        layerControls.toggleLayersBasedOnUrl();

        expect(layer1Checkbox.checked).toEqual(true)
        expect(layer2Checkbox.checked).toEqual(true)
        expect(layer3Checkbox.checked).toEqual(false)

        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer1-fill', 'visible')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer1-line', 'visible')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer2-fill', 'visible')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer2-line', 'visible')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer3-fill', 'none')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer3-line', 'none')
    })

    test('onControlChkbxChange', () => {

        const layerControls = new LayerControls(moduleMock, mapControllerMock, undefined, availableLayers, {});
        layerControls.onControlChkbxChange({target: 'unused'});

        expect(window.history.pushState).toHaveBeenCalledWith({}, '', 'http://localhost:3000/?layer=layer1&layer=layer2')
    })

    test('getClickableLayers', () => {
        const layerControls = new LayerControls(moduleMock, mapControllerMock, undefined, availableLayers, {});
        const clickableLayers = layerControls.getClickableLayers();

        expect(clickableLayers).toEqual(['layer1-fill', 'layer2-fill'])
    })
})
