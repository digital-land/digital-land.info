import {describe, expect, test, vi, beforeEach, afterEach} from 'vitest'
import FilterCheckboxesController from '../../../assets/javascripts/FilterCheckboxesController'

describe('FilterCheckboxesController', () => {

    afterEach(() => {
        vi.restoreAllMocks();
    })

    test('it correctly constructs', () => {
        let makeCheckboxMock = (value) => {
            return {
                querySelector: vi.fn(() => {
                    return {
                        value: value,
                    }
                }),
                style: {
                    display: 'block'
                }
            }
        };

        let fooCheckboxMock = makeCheckboxMock('foo');
        let barCheckboxMock = makeCheckboxMock('bar');

        let checkboxContainer = {
            children: [
                fooCheckboxMock,
                barCheckboxMock,
            ]
        }

        let searchBox = {
            addEventListener: vi.fn(),
            value: ''
        }

        vi.spyOn(FilterCheckboxesController.prototype, 'filterCheckboxes');

        const filterCheckboxController = new FilterCheckboxesController(checkboxContainer, searchBox);

        expect(fooCheckboxMock.querySelector).toHaveBeenCalledTimes(1);
        expect(barCheckboxMock.querySelector).toHaveBeenCalledTimes(1);

        expect(filterCheckboxController.checkboxStrings).toEqual(['foo', 'bar']);

        expect(searchBox.addEventListener).toHaveBeenCalledTimes(1);

        expect(filterCheckboxController.filterCheckboxes).toHaveBeenCalledTimes(1);

        FilterCheckboxesController.prototype.filterCheckboxes.mockRestore();
    })

    test('it correctly filters checkboxes', () => {
        let makeCheckboxMock = (value) => {
            return {
                querySelector: vi.fn(() => {
                    return {
                        value: value
                    }
                }),
                style: {
                    display: 'block'
                }
            }
        };

        let fooCheckboxMock = makeCheckboxMock('foo');
        let barCheckboxMock = makeCheckboxMock('bar');
        let fobaCheckboxMock = makeCheckboxMock('foba');

        let checkboxContainer = {
            children: [
                fooCheckboxMock,
                barCheckboxMock,
                fobaCheckboxMock
            ]
        }

        let searchBox = {
            addEventListener: vi.fn(),
            value: ''
        }

        const filterCheckboxController = new FilterCheckboxesController(checkboxContainer, searchBox);

        filterCheckboxController.filterCheckboxes();

        expect(fooCheckboxMock.style.display).toEqual('block');
        expect(barCheckboxMock.style.display).toEqual('block');
        expect(fobaCheckboxMock.style.display).toEqual('block');

        searchBox.value = 'foo';

        filterCheckboxController.filterCheckboxes();

        expect(fooCheckboxMock.style.display).toEqual('block');
        expect(barCheckboxMock.style.display).toEqual('none');
        expect(fobaCheckboxMock.style.display).toEqual('none');

        searchBox.value = 'ba';

        filterCheckboxController.filterCheckboxes();

        expect(fooCheckboxMock.style.display).toEqual('none');
        expect(barCheckboxMock.style.display).toEqual('block');
        expect(fobaCheckboxMock.style.display).toEqual('block');



    })
})
