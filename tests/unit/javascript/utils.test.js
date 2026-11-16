import {describe, expect, test, beforeEach, afterEach, vi} from 'vitest'
import {
    newMapController,
    capitalizeFirstLetter,
    isMapSupported,
    MAP_UNSUPPORTED_MESSAGE,
    resetMapSupportCheck,
} from '../../../assets/javascripts/utils.js'
import { stubGlobalDocument, stubGlobalFetch, stubGlobalMapLibre, waitForMapCreation } from '../../utils/mockUtils.js'

stubGlobalMapLibre();
stubGlobalFetch();
stubGlobalDocument();

// A canvas whose getContext('webgl2') returns the given value.
const stubCanvas = (webgl2Context) => {
    document.createElement.mockImplementation((tag) => {
        return tag === 'canvas' ? { getContext: () => webgl2Context } : {};
    });
}

// A map element inside a wrapper that has a loading overlay.
const stubMapElement = () => {
    const loader = { remove: vi.fn() };
    const mapElement = {
        textContent: '',
        closest: () => ({ querySelector: () => loader }),
    };
    document.getElementById.mockImplementation(() => mapElement);
    return { mapElement, loader };
}

describe('utils', () => {
    const maplibreStub = globalThis.maplibregl;

    beforeEach(() => {
        globalThis.maplibregl = maplibreStub;
        resetMapSupportCheck();
        stubCanvas({});
    })

    afterEach(() => {
        globalThis.maplibregl = maplibreStub;
    })

    test('newMapController works as expected', async () => {
        const mapController = newMapController();
        await waitForMapCreation(mapController)
        expect(mapController).toBeDefined();
        expect(mapController.map).toBeDefined();
    })

    describe('when the browser cannot show the map', () => {
        test('isMapSupported is false without WebGL2', () => {
            stubCanvas(null);
            expect(isMapSupported()).toBe(false);
        })

        test('isMapSupported is false if MapLibre did not load', () => {
            globalThis.maplibregl = undefined;
            expect(isMapSupported()).toBe(false);
        })

        test('newMapController shows a message instead of the map', () => {
            stubCanvas(null);
            const { mapElement, loader } = stubMapElement();

            const mapController = newMapController({ layers: [], mapId: 'test-map' });

            expect(mapController).toBeNull();
            expect(document.getElementById).toHaveBeenCalledWith('test-map');
            expect(mapElement.textContent).toBe(MAP_UNSUPPORTED_MESSAGE);
            expect(loader.remove).toHaveBeenCalled();
        })
    })

    // Each WebGL context counts against the browser's per-page limit (16 in
    // Chrome); going over it drops the oldest context and blanks that map. A
    // page of search results has one map per entity, so the support check must
    // not add a context per map.
    describe('the WebGL2 support check', () => {
        test('runs once per page, however many maps there are', () => {
            document.createElement.mockClear();
            for (let i = 0; i < 9; i++) {
                expect(isMapSupported()).toBe(true);
            }
            const canvases = document.createElement.mock.calls.filter(([tag]) => tag === 'canvas');
            expect(canvases).toHaveLength(1);
        })

        test('releases the context it creates', () => {
            const loseContext = vi.fn();
            stubCanvas({ getExtension: (name) => name === 'WEBGL_lose_context' ? { loseContext } : null });

            expect(isMapSupported()).toBe(true);
            expect(loseContext).toHaveBeenCalledTimes(1);
        })

        test('remembers that WebGL2 is unsupported too', () => {
            stubCanvas(null);
            expect(isMapSupported()).toBe(false);
            stubCanvas({});
            expect(isMapSupported()).toBe(false);
        })

        test('still checks for MapLibre every time', () => {
            expect(isMapSupported()).toBe(true);
            globalThis.maplibregl = undefined;
            expect(isMapSupported()).toBe(false);
        })
    })

    test('capitalizeFirstLetter works as expected', () => {

        const testCases = [
            ['hello', 'Hello'],
            ['Hello', 'Hello'],
            ['1hello', '1hello']
        ];

        testCases.forEach(([input, expected]) => {
            expect(capitalizeFirstLetter(input)).toBe(expected)
        })
    })
})
