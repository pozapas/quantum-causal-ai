"""One PNG with 6 evenly spaced frames of an animation, to inspect it at a glance.  Run from book/.

    python tests/contact_sheet.py _static/animations/l3_01_complex_plane.mp4 OUT.png
"""
import sys

import av
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
c = av.open(src)
s = c.streams.video[0]
total = s.frames or int(float(c.duration / 1e6) * float(s.average_rate))
want = {int(total * k / 6) + 2 for k in range(6)}
want = sorted(min(w, total - 1) for w in want)
frames = []
for i, f in enumerate(c.decode(s)):
    if i in want:
        frames.append((i, f.to_image().resize((640, 360))))
c.close()
sheet = Image.new("RGB", (1280, 360 * ((len(frames) + 1) // 2)), "white")
for k, (i, im) in enumerate(frames):
    ImageDraw.Draw(im).text((8, 6), f"frame {i} ({i / float(s.average_rate):.1f} s)", fill=(120, 120, 120))
    sheet.paste(im, ((k % 2) * 640, (k // 2) * 360))
sheet.save(out)
print("wrote", out, "frames", [i for i, _ in frames])
