#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Collab Profile — avatar generator (AI Horde).

Generates the RPG avatar via AI Horde (https://aihorde.net) — an open, volunteer-run
GPU network with a documented anonymous API key `0000000000` (official docs). Free,
no registration, no personal tokens. Stdlib only.

Anonymous constraints (honest): max 751x751 pixels (this script uses 576x832 portrait,
which fits the pixel budget), queue priority is lowest (typically 1-5 minutes), model
is whatever a worker provides unless --model is given. On any failure the skill says
so and leaves the avatar slot empty — no substitutes.

Usage:
  python avatar.py --from-profile profile.json -o avatar.webp
  python avatar.py --prompt "epic fantasy portrait ..." -o avatar.webp [--model "AlbedoBase XL (SDXL)"]
"""
import argparse
import json
import sys
import time
import urllib.request

API = "https://stablehorde.net/api/v2"
CLIENT = "ai-collab-profile:1.0:github.com/timoncool/ai-collab-profile"
WIDTH, HEIGHT, STEPS = 576, 832, 28  # fits the anonymous <=751x751 pixel budget
POLL_S, MAX_WAIT_S = 10, 1200


def call(path, payload=None, timeout=30):
    headers = {"apikey": "0000000000", "Client-Agent": CLIENT,
               "Content-Type": "application/json"}
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(API + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def generate(prompt, out_path, model=None):
    body = {
        "prompt": prompt,
        "params": {"width": WIDTH, "height": HEIGHT, "steps": STEPS,
                   "n": 1, "cfg_scale": 7, "sampler_name": "k_euler_a"},
        "nsfw": False, "r2": True,
    }
    if model:
        body["models"] = [model]
    job = call("/generate/async", body)
    job_id = job["id"]

    start = time.time()
    while time.time() - start < MAX_WAIT_S:
        state = call("/generate/check/" + job_id)
        if state.get("done"):
            break
        if state.get("faulted"):
            raise RuntimeError("horde job faulted")
        print("queue=%s wait~%ss" % (state.get("queue_position"),
                                     state.get("wait_time")), file=sys.stderr)
        time.sleep(POLL_S)
    else:
        raise RuntimeError("timed out after %ds in queue" % MAX_WAIT_S)

    result = call("/generate/status/" + job_id, timeout=60)
    gens = result.get("generations") or []
    if not gens:
        raise RuntimeError("no generations returned: " + json.dumps(result)[:300])
    gen = gens[0]
    with urllib.request.urlopen(gen["img"], timeout=60) as img, \
            open(out_path, "wb") as fh:
        data = img.read()
        if len(data) < 10000:
            raise RuntimeError("suspiciously small file (%d bytes)" % len(data))
        fh.write(data)
    return len(data), gen.get("model"), gen.get("worker_name")


def main():
    ap = argparse.ArgumentParser(description="RPG avatar via AI Horde (anonymous, free, open)")
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--from-profile", default=None, help="take avatar_prompt from profile.json")
    ap.add_argument("--model", default=None, help="preferred horde model, e.g. 'AlbedoBase XL (SDXL)'")
    ap.add_argument("-o", "--output", default="avatar.webp")
    args = ap.parse_args()

    prompt = args.prompt
    if args.from_profile:
        profile = json.load(open(args.from_profile, encoding="utf-8"))
        prompt = prompt or profile.get("avatar_prompt")
    if not prompt:
        print("error: no prompt (--prompt or --from-profile)", file=sys.stderr)
        sys.exit(2)

    try:
        size, model, worker = generate(prompt, args.output, args.model)
        print("written: %s (%d bytes, model=%s, worker=%s)" % (args.output, size, model, worker))
    except Exception as exc:
        print("avatar generation failed: %s" % exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
