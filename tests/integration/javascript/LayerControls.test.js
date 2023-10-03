// integration tests for the layer controller

import {describe, expect, test, vi, beforeEach} from 'vitest'
import LayerControls, { LayerOption } from '../../../assets/javascripts/LayerControls'
import { getDomElementMock, getMapControllerMock, getMapMock, stubGlobalDocument, stubGlobalUrl, stubGlobalWindow } from '../../utils/mockUtils'

const domElementMock = getDomElementMock();
const mapControllerMock = getMapControllerMock();

stubGlobalDocument();

stubGlobalWindow('http://localhost:3000/', '');

const urlParams = [];
stubGlobalUrl([{name: 'dataset', value: 'layer1'}, {name: 'dataset', value: 'layer2'}]);

const layers = [
    {
        dataset: 'layer1',
        checked: true
    },
    {
        dataset: 'layer2',
        checked: true
    },
    {
        dataset: 'layer3',
        checked: false
    }
]

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

const moduleMock = {...domElementMock};
moduleMock.querySelectorAll.mockImplementation(() => {
    return [
        {
            ...domElementMock,
            dataset: {
                layerControl: 'layer1'
            },
            querySelector: vi.fn().mockImplementation(() => {
                return layer1Checkbox
            }),
        },
        {
            ...domElementMock,
            dataset: {
                layerControl: 'layer2'
            },
            querySelector: vi.fn().mockImplementation(() => {
                return layer2Checkbox
            }),
        },
        {
            ...domElementMock,
            dataset: {
                layerControl: 'layer3'
            },
            querySelector: vi.fn().mockImplementation(() => {
                return layer3Checkbox
            }),
        }
    ];
});

describe('LayerControls', () => {
    test('toggleLayersBasedOnUrl', () => {

        const layerControls = new LayerControls(mapControllerMock, undefined, layers, availableLayers, {});

        LayerOption.prototype.makeElement = vi.fn().mockImplementation(() => { return domElementMock});

        layerControls.layerOptions = layers.map((layer, index) => {
            return new LayerOption(layer, availableLayers[layer.dataset], layerControls)
        });

        layerControls.toggleLayersBasedOnUrl();

        expect(layers[0].checked).toEqual(true)
        expect(layers[1].checked).toEqual(true)
        expect(layers[2].checked).toEqual(false)

        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer1-fill', 'visible')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer1-line', 'visible')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer2-fill', 'visible')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer2-line', 'visible')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer3-fill', 'none')
        expect(mapControllerMock.setLayerVisibility).toHaveBeenCalledWith('layer3-line', 'none')
    })

    test('getClickableLayers', () => {

        const layerControls = new LayerControls(moduleMock, mapControllerMock, layers, availableLayers, {});

        layerControls.layerOptions = layers.map((layer) => {
            return {
                getDatasetName: () => layer.dataset,
                isChecked: () => layer.checked
            }
        });

        const clickableLayers = layerControls.getClickableLayers();

        expect(clickableLayers).toEqual(['layer1-fill', 'layer2-fill'])
    })
})
