# SPDX-License-Identifier: MIT
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

fb = FontBuilder(1000, isTTF=True)
# Glyph 0 is .notdef (required by spec). All codepoints are mapped to glyph 1
# (`tofu`) so browsers see a real, covered glyph and do not fall back to
# system fonts -- the same trick Adobe's AND-Regular uses.
fb.setupGlyphOrder([".notdef", "tofu"])

# Build cmap manually with format 13 (many-to-one) to map all of Unicode to `tofu`.
# fontBuilder.setupCharacterMap() can't handle this because format 4 overflows
# when a single segment maps the entire BMP to one glyph.
all_codepoints = {
    cp: "tofu"
    for cp in range(0x110000)
    if not (0xD800 <= cp <= 0xDFFF)
}


def make_cmap_13(platform_id, plat_enc_id):
    sub = CmapSubtable.getSubtableClass(13)()
    sub.platformID = platform_id
    sub.platEncID = plat_enc_id
    sub.format = 13
    sub.length = 0
    sub.language = 0
    sub.cmap = all_codepoints
    return sub


cmap = newTable("cmap")
cmap.tableVersion = 0
cmap.tables = [
    make_cmap_13(0, 6),    # Unicode platform, full repertoire (format 13)
    make_cmap_13(3, 10),   # Microsoft platform, UCS-4
]
fb.font["cmap"] = cmap

# Tofu: outlined rectangle with an X across it. Five contours -- the outer
# rectangle plus four triangles that carve out the X-shaped hole. Coordinates
# come from an SVG path with y negated (SVG y-down -> font y-up).
pen = TTGlyphPen(None)

# Outer rectangle (clockwise = filled).
pen.moveTo((50, 700))
pen.lineTo((450, 700))
pen.lineTo((450, 0))
pen.lineTo((50, 0))
pen.closePath()

# Top triangle of the X (counter-clockwise = hole).
pen.moveTo((103.6908, 660))
pen.lineTo((250, 391.7665))
pen.lineTo((396.3092, 660))
pen.closePath()

# Left triangle of the X (hole).
pen.moveTo((90, 601.5668))
pen.lineTo((90, 98.4332))
pen.lineTo((227.2182, 350))
pen.closePath()

# Right triangle of the X (hole).
pen.moveTo((272.7818, 350))
pen.lineTo((410, 98.4332))
pen.lineTo((410, 601.5668))
pen.closePath()

# Bottom triangle of the X (hole).
pen.moveTo((250, 308.2335))
pen.lineTo((103.6908, 40))
pen.lineTo((396.3092, 40))
pen.closePath()

tofu_glyph = pen.glyph()

fb.setupGlyf({".notdef": tofu_glyph, "tofu": tofu_glyph})
fb.setupHorizontalMetrics({".notdef": (500, 50), "tofu": (500, 50)})
fb.setupHorizontalHeader(ascent=800, descent=-200)
fb.setupNameTable({
    "familyName": "Pure Tofu Sans",
    "styleName": "Regular",
    "psName": "PureTofuSans-Regular",
    "version": "Version 1.000",
    "uniqueFontIdentifier": "PureTofuSans-Regular;1.000",
    "copyright": "Copyright (c) 2026 Jan Boesenberg",
    "designer": "Jan Boesenberg",
    "description": (
        "Pure Tofu Sans is a single-glyph fallback font that maps every Unicode codepoint to "
        "the same placeholder \"tofu\" shape. It is designed to be installed as a browser "
        "fallback font so that codepoints not covered by the primary webfont render as a "
        "plain tofu instead of triggering HarfBuzz's fallback substitution and positioning. "
        "This makes missing-glyph rendering deterministic and matches the behavior of font "
        "engines that do not implement HarfBuzz fallback shaping."
    ),
    "licenseDescription": (
        "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
        "This license is available with a FAQ at: https://openfontlicense.org"
    ),
    "licenseInfoURL": "https://openfontlicense.org",
})
fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
fb.setupHead(unitsPerEm=1000, created=0, modified=0)
fb.setupPost()

# GDEF classifies `tofu` as a base glyph so HarfBuzz never treats it as a
# combining mark -- otherwise codepoints whose Unicode general category is
# "Mark" (e.g. U+0301) would trigger HB's generic mark-stacking fallback.
# No-op Arabic shaping features so HarfBuzz's Arabic fallback shaper does not kick in.
fb.addOpenTypeFeatures("""
    table GDEF {
        GlyphClassDef [tofu], , , ;
    } GDEF;

    languagesystem DFLT dflt;
    languagesystem arab dflt;
    feature isol { sub tofu by tofu; } isol;
    feature init { sub tofu by tofu; } init;
    feature medi { sub tofu by tofu; } medi;
    feature fina { sub tofu by tofu; } fina;

    # No-op GPOS so HarfBuzz registers the font as having positioning data
    # and skips its generic positioning fallback.
    feature kern { pos tofu tofu 0; } kern;
    feature mark { pos tofu tofu 0; } mark;
    feature mkmk { pos tofu tofu 0; } mkmk;
""")

fb.save("PureTofuSans-Regular.ttf")
fb.font.flavor = "woff"
fb.save("PureTofuSans-Regular.woff")
fb.font.flavor = "woff2"
fb.save("PureTofuSans-Regular.woff2")