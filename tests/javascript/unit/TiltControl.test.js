import {describe, expect, test, vi, beforeEach} from 'vitest'
import TiltControl from '../../../assets/javascripts/TiltControl.js'

const addEventListenerMock = vi.fn()
const removeEventListenerMock = vi.fn()

vi.stubGlobal('document', {
    createElement: () => {
        return {
            addEventListener: addEventListenerMock,
            removeEventListener: removeEventListenerMock,
            style: {},
            classList: {
                add: () => {},
            },
            appendChild: () => {},
        }
    }
})

describe('Tilt Control', () => {

    let tiltControl;
    beforeEach(() => {
        tiltControl = new TiltControl()
        vi.clearAllMocks()
    })

    test('onAdd() correctly executes', () => {
        tiltControl.clickHandler = vi.fn()
        const map = {
            on: vi.fn(),
        }
        tiltControl.onAdd(map)
        expect(addEventListenerMock).toHaveBeenCalledTimes(1)
        expect(map.on).toHaveBeenCalledTimes(1)
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
        expect(removeEventListenerMock).toHaveBeenCalledTimes(1)
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
