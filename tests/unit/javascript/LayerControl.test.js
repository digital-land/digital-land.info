import {describe, expect, test, it, beforeEach, vi} from 'vitest'

import LayerControls from '../../../assets/javascripts/LayerControls.js'

describe('Layer Control', () => {
    let layerControls;
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
    let mapMock = {
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

    beforeEach(() => {
        const module = document.createElement('div');
        layerControls = new LayerControls(module, mapMock, 'fakeTileSource', ['testLayer1', 'testLayer2'], { layerControlSelector: '[data-layer-control]' });
        vi.clearAllMocks();
    });

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

    test('getEnabledLayerNamesFromUrl() correctly executes',() => {
        vi.stubGlobal('URL', vi.fn(() => {
            return {
                searchParams: {
                    has: vi.fn().mockImplementation(() => {
                        return true
                    }),
                    delete: vi.fn(),
                    getAll: vi.fn().mockImplementation((param) => {
                        if(param == 'layer')
                            return ['testLayer1', 'testLayer2', 'testLayer3', 'testLayer4']
                    }),
                },
            }
        }))
        layerControls.datasetNames = ['testLayer1', 'testLayer2', 'testLayer3'];
        const enabledLayers = layerControls.getEnabledLayerNamesFromUrl();
        expect(enabledLayers).toEqual(['testLayer1', 'testLayer2', 'testLayer3']);
    })

    test('showEntitiesForLayers() correctly executes',() => {
        vi.stubGlobal('URL', vi.fn(() => {
            return {
                searchParams: {
                    has: vi.fn().mockImplementation(() => {
                        return true
                    }),
                    delete: vi.fn(),
                    getAll: vi.fn().mockImplementation((param) => {
                        if(param == 'layer')
                            return ['testLayer1', 'testLayer2', 'testLayer3', 'testLayer4']
                    }),
                },
            }
        }))
        vi.spyOn(Array.prototype, 'forEach');
        layerControls.getControlByName = vi.fn().mockImplementation((layerName) => {
            return `${layerName}-domElement`
        })
        layerControls.enable = vi.fn();
        layerControls.disable = vi.fn();

        layerControls.datasetNames = ['testLayer1', 'testLayer2', 'testLayer3'];

        layerControls.showEntitiesForLayers(['testLayer1', 'testLayer2']);

        expect(layerControls.enable).toHaveBeenCalledTimes(2);
        expect(layerControls.disable).toHaveBeenCalledTimes(1);
    })

    test('updateUrl() correctly executes',() => {
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
                    delete: urlDeleteMock,
                    getAll: vi.fn().mockImplementation(() => {
                        return ['testLayer1', 'testLayer2']
                    }),
                    append: urlAppendMock,
                },
            }
        }))

        urlAppendMock.mockClear();
        urlDeleteMock.mockClear();

        layerControls.getDatasetName = vi.fn().mockImplementation((layerName) => {
            return `${layerName}-domElement`
        })
        layerControls.enabledLayers = vi.fn().mockImplementation(() => {
            return ['testLayer1', 'testLayer2']
        })
        layerControls.toggleLayersBasedOnUrl = vi.fn();
        layerControls.updateUrl();

        expect(urlDeleteMock).toHaveBeenCalledTimes(1);
        expect(urlDeleteMock).toHaveBeenCalledWith('layer');
        expect(urlAppendMock).toHaveBeenCalledTimes(2);
        expect(urlAppendMock).toHaveBeenCalledWith('layer','testLayer1-domElement');
        expect(urlAppendMock).toHaveBeenCalledWith('layer','testLayer2-domElement');
        expect(window.history.pushState).toHaveBeenCalled();
        expect(window.history.pushState).toHaveBeenCalledWith({}, '', '/test?layer=Layer1-domElement&layer=Layer2-domElementtestHash');
        expect(layerControls.toggleLayersBasedOnUrl).toHaveBeenCalled();
    })

    test('enabledLayers() correctly executes',() => {
        layerControls.getCheckbox = vi.fn().mockImplementation((layer) => {
            return { checked: layer == 'testLayer1' }
        });

        layerControls.$controls = ['testLayer1', 'testLayer2', 'testLayer3'];

        const filteredLayers = layerControls.enabledLayers();

        expect(filteredLayers).toEqual(['testLayer1']);
    })

    test('disabledLayers() correctly executes',() => {
        layerControls.getCheckbox = vi.fn().mockImplementation((layer) => {
            return { checked: layer == 'testLayer1' }
        });

        layerControls.$controls = ['testLayer1', 'testLayer2', 'testLayer3'];

        const filteredLayers = layerControls.disabledLayers();

        expect(filteredLayers).toEqual(['testLayer2', 'testLayer3']);
    })

    test('getCheckbox() correctly executes',() => {
        layerControls.getCheckbox(domElementMock);
        expect(domElementMock.querySelector).toHaveBeenCalledWith('input[type="checkbox"]');
    })

    test('getControlByName() correctly executes',() => {
        layerControls.$controls = [{
            dataset: {
                layerControl: 'testLayer1',
            }
        },{
            dataset: {
                layerControl: 'testLayer2',
            }
        },{
            dataset: {
                layerControl: 'testLayer3',
            }
        }];
        let control = layerControls.getControlByName('testLayer2');
        expect(control).toEqual({
            dataset: {
                layerControl: 'testLayer2',
            }
        });
    })

    test('enable() correctly executes',() => {
        layerControls.getDatasetName = vi.fn().mockImplementation((layer) => {
            return `${layer.dataset.layerControl}`
        })
        let domQueriedElementMock = {
            checked: '',
        }
        domElementMock.querySelector = vi.fn().mockImplementation(() => {
            return domQueriedElementMock
        })

        layerControls.toggleLayerVisibility = vi.fn();
        layerControls.enable(domElementMock);
        expect(domElementMock.querySelector).toHaveBeenCalledWith('input[type="checkbox"]');
        expect(domElementMock.classList.remove).toHaveBeenCalledWith('deactivated-control');
        expect(layerControls.toggleLayerVisibility).toHaveBeenCalledWith('testLayer1', true);
        expect(domQueriedElementMock.checked).toBe(true);
        expect(domElementMock.dataset.layerControlActive).toBe('true');
    })

    test('disable() correctly executes',() => {
        layerControls.getDatasetName = vi.fn().mockImplementation((layer) => {
            return `${layer.dataset.layerControl}`
        })
        let domQueriedElementMock = {
            checked: '',
        }
        domElementMock.querySelector = vi.fn().mockImplementation(() => {
            return domQueriedElementMock
        })

        layerControls.toggleLayerVisibility = vi.fn();
        layerControls.disable(domElementMock);
        expect(domElementMock.querySelector).toHaveBeenCalledWith('input[type="checkbox"]');
        expect(domElementMock.classList.add).toHaveBeenCalledWith('deactivated-control');
        expect(layerControls.toggleLayerVisibility).toHaveBeenCalledWith('testLayer1', false);
        expect(domQueriedElementMock.checked).toBe(false);
        expect(domElementMock.dataset.layerControlActive).toBe('false');
    })

    test('getDatasetName() correctly executes',() => {
        let mockElement = {
            dataset: {
                layerControl: 'testLayer1',
            }
        };
        let datasetName = layerControls.getDatasetName(mockElement);
        expect(datasetName).toBe('testLayer1');
    })

    describe('toggleLayerVisibility()', () => {

        test('correctly executes when making visible',() => {
            layerControls.mapController.setLayerVisibility = vi.fn();
            layerControls.availableLayers = { testLayer1: ['testLayer1-1', 'testLayer1-2'], unselected: ['unselected-1', 'unselected-2'] };
            layerControls.toggleLayerVisibility('testLayer1', true);
            expect(layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-1', 'visible');
            expect(layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-2', 'visible');
            expect(layerControls.mapController.setLayerVisibility).not.toHaveBeenCalledWith('unselected-1', 'visible');
            expect(layerControls.mapController.setLayerVisibility).not.toHaveBeenCalledWith('unselected-2', 'visible');
        })

        test('correctly executes when making invisible',() => {
            layerControls.mapController.setLayerVisibility = vi.fn();
            layerControls.availableLayers = { testLayer1: ['testLayer1-1', 'testLayer1-2'], unselected: ['unselected-1', 'unselected-2'] };
            layerControls.toggleLayerVisibility('testLayer1', false);
            expect(layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-1', 'none');
            expect(layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-2', 'none');
            expect(layerControls.mapController.setLayerVisibility).not.toHaveBeenCalledWith('unselected-1', 'none');
            expect(layerControls.mapController.setLayerVisibility).not.toHaveBeenCalledWith('unselected-2', 'none');
        })
    })


    test('onControlChkbxChange() correctly executes',() => {
        layerControls.updateUrl = vi.fn();
        layerControls.onControlChkbxChange({ target: { dataset: { layerControl: 'testLayer1' } } });
        expect(layerControls.updateUrl).toHaveBeenCalledTimes(1);
    })

    test('getClickableLayers() correctly executes',() => {
        layerControls.enabledLayers = vi.fn().mockImplementation(() => {
            return ['testLayer1', 'testLayer2']
        })
        layerControls.getDatasetName = vi.fn().mockImplementation((layer) => {
            return layer
        })
        layerControls.availableLayers = { testLayer1: ['testLayer1-1', 'testLayer1-2'], testLayer2: ['testLayer2-1', 'testLayer2Fill'] };
        let clickableLayers = layerControls.getClickableLayers();

        expect(clickableLayers).toEqual(['testLayer1-1', 'testLayer2Fill']);
    })

})
