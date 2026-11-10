import {describe, expect, test, beforeEach, afterEach, vi} from 'vitest'
import {
    newMapController,
    capitalizeFirstLetter,
    isMapSupported,
    MAP_UNSUPPORTED_MESSAGE,
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
