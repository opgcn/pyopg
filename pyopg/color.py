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
__version__ = '.'.join(map(str, (0, 1, 0)))
__author__  = 'Lei Li <i@lilei.tech>'
__date__    = '2020-11-01'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import enum, functools

# import functools.cached_property() new in python 3.8
if not hasattr(functools, 'cached_property'):
    import new3
    functools.cached_property = new3.cached_property

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@enum.unique
class EnumCodes(enum.Enum):
    r"""Enumeration base class for SGR codes.
    """
    @classmethod
    def items(cls):
        r"""A generator of (name, value) pairs like dict.items().
        """
        return ((each.name, each.value) for each in cls)
        
    @enum.DynamicClassAttribute
    def pair(self):
        r"""A tuple of current enumeration member's (name, value).
        """
        return self.name, self.value
        
    def __repr__(self):
        r"""Short description in `repr()`.
        """
        return f"{self.name}:{self.value}"
        
# Enumeration class for SGR styles
STY = EnumCodes('EnumStyles', (
    ('RESET',       0),
    ('BOLD',        1),
    ('DIM',         2),
    ('ITALIC',      3),
    ('UNDERLINED',  4),
    ('BLINKED',     5),
    ('RAPID',       6),
    ('REVERSED',    7),
    ('HIDDEN',      8),
    ('CROSSED',     9),
))

# Enumeration class for SGR foregrounds
FG = EnumCodes('EnumForegrounds', (
    ('DEFAULT',     39),
    ('BLACK',       30),
    ('RED',         31),
    ('GREEN',       32),
    ('YELLOW',      33),
    ('BLUE',        34),
    ('MAGENTA',     35),
    ('CYAN',        36),
    ('WHITE',       37),
    ('BLACK_B',     90),
    ('RED_B',       91),
    ('GREEN_B',     92),
    ('YELLOW_B',    93),
    ('BLUE_B',      94),
    ('MAGENTA_B',   95),
    ('CYAN_B',      96),
    ('WHITE_B',     97),
))

# Enumeration class for SGR backgrounds
BG = EnumCodes('EnumBackgrounds', ( (each.name, each.value+10) for each in FG ))

class Renderer(tuple):
    r"""A renderer as a tuple of SGR codes, aka a palette.
    """
    
    # For CSI (Control Sequence Introducer), the starter `ESC [` is followed by any number (including none) of "parameter bytes", and then finally by a single ender "final byte"(aka `m`).
    csi_starter, csi_ender = "\x1b[", "m"
    
    # If no codes are given, `CSI m` is treated as `CSI 0 m` (reset / normal)
    csi_resetter = csi_starter + csi_ender
    
    def __new__(cls, *codes):
        r"""Create the object from SGR codes (can be enum.Enum instances, int numbers, strings, etc.).
        """
        return super().__new__(cls, codes)
        
    @functools.cached_property
    def csi_attributes(self):
        r"""Several attributes can be set in the same sequence, separated by semicolons.
        """
        return ';'.join(f"{x.value}" if isinstance(x, enum.Enum) else f"{x}" for x in self)
        
    @functools.cached_property
    def csi_seq(self):
        r"""A escaped CSI sequence of all SGR codes.
        """
        return f"{self.csi_starter}{self.csi_attributes}{self.csi_ender}"
        
    def wrap(self, text, reset=True):
        r"""Wrap text with CSI sequences, optionally reset all attributes off at the end.
        """
        return f"{self.csi_seq}{text}{self.csi_resetter if reset else ''}"
        
    def __call__(self, *t, **d):
        r"""Instance is called, same as `wrap()` does.
        """
        return self.wrap(*t, **d)
    
def get_cheet_sheet_16(styles=STY, backgrounds=BG, foregrounds=FG, col_width=12, col_sep='|'):
    r"""Demonstration of colors and styles in 16-colors terminal mode.
    """
    import io, os
    with io.StringIO() as sio:
        sio.write(f"ANSI 16-Color Cheet Sheet {os.linesep}")
        sio.write(f"@styles: {styles}{os.linesep}")
        sio.write(f"@backgrounds: {backgrounds}{os.linesep}")
        sio.write(f"@foregrounds: {foregrounds}{os.linesep}")
        for bg in backgrounds:
            sio.write(f"{os.linesep}Table of @BG={bg!r}{os.linesep}{'@FG & @STY':^{col_width}}")
            for sty in styles:
                sio.write(f"{col_sep}{sty!r:^{col_width}}")
            sio.write(os.linesep)
            for fg in foregrounds:
                sio.write(f"{fg!r:^{col_width}}")
                for sty in styles:
                    sio.write(f"{col_sep}")
                    palette = Renderer(sty, bg, fg)
                    text = palette.csi_attributes
                    sio.write(palette(f"{text:^{col_width}}"))
                sio.write(os.linesep)
        return sio.getvalue()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
if __name__ == "__main__":

    # only demonstrates given styles & colors
    print(
        get_cheet_sheet_16(
            styles      = [STY(n) for n in (0,1,2,4,5,7)],
            backgrounds = [x for x in BG if x.value != 49],
            foregrounds = [x for x in FG if x.value != 39],
        )
    )
