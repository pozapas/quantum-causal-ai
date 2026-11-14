"""Render a lesson's Manim animation into _static/animations/.  Run from book/.

    python scripts/render_animation.py _data/level1_drafts/L1-03.json [--quality m]

Reads `animation.scene` ("scripts/manim/l1_03.py:ClassName") and `animation.file`
from the lesson JSON, renders at 720p30 into a temporary media folder (nothing is
written inside book/ except the final MP4), then checks codec, length and size.
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


def render(lesson_path: str, quality: str = "m") -> pathlib.Path:
    L = json.loads(pathlib.Path(lesson_path).read_text(encoding="utf-8"))
    a = L["animation"]
    scene_file, _, cls = a["scene"].partition(":")
    out = BOOK / "_static" / "animations" / a["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as media:
        cmd = [PY, "-m", "manim", f"-q{quality}", "--format", "mp4", "--disable_caching", "--media_dir", media,
               "-o", "render", str(BOOK / scene_file), cls]
        r = subprocess.run(cmd, cwd=BOOK, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        if r.returncode != 0:
            sys.exit(f"manim failed for {a['scene']}:\n{(r.stdout + r.stderr)[-3000:]}")
        found = [p for p in pathlib.Path(media).rglob("render.mp4") if "partial_movie_files" not in p.parts]
        if not found:
            sys.exit(f"no output video found for {a['scene']}")
        shutil.copy2(found[0], out)
    c = av.open(str(out))
    v = c.streams.video[0]
    print(f"{out.name}: {v.codec_context.name}/{v.codec_context.pix_fmt} {v.codec_context.width}x{v.codec_context.height} "
          f"{float(c.duration / 1e6):.1f} s {out.stat().st_size // 1000} KB")
    c.close()
    return out


if __name__ == "__main__":
    q = "m"
    args = [x for x in sys.argv[1:] if not x.startswith("--quality")]
    if "--quality" in " ".join(sys.argv):
        q = sys.argv[sys.argv.index("--quality") + 1]
        args = [x for x in args if x != q]
    for p in args:
        render(p, q)
