#!/usr/bin/env python3

import tkinter as tk
from TestRun import TestRun

class PageManagerTests(TestRun):
    ''' A test suite ensuring correct functionality of PageManager. '''
    # wrapper for TestRun.run_tests, creates and destroys GUI window.
    def run_tests(self, *args, **kwargs):
        self.__doc__ = super().run_tests.__doc__
        self._root = tk.Tk()

        super().run_tests(*args, **kwargs)
        self._root.destroy()
        
    # helper functions
    def _general_getter_test(self, PM, upto, page_count, current_page):
        ''' '''
        upto_r = PM.get_upto()
        assert upto_r == upto[0], \
               'PageManager._up_to should be {}{}, not {}.'.format(*upto,
                                                                   upto_r)
        page_count_r = PM.get_page_count()
        assert page_count_r == page_count[0], \
               'PageManager._page_count should be {}{}, not {}.'.format(
                   *page_count, page_count_r)
        current_page_r = PM.get_current_page()
        assert current_page_r == current_page[0], \
               'PageManager._current_page should be {}{}, not {}.'.format(
                   *current_page, current_page_r)

    def _general_page_count(self, PM, page_count):
        ''' '''
        page_count_r = PM.get_page_count()
        assert page_count_r == page_count, \
               'Should have {} page count, not {}'.format(page_count,
                                                          page_count_r)

    # test functions
    def test_getters(self):
        ''' Tests 'get_upto', 'get_page_count', and 'get_current_page'. '''
        PM = PageManager(self._root) # start with no pages

        # create some basic helpers
        def_n = lambda n : (n, ' by default')
        getter_test = lambda a,b,c : self._general_getter_test(PM, a, b, c)
        # defaults should be up_to=-1, page_count=0, current_page=-1
        getter_test(def_n(-1), def_n(0), def_n(-1))

        PM.add_pages(Page(),Page()) # add two pages
        # values should be up_to=0, page_count=2, current_page=0
        getter_test(def_n(0), (2, ''), def_n(0))

        PM.change_page()
        # values should be up_to=1, page_count=2, current_page=1
        getter_test((1,''), (2, ''), (1,''))

    def test_add_pages(self):
        ''' Tests the 'add_pages' method. '''
        PM = PageManager(self._root) # start with no pages

        self._general_page_count(PM, 0) # no pages should exist

        PM.add_pages(Page()) # add one page
        self._general_page_count(PM, 1) # one page should exist

        PM.add_pages(Page(),Page()) # add two more pages
        self._general_page_count(PM, 3) # three pages should exist

    def test_remove_page(self):
        ''' Tests the 'remove_page' method. '''
        # start with two pages
        PM = PageManager(self._root, pages=[Page(),Page()])

        self._general_page_count(PM, 2) # two pages should exist

        PM.remove_page(0) # remove page 0 
        self._general_page_count(PM, 1) # one page should remain

        PM.add_pages(Page(),Page()) # add two pages
        PM.remove_page(1) # remove page 1
        self._general_page_count(PM, 2) # two pages should remain

        PM.remove_page(0) # remove page 0
        PM.remove_page(0) # remove the new page 0
        self._general_page_count(PM, 0) # no pages should remain

    def test_skip_to_page(self):
        ''' Tests the 'skip_to_page' method '''
        # start with 4 pages, and up to page 1
        PM = PageManager(self._root,
                         [Page(),Page(lambda:False),Page(),Page()], 1)

        # create some basic helpers
        def_n = lambda n : (n, ' by default') # 'by default' reasoning
        r = lambda n : (n, '') # no reasoning
        getter_test = lambda a,b : self._general_getter_test(PM, a, def_n(4), b)
        # default values should be up_to=1, current_page=0
        getter_test(def_n(1), def_n(0))

        PM.skip_to_page(3) # attempt to skip to page 3 (fail, 4 > 1+1)
        # values should be up_to=1, current_page=0
        getter_test(def_n(1), def_n(0))

        PM.skip_to_page(2) # attempt to skip to page 2 (should succeed)
        getter_test(r(2), r(2)) # values should be up_to=2, current_page=2

        PM.skip_to_page(1) # attempt to skip to page 1 (fail on entry)
        getter_test(r(2), r(2)) # values should be up_to=2, current_page=2

        PM.skip_to_page(0) # attempt to skip to page 0 (should succeed)
        getter_test(r(2), r(0)) # values should be up_to=2, current_page=0

        PM.skip_to_page(3) # attempt to skip to page 3 (should succeed)
        getter_test(r(3), r(3)) # values should be up_to=3m current_page=3

    def test_change_page(self):
        ''' Tests the 'change_page' method. '''
        PM = PageManager(self._root,
                         [Page(),Page(),Page(lambda:False),Page()], 2)

        # create some basic helpers
        def_n = lambda n : (n, ' by default') # 'by default' reasoning
        r = lambda n : (n, '') # no reasoning
        getter_test = lambda a,b : self._general_getter_test(PM, a, def_n(4), b)
        # default values should be up_to=0, current_page=0
        getter_test(def_n(2), def_n(0))

        PM.change_page(2) # attempt to change to page 2 (fail on entry)
        getter_test(r(2), r(1)) # values should be up_to=1, current_page=1

        PM.change_page(0) # attempt to change to page 0 (should succeed)
        getter_test(r(2), r(0)) # values should be up_to=1, current_page=0

        PM._current_page = 2 # enter unenterable page manually
        PM.change_page()  # attempt to change to page 3 (should succeed)
        getter_test(r(3), r(3)) # values should be up_to=3, current_page=3

        PM.change_page(1) # attempt to change back to page 1 (should succeed)
        getter_test(r(3), r(1)) # values should be up_to=3, current_page=1

        PM.add_pages(Page(), Page()) # add two pages
        PM.skip_to_page(3) # skip to page 3
        PM.change_page(5) # attempt to change to page 5 (should succeed)
        # values should be up_to=5, page_count=6, current_page=5
        self._general_getter_test(PM, r(5), r(6), r(5))

        PM.change_page(3) # return to page 3
        PM._up_to = 3 # decrease up_to value manually
        PM._enforce_upto = True # disallow skimming of unviewed pages
        PM.change_page(5) # attempt to change to page 5 (fail, 4 not viewed)
        # values should be up_to=3, page_count=6, current_page=3
        self._general_getter_test(PM, r(3), r(6), r(3))
        

if __name__ == '__main__':
    from page_classes import PageManager, Page
    Tests = PageManagerTests()
    Tests.run_tests(verbose=True)
