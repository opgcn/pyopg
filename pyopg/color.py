#!/usr/bin/env python3
# coding: utf-8
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
r"""SGR terminal text style and color renderer.

This module supplies "Select Graphic Rendition", which sets display attributes (styles, colors) on terminal text. See more:
https://en.wikipedia.org/wiki/ANSI_escape_code
https://misc.flogisoft.com/bash/tip_colors_and_formatting
"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# metadata

from . import __version__, __author__, __date__

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import enum, itertools, functools

# import compatibale functools.cached_property() new in python 3.8
if not hasattr(functools, 'cached_property'):
    from . import new3
    functools.cached_property = new3.cached_property

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@enum.unique
class EnumCodes(int, enum.Enum):
    r"""Enumeration base class for SGR codes.
    """
    def __init__(self, *t, **d):
        r"""Code must be in range 0 <= x < 256.
        """
        if not self.value in range(256):
            raise ValueError(f"Code element {self!r} not in range 0 <= x < 256.")

    @enum.DynamicClassAttribute
    def pair(self):
        r"""A tuple of current enumeration member's (name, value).
        """
        return self.name, self.value

    @classmethod
    def items(cls):
        r"""A generator of (name, value) pairs like dict.items().
        """
        return (member.pair for member in cls)

    def __repr__(self):
        r"""Short description of member.
        """
        return f"{self.__class__.__qualname__}.{self.name}:{self.value}"

# Enumeration class for SGR styles
STY = EnumCodes('STY', (
    ('RESET',       0), # All attributes off
    ('BOLD',        1), # Bold or increased intensity
    ('DIM',         2), # May be implemented as a light font weight like bold
    ('ITALIC',      3), # not widely supported, treated as inverse or blink
    ('UNDER',       4), # Underline
    ('BLINK',       5), # less than 150 per minute
    ('RAPID',       6), # not widely supported, 150+ per minute
    ('INVERT',      7), # swap fg and bg colors, aka reversed
    ('HIDE',        8), # not widely supported, aka Conceal
    ('CROSS',       9), # not widely supported, marked as deletion
))

# Enumeration class for SGR foregrounds
FG = EnumCodes('FG', (
    ('DEFAULT',     39),
    ('BLACK',       30), # without 'B_' indicates 'normal'
    ('RED',         31),
    ('GREEN',       32),
    ('YELLOW',      33),
    ('BLUE',        34),
    ('MAGENTA',     35),
    ('CYAN',        36),
    ('WHITE',       37),
    ('B_BLACK',     90), # with 'B_' indicates 'bright'
    ('B_RED',       91),
    ('B_GREEN',     92),
    ('B_YELLOW',    93),
    ('B_BLUE',      94),
    ('B_MAGENTA',   95),
    ('B_CYAN',      96),
    ('B_WHITE',     97),
))

# Enumeration class for SGR backgrounds
BG = EnumCodes('BG', ( (each.name, each.value+10) for each in FG ))

class Seq(bytes):
    r"""A SGR codes sequence, aka a palette, as a renderer.
    """

    # For CSI (Control Sequence Introducer), the starter `ESC [` is followed by any number (including none) of "parameter bytes", and then finally by a single ender "final byte"(aka `m`).
    csi_starter, csi_ender = "\x1b[", "m"

    # If no codes are given, `CSI m` is treated as `CSI 0 m` (reset / normal)
    csi_resetter = csi_starter + csi_ender

    def __new__(cls, *codes):
        r"""Create the object from SGR codes, each must be int convertable and 0 <= x < 256.
        """
        return super().__new__(cls, map(int, codes))

    @functools.cached_property
    def csi_attributes(self):
        r"""Several attributes can be set in the same sequence, separated by semicolons.
        """
        return ';'.join(map(str, self))

    @functools.cached_property
    def csi_seq(self):
        r"""A escaped CSI sequence of all SGR codes.
        """
        return f"{self.csi_starter}{self.csi_attributes}{self.csi_ender}"

    def render(self, text, reset=True):
        r"""Render text with CSI sequences, optionally reset all attributes off at the end.
        """
        return f"{self.csi_seq}{text}{self.csi_resetter if reset else ''}"

    def __call__(self, *t, **d):
        r"""Instance is called, same as `render()` does.
        """
        return self.render(*t, **d)

    def __str__(self):
        r"""Same as `csi_seq` property.
        """
        return self.csi_seq

    def __repr__(self):
        r"""Short description of self.
        """
        return f"{self.__class__.__qualname__}({','.join(map(str, self))})"

    def __add__(self, other):
        r"""Implement self + other.
        """
        return self.__class__(*itertools.chain(self, other))

    def __radd__(self, other):
        r"""Implement other + self.
        """
        return self.__class__(*itertools.chain(other, self))

def get_cheet_sheet_16(styles=STY, backgrounds=BG, foregrounds=FG, col_width=16, col_sep='|'):
    r"""Demonstration of colors and styles in 16-colors terminal mode.
    """
    import io, os
    seqKey=Seq(STY.DIM, STY.UNDER)
    seqTitle=Seq(STY.BOLD, STY.INVERT)
    table_width=(len(styles)+1)*(col_width+1)-1
    with io.StringIO(newline=None) as sio:
        sio.write(seqTitle(f"{'ANSI 16-Color Cheet Sheet'.center(table_width)}\n"))
        sio.write(seqKey(f"\n@styles: {styles}\n"))
        sio.write(seqKey(f"\n@backgrounds: {backgrounds}\n"))
        sio.write(seqKey(f"\n@foregrounds: {foregrounds}"))
        for bg in backgrounds:
            sio.write(seqTitle(f"\n\n{'Table of @background = {bg!r}'.center(table_width)}\n"))
            sio.write(seqKey(f"{'@FG & @STY':^{col_width}}"))
            for sty in styles:
                sio.write(f"{col_sep}{sty!r:^{col_width}}")
            for fg in foregrounds:
                sio.write(f"\n{fg!r:^{col_width}}")
                for sty in styles:
                    sio.write(f"{col_sep}")
                    seq = Seq(sty, bg, fg)
                    sio.write(seq(f"{seq.csi_attributes:^{col_width}}"))
        sio.write('\n')
        return sio.getvalue()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":
    # only demonstrates given styles & colors
    print(
        get_cheet_sheet_16(
            styles      = [STY(n) for n in (0,1,2,4,5,7)],
            backgrounds = [x for x in BG if x is not BG.DEFAULT],
            foregrounds = [x for x in FG if x != 39],
        )
    )
