import {describe, expect, test, vi, beforeEach, afterEach} from 'vitest'
import FilterCheckboxesController from '../../../assets/javascripts/FilterCheckboxesController'

describe('FilterCheckboxesController', () => {

    afterEach(() => {
        vi.restoreAllMocks();
    })



    let makeCheckboxMock = (value) => {
        return {
            querySelector: vi.fn(() => {
                return {
                    value: value,
                    innerText: value,
                    innerHTML: value,
                }
            }),
            style: {
                display: 'block'
            }
        }
    };



    test('it correctly constructs', () => {

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

        let container = {
            style: {
                display: 'none'
            }
        }

        vi.stubGlobal('document', {
            getElementById: vi.fn((id) => {
                if(id === 'checkboxes-123'){
                    return checkboxContainer;
                } else if(id === 'input-123'){
                    return searchBox;
                } else if(id === 'input-container-123'){
                    return container;
                } else {
                    throw new Error('Unexpected id: ' + id);
                }
            })
        })





        vi.spyOn(FilterCheckboxesController.prototype, 'filterCheckboxes');

        const filterCheckboxController = new FilterCheckboxesController('123');

        expect(container.style.display).toEqual('block');

        expect(fooCheckboxMock.querySelector).toHaveBeenCalledTimes(1);
        expect(barCheckboxMock.querySelector).toHaveBeenCalledTimes(1);

        expect(filterCheckboxController.checkboxStrings).toEqual(['foo', 'bar']);

        expect(searchBox.addEventListener).toHaveBeenCalledTimes(1);

        expect(filterCheckboxController.filterCheckboxes).toHaveBeenCalledTimes(1);

        FilterCheckboxesController.prototype.filterCheckboxes.mockRestore();
    })

    test('it correctly filters checkboxes', () => {
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

        let container = {
            style: {
                display: 'none'
            }
        }

        vi.stubGlobal('document', {
            getElementById: vi.fn((id) => {
                if(id === 'checkboxes-123'){
                    return checkboxContainer;
                } else if(id === 'input-123'){
                    return searchBox;
                } else if(id === 'input-container-123'){
                    return container;
                } else {
                    throw new Error('Unexpected id: ' + id);
                }
            })
        })

        const filterCheckboxController = new FilterCheckboxesController('123');

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
