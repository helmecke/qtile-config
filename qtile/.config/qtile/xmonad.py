# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Dustin Lacewell
# Copyright (c) 2011 Mounier Florian
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2012 Maximilian Köhl
# Copyright (c) 2012, 2014-2015 Tycho Andersen
# Copyright (c) 2013 jpic
# Copyright (c) 2013 babadoo
# Copyright (c) 2013 Jure Ham
# Copyright (c) 2013 Tao Sauvage
# Copyright (c) 2014 ramnes
# Copyright (c) 2014 Sean Vig
# Copyright (c) 2014 dmpayton
# Copyright (c) 2014 dequis
# Copyright (c) 2014 Florian Scherf
# Copyright (c) 2017 Dirk Hartmann
# Copyright (c) 2021 Jakob Helmecke
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math

from libqtile.layout.base import _SimpleLayoutBase


class MonadTall(_SimpleLayoutBase):
    """Emulate the behavior of XMonad's default tiling scheme.

    Master-Pane:

    A master pane that contains a single window takes up a vertical portion of
    the screen_rect based on the ratio setting. This ratio can be adjusted with
    the ``cmd_grow_master`` and ``cmd_shrink_master`` or, while the master pane is in
    focus, ``cmd_grow`` and ``cmd_shrink``.

    ::

        ---------------------
        |            |      |
        |            |      |
        |            |      |
        |            |      |
        |            |      |
        |            |      |
        ---------------------

    Using the ``cmd_flip`` method will switch which horizontal side the master
    pane will occupy. The master pane is considered the "top" of the stack.

    ::

        ---------------------
        |      |            |
        |      |            |
        |      |            |
        |      |            |
        |      |            |
        |      |            |
        ---------------------

    Slave-panes:

    Occupying the rest of the screen_rect are one or more slave panes.  The
    slave panes will share the vertical space of the screen_rect however
    they can be resized at will with the ``cmd_grow`` and ``cmd_shrink``
    methods.  The other slave panes will adjust their sizes to smoothly fill
    all of the space.

    ::

        ---------------------          ---------------------
        |            |      |          |            |______|
        |            |______|          |            |      |
        |            |      |          |            |      |
        |            |______|          |            |      |
        |            |      |          |            |______|
        |            |      |          |            |      |
        ---------------------          ---------------------

    Panes can be moved with the ``cmd_shuffle_up`` and ``cmd_shuffle_down``
    methods. As mentioned the master pane is considered the top of the stack;
    moving up is counter-clockwise and moving down is clockwise.

    The opposite is true if the layout is "flipped".

    ::

        ---------------------          ---------------------
        |            |  2   |          |   2   |           |
        |            |______|          |_______|           |
        |            |  3   |          |   3   |           |
        |     1      |______|          |_______|     1     |
        |            |  4   |          |   4   |           |
        |            |      |          |       |           |
        ---------------------          ---------------------


    Normalizing/Resetting:

    To restore all slave client windows to their default size ratios
    use the ``cmd_normalize`` method.

    To reset all client windows to their default sizes, including the primary
    window, use the ``cmd_reset`` method.

    Maximizing:

    To toggle a client window between its minimum and maximum sizes
    simply use the ``cmd_maximize`` on a focused client.

    Suggested Bindings::

        Key([modkey], "h", lazy.layout.left()),
        Key([modkey], "l", lazy.layout.right()),
        Key([modkey], "j", lazy.layout.down()),
        Key([modkey], "k", lazy.layout.up()),
        Key([modkey, "shift"], "h", lazy.layout.swap_left()),
        Key([modkey, "shift"], "l", lazy.layout.swap_right()),
        Key([modkey, "shift"], "j", lazy.layout.shuffle_down()),
        Key([modkey, "shift"], "k", lazy.layout.shuffle_up()),
        Key([modkey], "i", lazy.layout.grow()),
        Key([modkey], "m", lazy.layout.shrink()),
        Key([modkey], "n", lazy.layout.normalize()),
        Key([modkey], "o", lazy.layout.maximize()),
        Key([modkey, "shift"], "space", lazy.layout.flip()),
    """

    _left = 0
    _right = 1
    _vert = 0
    _hori = 1
    _med_ratio = 0.5

    defaults = [
        ("border_focus", "#ff0000", "Border colour(s) for the focused window."),
        ("border_normal", "#000000", "Border colour(s) for un-focused windows."),
        ("border_width", 2, "Border width."),
        ("single_border_width", None, "Border width for single window"),
        ("single_margin", None, "Margin size for single window"),
        ("margin", 0, "Margin of the layout"),
        ("ratio", .5,
            "The percent of the screen-space the master pane should occupy "
            "by default."),
        ("min_ratio", .25,
            "The percent of the screen-space the master pane should occupy "
            "at minimum."),
        ("max_ratio", .75,
            "The percent of the screen-space the master pane should occupy "
            "at maximum."),
        ("min_slave_size", 85,
            "minimum size in pixel for a slave pane window "),
        ("align", _left, "Which side master plane will be placed "
            "(one of ``MonadTall._left`` or ``MonadTall._right``)"),
        ("change_ratio", .05, "Resize ratio"),
        ("change_size", 20, "Resize change in pixels"),
        ("new_client_position", "top",
            "Place new windows: "
            " after_current - after the active window."
            " before_current - before the active window,"
            " top - at the top of the stack,"
            " bottom - at the bottom of the stack,"),
        ("master_length", 1,
            "Amount of windows displayed in the master stack. Surplus windows "
            "will be moved to the slave stack."),
        ("orientation", _vert, "Orientation in which master windows will be "
            "placed (one of ``MonadTall._vert`` or ``MonadTall._hori``)"),
        ("maximized", False, "Start maximized"),
    ]

    def __init__(self, **config):
        _SimpleLayoutBase.__init__(self, **config)
        self.add_defaults(MonadTall.defaults)
        if self.single_border_width is None:
            self.single_border_width = self.border_width
        if self.single_margin is None:
            self.single_margin = self.margin
        self.relative_sizes = []
        self.screen_rect = None

    @property
    def focused(self):
        return self.clients.current_index

    @property
    def master_windows(self):
        return self.clients[:self.master_length]

    @property
    def slave_windows(self):
        return self.clients[self.master_length:]

    def _get_relative_size_from_absolute(self, absolute_size):
        return absolute_size / self.screen_rect.height

    def _get_absolute_size_from_relative(self, relative_size):
        return int(relative_size * self.screen_rect.height)

    def clone(self, group):
        "Clone layout for other groups"
        c = _SimpleLayoutBase.clone(self, group)
        c.sizes = []
        c.relative_sizes = []
        c.screen_rect = group.screen.get_rect() if group.screen else None
        c.ratio = self.ratio
        c.align = self.align
        c.orientation = self.orientation
        return c

    def add(self, client):
        "Add client to layout"
        self.clients.add(client, client_position=self.new_client_position)
        self.do_normalize = True

    def remove(self, client):
        "Remove client from layout"
        self.do_normalize = True
        return self.clients.remove(client)

    def cmd_normalize(self, redraw=True):
        "Evenly distribute screen-space among slave clients"
        n = len(self.clients) - 1  # exclude master client, 0
        # if slave clients exist
        if n > 0 and self.screen_rect is not None:
            self.relative_sizes = [1.0 / n] * n
        # reset master pane ratio
        if redraw:
            self.group.layout_all()
        self.do_normalize = False

    def cmd_reset(self, redraw=True):
        "Reset Layout."
        self.ratio = self._med_ratio
        if self.align == self._right:
            self.align = self._left
        if self.orientation == self._hori:
            self.align = self._vert
        self.cmd_normalize(redraw)

    def _maximize_master(self):
        "Toggle the master pane between min and max size"
        if self.ratio <= self._med_ratio:
            self.ratio = self.max_ratio
        else:
            self.ratio = self.min_ratio
        self.group.layout_all()

    def _maximize_slave(self):
        "Toggle the focused slave pane between min and max size"
        n = len(self.clients) - 2  # total shrinking clients
        # total size of collapsed secondaries
        collapsed_size = self.min_slave_size * n
        nidx = self.focused - 1  # focused size index
        # total height of maximized slave
        maxed_size = self.group.screen.dheight - collapsed_size
        # if maximized or nearly maximized
        if abs(
            self._get_absolute_size_from_relative(self.relative_sizes[nidx]) -
            maxed_size
        ) < self.change_size:
            # minimize
            self._shrink_slave(
                self._get_absolute_size_from_relative(
                    self.relative_sizes[nidx]
                ) - self.min_slave_size
            )
        # otherwise maximize
        else:
            self._grow_slave(maxed_size)

    def cmd_maximize(self):
        "Grow the currently focused client to the max size"
        if self.maximized:
            self.maximized = False
        else:
            self.maximized = True
        self.group.layout_all()

    def configure(self, client, screen_rect):
        "Position client based on order and sizes"
        self.screen_rect = screen_rect

        # if no sizes or normalize flag is set, normalize
        if not self.relative_sizes or self.do_normalize:
            self.cmd_normalize(False)

        # if client not in this layout
        if not self.clients or client not in self.clients:
            client.hide()
            return

        # determine focus border-color
        if client.has_focus:
            px = self.border_focus
        else:
            px = self.border_normal

        # single client - fullscreen
        if len(self.clients) == 1 or self.maximized:
            if self.clients and client is self.clients.current_client:
                client.place(
                    self.screen_rect.x,
                    self.screen_rect.y,
                    self.screen_rect.width - 2 * self.single_border_width,
                    self.screen_rect.height - 2 * self.single_border_width,
                    self.single_border_width,
                    px,
                    margin=self.single_margin,
                )
                client.unhide()
            else:
                client.hide()
            return

        cidx = self.clients.index(client)
        self._configure_specific(client, screen_rect, px, cidx)
        client.unhide()

    def _configure_specific(self, client, screen_rect, px, cidx):
        """Specific configuration for xmonad tall."""
        self.screen_rect = screen_rect

        # calculate master/slave pane size
        width_master = int(self.screen_rect.width * self.ratio)
        width_slave = self.screen_rect.width - width_master

        # calculate client's x offset
        if self.align == self._left:  # left or up orientation
            if client in self.master_windows:
                # master client
                xpos = self.screen_rect.x
            else:
                # slave client
                xpos = self.screen_rect.x + width_master
        else:  # right or down orientation
            if client in self.master_windows:
                # master client
                xpos = self.screen_rect.x + width_slave - self.margin
            else:
                # slave client
                xpos = self.screen_rect.x

        # calculate client height and place
        if client in self.slave_windows:
            pos = self.clients.index(client)
            # slave client
            width = width_slave - 2 * self.border_width
            # ypos is the sum of all clients above it
            height = self.screen_rect.height // len(self.slave_windows)
            ypos = self.screen_rect.y + \
                self.clients[self.master_length:].index(client) * height
            # fix double margin
            if cidx > 1:
                ypos -= self.margin
                height += self.margin
            # place client based on calculated dimensions
            client.place(
                xpos,
                ypos,
                width,
                height - 2 * self.border_width,
                self.border_width,
                px,
                margin=self.margin,
            )
        else:
            pos = self.clients.index(client)
            if self.orientation == self._vert:
                height = self.screen_rect.height // self.master_length
                width = width_master
                ypos = self.screen_rect.y + pos * height
            else:
                height = self.screen_rect.height
                width = width_master // self.master_length
                ypos = self.screen_rect.y
                if self.align == self._left:
                    xpos = self.screen_rect.x + pos * width
                else:
                    xpos = self.screen_rect.width - (pos + 1) * width

            # master client
            client.place(
                xpos,
                ypos,
                width,
                height,
                self.border_width,
                px,
                margin=[
                    self.margin,
                    2*self.border_width,
                    self.margin + 2*self.border_width,
                    self.margin
                ],
            )

    def info(self):
        d = _SimpleLayoutBase.info(self)
        d.update(dict(
            master=[c.name for c in self.master_windows],
            slave=[c.name for c in self.slave_windows],
        ))
        return d

    def get_shrink_margin(self, cidx):
        "Return how many remaining pixels a client can shrink"
        return max(
            0,
            self._get_absolute_size_from_relative(
                self.relative_sizes[cidx]
            ) - self.min_slave_size
        )

    def shrink(self, cidx, amt):
        """Reduce the size of a client

        Will only shrink the client until it reaches the configured minimum
        size. Any amount that was prevented in the resize is returned.
        """
        # get max resizable amount
        margin = self.get_shrink_margin(cidx)
        if amt > margin:  # too much
            self.relative_sizes[cidx] -= \
                self._get_relative_size_from_absolute(margin)
            return amt - margin
        else:
            self.relative_sizes[cidx] -= \
                self._get_relative_size_from_absolute(amt)
            return 0

    def shrink_up(self, cidx, amt):
        """Shrink the window up

        Will shrink all slave clients above the specified index in order.
        Each client will attempt to shrink as much as it is able before the
        next client is resized.

        Any amount that was unable to be applied to the clients is returned.
        """
        left = amt  # track unused shrink amount
        # for each client before specified index
        for idx in range(0, cidx):
            # shrink by whatever is left-over of original amount
            left -= left - self.shrink(idx, left)
        # return unused shrink amount
        return left

    def shrink_up_shared(self, cidx, amt):
        """Shrink the shared space

        Will shrink all slave clients above the specified index by an equal
        share of the provided amount. After applying the shared amount to all
        affected clients, any amount left over will be applied in a non-equal
        manner with ``shrink_up``.

        Any amount that was unable to be applied to the clients is returned.
        """
        # split shrink amount among number of clients
        per_amt = amt / cidx
        left = amt  # track unused shrink amount
        # for each client before specified index
        for idx in range(0, cidx):
            # shrink by equal amount and track left-over
            left -= per_amt - self.shrink(idx, per_amt)
        # apply non-equal shrinkage slave pass
        # in order to use up any left over shrink amounts
        left = self.shrink_up(cidx, left)
        # return whatever could not be applied
        return left

    def shrink_down(self, cidx, amt):
        """Shrink current window down

        Will shrink all slave clients below the specified index in order.
        Each client will attempt to shrink as much as it is able before the
        next client is resized.

        Any amount that was unable to be applied to the clients is returned.
        """
        left = amt  # track unused shrink amount
        # for each client after specified index
        for idx in range(cidx + 1, len(self.relative_sizes)):
            # shrink by current total left-over amount
            left -= left - self.shrink(idx, left)
        # return unused shrink amount
        return left

    def shrink_down_shared(self, cidx, amt):
        """Shrink slave clients

        Will shrink all slave clients below the specified index by an equal
        share of the provided amount. After applying the shared amount to all
        affected clients, any amount left over will be applied in a non-equal
        manner with ``shrink_down``.

        Any amount that was unable to be applied to the clients is returned.
        """
        # split shrink amount among number of clients
        per_amt = amt / (len(self.relative_sizes) - 1 - cidx)
        left = amt  # track unused shrink amount
        # for each client after specified index
        for idx in range(cidx + 1, len(self.relative_sizes)):
            # shrink by equal amount and track left-over
            left -= per_amt - self.shrink(idx, per_amt)
        # apply non-equal shrinkage slave pass
        # in order to use up any left over shrink amounts
        left = self.shrink_down(cidx, left)
        # return whatever could not be applied
        return left

    def _grow_master(self, amt):
        """Will grow the client that is currently in the master pane"""
        self.ratio += amt
        self.ratio = min(self.max_ratio, self.ratio)

    def _grow_solo_slave(self, amt):
        """Will grow the solitary client in the slave pane"""
        self.ratio -= amt
        self.ratio = max(self.min_ratio, self.ratio)

    def _grow_slave(self, amt):
        """Will grow the focused client in the slave pane"""
        half_change_size = amt / 2
        # track unshrinkable amounts
        left = amt
        # first slave (top)
        if self.focused == 1:
            # only shrink downwards
            left -= amt - self.shrink_down_shared(0, amt)
        # last slave (bottom)
        elif self.focused == len(self.clients) - 1:
            # only shrink upwards
            left -= amt - self.shrink_up(len(self.relative_sizes) - 1, amt)
        # middle slave
        else:
            # get size index
            idx = self.focused - 1
            # shrink up and down
            left -= half_change_size - self.shrink_up_shared(
                idx,
                half_change_size
            )
            left -= half_change_size - self.shrink_down_shared(
                idx,
                half_change_size
            )
            left -= half_change_size - self.shrink_up_shared(
                idx,
                half_change_size
            )
            left -= half_change_size - self.shrink_down_shared(
                idx,
                half_change_size
            )
        # calculate how much shrinkage took place
        diff = amt - left
        # grow client by diff amount
        self.relative_sizes[self.focused - 1] += \
            self._get_relative_size_from_absolute(diff)

    def cmd_grow(self):
        """Grow current window

        Will grow the currently focused client reducing the size of those
        around it. Growing will stop when no other slave clients can reduce
        their size any further.
        """
        if self.focused == 0:
            self._grow_master(self.change_ratio)
        elif len(self.clients) == 2:
            self._grow_solo_slave(self.change_ratio)
        else:
            self._grow_slave(self.change_size)
        self.group.layout_all()

    def cmd_grow_master(self):
        """Grow master pane

        Will grow the master pane, reducing the size of clients in the slave
        pane.
        """
        self._grow_master(self.change_ratio)
        self.group.layout_all()

    def cmd_shrink_master(self):
        """Shrink master pane

        Will shrink the master pane, increasing the size of clients in the
        slave pane.
        """
        self._shrink_master(self.change_ratio)
        self.group.layout_all()

    def grow(self, cidx, amt):
        "Grow slave client by specified amount"
        self.relative_sizes[cidx] += self._get_relative_size_from_absolute(amt)

    def grow_up_shared(self, cidx, amt):
        """Grow higher slave clients

        Will grow all slave clients above the specified index by an equal
        share of the provided amount.
        """
        # split grow amount among number of clients
        per_amt = amt / cidx
        for idx in range(0, cidx):
            self.grow(idx, per_amt)

    def grow_down_shared(self, cidx, amt):
        """Grow lower slave clients

        Will grow all slave clients below the specified index by an equal
        share of the provided amount.
        """
        # split grow amount among number of clients
        per_amt = amt / (len(self.relative_sizes) - 1 - cidx)
        for idx in range(cidx + 1, len(self.relative_sizes)):
            self.grow(idx, per_amt)

    def _shrink_master(self, amt):
        """Will shrink the client that currently in the master pane"""
        self.ratio -= amt
        self.ratio = max(self.min_ratio, self.ratio)

    def _shrink_solo_slave(self, amt):
        """Will shrink the solitary client in the slave pane"""
        self.ratio += amt
        self.ratio = min(self.max_ratio, self.ratio)

    def _shrink_slave(self, amt):
        """Will shrink the focused client in the slave pane"""
        # get focused client
        client = self.clients[self.focused]

        # get default change size
        change = amt

        # get left-over height after change
        left = client.height - amt
        # if change would violate min_slave_size
        if left < self.min_slave_size:
            # just reduce to min_slave_size
            change = client.height - self.min_slave_size

        # calculate half of that change
        half_change = change / 2

        # first slave (top)
        if self.focused == 1:
            # only grow downwards
            self.grow_down_shared(0, change)
        # last slave (bottom)
        elif self.focused == len(self.clients) - 1:
            # only grow upwards
            self.grow_up_shared(len(self.relative_sizes) - 1, change)
        # middle slave
        else:
            idx = self.focused - 1
            # grow up and down
            self.grow_up_shared(idx, half_change)
            self.grow_down_shared(idx, half_change)
        # shrink client by total change
        self.relative_sizes[self.focused - 1] -= \
            self._get_relative_size_from_absolute(change)

    cmd_next = _SimpleLayoutBase.next
    cmd_previous = _SimpleLayoutBase.previous

    def cmd_shrink(self):
        """Shrink current window

        Will shrink the currently focused client reducing the size of those
        around it. Shrinking will stop when the client has reached the minimum
        size.
        """
        if self.focused == 0:
            self._shrink_master(self.change_ratio)
        elif len(self.clients) == 2:
            self._shrink_solo_slave(self.change_ratio)
        else:
            self._shrink_slave(self.change_size)
        self.group.layout_all()

    cmd_up = cmd_previous
    cmd_down = cmd_next

    def cmd_shuffle_up(self):
        """Shuffle the client up the stack"""
        self.clients.shuffle_up()
        self.group.layout_all()
        self.group.focus(self.clients.current_client)

    def cmd_shuffle_down(self):
        """Shuffle the client down the stack"""
        self.clients.shuffle_down()
        self.group.layout_all()
        self.group.focus(self.clients[self.focused])

    def cmd_flip(self):
        """Flip the layout horizontally"""
        self.align = self._left if self.align == self._right else self._right
        self.group.layout_all()

    def _get_closest(self, x, y, clients):
        """Get closest window to a point x,y"""
        target = min(
            clients,
            key=lambda c: math.hypot(c.info()["x"] - x, c.info()["y"] - y)
        )
        return target

    def cmd_swap(self, window1, window2):
        """Swap two windows"""
        self.clients.swap(window1, window2, 1)
        self.group.layout_all()
        self.group.focus(window1)

    def cmd_swap_left(self):
        """Swap current window with closest window to the left"""
        win = self.clients.current_client
        x, y = win.x, win.y
        candidates = [c for c in self.clients if c.info()['x'] < x]
        target = self._get_closest(x, y, candidates)
        self.cmd_swap(win, target)

    def cmd_swap_right(self):
        """Swap current window with closest window to the right"""
        win = self.clients.current_client
        x, y = win.x, win.y
        candidates = [c for c in self.clients if c.info()['x'] > x]
        target = self._get_closest(x, y, candidates)
        self.cmd_swap(win, target)

    def cmd_swap_master(self):
        """Swap current window to master pane"""
        win = self.clients.current_client
        cidx = self.clients.index(win)

        if cidx < self.master_length - 1:
            target = self.clients[cidx + 1]
        else:
            target = self.clients[0]

        self.cmd_swap(win, target)

    def cmd_left(self):
        """Focus on the closest window to the left of the current window"""
        win = self.clients.current_client
        x, y = win.x, win.y
        candidates = [c for c in self.clients if c.info()["x"] < x]
        self.clients.current_client = self._get_closest(x, y, candidates)
        self.group.focus(self.clients.current_client)

    def cmd_right(self):
        """Focus on the closest window to the right of the current window"""
        win = self.clients.current_client
        x, y = win.x, win.y
        candidates = [c for c in self.clients if c.info()["x"] > x]
        self.clients.current_client = self._get_closest(x, y, candidates)
        self.group.focus(self.clients.current_client)

    cmd_shuffle_left = cmd_swap_left
    cmd_shuffle_right = cmd_swap_right

    def cmd_decrease_nmaster(self):
        """Decrease number of windows in master pane"""
        self.master_length -= 1
        if self.master_length <= 0:
            self.master_length = 1
        self.group.layout_all()

    def cmd_increase_nmaster(self):
        """Increase number of windows in master pane"""
        self.master_length += 1
        if self.master_length >= len(self.clients) - 1:
            self.master_length = len(self.clients) - 1
        self.group.layout_all()

    def cmd_master(self):
        """Focus windows in master pane"""
        win = self.clients.current_client
        cidx = self.clients.index(win)
        if cidx < self.master_length - 1:
            self.group.focus(self.clients[cidx + 1])
        else:
            self.group.focus(self.clients[0])

    def cmd_flip_master(self):
        """Flip the layout horizontally"""
        self.orientation = self._vert if self.orientation == self._hori else self._hori
        self.group.layout_all()


class MonadWide(MonadTall):
    """Emulate the behavior of XMonad's horizontal tiling scheme.

    This layout attempts to emulate the behavior of XMonad wide
    tiling scheme.

    Master-Pane:

    A master pane that contains a single window takes up a horizontal
    portion of the screen_rect based on the ratio setting. This ratio can be
    adjusted with the ``cmd_grow_master`` and ``cmd_shrink_master`` or,
    while the master pane is in focus, ``cmd_grow`` and ``cmd_shrink``.

    ::

        ---------------------
        |                   |
        |                   |
        |                   |
        |___________________|
        |                   |
        |                   |
        ---------------------

    Using the ``cmd_flip`` method will switch which vertical side the
    master pane will occupy. The master pane is considered the "top" of
    the stack.

    ::

        ---------------------
        |                   |
        |___________________|
        |                   |
        |                   |
        |                   |
        |                   |
        ---------------------

    Slave-panes:

    Occupying the rest of the screen_rect are one or more slave panes.
    The slave panes will share the horizontal space of the screen_rect
    however they can be resized at will with the ``cmd_grow`` and
    ``cmd_shrink`` methods. The other slave panes will adjust their
    sizes to smoothly fill all of the space.

    ::

        ---------------------          ---------------------
        |                   |          |                   |
        |                   |          |                   |
        |                   |          |                   |
        |___________________|          |___________________|
        |     |       |     |          |   |           |   |
        |     |       |     |          |   |           |   |
        ---------------------          ---------------------

    Panes can be moved with the ``cmd_shuffle_up`` and ``cmd_shuffle_down``
    methods. As mentioned the master pane is considered the top of the
    stack; moving up is counter-clockwise and moving down is clockwise.

    The opposite is true if the layout is "flipped".

    ::

        ---------------------          ---------------------
        |                   |          |  2  |   3   |  4  |
        |         1         |          |_____|_______|_____|
        |                   |          |                   |
        |___________________|          |                   |
        |     |       |     |          |        1          |
        |  2  |   3   |  4  |          |                   |
        ---------------------          ---------------------

    Normalizing/Resetting:

    To restore all slave client windows to their default size ratios
    use the ``cmd_normalize`` method.

    To reset all client windows to their default sizes, including the primary
    window, use the ``cmd_reset`` method.


    Maximizing:

    To toggle a client window between its minimum and maximum sizes
    simply use the ``cmd_maximize`` on a focused client.

    Suggested Bindings::

        Key([modkey], "h", lazy.layout.left()),
        Key([modkey], "l", lazy.layout.right()),
        Key([modkey], "j", lazy.layout.down()),
        Key([modkey], "k", lazy.layout.up()),
        Key([modkey, "shift"], "h", lazy.layout.swap_left()),
        Key([modkey, "shift"], "l", lazy.layout.swap_right()),
        Key([modkey, "shift"], "j", lazy.layout.shuffle_down()),
        Key([modkey, "shift"], "k", lazy.layout.shuffle_up()),
        Key([modkey], "i", lazy.layout.grow()),
        Key([modkey], "m", lazy.layout.shrink()),
        Key([modkey], "n", lazy.layout.normalize()),
        Key([modkey], "o", lazy.layout.maximize()),
        Key([modkey, "shift"], "space", lazy.layout.flip()),
    """

    _up = 0
    _down = 1
    _hori = 0
    _vert = 1

    def _get_relative_size_from_absolute(self, absolute_size):
        return absolute_size / self.screen_rect.width

    def _get_absolute_size_from_relative(self, relative_size):
        return int(relative_size * self.screen_rect.width)

    def _maximize_slave(self):
        """Toggle the focused slave pane between min and max size."""
        n = len(self.clients) - 2  # total shrinking clients
        # total size of collapsed secondaries
        collapsed_size = self.min_slave_size * n
        nidx = self.focused - 1  # focused size index
        # total width of maximized slave
        maxed_size = self.screen_rect.width - collapsed_size
        # if maximized or nearly maximized
        if abs(
            self._get_absolute_size_from_relative(self.relative_sizes[nidx]) -
            maxed_size
        ) < self.change_size:
            # minimize
            self._shrink_slave(
                self._get_absolute_size_from_relative(
                    self.relative_sizes[nidx]
                ) - self.min_slave_size
            )
        # otherwise maximize
        else:
            self._grow_slave(maxed_size)

    def _configure_specific(self, client, screen_rect, px, cidx):
        """Specific configuration for xmonad wide."""
        self.screen_rect = screen_rect

        # calculate master/slave column widths
        height_master = int(self.screen_rect.height * self.ratio)
        height_slave = self.screen_rect.height - height_master

        # calculate client's x offset
        if self.align == self._up:  # up orientation
            if client in self.master_windows:
                # master client
                ypos = self.screen_rect.y
            else:
                # slave client
                ypos = self.screen_rect.y + height_master
        else:  # right or down orientation
            if client in self.master_windows:
                # master client
                ypos = self.screen_rect.y + height_slave - self.margin
            else:
                # slave client
                ypos = self.screen_rect.y

        # calculate client height and place
        if client in self.slave_windows:
            # slave client
            height = height_slave - 2 * self.border_width
            # xpos is the sum of all clients left of it
            width = self.screen_rect.width // len(self.slave_windows)
            xpos = self.screen_rect.x + \
                self.clients[self.master_length:].index(client) * width
            # get width from precalculated width list
            width = self.screen_rect.width // len(self.slave_windows)

            # fix double margin
            if cidx > 1:
                xpos -= self.margin
                width += self.margin
            # place client based on calculated dimensions
            client.place(
                xpos,
                ypos,
                width - 2 * self.border_width,
                height,
                self.border_width,
                px,
                margin=self.margin,
            )
        else:
            pos = self.clients.index(client)
            if self.orientation == self._hori:
                width = self.screen_rect.width // self.master_length
                height = height_master
                xpos = self.screen_rect.x + pos * width
            else:
                width = self.screen_rect.width
                height = height_master // self.master_length
                xpos = self.screen_rect.x
                if self.align == self._up:
                    ypos = self.screen_rect.y + pos * height
                else:
                    ypos = (self.screen_rect.y + height_slave + height_master) - (pos + 1) * height

            # master client
            client.place(
                xpos,
                ypos,
                width,
                height,
                self.border_width,
                px,
                margin=[
                    self.margin,
                    self.margin + 2*self.border_width,
                    2*self.border_width,
                    self.margin,
                ],
            )

    def _shrink_slave(self, amt):
        """Will shrink the focused client in the slave pane"""
        # get focused client
        client = self.clients[self.focused]

        # get default change size
        change = amt

        # get left-over height after change
        left = client.width - amt
        # if change would violate min_slave_size
        if left < self.min_slave_size:
            # just reduce to min_slave_size
            change = client.width - self.min_slave_size

        # calculate half of that change
        half_change = change / 2

        # first slave (top)
        if self.focused == 1:
            # only grow downwards
            self.grow_down_shared(0, change)
        # last slave (bottom)
        elif self.focused == len(self.clients) - 1:
            # only grow upwards
            self.grow_up_shared(len(self.relative_sizes) - 1, change)
        # middle slave
        else:
            idx = self.focused - 1
            # grow up and down
            self.grow_up_shared(idx, half_change)
            self.grow_down_shared(idx, half_change)
        # shrink client by total change
        self.relative_sizes[self.focused - 1] -= \
            self._get_relative_size_from_absolute(change)

    def cmd_swap_left(self):
        """Swap current window with closest window to the down"""
        win = self.clients.current_client
        x, y = win.x, win.y
        candidates = [c for c in self.clients.clients if c.info()["y"] > y]
        target = self._get_closest(x, y, candidates)
        self.cmd_swap(win, target)

    def cmd_swap_right(self):
        """Swap current window with closest window to the up"""
        win = self.clients.current_client
        x, y = win.x, win.y
        candidates = [c for c in self.clients if c.info()["y"] < y]
        target = self._get_closest(x, y, candidates)
        self.cmd_swap(win, target)
