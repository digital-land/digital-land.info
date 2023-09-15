import {describe, expect, test, beforeEach} from 'vitest'
import {newMapController, capitalizeFirstLetter} from '../../../assets/javascripts/utils.js'
import { stubGlobalDocument, stubGlobalFetch, stubGlobalMapLibre, waitForMapCreation } from '../../utils/mockUtils.js'

stubGlobalMapLibre();
stubGlobalFetch();
stubGlobalDocument();

describe('utils', () => {
    test('newMapController works as expected', async () => {
        const mapController = newMapController();
        await waitForMapCreation(mapController)
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
