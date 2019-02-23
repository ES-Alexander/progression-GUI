#!/usr/bin/env python3

import tkinter as tk
from math import radians, cos, sin

class PageManager(tk.Frame):
    ''' A class for managing Pages. '''
    def __init__(self, master=None, pages=[], up_to=-1, enforce_upto=False,
                 *args, **kwargs):
        '''

        'enforce_upto' is a boolean specifying if the user should not be able
            to go beyond one page past where they are currently up to.
            - Setting this to True means no page can be skipped to without
                having viewed all pages before it.
            - Setting it to False allows for skipping pages that are not
                required viewing (e.g. pages with enter_page() and leave_page()
                methods that return True on their first call, without user
                input).

        '''
        super().__init__(master)

        self._enforce_upto = enforce_upto
        self._setup_pages(up_to)
        self._setup_progress(*args, **kwargs)
        self.add_pages(*pages)


    def _setup_pages(self, up_to):
        ''' '''
        self._page_count = 0
        self._current_page = -1
        self._up_to = up_to
        self._pages = []
        self._page_frame = tk.Frame(self)
        self._page_frame.grid(sticky='nsew')

    def _setup_progress(self, *args, **kwargs):
        ''' '''
        self._progress = Progress(self, self.change_page, self._page_count,
                                  self._up_to, *args, **kwargs)
        self._progress.grid(sticky='nsew', row=1)

    def get_upto(self):
        ''' Returns the furthest Page instance viewed so far. 

        self.get_upto() -> int

        '''
        return self._up_to

    def get_page_count(self):
        ''' Returns the current number of Page instances being managed.

        self.get_page_count() -> int

        '''
        return self._page_count

    def get_current_page_id(self):
        ''' Returns the (0-indexed) id of the current Page being viewed.

        self.get_current_page_id() -> int

        '''
        return self._current_page

    def get_page(self, page_id=None):
        ''' '''
        if page_id is None:
            page_id = self._current_page

        return self._pages[page_id]

    def add_pages(self, *pages):
        ''' Adds the specified Page instances to the manager.

        If no page is currently being viewed, sets the current page to 0.

        self.add_pages(*Page) -> None

        '''
        for page in pages:
            self._pages += [Page(self._page_frame, *page)]
            self._pages[-1].grid(sticky='nsew')
            self._pages[-1].grid_remove()
            self._page_count += 1
        if self._current_page < 0 and self._page_count > 0:
            self._current_page = 0
            self._open_page()
        pages_added = len(pages)
        self._progress.add_pages(pages_added)

    def remove_page(self, page_id):
        ''' '''
        self._pages.pop(page_id)
        self._page_count -= 1
        if self._current_page >= page_id:
            self._current_page -= 1
        if self._up_to >= page_id:
            self._up_to -= 1
        self._progress.remove_page(page_id)

    def _open_page(self, page_id=None):
        ''' '''
        if page_id is None:
            page_id = self._current_page
            
        if self._pages[page_id].enter_page():
            self._pages[page_id].grid()
            self._current_page = page_id
            if self._up_to < page_id:
                self._up_to = page_id
            self._progress.change_page(self._current_page)
            return True
        return False

    def _close_page(self):
        ''' '''
        if self._pages[self._current_page].leave_page():
            self._pages[self._current_page].grid_remove()
            return True
        return False

    def skip_to_page(self, page_id):
        ''' '''
        if page_id > self._up_to+1 or not self._open_page(page_id):
            self._open_page()
            return False
        return True

    def _can_skim_next(self, page_id):
        ''' Returns True if the next page can be skimmed, else False.

        Skimming involves calling a page's enter_page() and leave_page() methods
            without requiring the page to be displayed between the calls.

        The next page is that with the page id: self.get_current_page_id() + 1.
            
        'page_id' is the integer id of the page being skimmed towards. Skim
            checks apply to the pages between the current page and page_id.

        self._can_skim_next(int, bool) -> bool

        '''
        if self._enforce_upto:
            return self._up_to > self._current_page < page_id - 1
        return self._current_page < page_id - 1
    
    def change_page(self, page_id=None):
        ''' Returns True on change from the current page to the specified page.

        Returns False on failure to change to the specified page.

        If enforce_upto was initialised as True, the furthest page reachable in
            a single forwards change_page call is self.get_upto() + 1. Otherwise
            the furthest reachable page is self.get_page_count() - 1.

        'page_id' is the integer id of the page to change to (starting from 0).
            - Changing forwards runs every leave_page() and enter_page()
                function between the current page and the page being changed to.
            - Changing backwards runs leave_page() on the current page, and
                enter_page() on the specified page.
            - If no page_id is specified, changes forwards to the next page
                (if possible).
            - If page_id is the current page, the page is refreshed

        The new page is that specified (subject to enforce_upto, as above),
            unless an error occurs or a transition function returns False, in
            which case the new page is the page before the last successful
            leave_page call, or, if no leave_page calls were made successfully,
            the current page.

        The current page is 'grid_remove'd, and the new page is 'grid'ed,
            skipping display of any and all pages in between.

        self.change_page(*int, *bool) -> bool
        
        '''
        if page_id is None:
            page_id = self._current_page + 1 # next page

        # check if new page out of bounds, or if cannot leave current page
        if page_id >= self._page_count or page_id < 0 or not self._close_page():
            return False
        
        if page_id < self._current_page:
            return self.skip_to_page(page_id)

        while self._can_skim_next(page_id):
            self._current_page += 1
            if not self._pages[self._current_page].enter_page():
                self._open_page(self._current_page - 1)
            elif not self._pages[self._current_page].leave_page():
                self._open_page()
            else:
                if self._up_to < self._current_page:
                    self._up_to = self._current_page
                continue
            return False
        
        return self.skip_to_page(page_id)

    def str(self):
        ''' '''
        return ('PageManager:\n\tcurrent page: {!s}\n\tup to: {!s} \n\tpage '+\
                'count: {!s}\n\tpages: {!s}').format(self._current_page,
                                                     self._up_to,
                                                     self._page_count,
                                                     self._pages)

    
class Page(tk.Frame):
    ''' A class for a Page. '''
    def __init__(self, master, enter=lambda:True, leave=lambda:True, label='',
                 *args, **kwargs):
        ''' '''
        super().__init__(master, *args, **kwargs)
        self.enter_page = enter
        self.leave_page = leave
        self._label = label

    def get_label(self):
        ''' '''
        return self._label

    def set_label(self, label):
        ''' '''
        self._label = label


class Progress(tk.Frame):
    ''' '''
    def __init__(self, master, change_page, num_pages, up_to=-1,
                 *args, **kwargs):
        ''' '''
        self._ratios = kwargs.pop('ratios', [7/9, 5/9, 1/3])
        # extract options
        progress_bar = kwargs.pop('progress_bar', False)
        bar_labels = kwargs.pop('bar_labels', False)
        arrows = kwargs.pop('arrows', False)
        arrow_labels = kwargs.pop('arrow_labels', False)
        number = kwargs.pop('number', False)
        labels = kwargs.pop('labels', False)
        
        super().__init__(master, *args, **kwargs)
        self._master = master
        self._num_pages = num_pages
        self._current_page = 0
        self._up_to = up_to
        self._change_page = change_page # used in callback on clicks
        self._displays = {}

        if progress_bar:
            pb = ProgressBar(self, *args, bar_labels=bar_labels, **kwargs)
            self._displays['progress_bar'] = pb
            self._displays['progress_bar'].grid(row=0, column=1, sticky='nsew')
            self._displays['progress_bar'].bind('<Button-1>',
                    lambda e: self._change_page(self._displays['progress_bar']\
                                                ._detect_page_number(e.x, e.y)))
        if arrows:
            pass
            # grid(r0,c0), grid(r0,c2)
            if arrow_labels:
                pass
                # labels under arrows
        if number:
            pass
            # if progress_bar: under middle, to the right, canvas item
            # elif arrows: between arrows, else: r0,c0

    def change_page(self, page_id):
        ''' '''
        if page_id is not None:
            self._current_page = page_id
            if page_id > self._up_to and self._up_to >= 0:
                self._up_to = page_id
        self.redraw()

    def grid(self, *args, **kwargs):
        ''' '''
        super().grid(*args, **kwargs)
        self._initialise_display()

    def _initialise_display(self):
        ''' '''
        #print(self.get_size())
        # draw the outline, up_to, and current_page for the first time
        self.redraw()
        pass

    def get_size(self):
        ''' '''
        self.update() # ensure the retrieved values are current
        return self.winfo_width(), self.winfo_height()

    def redraw(self):
        ''' '''
        for display in self._displays.values():
            display.redraw(self._num_pages, self._up_to, self._current_page)

    def add_pages(self, n):
        ''' '''
        self._num_pages += n
        self.redraw()

    def remove_page(self, page_id):
        ''' '''
        self._num_pages -= 1
        if self._current_page >= page_id:
            self._current_page -= 1
        if self._up_to >= page_id:
            self._up_to -= 1
        self.redraw()

class ProgressBar(tk.Canvas):
    ''' '''
    OUTER = 'outer'
    UPTO = 'up_to'
    CURRENT = 'current'
    WIRE = 'wireframe'
    FILLED = 'filled'
    
    def __init__(self, master, *args, **kwargs):
        ''' '''
        self._parse_kwargs(kwargs) # ratios, colours, modes, thetas, bar_labels
        super().__init__(master, *args, **kwargs)
        self._master = master

    def _parse_kwargs(self, kwargs):
        ''' '''
        self._ratios = kwargs.pop('ratios', [7/9, 5/9, 1/3])
        self._colours = kwargs.pop('colours', {self.OUTER: None,
                                               self.UPTO: 'black',
                                               self.CURRENT: 'MediumPurple2'})
        self._modes = kwargs.pop('modes', {self.OUTER: self.WIRE,
                                           self.UPTO: self.FILLED,
                                           self.CURRENT: self.FILLED})
        self._thetas = kwargs.pop('thetas', {self.OUTER: 30,
                                             self.UPTO: 25,
                                             self.CURRENT: 10})
        self._bar_labels = kwargs.pop('bar_labels', True)

    def get_size(self):
        ''' '''
        self.update() # ensure the retrieved values are current
        return self.winfo_width(), self.winfo_height()

    def redraw(self, num_pages, up_to, current_page, labels=[]):
        ''' '''
        # selectively clear things if:
        #   size has changed
        #   page has changed
        self.delete('all') # TEMPORARY - FULL REFRESH EVERY REDRAW
        if num_pages == 0:
            return
        self._num_pages = num_pages
        positions, max_r = self._get_positions()

        if self._bar_labels:
            self._draw_labels(positions, max_r, labels)
        self._draw_outer(positions, max_r * self._ratios[0])
        self._draw_upto(positions, max_r * self._ratios[1], up_to)
        self._draw_current(positions, max_r * self._ratios[2], current_page)

    def _draw_labels(self, positions, r, labels):
        ''' '''
        if not labels or len(labels) > len(positions):
            return
        pass # do actual drawing of labels under position markers
        # for label in labels: ...

    def _draw_positions(self, positions, r, key, **kwargs):
        ''' '''
        colour = self._colours[key]
        mode = self._modes[key]
        theta = self._thetas[key]
        
        kwargs['fill'] = colour
        if mode == self.FILLED:
            kwargs['outline'] = colour
                
        cx, cy = positions[0]
        if len(positions) == 1:
            self._draw_circle(cx, cy, r, 'misc', tags=(key, '0'), **kwargs)
            return
        rct = r * cos(radians(theta))
        rst = r * sin(radians(theta))
        cx1, cy1 = positions[1]
        self._draw_line(cx, cy, cx1, cy1, rct, rst, mode, tags=(key, '0'),
                        **kwargs)
        positions = positions[1:]

        self._draw_circle(cx, cy, r, mode, pos='start', theta=theta,
                          tags=(key, '0'), **kwargs)
        for index in range(len(positions)-1):
            cx, cy = positions[index]
            self._draw_circle(cx, cy, r, mode, theta=theta,
                              tags=(key, str(index+1)), **kwargs)
            cx1, cy1 = positions[index+1]
            self._draw_line(cx, cy, cx1, cy1, rct, rst, mode,
                            tags=(key, str(index+1)), **kwargs)
        self._draw_circle(cx1, cy1, r, mode, pos='end', theta=theta,
                          tags=(key, str(len(positions)+1)), **kwargs)

    def _draw_outer(self, positions, r, **kwargs):
        ''' '''
        self._draw_positions(positions, r, self.OUTER, **kwargs)

    def _draw_upto(self, positions, r, up_to, **kwargs):
        ''' '''
        if up_to == -1:
            up_to = len(positions)-1
        self._draw_positions(positions[0:up_to+1], r, self.UPTO, **kwargs)

    def _draw_current(self, positions, r, current, **kwargs):
        ''' '''
        self._draw_positions(positions[0:current+1], r, self.CURRENT, **kwargs)

    def _get_positions(self):
        ''' '''
        num_pages = self._num_pages
        labels = self._bar_labels
        c_width, c_height = self.get_size()
        # TODO: redifine c_height depending on label height
        p_vert = c_height/2
        spacing = c_width/num_pages
        positions = [[spacing/2, p_vert]]
        for i in range(num_pages-1):
            positions += [[positions[-1][0] + spacing, p_vert]]
        return positions, min(c_height/2, spacing/2) * 0.9

    def _draw_line(self, cx, cy, cx1, cy1, rct, rst, mode, **kwargs):
        ''' '''
        if mode == 'wireframe':
            self.create_line(cx + rct, cy + rst, cx1 - rct, cy1 + rst, **kwargs)
            self.create_line(cx + rct, cy - rst, cx1 - rct, cy1 - rst, **kwargs)
        else:
            self.create_rectangle(cx + rct, cy + rst, cx1 - rct, cy1 - rst,
                                  **kwargs)

    def _draw_circle(self, cx, cy, r, mode, **kwargs):
        ''' '''
        if mode == 'wireframe':
            pos = kwargs.pop('pos', 'center')
            if 'theta' in kwargs:
                theta = kwargs.pop('theta')
                if pos == 'start':
                    kwargs.update(start=theta, end=-theta)
                elif pos == 'end':
                    kwargs.update(start=180+theta, end=180-theta)
                elif pos == 'center':
                    kwargs.update(start=theta, end=180-theta)  # top arc
                    self.create_circle_arc(cx, cy, r, style=tk.ARC, **kwargs)
                    kwargs.update(start=180+theta, end=-theta) # bottom arc
            self.create_circle_arc(cx, cy, r, style=tk.ARC, **kwargs)
        else:
            for excess in ['pos', 'theta']:
                kwargs.pop(excess, None)
            self.create_ellipse(cx, cy, r, **kwargs)

    def create_ellipse(self, cx, cy, a, b=None, **kwargs):
        ''' Draws an ellipse centered on (cx,cy) with axes (a,b) on the canvas.

        Returns the integer id of the created item.

        (cx, cy) form the pixel coordinates of the center of the ellipse.
        'a' is the horizontal axis length of the ellipse.
        'b' is the vertical axis length of the ellipse (if left as None, b=a
            and a circle of radius 'a' is drawn).

        self.create_ellipse(int, int, float, *float/None, **kwargs) -> int

        '''
        if b is None:
            b = a
        return self.create_oval(cx-a, cy-b, cx+a, cy+b, **kwargs)

    def create_circle_arc(self, cx, cy, r, **kwargs):
        ''' Draws a circular arc, pieslice, or chord on the canvas.

        Returns the integer id of the created item.

        (cx,cy) form the pixel coordinates of the center of the full arc.
        r is the radius of the arc.
        **kwargs can include:
        'style': one of tk.PIESLICE, tk.CHORD, or tk.ARC (default tk.PIESLICE)
        'start': the starting angle (default 0.0 degrees)
        'end': the end angle (default unspecified)
        'extent': the angular extent, relative to 'start' (default 90.0 degrees)

        self.create_circular_arc(int, int, float, **kwargs) -> int

        '''
        if 'start' in kwargs and 'end' in kwargs:
            kwargs['extent'] = (kwargs['end'] - kwargs['start']) % 360
            del kwargs['end']
        if 'style' not in kwargs:
            kwargs['style'] = tk.ARC
        return self.create_arc(cx-r, cy-r, cx+r, cy+r, **kwargs)

    def find_withtags(*tags):
        ''' '''
        for item in self.find_withtag(tags[0]):
            if list(self.gettags(item)) == list(tags):
                return item

    def _detect_page_number(self, ex, ey):
        ''' '''
        positions, max_r = self._get_positions()
        rsq = (max_r * self._ratios[0]) ** 2
        for index, position in enumerate(positions):
            x, y = position
            if rsq >= self.distsq(x, y, ex, ey):
                return index
        return -1

    @staticmethod
    def distsq(x1, y1, x2, y2):
        ''' '''
        return (x2 - x1)**2 + (y2 - y1)**2


if __name__ == '__main__':
    from random import randint
    root = tk.Tk()
    N = 5 # number of pages to generate
    pN = lambda n : (lambda: print('p{}_in'.format(n)) or True,
                     lambda: print('p{}_out'.format(n)) or True)
    PM = PageManager(root, [pN(n) for n in range(N)], up_to=0,
                     enforce_upto=True, progress_bar=True)
    
    for n in range(N):
        tk.Label(PM.get_page(n), text='I am page {}'.format(n),
                 bg='#{:06x}'.format(randint(0xAAAAAA,0xFFFFFF))).grid(sticky='nsew')

    PM.grid(sticky='nsew')
