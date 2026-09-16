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

        vi.clearAllMocks();
    });

    describe('attach()', () => {
        test('wires up behaviour onto the pre-rendered controls panel markup',() => {
            layerControls.layers = [{dataset: 'testLayer1'}, {dataset: 'testLayer2'}];
            layerControls.availableLayers = {testLayer1: ['testLayer1-1'], testLayer2: ['testLayer2-1']};
            layerControls.updateUrl = vi.fn();
            layerControls.toggleLayersBasedOnUrl = vi.fn();

            layerControls.attach();

            expect(document.getElementById).toHaveBeenCalledWith('dl-map-settings-content');
            expect(document.getElementById).toHaveBeenCalledWith('show-historical-data');
            expect(document.getElementById).toHaveBeenCalledWith('layer-filter-input');
            expect(layerControls.layerOptions.length).toBe(2);
            expect(layerControls.$historicalDataCheckbox.addEventListener).toHaveBeenCalledWith('change', expect.any(Function));
            expect(layerControls.$textbox.addEventListener).toHaveBeenCalledWith('input', expect.any(Function));
            // no `dataset` param in the URL (default stub), so falls back to
            // writing the default-checked state to the URL
            expect(layerControls.updateUrl).toHaveBeenCalled();
        })

        test('wires up the key panel toggle/close buttons',() => {
            layerControls.layers = [];
            layerControls.availableLayers = {};
            layerControls.updateUrl = vi.fn();
            layerControls.toggleLayersBasedOnUrl = vi.fn();

            layerControls.attach();

            expect(document.getElementById).toHaveBeenCalledWith('dl-map-key-panel');
            expect(document.getElementById).toHaveBeenCalledWith('dl-map-key-panel-toggle');
            expect(document.getElementById).toHaveBeenCalledWith('dl-map-key-panel-close');
            expect(layerControls.$keyPanelToggle.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
            expect(layerControls.$keyPanelClose.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        })

        test('wires up the "Clear all filters" button',() => {
            layerControls.layers = [];
            layerControls.availableLayers = {};
            layerControls.updateUrl = vi.fn();
            layerControls.toggleLayersBasedOnUrl = vi.fn();

            layerControls.attach();

            expect(document.getElementById).toHaveBeenCalledWith('dl-map-clear-filters-wrapper');
            expect(document.getElementById).toHaveBeenCalledWith('dl-map-clear-filters-button');
            expect(layerControls.$clearFiltersButton.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
        })

        test('wires up the "Select data layers" card toggle/close buttons',() => {
            layerControls.layers = [];
            layerControls.availableLayers = {};
            layerControls.updateUrl = vi.fn();
            layerControls.toggleLayersBasedOnUrl = vi.fn();

            layerControls.attach();

            expect(document.getElementById).toHaveBeenCalledWith('dl-select-data-layers-card');
            expect(document.getElementById).toHaveBeenCalledWith('dl-select-data-layers-card-toggle');
            expect(document.getElementById).toHaveBeenCalledWith('dl-select-data-layers-card-close');
            expect(layerControls.$dataLayersCardToggle.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
            expect(layerControls.$dataLayersCardClose.addEventListener).toHaveBeenCalledWith('click', expect.any(Function));
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
        layerControls.updateKeyPanel = vi.fn();
        layerControls.updateClearFiltersLink = vi.fn();

        layerControls.showEntitiesForLayers([l1, l2]);

        expect(l1.enable).toHaveBeenCalledTimes(1);
        expect(l2.enable).toHaveBeenCalledTimes(1);
        expect(l3.disable).toHaveBeenCalledTimes(1);
        expect(layerControls.updateKeyPanel).toHaveBeenCalledTimes(1);
        expect(layerControls.updateClearFiltersLink).toHaveBeenCalledTimes(1);
    })

    describe('updateClearFiltersLink()', () => {
        test('reveals the link when one or more layers are checked',() => {
            layerControls.$clearFiltersWrapper = { setAttribute: vi.fn(), removeAttribute: vi.fn() };
            layerControls.layerOptions = [{ isChecked: () => false }, { isChecked: () => true }];

            layerControls.updateClearFiltersLink();

            expect(layerControls.$clearFiltersWrapper.removeAttribute).toHaveBeenCalledWith('hidden');
            expect(layerControls.$clearFiltersWrapper.setAttribute).not.toHaveBeenCalled();
        })

        test('hides the link when nothing is checked',() => {
            layerControls.$clearFiltersWrapper = { setAttribute: vi.fn(), removeAttribute: vi.fn() };
            layerControls.layerOptions = [{ isChecked: () => false }];

            layerControls.updateClearFiltersLink();

            expect(layerControls.$clearFiltersWrapper.setAttribute).toHaveBeenCalledWith('hidden', '');
            expect(layerControls.$clearFiltersWrapper.removeAttribute).not.toHaveBeenCalled();
        })

        test('does nothing when the link element is not present',() => {
            layerControls.$clearFiltersWrapper = null;
            layerControls.layerOptions = [{ isChecked: () => true }];

            expect(() => layerControls.updateClearFiltersLink()).not.toThrow();
        })
    })

    describe('clearAllFilters()', () => {
        test('unchecks every layer checkbox, pushes the URL update, and moves focus off itself',() => {
            const chkbx1 = { checked: true };
            const chkbx2 = { checked: true };
            const l1 = { element: { querySelector: vi.fn(() => chkbx1) } };
            const l2 = { element: { querySelector: vi.fn(() => chkbx2) } };

            layerControls.layerOptions = [l1, l2];
            layerControls.updateUrl = vi.fn();
            layerControls.$textbox = { focus: vi.fn() };

            const event = { preventDefault: vi.fn() };
            layerControls.clearAllFilters(event);

            expect(event.preventDefault).toHaveBeenCalled();
            expect(chkbx1.checked).toBe(false);
            expect(chkbx2.checked).toBe(false);
            expect(layerControls.updateUrl).toHaveBeenCalledTimes(1);
            expect(layerControls.$textbox.focus).toHaveBeenCalledTimes(1);
        })

        test('does not throw when called without an event or without a filter textbox',() => {
            layerControls.layerOptions = [];
            layerControls.updateUrl = vi.fn();
            layerControls.$textbox = null;

            expect(() => layerControls.clearAllFilters()).not.toThrow();
        })
    })

    describe('updateKeyPanel()', () => {
        const makeKeyPanel = (querySelector) => ({
            querySelector,
            classList: { toggle: vi.fn() },
            setAttribute: vi.fn(),
            removeAttribute: vi.fn(),
        })

        test('shows only checked layers\' key rows, reveals the panel, and expands it',() => {
            const row1 = { style: {} };
            const row2 = { style: {} };
            const querySelector = vi.fn((selector) => {
                if (selector === '[data-layer-key="l1"]') return row1;
                if (selector === '[data-layer-key="l2"]') return row2;
                return null;
            });

            layerControls.$keyPanel = makeKeyPanel(querySelector);
            layerControls.$keyPanelToggle = { setAttribute: vi.fn() };
            layerControls.layerOptions = [
                { getDatasetName: () => 'l1', isChecked: () => true },
                { getDatasetName: () => 'l2', isChecked: () => false },
            ];

            layerControls.updateKeyPanel();

            expect(row1.style.display).toBe('flex');
            expect(row2.style.display).toBe('none');
            expect(layerControls.$keyPanel.removeAttribute).toHaveBeenCalledWith('hidden');
            expect(layerControls.$keyPanel.setAttribute).not.toHaveBeenCalledWith('hidden', '');
            expect(layerControls.$keyPanel.classList.toggle).toHaveBeenCalledWith('dl-map-key-panel--collapsed', false);
            expect(layerControls.$keyPanelToggle.setAttribute).toHaveBeenCalledWith('aria-expanded', 'true');
        })

        test('hides the panel entirely (not just collapsed to its "Key" pill) when nothing is checked',() => {
            layerControls.$keyPanel = makeKeyPanel(vi.fn(() => null));
            layerControls.$keyPanelToggle = { setAttribute: vi.fn() };
            layerControls.layerOptions = [{ getDatasetName: () => 'l1', isChecked: () => false }];

            layerControls.updateKeyPanel();

            expect(layerControls.$keyPanel.setAttribute).toHaveBeenCalledWith('hidden', '');
            expect(layerControls.$keyPanel.removeAttribute).not.toHaveBeenCalledWith('hidden');
            expect(layerControls.$keyPanel.classList.toggle).toHaveBeenCalledWith('dl-map-key-panel--collapsed', true);
            expect(layerControls.$keyPanelToggle.setAttribute).toHaveBeenCalledWith('aria-expanded', 'false');
        })

        test('does nothing when the key panel element is not present',() => {
            layerControls.$keyPanel = null;
            layerControls.layerOptions = [{ getDatasetName: () => 'l1', isChecked: () => true }];

            expect(() => layerControls.updateKeyPanel()).not.toThrow();
        })

        test('shows the "Show historical data" row when it is checked, even with no layers selected',() => {
            const historicalRow = { style: {} };
            layerControls.$keyPanel = makeKeyPanel(
                vi.fn((selector) => (selector === '[data-layer-key="show-historical-data"]' ? historicalRow : null))
            );
            layerControls.$keyPanelToggle = { setAttribute: vi.fn() };
            layerControls.$historicalDataCheckbox = { checked: true };
            layerControls.layerOptions = [];

            layerControls.updateKeyPanel();

            expect(historicalRow.style.display).toBe('flex');
            expect(layerControls.$keyPanel.removeAttribute).toHaveBeenCalledWith('hidden');
            expect(layerControls.$keyPanel.classList.toggle).toHaveBeenCalledWith('dl-map-key-panel--collapsed', false);
        })

        test('hides the "Show historical data" row when it is unchecked',() => {
            const historicalRow = { style: {} };
            layerControls.$keyPanel = makeKeyPanel(
                vi.fn((selector) => (selector === '[data-layer-key="show-historical-data"]' ? historicalRow : null))
            );
            layerControls.$keyPanelToggle = { setAttribute: vi.fn() };
            layerControls.$historicalDataCheckbox = { checked: false };
            layerControls.layerOptions = [];

            layerControls.updateKeyPanel();

            expect(historicalRow.style.display).toBe('none');
            expect(layerControls.$keyPanel.setAttribute).toHaveBeenCalledWith('hidden', '');
        })
    })

    describe('setKeyPanelExpanded()', () => {
        test('toggles the collapsed class and aria-expanded together',() => {
            layerControls.$keyPanel = { classList: { toggle: vi.fn() } };
            layerControls.$keyPanelToggle = { setAttribute: vi.fn() };

            layerControls.setKeyPanelExpanded(true);
            expect(layerControls.$keyPanel.classList.toggle).toHaveBeenCalledWith('dl-map-key-panel--collapsed', false);
            expect(layerControls.$keyPanelToggle.setAttribute).toHaveBeenCalledWith('aria-expanded', 'true');

            layerControls.setKeyPanelExpanded(false);
            expect(layerControls.$keyPanel.classList.toggle).toHaveBeenCalledWith('dl-map-key-panel--collapsed', true);
            expect(layerControls.$keyPanelToggle.setAttribute).toHaveBeenCalledWith('aria-expanded', 'false');
        })

        test('does nothing when the key panel element is not present',() => {
            layerControls.$keyPanel = null;
            expect(() => layerControls.setKeyPanelExpanded(true)).not.toThrow();
        })
    })

    describe('setDataLayersCardExpanded()', () => {
        test('toggles the collapsed class and aria-expanded together',() => {
            layerControls.$dataLayersCard = { classList: { toggle: vi.fn() } };
            layerControls.$dataLayersCardToggle = { setAttribute: vi.fn() };

            layerControls.setDataLayersCardExpanded(true);
            expect(layerControls.$dataLayersCard.classList.toggle).toHaveBeenCalledWith('dl-map-overlay-card--collapsed', false);
            expect(layerControls.$dataLayersCardToggle.setAttribute).toHaveBeenCalledWith('aria-expanded', 'true');

            layerControls.setDataLayersCardExpanded(false);
            expect(layerControls.$dataLayersCard.classList.toggle).toHaveBeenCalledWith('dl-map-overlay-card--collapsed', true);
            expect(layerControls.$dataLayersCardToggle.setAttribute).toHaveBeenCalledWith('aria-expanded', 'false');
        })

        test('does nothing when the card element is not present',() => {
            layerControls.$dataLayersCard = null;
            expect(() => layerControls.setDataLayersCardExpanded(true)).not.toThrow();
        })
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
        expect(window.history.pushState).toHaveBeenCalledWith({}, '', 'http://localhost:3000?dataset=testLayer1&dataset=testLayer2');
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

    test('correctly displays an error message when no data layers are checked first', () => {
        const mockCheckbox = { checked: true };
        const mockErrorMessage = {};
        layerControls.$historicalDataCheckbox = mockCheckbox;
        layerControls.$settingsPanelContent = domElementMock;
        layerControls.$settingsErrorMessage = mockErrorMessage;
        layerControls.enabledLayers = vi.fn().mockReturnValue([]);
        layerControls.updateKeyPanel = vi.fn();

        layerControls.toggleHistoricalData({ target: mockCheckbox });

        expect(mockCheckbox.checked).toBe(false);
        expect(domElementMock.classList.add).toHaveBeenCalledWith('govuk-form-group--error');
        expect(domElementMock.prepend).toHaveBeenCalledWith(mockErrorMessage);
        expect(layerControls.updateKeyPanel).toHaveBeenCalled();
    })

    test('correctly removes error message when a data layer is checked', () => {
        const mockCheckbox = { checked: false };
        const mockErrorMessage = { remove: vi.fn() };
        layerControls.$historicalDataCheckbox = mockCheckbox;
        layerControls.$settingsPanelContent = domElementMock;
        layerControls.$settingsErrorMessage = mockErrorMessage;
        layerControls.enabledLayers = vi.fn().mockReturnValue([{ availableLayers: ['layer1-fill'] }]);

        layerControls.updateHistoricalCheckboxState();

        expect(domElementMock.classList.remove).toHaveBeenCalledWith('govuk-form-group--error');
        expect(mockErrorMessage.remove).toHaveBeenCalled();
    })

    test('shows historical data on the map correctly when a data layer is checked and "Show historical data" is checked', () => {
        const mockLayerOption = { availableLayers: ['layer1-fill', 'layer1-line'] };
        layerControls.$settingsPanelContent = domElementMock;
        layerControls.$settingsErrorMessage = {};
        layerControls.enabledLayers = vi.fn().mockReturnValue([mockLayerOption]);
        layerControls.mapController = { setLayerCurrentEntityFilter: vi.fn() };
        layerControls.updateKeyPanel = vi.fn();

        layerControls.toggleHistoricalData({ target: { checked: true } });

        expect(layerControls.mapController.setLayerCurrentEntityFilter).toHaveBeenCalledWith('layer1-fill', true);
        expect(layerControls.mapController.setLayerCurrentEntityFilter).toHaveBeenCalledWith('layer1-line', true);
        expect(layerControls.updateKeyPanel).toHaveBeenCalled();
    })

    test('removes historical data layers from the map upon un-checking the "Show historical data" checkboxc', () => {
        const mockLayerOption = { availableLayers: ['layer1-fill'] };
        layerControls.$settingsPanelContent = domElementMock;
        layerControls.$settingsErrorMessage = {};
        layerControls.enabledLayers = vi.fn().mockReturnValue([mockLayerOption]);
        layerControls.mapController = { setLayerCurrentEntityFilter: vi.fn() };
        layerControls.updateKeyPanel = vi.fn();

        layerControls.toggleHistoricalData({ target: { checked: false } });

        expect(layerControls.mapController.setLayerCurrentEntityFilter).toHaveBeenCalledWith('layer1-fill', false);
        expect(layerControls.updateKeyPanel).toHaveBeenCalled();
    })

    test('resets "Show historical data" checkbox when no data layers are checked', () => {
        const mockCheckbox = { checked: true };
        layerControls.$historicalDataCheckbox = mockCheckbox;
        layerControls.$settingsPanelContent = domElementMock;
        layerControls.$settingsErrorMessage = { remove: vi.fn() };
        layerControls.enabledLayers = vi.fn().mockReturnValue([]);
        layerControls.layerOptions = [{ availableLayers: ['layer1-fill'] }];
        layerControls.mapController = { setLayerCurrentEntityFilter: vi.fn() };
        layerControls.updateKeyPanel = vi.fn();

        layerControls.updateHistoricalCheckboxState();

        expect(mockCheckbox.checked).toBe(false);
        expect(layerControls.mapController.setLayerCurrentEntityFilter).toHaveBeenCalledWith('layer1-fill', false);
        expect(layerControls.updateKeyPanel).toHaveBeenCalled();
    })

    describe('layer option', () => {
        test('findElement() correctly executes',() => {
            const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);
            expect(document.querySelector).toHaveBeenCalledWith('[data-layer-control="testLayer1"]');
            expect(option.element).toEqual(domElementMock);
        })

        test('enable() correctly executes',() => {

            const mockCheckbox = {...domElementMock, checked: false}

            LayerOption.prototype.findElement = vi.fn()
            .mockImplementation(() => {
                return {
                    ...domElementMock,
                    dataset: {layerControlActive: 'false'},
                    querySelector: () => {
                        return mockCheckbox;
                    }
                };
            })

            const option = new LayerOption('testLayer1', ['testLayer1-1', 'testLayer1-2'], { updateHistoricalCheckboxState: vi.fn() });

            option.setLayerVisibility = vi.fn();
            option.enable();
            expect(option.element.dataset.layerControlActive).toEqual('true');
            expect(mockCheckbox.checked).toBe(true);
            expect(option.setLayerVisibility).toHaveBeenCalledWith(true);
        })

        test('disable() correctly executes',() => {

            const mockCheckbox = {...domElementMock, checked: true}

            LayerOption.prototype.findElement = vi.fn().mockImplementation(() => {
                return {
                    ...domElementMock,
                    dataset: {layerControlActive: 'true'},
                    querySelector: () => {
                        return mockCheckbox;
                    }
                };
            })

            const option = new LayerOption('testLayer1', ['testLayer1-1', 'testLayer1-2'], { updateHistoricalCheckboxState: vi.fn() });

            option.setLayerVisibility = vi.fn();
            option.disable();
            expect(option.element.dataset.layerControlActive).toEqual('false');
            expect(mockCheckbox.checked).toBe(false);
            expect(option.setLayerVisibility).toHaveBeenCalledWith(false);
        })

        test('getDatasetName() correctly executes',() => {
            LayerOption.prototype.findElement = vi.fn();
            const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);
            let datasetName = option.getDatasetName();
            expect(datasetName).toBe('testLayer1');
        })

        describe('setLayerVisibility()', () => {
            test('correctly executes when making visible',() => {
                LayerOption.prototype.findElement = vi.fn();
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);

                option.layerControls = {
                    mapController: {
                        setLayerVisibility: vi.fn(),
                        setLayerCurrentEntityFilter: vi.fn(),
                    }
                }
                option.setLayerVisibility(true);

                expect(option.layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-1', 'visible');
                expect(option.layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-2', 'visible');
            })

            test('correctly executes when making invisible',() => {
                LayerOption.prototype.findElement = vi.fn();
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);

                option.layerControls = {
                    mapController: {
                        setLayerVisibility: vi.fn(),
                        setLayerCurrentEntityFilter: vi.fn(),
                    }
                }
                option.setLayerVisibility(false);

                expect(option.layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-1', 'none');
                expect(option.layerControls.mapController.setLayerVisibility).toHaveBeenCalledWith('testLayer1-2', 'none');
            })
        })

        describe('setLayerCheckboxVisibility()', () => {
            test('correctly executes when making visible',() => {
                LayerOption.prototype.findElement = vi.fn().mockImplementation(() => domElementMock);
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);

                option.setLayerCheckboxVisibility(true);

                expect(domElementMock.style.display).toEqual('block');
            })

            test('correctly executes when making invisible',() => {
                LayerOption.prototype.findElement = vi.fn().mockImplementation(() => domElementMock);
                const option = new LayerOption({dataset: 'testLayer1'}, ['testLayer1-1', 'testLayer1-2'], undefined);

                option.setLayerCheckboxVisibility(false);

                expect(domElementMock.style.display).toEqual('none');
            })
        })

        describe('isChecked', () => {
            test('correctly executes when checked',() => {
                const mockCheckbox = {...domElementMock, checked: true}
                LayerOption.prototype.findElement = vi.fn().mockImplementation(() => {
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
                LayerOption.prototype.findElement = vi.fn().mockImplementation(() => {
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
