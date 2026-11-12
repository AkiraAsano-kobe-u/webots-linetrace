"""Generate textures/track.png: black ellipse line on white, 2048x2048 px for a 2x2 m floor."""
import math, struct, zlib, pathlib

N, SIZE_M = 2048, 2.0
A, B, HALF_W = 0.7, 0.5, 0.0125  # ellipse semi-axes and half line width [m]

pts = [(A * math.cos(t), B * math.sin(t)) for t in (2 * math.pi * i / 4000 for i in range(4000))]
img = [bytearray(b"\xff" * N) for _ in range(N)]
r = int(HALF_W / SIZE_M * N) + 1
for x, y in pts:
    cx, cy = (x / SIZE_M + 0.5) * N, (0.5 - y / SIZE_M) * N
    for py in range(int(cy) - r, int(cy) + r + 1):
        for px in range(int(cx) - r, int(cx) + r + 1):
            if (px - cx) ** 2 + (py - cy) ** 2 <= (HALF_W / SIZE_M * N) ** 2:
                img[py][px] = 0

def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

raw = b"".join(b"\x00" + bytes(row) for row in img)
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", N, N, 8, 0, 0, 0, 0)) \
    + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
out = pathlib.Path(__file__).resolve().parent.parent / "textures" / "track.png"
out.write_bytes(png)
print(out, len(png))
