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
        super().__init__(master, *args, **kwargs)

        self._enforce_upto = enforce_upto
        self._setup_pages(up_to)
        self._setup_progress()
        self.add_pages(*pages)

    def _setup_pages(self, up_to):
        ''' '''
        self._page_count = 0
        self._current_page = -1
        self._up_to = up_to
        self._pages = []

    def _setup_progress(self):
        ''' '''
        self._progress = Progress(self, self.change_page, self._page_count,
                                  self._up_to)

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

    def get_current_page(self):
        ''' Returns the (0-indexed) id of the current Page being viewed.

        self.get_current_page() -> int

        '''
        return self._current_page

    def add_pages(self, *pages):
        ''' Adds the specified Page instances to the manager.

        If no page is currently being viewed, sets the current page to 0.

        self.add_pages(*Page) -> None

        '''
        for page in pages:
            self._pages += [page]
            page.grid(row=0, column=self._page_count, in_=self, sticky='nsew')
            page.grid_remove()
            self._page_count += 1
        if self._current_page < 0 and self._page_count > 0:
            self._current_page = 0
            self._open_page()
        pages_added = len(pages)
        if self._page_count > pages_added:
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

        The next page is that with the page id: self.get_current_page() + 1.
            
        'page_id' is the integer id of the page being skimmed towards. Skim
            checks apply to the pages between the current page and page_id.

        self._can_skim_next(int, bool) -> bool

        '''
        if self._enforce_upto:
            return self._up_to > self._current_page < page_id
        return self._current_page < page_id
    
    def change_page(self, page_id=None):
        ''' Returns True on change from the current page to the specified page.

        Returns False on failure to change to the specified page.
        Raises IndexError if page_id is negative or outside the stored pages.

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
        next_page = self._current_page + 1
        if page_id is None:
            page_id = next_page
        
        if page_id >= self._page_count or page_id < 0:
            raise IndexError('Cannot change to page {} - out of range.'.format(
                page_id))

        if not self._close_page():
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
    def __init__(self, enter=lambda:True, leave=lambda:True, *args, **kwargs):
        ''' '''
        super().__init__(*args, **kwargs)
        self.enter_page = enter
        self.leave_page = leave

            
class Progress(tk.Canvas):
    ''' '''
    def __init__(self, master, change_page, num_pages=1, up_to=-1,
                 *args, **kwargs):
        ''' '''
        super().__init__(master, *args, **kwargs)
        self._master = master
        self._num_pages = num_pages
        self._current_page = 0
        self._up_to = up_to
        self._change_page = change_page # used in callback on clicks

    def grid(self, *args, **kwargs):
        ''' '''
        super().grid(*args, **kwargs)
        self._initialise_display()

    def _initialise_display(self):
        ''' '''
        print(self.get_size())
        # draw the outline, up_to, and current_page for the first time
        self.redraw()
        pass

    def get_size(self):
        ''' '''
        self.update() # ensure the retrieved values are current
        return self.winfo_width(), self.winfo_height()

    def change_page(self, current_page):
        ''' '''
        self._current_page = current_page
        
        if current_page > self._up_to and self._up_to >= 0:
            self._up_to = current_page

        if current_page > self._num_pages:
            self._num_pages = current_page

        self.redraw()

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

    def redraw(self):
        ''' '''
        # selectively clear things if:
        #   size has changed
        #   page has changed
        self.delete('all') # TEMPORARY - FULL REFRESH EVERY REDRAW
        positions, max_r = self._get_positions()
        self._draw_positions(positions, (max_r * 7) / 9)
        up_to = self._up_to
        if up_to == -1:
            up_to = len(positions)-1
        self._draw_upto(positions[0:up_to+1], (max_r * 5) / 9,
                        colour='black')
        self._draw_current(positions[0:self._current_page+1], max_r / 3,
                           colour='light green')

    def _get_positions(self):
        ''' '''
        c_width, c_height = self.get_size()
        p_vert = c_height/2
        spacing = c_width/self._num_pages
        positions = [[spacing/2, p_vert]]
        for i in range(self._num_pages-1):
            positions += [[positions[-1][0] + spacing, p_vert]]
        return positions, (min(c_height/2, spacing/2) * 9) / 10

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
        
            

    def _draw_positions(self, positions, r, theta=30, mode='wireframe',
                        **kwargs):
        ''' '''
        cx, cy = positions[0]
        if len(positions) == 1:
            self._draw_circle(cx, cy, r, 'misc', **kwargs)
            return
        rct = r * cos(radians(theta))
        rst = r * sin(radians(theta))
        cx1, cy1 = positions[1]
        self._draw_line(cx, cy, cx1, cy1, rct, rst, mode, **kwargs)
        positions = positions[1:]

        self._draw_circle(cx, cy, r, mode, pos='start', theta=theta, **kwargs)
        for index in range(len(positions)-1):
            cx, cy = positions[index]
            self._draw_circle(cx, cy, r, mode, theta=theta, **kwargs)
            cx1, cy1 = positions[index+1]
            self._draw_line(cx, cy, cx1, cy1, rct, rst, mode, **kwargs)
            '''
            self.create_line(cx + rct, cy + rst, cx1 - rct, cy1 + rst)
            self.create_line(cx + rct, cy - rst, cx1 - rct, cy1 - rst)
            '''
        self._draw_circle(cx1, cy1, r, mode, pos='end', theta=theta, **kwargs)

    def _draw_upto(self, positions, r, mode='filled', **kwargs):
        ''' '''
        if 'colour' in kwargs:
            colour = kwargs.pop('colour')
            kwargs['fill'] = colour
            if mode == 'filled':
                kwargs['outline'] = colour
        self._draw_positions(positions, r, 25, mode, **kwargs)

    def _draw_current(self, positions, r, mode='filled', **kwargs):
        ''' '''
        if 'colour' in kwargs:
            colour = kwargs.pop('colour')
            kwargs['fill'] = kwargs['outline'] = colour
        self._draw_positions(positions, r, 10, mode, **kwargs)

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
        

if __name__ == '__main__':
    root = tk.Tk()
    p3 = Progress(root, lambda: None, 7, up_to=0)
    p3.grid(sticky='nsew')
