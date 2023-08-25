import {describe, expect, test, vi, beforeEach, afterEach} from 'vitest'
import { goBack } from '../../../assets/javascripts/back-button'



describe('back-button', () => {

    vi.stubGlobal('window', {
        history: {
            back: vi.fn(),
        }
    })

    describe('goBack', () => {

        afterEach(() => {
            window.history.back.mockClear()
        })

        test('initiates a window.history.back if the referer matches the parent page path', () => {
            vi.stubGlobal('document', {
                location: {
                    origin: 'http://localhost:3000',
                    pathname: '/foo',
                },
                referrer: 'http://localhost:3000/bar',
            })

            const result = goBack('/bar')
            expect(result).toBe(false)
            expect(window.history.back).toHaveBeenCalled()
        })

        test('navigates to the parent page if the referer doesn\'t match the parent page path', () => {
            vi.stubGlobal('document', {
                location: {
                    origin: 'http://localhost:3000',
                    pathname: '/foo',
                },
                referrer: 'http://localhost:3000/baz',
            })

            const result = goBack('/bar')
            expect(result).toBe(true)
            expect(window.history.back).not.toHaveBeenCalled()
        })
    })
})
