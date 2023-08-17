import {describe, expect, test, vi, beforeEach} from 'vitest'
import {newMapController, capitalizeFirstLetter} from '../../assets/javascripts/utils.js'

vi.stubGlobal('maplibregl', {
    Map: vi.fn().mockImplementation(() => {
        return {
            on: vi.fn(),
            loadImage: vi.fn().mockImplementation(vi.fn().mockImplementation((src, callback) => {
                callback(false, 'the Image');
            })),
            addImage: vi.fn(),
            addSource: vi.fn(),
        }
    })
}
)

describe('utils', () => {
    test('newMapController works as expected', () => {
        const mapController = newMapController();
        expect(mapController).toBeDefined();
        expect(mapController.map).toBeDefined();
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
