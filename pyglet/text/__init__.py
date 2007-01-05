#!/usr/bin/env python

'''

TODO in near future:
 - Kerning
 - Character spacing
 - Word spacing

TODO much later:
 - BIDI
 - Vertical text
 - Path following?
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import sys
import os

from pyglet.GL.VERSION_1_1 import *
from pyglet.window import *
from pyglet.image import *
import pyglet.layout.base

class Glyph(TextureSubImage):
    advance = 0
    vertices = (0, 0, 0, 0)

    def set_bearings(self, baseline, left_side_bearing, advance):
        self.advance = advance
        self.vertices = (
            left_side_bearing,
            -baseline,
            left_side_bearing + self.width,
            -baseline + self.height)

    def draw(self):
        '''Debug method: use the higher level APIs for performance and
        kerning.'''
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        glBegin(GL_QUADS)
        self.draw_quad_vertices()
        glEnd()

    def draw_quad_vertices(self):
        '''Debug method: use the higher level APIs for performance and
        kerning.'''
        glTexCoord2f(self.tex_coords[0], self.tex_coords[1])
        glVertex2f(self.vertices[0], self.vertices[1])
        glTexCoord2f(self.tex_coords[2], self.tex_coords[1])
        glVertex2f(self.vertices[2], self.vertices[1])
        glTexCoord2f(self.tex_coords[2], self.tex_coords[3])
        glVertex2f(self.vertices[2], self.vertices[3])
        glTexCoord2f(self.tex_coords[0], self.tex_coords[3])
        glVertex2f(self.vertices[0], self.vertices[3])

    def get_kerning_pair(self, right_glyph):
        return 0

class GlyphTextureAtlas(AllocatingTextureAtlas):
    subimage_class = Glyph

    def apply_blend_state(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

class GlyphRenderer(object):
    def __init__(self, font):
        pass

    def render(self, text):
        raise NotImplementedError('Subclass must override')

class FontException(Exception):
    pass

class BaseFont(object):
    texture_width = 256
    texture_height = 256
    texture_internalformat = GL_ALPHA

    # These two need overriding by subclasses
    glyph_texture_atlas_class = GlyphTextureAtlas
    glyph_renderer_class = GlyphRenderer

    # These should also be set by subclass when known
    ascent = 0
    descent = 0

    def __init__(self):
        self.textures = []
        self.glyphs = {}

    @classmethod
    def add_font_data(cls, data):
        # Ignored unless overridden
        pass

    @classmethod
    def have_font(cls, name):
        # Subclasses override
        return True

    def allocate_glyph(self, width, height):
        # Search atlases for a free spot
        for texture in self.textures:
            try:
                return texture.allocate(width, height)
            except AllocatingTextureAtlasOutOfSpaceException:
                pass

        # If requested glyph size is bigger than atlas size, increase
        # next atlas size.  A better heuristic could be applied earlier
        # (say, if width is > 1/4 texture_width).
        if width > self.texture_width or height > self.texture_height:
            self.texture_width, self.texture_height, u, v= \
                Texture.get_texture_size(width * 2, height * 2)

        texture = self.glyph_texture_atlas_class.create(
            self.texture_width,
            self.texture_height,
            self.texture_internalformat)
        self.textures.insert(0, texture)

        # This can't fail.
        return texture.allocate(width, height)

    def get_glyphs(self, text):
        '''Create and return a list of Glyphs for 'text'.
        '''
        glyph_renderer = None
        glyphs = []         # glyphs that are committed.
        for c in text:
            # Get the glyph for 'c'
            if c not in self.glyphs:
                if not glyph_renderer:
                    glyph_renderer = self.glyph_renderer_class(self)
                self.glyphs[c] = glyph_renderer.render(c)
            glyphs.append(self.glyphs[c])
        return glyphs


    def get_glyphs_for_width(self, text, width):
        '''Create and return a list of Glyphs that fit within 'width',
        beginning with the text 'text'.  If the entire text is larger than
        'width', as much as possible will be used while breaking after
        a space or zero-width space character.  If a newline is enountered
        in text, only text up to that newline will be used.  If no break
        opportunities (newlines or spaces) occur within 'width', the text
        up to the first break opportunity will be used (this will exceed
        'width').  If there are no break opportunities, the entire text
        will be used.
        '''
        glyph_renderer = None
        glyph_buffer = []   # next glyphs to be added, as soon as a BP is found
        glyphs = []         # glyphs that are committed.
        for c in text:
            if c == '\n':
                glyphs += glyph_buffer
                break

            # Get the glyph for 'c'
            if c not in self.glyphs:
                if not glyph_renderer:
                    glyph_renderer = self.glyph_renderer_class(self)
                self.glyphs[c] = glyph_renderer.render(c)
            glyph = self.glyphs[c]
            
            # Add to holding buffer and measure
            glyph_buffer.append(glyph)
            width -= glyph.advance
            
            # If over width and have some committed glyphs, finish.
            if width <= 0 and len(glyphs) > 0:
                break

            # If a valid breakpoint, commit holding buffer
            if c in u'\u0020\u200b':
                glyphs += glyph_buffer
                glyph_buffer = []

        # If nothing was committed, commit everything (no breakpoints found).
        if len(glyphs) == 0:
            glyphs = glyph_buffer

        return glyphs

    def render(self, text, color=(1, 1, 1, 1)):
        raise NotImplementedError('Functionality temporarily removed')
        
    
# Load platform dependent module
if sys.platform == 'darwin':
    from pyglet.text.carbon import CarbonFont
    _font_class = CarbonFont
elif sys.platform == 'win32':
    from pyglet.text.win32 import Win32Font
    _font_class = Win32Font
else:
    from pyglet.text.freetype import FreeTypeFont
    _font_class = FreeTypeFont

class Font(object):
    def __new__(cls, name, size, bold=False, italic=False):
        # Find first matching name
        if type(name) in (tuple, list):
            for n in name:
                if _font_class.have_font(n):
                    name = n
                    break
            else:
                name = None
    
        # Locate or create font cache   
        shared_object_space = get_current_context().get_shared_object_space()
        if not hasattr(shared_object_space, 'pyglet_text_font_cache'):
            shared_object_space.pyglet_text_font_cache = {}
        font_cache = shared_object_space.pyglet_text_font_cache

        # Look for font name in font cache
        descriptor = (name, size, bold, italic)
        if descriptor in font_cache:
            return font_cache[descriptor]

        # Not in cache, create from scratch
        font = _font_class(name, size, bold=bold, italic=italic)
        font_cache[descriptor] = font
        return font

    @staticmethod
    def add_font(font):
        if type(font) in (str, unicode):
            font = open(font, 'r')
        if hasattr(font, 'read'):
            font = font.read()
        _font_class.add_font_data(font)


    @staticmethod
    def add_font_dir(dir):
        import os
        for file in os.listdir(dir):
            if file[:-4].lower() == '.ttf':
                add_font(file)


