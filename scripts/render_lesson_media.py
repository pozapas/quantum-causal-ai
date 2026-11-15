"""Render the Manim animations of an advanced (schema 3) lesson into _static/animations/.  Run from book/.

    python scripts/render_lesson_media.py _data/level3_drafts/L3-01.json            # every animation block
    python scripts/render_lesson_media.py _data/level3_drafts/L3-01.json --only Cls  # one scene class

Renders at 720p30 in a temporary media folder, copies the MP4, and prints codec, length and size.
"""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

import av

BOOK = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable


def render(scene: str, file: str, quality: str = "m") -> str:
    scene_file, _, cls = scene.partition(":")
    out = BOOK / "_static" / "animations" / file
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as media:
        cmd = [PY, "-m", "manim", f"-q{quality}", "--format", "mp4", "--disable_caching", "--media_dir", media,
               "-o", "render", str(BOOK / scene_file), cls]
        r = subprocess.run(cmd, cwd=BOOK, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
        if r.returncode != 0:
            sys.exit(f"manim failed for {scene}:\n{(r.stdout + r.stderr)[-3000:]}")
        found = [p for p in pathlib.Path(media).rglob("render.mp4") if "partial_movie_files" not in p.parts]
        if not found:
            sys.exit(f"no output video found for {scene}")
        shutil.copy2(found[0], out)
    c = av.open(str(out))
    v = c.streams.video[0]
    msg = (f"{out.name}: {v.codec_context.name}/{v.codec_context.pix_fmt} {v.codec_context.width}x{v.codec_context.height} "
           f"{float(c.duration / 1e6):.1f} s {out.stat().st_size // 1000} KB")
    c.close()
    return msg


if __name__ == "__main__":
    args = sys.argv[1:]
    only = None
    if "--only" in args:
        only = args[args.index("--only") + 1]
        args = [a for a in args if a not in ("--only", only)]
    for p in args:
        L = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        for s in L["sections"]:
            for b in s["blocks"]:
                if b["type"] == "animation" and (only is None or b["scene"].endswith(":" + only)):
                    print(render(b["scene"], b["file"]))
