import { ListFilter } from '../../../assets/javascripts/ListFilter.js';
import {describe, expect, test, it, beforeEach, afterEach, vi} from 'vitest'
import { JSDOM } from 'jsdom';

import {
    getDomElementMock,
    stubGlobalDocument,
} from '../../utils/mockUtils.js';

stubGlobalDocument();



describe('ListFilter', () => {
    afterEach(() => {
        vi.restoreAllMocks();
        vi.resetAllMocks();
    });

    let mockFormElement = getDomElementMock();

    ListFilter.prototype.init = vi.fn();
    const listFilter = new ListFilter(mockFormElement);

    describe('constructor', () => {

        test('it calls init', () => {
            expect(listFilter.init).toHaveBeenCalledOnce();
        });

        test('it returns an instance of a List filter', () => {
            expect(listFilter).toBeInstanceOf(ListFilter);
        });

        test('it throws an error if no form is provided', () => {
            expect(() => new ListFilter()).toThrow('ListFilter requires a form element');
        });

        test('it sets the form element to the mock element', () => {
            expect(listFilter.$form).toBe(mockFormElement);
        });


    });

    describe('setupOptions', () => {

        test('it sets up the options with the correct params', () => {
            const callParams = {'test': 'test', 'test2': 2, 'list_section_selector': 'test_selector', 'count_wrapper_selector': 'test_count_wrapper_selector'};

            const listFilterer = {
                setupOptions: ListFilter.prototype.setupOptions,
            }

            listFilterer.setupOptions(callParams);

            expect(listFilterer.list_section_selector).toEqual(callParams.list_section_selector);
            expect(listFilterer.count_wrapper_selector).toEqual(callParams.count_wrapper_selector);
        });

        test('it sets the correct default options', () => {
            const callParams = {'test': 'test', 'test2': 2};

            const listFilterer = {
                setupOptions: ListFilter.prototype.setupOptions,
            }

            listFilterer.setupOptions(callParams);

            expect(listFilterer.list_section_selector).toEqual('.dl-list-filter__count');
            expect(listFilterer.count_wrapper_selector).toEqual('.dl-list-filter__count__wrapper');
        })
    });

    test('filterViaTimeout', () => {

        const setTimeoutMock = vi.fn().mockImplementation(() => 'test2');
        const clearTimeoutMock = vi.fn();

        vi.stubGlobal('setTimeout', setTimeoutMock);
        vi.stubGlobal('clearTimeout', clearTimeoutMock);

        const lfMock = {
            filterViaTimeout: ListFilter.prototype.filterViaTimeout,
            ListFilter: ListFilter.prototype.ListFilter,
            filterTimeout: 'test',
            filterListItems: {
                bind: vi.fn().mockImplementation((that) => {
                    return 'test';
                }),
            }
        }

        lfMock.filterViaTimeout();

        expect(clearTimeoutMock).toHaveBeenCalledWith('test');
        expect(setTimeoutMock).toHaveBeenCalledOnce();
        expect(setTimeoutMock).toHaveBeenCalledWith(expect.any(Function), 200);

        lfMock.filterViaTimeout();

        expect(clearTimeoutMock).toHaveBeenCalledWith('test2');
    })

    test('matchSearchTerm', () => {
        let mockListFilter = {
            termToMatchOn: vi.fn().mockImplementation((value) => value.textContent),
            matchSearchTerm: ListFilter.prototype.matchSearchTerm,
        }

        let item1 = {
            textContent: 'test1',
            classList: {
                remove: vi.fn(),
            }
        };

        let result = mockListFilter.matchSearchTerm(
            item1,
            'test'
        );

        expect(mockListFilter.termToMatchOn).toHaveBeenCalledWith({
            textContent: 'test1',
            classList: {
                remove: expect.any(Function),
            }
        });

        expect(item1.classList.remove).toHaveBeenCalledWith('js-hidden');

        expect(result).toEqual(true);

        let item2 = {
            textContent: 'test2',
            classList: {
                remove: vi.fn(),
            }
        };

        result = mockListFilter.matchSearchTerm(
            item2,
            'should not match'
        );

        expect(result).toEqual(false);
    })

    describe('termToMatchOn', () => {
        // test with just a link
        // test with a div containing multiple search terms

        test('works with just a link', () => {
            let item = {
                querySelector: vi.fn().mockImplementation((selector) => {
                    if(selector === 'a') {
                        return {
                            textContent: 'test1',
                        }
                    }else{
                        throw new Error('Unexpected selector');
                    }
                }),
                querySelectorAll: vi.fn().mockImplementation(() => {
                    return []
                }),
            }

            let result = listFilter.termToMatchOn(item);

            expect(item.querySelector).toHaveBeenCalledWith('a');
            expect(result).toEqual('test1');
        })

        test('works with a div containing multiple search terms', () => {
            let item = {
                querySelectorAll: vi.fn().mockImplementation((selector) => {
                    if(selector === '[data-filter="match-content"]') {
                        return [{
                            textContent: 'test1',
                        },{
                            textContent: 'test2',
                        }]
                    }else{
                        throw new Error('Unexpected selector');
                    }
                }),
            }

            let result = listFilter.termToMatchOn(item);

            expect(item.querySelectorAll).toHaveBeenCalledWith('[data-filter="match-content"]');
            expect(result).toEqual('test1;test2');
        })
    })

    test('filterListItems', () => {
        stubGlobalDocument();
        const domElementMock = getDomElementMock();

        let boundFunctionMock = vi.fn();

        let listFilterMock = {
            filterListItems: ListFilter.prototype.filterListItems,
            matchSearchTerm: {
                bind: vi.fn().mockImplementation((that) => {
                    return boundFunctionMock;
                }),
            },
            updateListCounts: vi.fn(),
        }

        listFilterMock.filterListItems({
            target: {
                value: 'test',
            }
        });

        expect(listFilterMock.matchSearchTerm.bind).toHaveBeenCalledWith(listFilterMock);
        expect(boundFunctionMock).toHaveBeenCalledWith(domElementMock, 'test');
        expect(domElementMock.classList.add).toHaveBeenCalledWith('js-hidden');
        expect(listFilterMock.updateListCounts).toHaveBeenCalledWith([domElementMock,domElementMock]);
    });

    describe('updateListCounts', () => {
        let dom;
        let lists;
        let countWrapper;
        let listCount;
        let accessibleListCount;
        let noMatches;
        let listFilterMock;

        beforeEach(() => {
          dom = new JSDOM(`
            <html>
              <body>
                <div class="list-section">
                  <div class="count-wrapper">
                    <span class="js-list-filter__count"></span>
                    <span class="js-accessible-list-filter__count"></span>
                  </div>
                  <div data-filter="list">
                    <div data-filter="item"></div>
                    <div data-filter="item"></div>
                  </div>
                </div>
                <div class="list-section">
                  <div class="count-wrapper">
                    <span class="js-list-filter__count"></span>
                    <span class="js-accessible-list-filter__count"></span>
                  </div>
                  <div data-filter="list">
                    <div data-filter="item"></div>
                    <div data-filter="item"></div>
                  </div>
                </div>
                <div class="dl-list-filter__no-filter-match js-hidden"></div>
              </body>
            </html>
          `);
          lists = dom.window.document.querySelectorAll('[data-filter="list"]');
          countWrapper = dom.window.document.querySelector('.count-wrapper');
          listCount = dom.window.document.querySelector('.js-list-filter__count');
          accessibleListCount = dom.window.document.querySelector('.js-accessible-list-filter__count');
          noMatches = dom.window.document.querySelector('.dl-list-filter__no-filter-match');

            listFilterMock = {
                updateListCounts: ListFilter.prototype.updateListCounts,
                list_section_selector: '.list-section',
                count_wrapper_selector: '.count-wrapper',
                $noMatches: noMatches,
            }
        });

        it('should update the list counts and show/hide the corresponding sections', () => {
          lists[0].querySelectorAll('[data-filter="item"]')[0].classList.add('js-hidden');
          listFilterMock.updateListCounts(lists);
          expect(lists[0].closest('.list-section').classList.contains('js-hidden')).toBe(false);
          expect(lists[1].closest('.list-section').classList.contains('js-hidden')).toBe(false);
          expect(listCount.textContent).toBe('1');
          expect(accessibleListCount.textContent).toBe('1');
        });

        it('should show the "no matches" message if there are no matches', () => {
          lists[0].querySelectorAll('[data-filter="item"]')[0].classList.add('js-hidden');
          lists[0].querySelectorAll('[data-filter="item"]')[1].classList.add('js-hidden');
          lists[1].querySelectorAll('[data-filter="item"]')[0].classList.add('js-hidden');
          lists[1].querySelectorAll('[data-filter="item"]')[1].classList.add('js-hidden');
          listFilterMock.updateListCounts(lists);
          expect(noMatches.classList.contains('js-hidden')).toBe(false);
        });
    });
});
