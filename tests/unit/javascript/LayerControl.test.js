import {describe, expect, test, it, beforeEach, vi} from 'vitest'
import LayerControls from '../../../assets/javascripts/LayerControls.js'

describe('Layer Control', () => {
    let layerControls;
    let domElementMock;
    let mapMock;

    const resetMocks = () => {
        vi.resetAllMocks();

        domElementMock = {
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

        mapMock = {
            map: {
                getContainer: vi.fn().mockImplementation(() => {
                    return domElementMock
                }),
            },
        }

        vi.stubGlobal('document', {
            createElement: vi.fn().mockImplementation(() => {
                return domElementMock
            }),
        })

        vi.stubGlobal('window', {
            addEventListener: vi.fn(),
            location: {
                pathname: '/test',
            },
            history: {
                pushState: vi.fn(),
            },
        })

        vi.stubGlobal('URL', vi.fn(() => {
            return {
                searchParams: {
                    has: vi.fn().mockImplementation(() => {
                        return false
                    }),
                    delete: vi.fn(),
                    getAll: vi.fn().mockImplementation(() => {
                        return ['testLayer1', 'testLayer2']
                    }),
                },
            }
        }))
    }


    beforeEach(() => {
        // create a new instance of LayerControls before each test
        resetMocks();
        const module = document.createElement('div');
        layerControls = new LayerControls(module, mapMock, 'fakeTileSource', ['testLayer1', 'testLayer2'], { layerControlSelector: '[data-layer-control]' });


    });

    // test layerControls.createCloseButton()
    test('createCloseButton() correctly executes',() => {
        layerControls.createCloseButton();
        expect(document.createElement).toHaveBeenCalledWith('button');
        expect(domElementMock.appendChild).toHaveBeenCalled();
        expect(domElementMock.addEventListener).toHaveBeenCalled();

    });

    test('createOpenButton() correctly executes',() => {
        layerControls.createOpenButton();
        expect(document.createElement).toHaveBeenCalledWith('button');
        expect(domElementMock.appendChild).toHaveBeenCalled();
        expect(domElementMock.addEventListener).toHaveBeenCalled();

    })

    describe('togglePanel()', () => {
        test('togglePanel() correctly executes when opening',() => {
            layerControls.togglePanel({ target: { dataset: { action: 'close' }}});
            expect(domElementMock.classList.add).toHaveBeenCalled();
            expect(domElementMock.classList.add).toHaveBeenCalled();
            expect(domElementMock.setAttribute).toHaveBeenCalled();
            expect(domElementMock.focus).toHaveBeenCalled();
        })

        test('correctly executes when closing',() => {
            layerControls.togglePanel({ target: { dataset: { action: 'close' }}});
            expect(domElementMock.classList.remove).toHaveBeenCalled();
            expect(domElementMock.classList.add).toHaveBeenCalled();
            expect(domElementMock.setAttribute).toHaveBeenCalled();
            expect(domElementMock.focus).toHaveBeenCalled();
        })
    })


    test('toggleLayersBasedOnUrl() correctly executes',() => {
        layerControls.getEnabledLayerNamesFromUrl = vi.fn().mockImplementation(() => {
            return ['testLayer1', 'testLayer2']
        })
        layerControls.showEntitiesForLayers = vi.fn();
        layerControls.toggleLayersBasedOnUrl();
        expect(layerControls.showEntitiesForLayers).toHaveBeenCalledWith(['testLayer1', 'testLayer2']);
    })

    test('showEntitiesForLayers() correctly executes',() => {
        layerControls.getControlByName = vi.fn().mockImplementation((layerName) => {
            return `${layerName}-domElement`
        })
        layerControls.enable = vi.fn();
        layerControls.disable = vi.fn();

        layerControls.datasetNames = ['testLayer1', 'testLayer2', 'testLayer3'];

        layerControls.showEntitiesForLayers(['testLayer1', 'testLayer2']);

        // expect(layerControls.enable).toHaveBeenCalledWith('testLayer1-domElement');
        // expect(layerControls.enable).toHaveBeenCalledWith('testLayer2-domElement');
        // expect(layerControls.disable).toHaveBeenCalledWith('testLayer3-domElement');
    })

    // test('updateUrl() correctly executes',() => {

    // })

    // test('enabledLayers() correctly executes',() => {

    // })

    // test('disabledLayers() correctly executes',() => {

    // })

    // test('getCheckbox() correctly executes',() => {

    // })

    // test('getControlByName() correctly executes',() => {

    // })

    // test('enable() correctly executes',() => {

    // })

    // test('disable() correctly executes',() => {

    // })

    // test('getDatasetName() correctly executes',() => {

    // })

    // test('toggleLayerVisibility() correctly executes',() => {

    // })

    // test('onControlChkbxChange() correctly executes',() => {

    // })

    // test('getClickableLayers() correctly executes',() => {

    // })

})
