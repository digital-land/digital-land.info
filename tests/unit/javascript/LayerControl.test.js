import {describe, expect, test, it, beforeEach, vi} from 'vitest'

import LayerControls from '../../../assets/javascripts/LayerControls.js'
import { LayerOption } from '../../../assets/javascripts/LayerControls.js';
import {
    getDomElementMock,
    getMapMock,
    getUrlDeleteMock,
    getUrlAppendMock,
    stubGlobalDocument,
    stubGlobalUrl,
    stubGlobalWindow
} from '../../utils/mockUtils.js';

describe('Layer Controls', () => {
    let layerControls;
    const domElementMock = getDomElementMock();
    const mapMock = getMapMock();

    stubGlobalDocument();
    stubGlobalWindow('http://localhost:3000', '');
    stubGlobalUrl();

    beforeEach(() => {
        const module = document.createElement('div');
        layerControls = new LayerControls(module, {map: mapMock}, 'fakeTileSource', ['testLayer1', 'testLayer2'], { layerControlSelector: '[data-layer-control]' });
        layerControls.$sidePanelContent = domElementMock;
        layerControls._container = domElementMock;
        layerControls.$openBtn = domElementMock;
        layerControls.$closeBtn = domElementMock;

        vi.clearAllMocks();
    });

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
        const makeMockLayerOption = (name) => {
            return {
                getDatasetName: () => { return name },
            }
        }
        const l1 = makeMockLayerOption('testLayer1');
        const l2 = makeMockLayerOption('testLayer2');
        const l3 = makeMockLayerOption('testLayer3');

        layerControls.getEnabledLayersFromUrl = vi.fn().mockImplementation(() => {
            return [l1, l2]
        })
        layerControls.layerOptions = [l1,l2,l3];
        layerControls.showEntitiesForLayers = vi.fn();
        layerControls.toggleLayersBasedOnUrl();
        expect(layerControls.showEntitiesForLayers).toHaveBeenCalledWith([l1, l2]);
    })

    test('getEnabledLayerNamesFromUrl() correctly executes',() => {
        stubGlobalUrl([{name: 'dataset', value: 'testLayer1'}, {name: 'dataset', value: 'testLayer2'}, {name: 'dataset', value: 'testLayer3'}, {name: 'dataset', value: 'testLayer4'}]);
        const makeMockLayerOption = (name) => {
            return {
                getDatasetName: () => { return name },
            }
        }
        const l1 = makeMockLayerOption('testLayer1');
        const l2 = makeMockLayerOption('testLayer2');
        const l3 = makeMockLayerOption('testLayer3');

        layerControls.layerOptions = [l1,l2,l3]

        const enabledLayers = layerControls.getEnabledLayersFromUrl();
        expect(enabledLayers).toEqual([l1, l2, l3]);
    })

    test('showEntitiesForLayers() correctly executes',() => {
        stubGlobalUrl([{name: 'dataset', value: 'testLayer1'}, {name: 'dataset', value: 'testLayer2'}, {name: 'dataset', value: 'testLayer3'}, {name: 'dataset', value: 'testLayer4'}]);

        const makeMockLayerOption = (name) => {
            return {
                getDatasetName: () => { return name },
                enable: vi.fn(),
                disable: vi.fn(),
            }
        }

        const l1 = makeMockLayerOption('testLayer1');
        const l2 = makeMockLayerOption('testLayer2');
        const l3 = makeMockLayerOption('testLayer3');

        layerControls.layerOptions = [l1,l2,l3];

        layerControls.showEntitiesForLayers([l1, l2]);

        expect(l1.enable).toHaveBeenCalledTimes(1);
        expect(l2.enable).toHaveBeenCalledTimes(1);
        expect(l3.disable).toHaveBeenCalledTimes(1);
    })

    test('updateUrl() correctly executes',() => {
        const [urlDeleteMock, urlAppendMock] = stubGlobalUrl([]);

        layerControls.layerOptions = [
            {
                getDatasetName: () => { return 'testLayer1' },
                isChecked: () => { return true },
            },
            {
                getDatasetName: () => { return 'testLayer2' },
                isChecked: () => { return true },
            }
        ]

        layerControls.toggleLayersBasedOnUrl = vi.fn();
        layerControls.updateUrl();

        expect(urlDeleteMock).toHaveBeenCalledTimes(1);
        expect(urlDeleteMock).toHaveBeenCalledWith('dataset');
        expect(urlAppendMock).toHaveBeenCalledTimes(2);
        expect(urlAppendMock).toHaveBeenCalledWith('dataset','testLayer1');
        expect(urlAppendMock).toHaveBeenCalledWith('dataset','testLayer2');
        expect(window.history.pushState).toHaveBeenCalled();
        expect(window.history.pushState).toHaveBeenCalledWith({}, '', 'http://localhost:3000');
        expect(layerControls.toggleLayersBasedOnUrl).toHaveBeenCalled();
    })

    test('filterCheckboxes() correctly executes',() => {

        layerControls.filterCheckboxesArr = vi.fn().mockImplementation(() => {
            return ['test1', 'test2'];
        });
        layerControls.displayMatchingCheckboxes = vi.fn();
        layerControls.filterCheckboxes({target: {value: 'test'}});

        expect(layerControls.filterCheckboxesArr).toHaveBeenCalledWith('test');
        expect(layerControls.displayMatchingCheckboxes).toHaveBeenCalledWith(['test1', 'test2']);

    })

    test('filterCheckboxesArray() correctly executes',() => {
        const generateLayerControlWithName = (name) => {
            return {
                textContent: name,
                getDatasetName: () => { return name }
            }
        }

        const BrownfieldLandCheckbox = generateLayerControlWithName('Brownfield-land');
        const GreenBeltCheckbox = generateLayerControlWithName('Green-belt');
        const TreeCheckbox = generateLayerControlWithName('Tree');

        layerControls.layerOptions = [
            BrownfieldLandCheckbox,
            GreenBeltCheckbox,
            TreeCheckbox
        ]

        let filteredCheckboxes = layerControls.filterCheckboxesArr('l');
        expect(filteredCheckboxes).toEqual([BrownfieldLandCheckbox, GreenBeltCheckbox]);

        filteredCheckboxes = layerControls.filterCheckboxesArr('la');
        expect(filteredCheckboxes).toEqual([BrownfieldLandCheckbox]);

        filteredCheckboxes = layerControls.filterCheckboxesArr('nothing Should Return');
        expect(filteredCheckboxes).toEqual([]);

        filteredCheckboxes = layerControls.filterCheckboxesArr('');
        expect(filteredCheckboxes).toEqual([BrownfieldLandCheckbox, GreenBeltCheckbox, TreeCheckbox]);
    })

    test('displayMatchingCheckboxes() correctly executes',() => {
        const generateLayerOption = (name) => {
            return {
                style: {
                    display: '',
                },
                setLayerCheckboxVisibility: vi.fn(),
            }
        }

        const BrownfieldLandCheckbox = generateLayerOption('Brownfield-land');
        const GreenBeltCheckbox = generateLayerOption('Green-belt');
        const TreeCheckbox = generateLayerOption('Tree');

        layerControls.layerOptions = [
            BrownfieldLandCheckbox,
            GreenBeltCheckbox,
            TreeCheckbox
        ]

        layerControls.displayMatchingCheckboxes([BrownfieldLandCheckbox, GreenBeltCheckbox]);
        expect(BrownfieldLandCheckbox.setLayerCheckboxVisibility).toHaveBeenCalledWith(true);
        expect(GreenBeltCheckbox.setLayerCheckboxVisibility).toHaveBeenCalledWith(true);
        expect(TreeCheckbox.setLayerCheckboxVisibility).toHaveBeenCalledWith(false);

    })

    test('getClickableLayers() correctly executes',() => {
        layerControls.enabledLayers = vi.fn().mockImplementation(() => {
            return [
                {
                    getDatasetName: () => 'testLayer1',
                },
                {
                    getDatasetName: () => 'testLayer2'
                },
            ]
        })
        layerControls.availableLayers = { testLayer1: ['testLayer1-1', 'testLayer1-2'], testLayer2: ['testLayer2-1', 'testLayer2Fill'] };
        let clickableLayers = layerControls.getClickableLayers();

        expect(clickableLayers).toEqual(['testLayer1-1', 'testLayer2Fill']);
    })

    describe('layer option', () => {
        test('makeElement() correctly executes',() => {
            let spy = vi.spyOn(LayerOption.prototype, 'makeLayerSymbol').mockImplementation(() => { return ''});
            const option = new LayerOption('testLayer1', ['testLayer1-1', 'testLayer1-2'], undefined);
            expect(option.element).toEqual(domElementMock);
            spy.mockRestore();
        })

        describe('makeLayerSymbol()', () => {
            test('correctly executes when type is fill',() => {
                const layerOptionMock = {
                    paint_options: {
                        type: 'fill',
                        opacity: 0.5,
                        colour: '#AABBCC',
                    },
                    dataset: 'testLayer1',
                    name: 'TestLayer1',
                }

                const result = LayerOption.prototype.makeLayerSymbol(layerOptionMock);

                expect(result).toContain('border-color: #AABBCC;')
                expect(result).toContain('background: #AABBCC7f')
                expect(result).toContain('TestLayer1')
            })

            test('correctly executes when type is point',() => {
                const layerOptionMock = {
                    paint_options: {
                        type: 'point',
                        opacity: 0.5,
                        colour: '#AABBCC',
                    },
                    dataset: 'testLayer1',
                    name: 'TestLayer1',
                }

                const result = LayerOption.prototype.makeLayerSymbol(layerOptionMock);

                expect(result).toContain('fill: #AABBCC;')
                expect(result).toContain('opacity: 0.5;')
                expect(result).toContain('TestLayer1')
            })
        })

        test('enable() correctly executes',() => {

            const mockCheckbox = {...domElementMock, checked: false}

            LayerOption.prototype.makeElement = vi.fn()
            .mockImplementation(() => {
                return {
                    ...domElementMock,
                    dataset: {layerControlActive: 'false'},
                    querySelector: () => {
                        return mockCheckbox;
                    }
                };
            })

            const option = new LayerOption('testLayer1', ['testLayer1-1', 'testLayer1-2'], undefined);

            option.setLayerVisibility = vi.fn();
            option.enable();
            expect(option.element.dataset.layerControlActive).toEqual('true');
            expect(mockCheckbox.checked).toBe(true);
            expect(option.setLayerVisibility).toHaveBeenCalledWith(true);
        })

        test('disable() correctly executes',() => {

            const mockCheckbox = {...domElementMock, checked: true}

            LayerOption.prototype.makeElement = vi.fn().mockImplementation(() => {
                return {
                    ...domElementMock,
                    dataset: {layerControlActive: 'true'},
                    querySelector: () => {
                        return mockCheckbox;
                    }
                };
            })

            const option = new LayerOption('testLayer1', ['testLayer1-1', 'testLayer1-2'], undefined);

            option.setLayerVisibility = vi.fn();
            option.disable();
            expect(option.element.dataset.layerControlActive).toEqual('false');
            expect(mockCheckbox.checked).toBe(false);
            expect(option.setLayerVisibility).toHaveBeenCalledWith(false);
        })

        test('getDatasetName() correctly executes',() => {
            LayerOption.prototype.makeElement = vi.fn();
            const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);
            let datasetName = option.getDatasetName();
            expect(datasetName).toBe('testLayer1');
        })

        describe('setLayerVisibility()', () => {
            test('correctly executes when making visible',() => {
                LayerOption.prototype.makeElement = vi.fn();
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);

                option.layerControls = {
                    mapController: {
                        setLayerVisibility: vi.fn(),
                    }
                }
                option.setLayerVisibility(true);

                expect(option.layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-1', 'visible');
                expect(option.layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-2', 'visible');
            })

            test('correctly executes when making invisible',() => {
                LayerOption.prototype.makeElement = vi.fn();
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);

                option.layerControls = {
                    mapController: {
                        setLayerVisibility: vi.fn(),
                    }
                }
                option.setLayerVisibility(false);

                expect(option.layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-1', 'none');
                expect(option.layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-2', 'none');
            })
        })

        describe('setLayerCheckboxVisibility()', () => {
            test('correctly executes when making visible',() => {
                LayerOption.prototype.makeElement = vi.fn().mockImplementation(() => domElementMock);
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);

                option.setLayerCheckboxVisibility(true);

                expect(domElementMock.style.display).toEqual('block');
            })

            test('correctly executes when making invisible',() => {
                LayerOption.prototype.makeElement = vi.fn().mockImplementation(() => domElementMock);
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);

                option.setLayerCheckboxVisibility(false);

                expect(domElementMock.style.display).toEqual('none');
            })
        })

        describe('isChecked', () => {
            test('correctly executes when checked',() => {
                const mockCheckbox = {...domElementMock, checked: true}
                LayerOption.prototype.makeElement = vi.fn().mockImplementation(() => {
                    return {
                        ...domElementMock,
                        dataset: {layerControlActive: 'false'},
                        querySelector: () => {
                            return mockCheckbox;
                        }
                    };
                })
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);
                const result = option.isChecked();
                expect(result).toBe(true);
            })

            test('correctly executes when not checked',() => {
                const mockCheckbox = {...domElementMock, checked: false}
                LayerOption.prototype.makeElement = vi.fn().mockImplementation(() => {
                    return {
                        ...domElementMock,
                        dataset: {layerControlActive: 'false'},
                        querySelector: () => {
                            return mockCheckbox;
                        }
                    };
                })
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);
                const result = option.isChecked();
                expect(result).toBe(false);
            })
        })

        test('replaceRedirectParamNames works as expected', () => {
            stubGlobalUrl([{name: 'dataset', value: 'testLayer1'}, {name: 'unchanged', value: 'testLayer2'}, {name: 'layer', value: 'testLayer3'}, {name: 'layer', value: 'testLayer4'}]);
            let layerControlsMock = {
                redirectURLParamNames: ['layer'],
                layerURLParamName: 'dataset',
                replaceRedirectParamNames: LayerControls.prototype.replaceRedirectParamNames,
            }
            layerControlsMock.replaceRedirectParamNames();

            expect(window.history.replaceState).toHaveBeenCalledWith({}, '', 'http://localhost:3000?dataset=testLayer1&unchanged=testLayer2&dataset=testLayer3&dataset=testLayer4');
        })

    })

})
