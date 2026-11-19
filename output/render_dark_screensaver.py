import sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from multiprocessing import Pool

SRC = sys.argv[1]; OUT = sys.argv[2]
PREVIEW = len(sys.argv) > 3
W, H, FPS, DUR = 1920, 1080, 30, 20.0
N = int(FPS * DUR)
TAU = 2 * np.pi

src = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
Lum = src.mean(2)

def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

# ---- layers extracted from the original ----
# logo (vase / faces): blue pixels
LX0, LY0, LX1, LY1 = 470, 140, 880, 725
logo_a = np.zeros((H, W), np.float32)
reg = src[LY0:LY1, LX0:LX1]
blue = reg[..., 2] - reg[..., 0]
logo_a[LY0:LY1, LX0:LX1] = (1 - smooth(70, 190, Lum[LY0:LY1, LX0:LX1])) * smooth(40, 90, blue)
# wordmark: dark neutral pixels
TX0, TY0, TX1, TY1 = 430, 740, 955, 940
text_a = np.zeros((H, W), np.float32)
text_a[TY0:TY1, TX0:TX1] = 1 - smooth(45, 185, Lum[TY0:TY1, TX0:TX1])
# QR card
CX0, CY0, CX1, CY1, CR = 1221, 267, 1640, 814, 30
cw, ch = CX1 - CX0, CY1 - CY0
m = Image.new('L', (cw * 4, ch * 4), 0)
ImageDraw.Draw(m).rounded_rectangle([4, 4, cw * 4 - 5, ch * 4 - 5], CR * 4, fill=255)
card_mask = np.asarray(m.resize((cw, ch), Image.LANCZOS)).astype(np.float32) / 255
card_rgb = src[CY0:CY1, CX0:CX1] / 255 * 0.90  # slightly dimmed white, QR stays crisp & scannable

def _box(a, r, ax):
    a = np.moveaxis(a, ax, 0)
    p = np.concatenate([np.repeat(a[:1], r + 1, 0), a, np.repeat(a[-1:], r, 0)])
    c = np.cumsum(p, 0, dtype=np.float64)
    return np.moveaxis(((c[2 * r + 1:] - c[:-2 * r - 1]) / (2 * r + 1)).astype(np.float32), 0, ax)

def blur(a, sigma):
    """approx gaussian: 3 box passes at 1/4 resolution, float precision."""
    f = 4
    small = np.asarray(Image.fromarray(np.ascontiguousarray(a, np.float32), 'F').resize((W // f, H // f), Image.BOX))
    r = max(1, int(round(sigma / f * 1.0)))
    for _ in range(3):
        small = _box(_box(small, r, 0), r, 1)
    return np.asarray(Image.fromarray(np.ascontiguousarray(small), 'F').resize((W, H), Image.BICUBIC)).astype(np.float32)

logo_glow = blur(logo_a, 40)
logo_glow2 = blur(logo_a, 110)
text_glow = blur(text_a, 14)
cm_full = np.zeros((H, W), np.float32); cm_full[CY0:CY1, CX0:CX1] = card_mask
card_glow = blur(cm_full, 60)

def shift(a, dx, dy):
    """sub-pixel translate via PIL affine (bilinear)."""
    if a.ndim == 2:
        im = Image.fromarray(a, 'F')
        return np.asarray(im.transform(im.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BILINEAR))
    return np.stack([shift(np.ascontiguousarray(a[..., i]), dx, dy) for i in range(a.shape[2])], 2)

# ---- palette (dark) ----
BG_TOP = np.array([6, 9, 20]) / 255
BG_BOT = np.array([11, 17, 38]) / 255
LOGO_C1 = np.array([72, 106, 214]) / 255   # brand blue, lifted for dark bg
LOGO_C2 = np.array([132, 162, 240]) / 255
TEXT_C = np.array([226, 231, 242]) / 255
GLOW_C = np.array([60, 95, 200]) / 255

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
grad = (yy / H)[..., None]
bg_base = BG_TOP * (1 - grad) + BG_BOT * grad
vign = 1 - 0.55 * smooth(0.35, 1.0, np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2))

# low-res grid for aurora blobs
sh, sw = H // 8, W // 8
gy, gx = np.mgrid[0:sh, 0:sw].astype(np.float32) * 8
BLOBS = [  # cx, cy, ax, ay, radius, color, intensity, phase, harmonic
    (520, 420, 160, 90, 520, (40, 70, 170), 0.55, 0.0, 1),
    (1430, 560, 140, 110, 480, (30, 90, 150), 0.40, 1.7, 1),
    (960, 900, 260, 60, 600, (70, 50, 150), 0.30, 3.1, 1),
    (1200, 160, 200, 80, 420, (35, 60, 140), 0.30, 4.4, 2),
]

rng = np.random.default_rng(7)
NP = 46
P = dict(x=rng.uniform(0, W, NP), y=rng.uniform(0, H + 200, NP), r=rng.uniform(2, 9, NP) ** 1.0,
         cyc=rng.integers(1, 3, NP), sway=rng.uniform(10, 40, NP), ph=rng.uniform(0, TAU, NP),
         a=rng.uniform(0.15, 0.5, NP), tw=rng.integers(1, 4, NP))

def frame(i):
    t = i / N  # 0..1, everything periodic in t -> seamless loop
    s = lambda k=1, p=0.0: np.sin(TAU * k * t + p)
    img = bg_base.copy()

    # aurora
    acc = np.zeros((sh, sw, 3), np.float32)
    for cx, cy, ax, ay, rad, col, inten, ph, k in BLOBS:
        bx = cx + ax * s(k, ph); by = cy + ay * np.sin(TAU * k * t + ph * 1.3 + 1)
        inten2 = inten * (0.8 + 0.2 * s(1, ph + 2))
        g = np.exp(-((gx - bx) ** 2 + (gy - by) ** 2) / (2 * (rad * 0.5) ** 2)) * inten2
        acc += g[..., None] * (np.array(col) / 255)
    up = np.stack([np.asarray(Image.fromarray(np.ascontiguousarray(acc[..., c]), 'F').resize((W, H), Image.BICUBIC)) for c in range(3)], 2)
    img = img + up * 0.85

    # particles (bokeh), drift upward, loop seamlessly
    span = H + 200
    for j in range(NP):
        py = (P['y'][j] - span * P['cyc'][j] * t) % span - 100
        px = P['x'][j] + P['sway'][j] * np.sin(TAU * t * P['tw'][j] + P['ph'][j])
        r = P['r'][j]
        al = P['a'][j] * (0.55 + 0.45 * np.sin(TAU * P['tw'][j] * t + P['ph'][j] * 2))
        x0, x1 = int(max(px - 4 * r, 0)), int(min(px + 4 * r + 1, W))
        y0, y1 = int(max(py - 4 * r, 0)), int(min(py + 4 * r + 1, H))
        if x1 <= x0 or y1 <= y0: continue
        d2 = (xx[y0:y1, x0:x1] - px) ** 2 + (yy[y0:y1, x0:x1] - py) ** 2
        g = np.exp(-d2 / (2 * r * r)) * al
        img[y0:y1, x0:x1] += g[..., None] * np.array([0.55, 0.68, 1.0]) * 0.6

    img *= vign[..., None]

    # logo group: gentle float + breathing glow
    ldx = 4 * s(1, 0.3); ldy = 7 * s(2, 0.0)
    breath = 0.5 + 0.5 * s(2, -1.2)
    la = shift(logo_a, ldx, ldy); ta = shift(text_a, ldx, ldy)
    lg = shift(logo_glow, ldx, ldy); lg2 = shift(logo_glow2, ldx, ldy); tg = shift(text_glow, ldx, ldy)
    img += (lg * (0.35 + 0.25 * breath) + lg2 * (0.25 + 0.2 * breath))[..., None] * GLOW_C
    # logo color: vertical gradient + slow diagonal sheen sweep
    lv = smooth(LY0, LY1, yy - ldy)[..., None]
    lcol = LOGO_C2 * (1 - lv) + LOGO_C1 * lv
    sweep = (t * 1.0) % 1.0
    pos = -500 + sweep * 2400  # band travels across, mostly off-screen half the loop
    band = np.exp(-(((xx - ldx) + (yy - ldy) * 0.45 - pos) / 90) ** 2)
    lcol = lcol + band[..., None] * 0.22
    img = img * (1 - la[..., None]) + lcol * la[..., None]
    img += tg[..., None] * np.array([0.35, 0.45, 0.8]) * (0.12 + 0.08 * breath)
    tcol = TEXT_C + band[..., None] * 0.08
    img = img * (1 - ta[..., None]) + tcol * ta[..., None]

    # QR card: float in counter-phase + soft glow; content kept intact
    cdx = -3 * s(1, 0.3); cdy = 6 * s(2, np.pi * 0.6)
    cgl = shift(card_glow, cdx, cdy)
    img += cgl[..., None] * GLOW_C * (0.35 + 0.15 * s(2, 0.8))
    ix, iy = int(np.floor(cdx)), int(np.floor(cdy)); fx, fy = cdx - ix, cdy - iy
    pad = 2
    sub_rgb = np.zeros((ch + 2 * pad, cw + 2 * pad, 3), np.float32); sub_rgb[pad:-pad, pad:-pad] = card_rgb
    sub_m = np.zeros((ch + 2 * pad, cw + 2 * pad), np.float32); sub_m[pad:-pad, pad:-pad] = card_mask
    sub_rgb = shift(sub_rgb, fx, fy); sub_m = shift(sub_m, fx, fy)
    oy, ox = CY0 + iy - pad, CX0 + ix - pad
    roi = img[oy:oy + sub_m.shape[0], ox:ox + sub_m.shape[1]]
    img[oy:oy + sub_m.shape[0], ox:ox + sub_m.shape[1]] = roi * (1 - sub_m[..., None]) + sub_rgb * sub_m[..., None]

    # dither against banding on TVs
    img = img * 255 + np.random.default_rng(i).uniform(-0.6, 0.6, (H, W, 1))
    return np.clip(img + 0.5, 0, 255).astype(np.uint8).tobytes()

if __name__ == '__main__':
    if PREVIEW:
        for i in (0, 150, 300, 450):
            Image.frombytes('RGB', (W, H), frame(i)).save(f'{OUT}_{i}.png')
        sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
                           '-tune', 'grain', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
                           '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, b in enumerate(pool.imap(frame, range(N), chunksize=4)):
            ff.stdin.write(b)
            if k % 60 == 0: print(k, flush=True)
    ff.stdin.close(); ff.wait()
