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
import enum, functools

# import compatibale functools.cached_property() new in python 3.8
if not hasattr(functools, 'cached_property'):
    from . import new3
    functools.cached_property = new3.cached_property

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@enum.unique
class EnumCodes(int, enum.Enum):
    r"""Enumeration base class for SGR codes.
    """
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
        return f"{self.__class__.__name__}.{self.name}:{self.value}"

    def __str__(self):
        r"""String of member's value.
        """
        return str(self.value)
        
# Enumeration class for SGR styles
STY = EnumCodes('STY', (
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
FG = EnumCodes('FG', (
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
BG = EnumCodes('BG', ( (each.name, each.value+10) for each in FG ))

class Seq(tuple):
    r"""A renderer as a tuple of SGR codes sequence, aka a palette.
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
        
    def __str__(self):
        r"""Same as `csi_seq` property.
        """
        return self.csi_seq

    def __repr__(self):
        r"""Short description of self.
        """
        return self.__class__.__name__+super().__repr__().replace(' ','')
    
    def __call__(self, *t, **d):
        r"""Instance is called, same as `render()` does.
        """
        return self.render(*t, **d)
    
def get_cheet_sheet_16(styles=STY, backgrounds=BG, foregrounds=FG, col_width=16, col_sep='|'):
    r"""Demonstration of colors and styles in 16-colors terminal mode.
    """
    import io, os
    with io.StringIO(newline=None) as sio:
        sio.write(f"ANSI 16-Color Cheet Sheet\n\n")
        sio.write(f"@styles: {styles}\n\n")
        sio.write(f"@backgrounds: {backgrounds}\n\n")
        sio.write(f"@foregrounds: {foregrounds}\n")
        for bg in backgrounds:
            sio.write(f"\nTable of @background={bg!r}\n{'@FG & @STY':^{col_width}}")
            for sty in styles:
                sio.write(f"{col_sep}{sty!r:^{col_width}}")
            sio.write('\n')
            for fg in foregrounds:
                sio.write(f"{fg!r:^{col_width}}")
                for sty in styles:
                    sio.write(f"{col_sep}")
                    palette = Seq(sty, bg, fg)
                    text = palette.csi_attributes
                    sio.write(palette(f"{text:^{col_width}}"))
                sio.write('\n')
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
