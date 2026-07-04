#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt Warrior — inline-SVG generator for the card.

Prints READY-TO-PASTE inline SVG for icons, the favicon <link> and the footer seal,
so the model NEVER has to read raw .svg files into context. Path data is extracted
here (background rectangle stripped, fill="currentColor" applied).

Usage:
  python icons.py achievement <id> <rarity> [size=38]   # medallion icon (falls back to _<rarity>)
  python icons.py section <name> [size=20]              # section header icon
  python icons.py favicon                               # data-URI <link rel="icon"> for <head>
  python icons.py seal [size=32]                        # emblem+PW SVG for the footer wax seal
  python icons.py list                                  # available icon names
"""
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACH_DIR = os.path.join(ROOT, "assets", "achievement-icons")
SECT_DIR = os.path.join(ROOT, "assets", "section-icons")
EMBLEM = os.path.join(ROOT, "assets", "swords-emblem.svg")

BG_RE = re.compile(r"^[Mm]0[,]?0[Hh]512[Vv]512[Hh]0[Zz]?$")


def paths(svg_file):
    """(viewBox, [<path d> values]) except the background rectangle."""
    svg = open(svg_file, encoding="utf-8").read()
    vb = re.search(r'viewBox="([^"]+)"', svg)
    ds = [d for d in re.findall(r'<path[^>]*\bd="([^"]+)"', svg)
          if not BG_RE.match(d.replace(" ", ""))]
    return (vb.group(1) if vb else "0 0 512 512"), ds


def inline(svg_file, size, style=""):
    vb, ds = paths(svg_file)
    body = "".join('<path fill="currentColor" d="%s"/>' % d for d in ds)
    st = ' style="%s"' % style if style else ""
    return '<svg viewBox="%s" width="%d" height="%d"%s>%s</svg>' % (vb, size, size, st, body)


def achievement(aid, rarity, size=38):
    for name in (aid, "_" + rarity):
        fp = os.path.join(ACH_DIR, name + ".svg")
        if os.path.exists(fp):
            return inline(fp, size)
    raise SystemExit("no icon for %s/%s" % (aid, rarity))


def section(name, size=20):
    fp = os.path.join(SECT_DIR, name + ".svg")
    if not os.path.exists(fp):
        raise SystemExit("no section icon %r (see: icons.py list)" % name)
    return inline(fp, size, "flex:none;filter:drop-shadow(0 1px 1px rgba(0,0,0,.5))")


def _emblem_svg(with_circle):
    ds = paths(EMBLEM)[1]
    parts = []
    if with_circle:
        parts.append('<circle cx="256" cy="256" r="246" fill="#8B2635"/>')
        parts += ['<path fill="#E8CFB4" transform="translate(56 56) scale(0.78)" d="%s"/>' % d for d in ds]
        parts.append('<text x="256" y="300" font-family="Georgia,serif" font-weight="bold" '
                     'font-size="96" fill="#8B2635" text-anchor="middle">PW</text>')
    else:
        parts += ['<path fill="#E8CFB4" d="%s"/>' % d for d in ds]
        parts.append('<text x="256" y="316" font-family="Georgia,serif" font-weight="bold" '
                     'font-size="124" fill="#5E1822" text-anchor="middle">PW</text>')
    return "".join(parts)


def favicon():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">%s</svg>'
           % _emblem_svg(True))
    return '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%s">' % urllib.parse.quote(svg)


def seal(size=32):
    return '<svg viewBox="0 0 512 512" width="%d" height="%d">%s</svg>' % (size, size, _emblem_svg(False))


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    cmd = args[0]
    if cmd == "achievement":
        print(achievement(args[1], args[2], int(args[3]) if len(args) > 3 else 38))
    elif cmd == "section":
        print(section(args[1], int(args[2]) if len(args) > 2 else 20))
    elif cmd == "favicon":
        print(favicon())
    elif cmd == "seal":
        print(seal(int(args[1]) if len(args) > 1 else 32))
    elif cmd == "list":
        print("sections:", ", ".join(sorted(f[:-4] for f in os.listdir(SECT_DIR) if f.endswith(".svg"))))
        print("achievements:", ", ".join(sorted(f[:-4] for f in os.listdir(ACH_DIR) if f.endswith(".svg"))))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
