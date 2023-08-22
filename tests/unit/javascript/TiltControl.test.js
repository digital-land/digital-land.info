import {describe, expect, test, vi, beforeEach} from 'vitest'
import TiltControl from '../../../assets/javascripts/TiltControl.js'
import { getDomElementMock, getMapMock, stubGlobalDocument } from '../../utils/mockUtils.js'

stubGlobalDocument();
const domElementMock = getDomElementMock();

describe('Tilt Control', () => {

    let tiltControl;
    beforeEach(() => {
        tiltControl = new TiltControl()
        vi.clearAllMocks()
    })

    test('onAdd() correctly executes', () => {
        tiltControl.clickHandler = vi.fn()
        const mapMock = getMapMock()
        tiltControl.onAdd(mapMock)
        expect(domElementMock.addEventListener).toHaveBeenCalledTimes(1)
        expect(mapMock.on).toHaveBeenCalledTimes(1)
    })

    test('onRemove() correctly executes', () => {
        tiltControl._map = {
            removeEventListener: vi.fn(),
        }
        tiltControl._container = {
            parentNode: {
                removeChild: vi.fn(),
            },
        }
        tiltControl.button = document.createElement('button')
        tiltControl.onRemove()
        expect(tiltControl._container.parentNode.removeChild).toHaveBeenCalledTimes(1)
        expect(domElementMock.removeEventListener).toHaveBeenCalledTimes(1)
        expect(tiltControl._map).toBe(undefined)
    })

    describe('tiltHandler()', () => {
        test('tiltHandler() correctly executes when tilted', () => {
            tiltControl.button = {
                textContent: '',
            }

            tiltControl._map = {
                getPitch: () => 45,
            }
            tiltControl.tiltHandler()

            expect(tiltControl.button.textContent).toBe('2D')

        })

        test('tiltHandler() correctly executes when not tilted', () => {
            tiltControl.button = {
                textContent: '',
            }

            tiltControl._map = {
                getPitch: () => 0,
            }
            tiltControl.tiltHandler()

            expect(tiltControl.button.textContent).toBe('3D')
        })
    })

    describe('clickHandler()', () => {
        test('clickHandler() correctly executes when tilted', () => {
            tiltControl._map = {
                easeTo: vi.fn(),
            }
            tiltControl.tilted = true
            tiltControl.clickHandler()
            expect(tiltControl._map.easeTo).toHaveBeenCalledTimes(1)
            expect(tiltControl._map.easeTo).toHaveBeenCalledWith({
                pitch: 0,
                duration: 200,
            })
        })

        test('clickHandler() correctly executes when not tilted', () => {
            tiltControl._map = {
                easeTo: vi.fn(),
            }
            tiltControl.tilted = false
            tiltControl.clickHandler()
            expect(tiltControl._map.easeTo).toHaveBeenCalledTimes(1)
            expect(tiltControl._map.easeTo).toHaveBeenCalledWith({
                pitch: 45,
                duration: 200,
            })
        })
    })

})
