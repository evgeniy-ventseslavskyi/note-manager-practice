import os, sys, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from multiprocessing import Pool

SRC = sys.argv[1]; OUT = sys.argv[2]
PREVIEW = len(sys.argv) > 3
W, H, FPS = 1920, 1080, 30
DUR = float(os.environ.get('DUR', 300))  # seconds; end flows seamlessly into start
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

def K(period):
    """integer cycles over the whole video closest to the wanted period -> seamless wrap."""
    return max(1, round(DUR / period))

# low-res grid for aurora blobs
sh, sw = H // 8, W // 8
gy, gx = np.mgrid[0:sh, 0:sw].astype(np.float32) * 8
rng = np.random.default_rng(11)
# cx, cy, radius, colorA, colorB, intensity
BLOB_BASE = [
    (520, 420, 520, (40, 70, 170), (60, 50, 160), 0.55),
    (1430, 560, 480, (30, 90, 150), (40, 70, 175), 0.40),
    (960, 900, 600, (70, 50, 150), (30, 80, 160), 0.30),
    (1200, 160, 420, (35, 60, 140), (55, 45, 140), 0.30),
    (200, 950, 450, (30, 60, 130), (50, 60, 150), 0.25),
]
BLOBS = []
for cx, cy, rad, ca, cb, inten in BLOB_BASE:
    BLOBS.append(dict(cx=cx, cy=cy, rad=rad, ca=np.array(ca) / 255, cb=np.array(cb) / 255, inten=inten,
                      ax=rng.uniform(120, 260), ay=rng.uniform(60, 120), bx=rng.uniform(30, 70), by=rng.uniform(20, 50),
                      k1=K(rng.uniform(55, 95)), k2=K(rng.uniform(17, 31)), k3=K(rng.uniform(70, 140)),
                      ki=K(rng.uniform(25, 45)), p=rng.uniform(0, TAU, 6)))

NP = 70
span = H + 200
depth = rng.uniform(0, 1, NP)  # 0 = far (small, slow, faint), 1 = near
P = dict(x=rng.uniform(0, W, NP), y=rng.uniform(0, span, NP), r=2 + 8 * depth ** 1.5,
         cyc=np.array([max(1, round((14 + 34 * d) * rng.uniform(0.8, 1.2) * DUR / span)) for d in depth]),
         sway=rng.uniform(10, 45, NP), ksw=np.array([K(rng.uniform(9, 26)) for _ in range(NP)]),
         ktw=np.array([K(rng.uniform(3.5, 9)) for _ in range(NP)]), ph=rng.uniform(0, TAU, (NP, 2)),
         a=0.12 + 0.33 * depth * rng.uniform(0.6, 1.0, NP))

# light sheen across the logo at irregular moments
SWEEPS, tt = [], rng.uniform(3, 8)
while tt + 6 < DUR:
    SWEEPS.append((tt, rng.uniform(4.5, 6.5), rng.uniform(0.3, 0.6), rng.uniform(0.7, 1.0)))
    tt += SWEEPS[-1][1] + rng.uniform(9, 22)

def sheen_band(sec, X, Y):
    for t0, d, slope, strength in SWEEPS:
        if t0 <= sec <= t0 + d:
            u = (sec - t0) / d; u = u * u * (3 - 2 * u)
            pos = 300 + u * 1100
            return np.exp(-((X + Y * slope - pos - 250 * slope) / 90) ** 2) * strength
    return None

def frame(i):
    t = i / N  # 0..1 over the whole video
    sec = i / FPS
    s = lambda k=1, p=0.0: np.sin(TAU * k * t + p)
    img = bg_base.copy()

    # aurora: each blob drifts on two incommensurate orbits and slowly shifts hue
    acc = np.zeros((sh, sw, 3), np.float32)
    for b in BLOBS:
        p = b['p']
        bx = b['cx'] + b['ax'] * s(b['k1'], p[0]) + b['bx'] * s(b['k2'], p[1])
        by = b['cy'] + b['ay'] * s(b['k1'], p[2]) + b['by'] * s(b['k2'], p[3])
        mix = 0.5 + 0.5 * s(b['k3'], p[4])
        col = b['ca'] * (1 - mix) + b['cb'] * mix
        inten = b['inten'] * (0.75 + 0.25 * s(b['ki'], p[5]))
        g = np.exp(-((gx - bx) ** 2 + (gy - by) ** 2) / (2 * (b['rad'] * 0.5) ** 2)) * inten
        acc += g[..., None] * col
    up = np.stack([np.asarray(Image.fromarray(np.ascontiguousarray(acc[..., c]), 'F').resize((W, H), Image.BICUBIC)) for c in range(3)], 2)
    img = img + up * 0.85

    # particles (bokeh) with depth: near ones bigger, faster, brighter
    for j in range(NP):
        py = (P['y'][j] - span * P['cyc'][j] * t) % span - 100
        px = P['x'][j] + P['sway'][j] * s(P['ksw'][j], P['ph'][j, 0])
        r = P['r'][j]
        al = P['a'][j] * (0.55 + 0.45 * s(P['ktw'][j], P['ph'][j, 1]))
        x0, x1 = int(max(px - 4 * r, 0)), int(min(px + 4 * r + 1, W))
        y0, y1 = int(max(py - 4 * r, 0)), int(min(py + 4 * r + 1, H))
        if x1 <= x0 or y1 <= y0: continue
        d2 = (xx[y0:y1, x0:x1] - px) ** 2 + (yy[y0:y1, x0:x1] - py) ** 2
        g = np.exp(-d2 / (2 * r * r)) * al
        img[y0:y1, x0:x1] += g[..., None] * np.array([0.55, 0.68, 1.0]) * 0.6

    img *= vign[..., None]

    # logo group: gentle float on two mixed periods + breathing glow
    ldx = 3.5 * s(K(23), 0.3) + 1.5 * s(K(9.7), 1.1)
    ldy = 5.5 * s(K(10.3), 0.0) + 2.0 * s(K(37), 2.0)
    breath = (0.5 + 0.5 * s(K(9.1), -1.2)) * (0.75 + 0.25 * s(K(61), 0.4))
    la = shift(logo_a, ldx, ldy); ta = shift(text_a, ldx, ldy)
    lg = shift(logo_glow, ldx, ldy); lg2 = shift(logo_glow2, ldx, ldy); tg = shift(text_glow, ldx, ldy)
    img += (lg * (0.35 + 0.25 * breath) + lg2 * (0.25 + 0.2 * breath))[..., None] * GLOW_C
    lv = smooth(LY0, LY1, yy - ldy)[..., None]
    lcol = LOGO_C2 * (1 - lv) + LOGO_C1 * lv
    band = sheen_band(sec, xx - ldx, yy - ldy)
    if band is not None:
        lcol = lcol + band[..., None] * 0.22
    img = img * (1 - la[..., None]) + lcol * la[..., None]
    img += tg[..., None] * np.array([0.35, 0.45, 0.8]) * (0.12 + 0.08 * breath)
    tcol = TEXT_C + (band[..., None] * 0.08 if band is not None else 0)
    img = img * (1 - ta[..., None]) + tcol * ta[..., None]

    # QR card: its own float rhythm + soft glow; content kept intact
    cdx = -2.5 * s(K(27), 0.9) - 1.0 * s(K(11.3), 0.2)
    cdy = 5.0 * s(K(12.1), np.pi * 0.6) + 1.5 * s(K(43), 1.4)
    cgl = shift(card_glow, cdx, cdy)
    img += cgl[..., None] * GLOW_C * (0.35 + 0.15 * s(K(13.7), 0.8))
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
        for i in (0, 1500, 4500, 7800):
            Image.frombytes('RGB', (W, H), frame(i)).save(f'{OUT}_{i}.png')
        sys.exit()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                           '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '16',
                           '-tune', 'grain', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
                           '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for k, b in enumerate(pool.imap(frame, range(N), chunksize=4)):
            ff.stdin.write(b)
            if k % 300 == 0: print(f'{k}/{N}', flush=True)
    ff.stdin.close(); ff.wait()
