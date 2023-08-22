import {describe, expect, test, vi, beforeEach} from 'vitest'
import {newMapController, capitalizeFirstLetter} from '../../../assets/javascripts/utils.js'
import { stubGlobalMapLibre } from '../../utils/mockUtils.js'

stubGlobalMapLibre();

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
