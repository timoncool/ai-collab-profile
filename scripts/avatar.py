#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prompt Warrior — local avatar: a deterministic monster from your title.

Uses the `robohash` package (MIT; assembles PNG layers bundled with the package —
fully offline, no network, no API). Monster art set2 by Hrvoje Novakovic (CC-BY-3.0).
The seed is your title, so when your title changes, your monster evolves.

Optional dependency:
  pip install robohash

Usage:
  python avatar.py --from-profile profile.json -o avatar.png
  python avatar.py --seed "любая строка" -o avatar.png [--set set2] [--size 512]
"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser(description="Local deterministic monster avatar (RoboHash)")
    ap.add_argument("--from-profile", default=None, help="use title from profile.json as seed")
    ap.add_argument("--seed", default=None)
    ap.add_argument("--set", dest="roboset", default="set2",
                    help="set2 = monsters (default), set1 = robots, set4 = kittens")
    ap.add_argument("--size", type=int, default=512)
    ap.add_argument("-o", "--output", default="avatar.png")
    args = ap.parse_args()

    seed = args.seed
    if args.from_profile:
        profile = json.load(open(args.from_profile, encoding="utf-8"))
        seed = seed or profile["title"]["ru"]
    if not seed:
        print("error: no seed (--seed or --from-profile)", file=sys.stderr)
        sys.exit(2)

    try:
        from robohash import Robohash
    except ImportError:
        print("robohash is not installed. Local avatars are optional; to enable:\n"
              "  pip install robohash", file=sys.stderr)
        sys.exit(3)

    rh = Robohash(seed)
    rh.assemble(roboset=args.roboset, sizex=args.size, sizey=args.size)
    with open(args.output, "wb") as fh:
        rh.img.save(fh, format="PNG")
    print("written: %s (seed=%r, set=%s)" % (args.output, seed, args.roboset))


if __name__ == "__main__":
    main()
