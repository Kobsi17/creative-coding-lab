# Winter Wonderland Snow Globe — Kobsi · 2026
# Kobsi · @Kobsi17 · 2026. Free for learning and personal projects. See LICENSE.txt.
# Don't repost it or sell it as your own, and don't use it to train AI models.
import sys
import time
from pathlib import Path
import numpy as np
import pygame

TAU = np.pi * 2
LOOP = 28.0  # slower, cinematic animation cycle (seconds)

# ASCII character ramp from delicate/dark to dense/bright
POOLS = ["1il!;:", "rtfjcvxz=+", "aeoun0{}[]<>", "08B$#&%Q"]
CHARS = " .,:~+*^01|/\\-_#()x" + "".join(POOLS)
AT = {c: i for i, c in enumerate(CHARS)}
FILL = np.array([[AT[p[k % len(p)]] for k in range(12)] for p in POOLS])

def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)

# Palette: Deep Pine, Emerald, Gold, Crimson, Ice Cyan, Warm White, Wood Amber, Aurora Teal, Carrot Orange
TAG_COLOR = [
    [18, 125, 68],     # 0: DEEP_GREEN (tree shadow)
    [46, 235, 130],    # 1: NEON_GREEN (pine needles)
    [255, 208, 65],    # 2: GOLD (star, garland, window light)
    [255, 58, 92],     # 3: CRIMSON (ornaments, scarf, gift)
    [135, 225, 255],   # 4: ICE_BLUE (snowglobe dome, snow, snowman)
    [255, 248, 230],   # 5: WARM_WHITE (star core, moon, smoke)
    [175, 102, 48],    # 6: WOOD (pedestal, cabin, trunk)
    [38, 185, 165],    # 7: AURORA (northern lights)
    [255, 132, 35],    # 8: CARROT (snowman nose)
]
DEEP_GREEN, NEON_GREEN, GOLD, CRIMSON, ICE_BLUE, WARM_WHITE, WOOD, AURORA, CARROT = range(9)

_grid = {}
def grid(cols, rows, aspect):
    key = (cols, rows)
    if key not in _grid:
        rng = np.random.default_rng(25)
        x = ((np.arange(cols) + 0.5) / cols - 0.5) * aspect
        y = (np.arange(rows) + 0.5) / rows - 0.5
        X, Y = np.meshgrid(x, y)
        _grid[key] = X, Y, rng.random((rows, cols)), rng.integers(0, 12, (rows, cols))
    return _grid[key]

def frame(t, cols, rows, aspect):
    X, Y, rnd, hsh = grid(cols, rows, aspect)

    # Gentle breathing zoom after the full village finishes building (~11.5s)
    magic_on = smooth((t - 11.2) / 2.2)
    zoom = 1.0 + 0.035 * magic_on * np.sin(0.95 * t)
    X, Y = X / zoom, Y / zoom

    # --- BACKGROUND: Northern Lights Aurora, Crescent Moon & Stars ---
    gx, gy = 0.0, -0.04
    r_dome = np.hypot(X, Y - gy)
    outside_dome = r_dome > 0.435

    # Soft waving aurora ribbons across the upper sky
    aurora_reveal = smooth((t - 0.2) / 3.0)
    wave1 = -0.34 + 0.055 * np.sin(5.2 * X + 0.55 * t) + 0.025 * np.cos(9.0 * X - 0.35 * t)
    wave2 = -0.24 + 0.045 * np.cos(4.4 * X - 0.45 * t + 1.2)
    ribbon1 = np.exp(-((Y - wave1) / 0.042) ** 2) * (0.65 + 0.35 * np.sin(14.0 * X + 0.8 * t))
    ribbon2 = np.exp(-((Y - wave2) / 0.034) ** 2) * (0.55 + 0.45 * np.cos(11.0 * X - 0.6 * t))
    aurora_mask = outside_dome & (Y < -0.05)
    aurora_heat = np.where(
        aurora_mask,
        aurora_reveal * np.maximum(ribbon1 * 0.55, ribbon2 * 0.42),
        0.0,
    )

    # Glowing crescent moon in the top-left sky
    moon_reveal = smooth((t - 1.2) / 2.0)
    mx, my = -0.44, -0.35
    in_moon = (np.hypot(X - mx, Y - my) < 0.046) & (np.hypot(X - (mx + 0.020), Y - (my - 0.012)) > 0.040)
    moon_heat = np.where(in_moon & outside_dome, moon_reveal * 0.95, 0.0)

    # Twinkling background stars
    outside_star = (r_dome > 0.45) & (aurora_heat < 0.15) & (rnd < 0.0055)
    sky_heat = np.where(outside_star, 0.55 + 0.4 * np.sin(1.2 * t + rnd * 99.0), 0.0)

    # --- 1. SNOWGLOBE GLASS DOME, PEDESTAL & SNOWY GROUND (0.5s -> 3.8s) ---
    ang = np.arctan2(Y - gy, X)
    around = ((ang + np.pi / 2) % TAU) / TAU
    dome_reveal = smooth((t - 0.5) / 2.6)
    dome = (
        np.exp(-((r_dome - 0.42) / 0.013) ** 2)
        * smooth((dome_reveal * 1.08 - around) / 0.08)
        * (Y < 0.28)
    )

    # Ornate wooden snowglobe pedestal (0.8s -> 2.8s)
    base_reveal = smooth((t - 0.8) / 2.0)
    base_half_w = 0.25 + 0.24 * np.clip((Y - 0.27) / 0.15, 0.0, 1.0)
    in_base = (Y >= 0.27) & (Y <= 0.42) & (np.abs(X) <= base_half_w)
    is_plaque = (Y >= 0.32) & (Y <= 0.37) & (np.abs(X) <= 0.15)
    base_heat = np.where(in_base, base_reveal * (0.72 + 0.22 * np.cos(X * 36.0)), 0.0)
    base_heat = np.where(is_plaque, base_reveal * 1.05, base_heat)

    # Curved snowy floor inside the bottom of the globe (1.8s -> 3.6s)
    floor_y = 0.25 - 0.055 * (X / 0.38) ** 2
    ground_reveal = smooth((t - 1.8) / 1.8)
    ground = (
        ((np.abs(X) < 0.375) & (Y >= floor_y) & (Y < 0.275))
        * ground_reveal
    ).astype(np.float32) * (0.78 + 0.22 * np.sin(16.0 * X + 0.6 * t))

    # --- 2. CENTRAL PINE TREE (2.8s -> 6.6s) ---
    tx = 0.02
    trunk_reveal = smooth((t - 2.8) / 1.0)
    in_trunk = (np.abs(X - tx) < 0.032) & (Y > 0.14) & (Y < 0.245)
    trunk_heat = np.where(in_trunk, trunk_reveal * (0.75 + 0.25 * np.cos((X - tx) * 50.0)), 0.0)

    tree_reveal = smooth((t - 3.3) / 3.3)
    y_top, y_bot = -0.28, 0.15
    cut_y = y_bot - tree_reveal * (y_bot - y_top + 0.05)
    in_y = (Y >= np.maximum(y_top, cut_y)) & (Y <= y_bot)

    norm_y = np.clip((Y - y_top) / (y_bot - y_top), 0.0, 1.0)
    tier_wave = (norm_y * 5.0) % 1.0
    sway = 0.009 * np.sin(1.4 * t + norm_y * 4.5) * (1.0 - norm_y)
    max_w = (0.024 + 0.20 * norm_y) * (0.68 + 0.38 * tier_wave)
    max_w += 0.011 * np.sin(22.0 * norm_y + 1.0 * t)

    dx = X - tx - sway
    in_tree = in_y & (np.abs(dx) <= max_w)
    edge_glow = np.exp(-((np.abs(dx) - max_w) / 0.019) ** 2)
    bough_tex = 0.56 + 0.28 * np.sin(36.0 * norm_y - 12.0 * np.abs(dx)) + 0.14 * np.cos(24.0 * dx + 0.8 * t)
    tree_heat = np.where(in_tree, np.clip(bough_tex + 0.42 * edge_glow, 0.15, 1.12), 0.0)

    # --- 3. COZY MINIATURE CABIN ON THE LEFT (5.6s -> 8.2s) ---
    cabin_reveal = smooth((t - 5.6) / 2.2)
    cx = -0.225
    in_cabin_wall = (np.abs(X - cx) <= 0.068) & (Y >= 0.13) & (Y <= 0.235)
    roof_y_min = 0.055 + np.abs(X - cx) * 0.95
    in_cabin_roof = (np.abs(X - cx) <= 0.084) & (Y >= roof_y_min) & (Y < 0.135)
    in_chimney = (X >= cx + 0.032) & (X <= cx + 0.052) & (Y >= 0.045) & (Y <= 0.10)
    in_window = (np.abs(X - (cx - 0.018)) <= 0.020) & (Y >= 0.16) & (Y <= 0.205)
    in_door = (np.abs(X - (cx + 0.026)) <= 0.015) & (Y >= 0.175) & (Y <= 0.235)

    cabin_heat = np.where(in_cabin_wall | in_chimney | in_door, cabin_reveal * 0.78, 0.0)
    cabin_heat = np.where(in_cabin_roof, cabin_reveal * 0.92, cabin_heat)
    win_pulse = 0.95 + 0.20 * np.sin(2.0 * t)
    cabin_heat = np.where(in_window, cabin_reveal * win_pulse, cabin_heat)

    # Rising chimney smoke puffs (after 7.4s)
    smoke_reveal = smooth((t - 7.4) / 1.5)
    smoke_heat = np.zeros_like(X)
    for k in range(5):
        age = (0.35 * t + k * 0.2) % 1.0
        sy_puff = 0.035 - age * 0.14
        sx_puff = (cx + 0.042) + 0.016 * np.sin(age * 7.0 + t) + age * 0.02
        d_puff = np.hypot(X - sx_puff, Y - sy_puff)
        smoke_heat = np.maximum(
            smoke_heat,
            smoke_reveal * (1.0 - age) * 0.72 * np.exp(-((d_puff / (0.011 + 0.010 * age)) ** 2)),
        )

    # --- 4. CUTE SNOWMAN & WRAPPED PRESENTS ON THE RIGHT (6.6s -> 9.2s) ---
    sm_reveal = smooth((t - 6.6) / 2.2)
    sx0 = 0.235
    sm_bot = np.hypot(X - sx0, Y - 0.195) <= 0.046
    sm_top = np.hypot(X - sx0, Y - 0.125) <= 0.032
    in_snowman = sm_bot | sm_top

    in_scarf = (np.abs(X - sx0) <= 0.034) & (Y >= 0.150) & (Y <= 0.164)
    in_eye = ((np.hypot(X - (sx0 - 0.011), Y - 0.116) < 0.006) | (np.hypot(X - (sx0 + 0.011), Y - 0.116) < 0.006))
    in_nose = (X >= sx0) & (X <= sx0 + 0.026) & (np.abs(Y - 0.126) <= 0.006 * (1.0 - (X - sx0) / 0.028))

    snowman_heat = np.where(in_snowman, sm_reveal * 0.88, 0.0)
    snowman_heat = np.where(in_scarf | in_nose, sm_reveal * 1.05, snowman_heat)

    # Two wrapped gift boxes at the base of the tree (7.6s -> 9.4s)
    gift_reveal = smooth((t - 7.6) / 1.8)
    g1_box = (np.abs(X - 0.115) <= 0.026) & (Y >= 0.205) & (Y <= 0.245)
    g1_rib = g1_box & ((np.abs(X - 0.115) < 0.005) | (np.abs(Y - 0.225) < 0.005))
    g2_box = (np.abs(X - (-0.085)) <= 0.022) & (Y >= 0.212) & (Y <= 0.245)
    g2_rib = g2_box & ((np.abs(X - (-0.085)) < 0.005) | (np.abs(Y - 0.228) < 0.005))
    gift_heat = np.where(g1_box | g2_box, gift_reveal * 0.92, 0.0)

    # --- 5. GOLDEN GARLAND, ORNAMENTS & STAR IGNITION (8.2s -> 11.5s) ---
    garland_reveal = smooth((t - 8.2) / 2.0)
    garland_phase = norm_y * 14.0 - 1.2 * t
    garland_x = tx + sway + max_w * 0.86 * np.sin(garland_phase)
    front_wrap = np.cos(garland_phase) > -0.15
    garland = (
        (in_tree & front_wrap & (norm_y > (1.0 - garland_reveal)))
        * np.exp(-(np.abs(X - garland_x) / 0.012) ** 2)
        * (0.85 + 0.30 * np.sin(2.5 * t + norm_y * 20.0))
    )

    orn_reveal = smooth((t - 8.8) / 1.8)
    is_orn = in_tree & (rnd < 0.044 * orn_reveal) & (norm_y > 0.08)
    orn_pulse = 0.68 + 0.48 * np.sin(2.4 * t + rnd * 40.0)
    orn_heat = np.where(is_orn, orn_pulse, 0.0)

    # Five-pointed star ignites at t = 10.4s
    star_reveal = smooth((t - 10.2) / 1.0)
    star_burst = np.exp(-((t - 10.5) / 0.35) ** 2)
    stx, sty = X - (tx + 0.009 * np.sin(1.4 * t)), Y - (y_top - 0.030)
    sr = np.hypot(stx, sty)
    sa = np.arctan2(sty, stx) + np.pi / 2 + 0.20 * np.sin(0.9 * t)
    star_shape = 0.023 + 0.017 * np.cos(5.0 * sa)
    star_heat = star_reveal * np.exp(-((sr / star_shape) ** 1.8)) * (1.2 + 1.2 * star_burst)

    shock = 0.0
    if t > 10.4:
        shock_r = (t - 10.4) * 0.30
        shock = np.exp(-((sr - shock_r) / 0.016) ** 2) * np.exp(-(t - 10.4) / 0.75) * 0.75

    # --- 6. GENTLE FALLING SNOW INSIDE THE DOME ---
    snow_y = ((Y + 0.42 - 0.085 * t - 0.035 * np.sin(0.7 * t + rnd * 12.0)) % 0.68) - 0.42
    snow_x = X + 0.014 * np.sin(1.1 * t + rnd * 25.0)
    inside_dome = np.hypot(snow_x, Y - gy) < 0.405
    solid_obj = (tree_heat > 0.2) | (star_heat > 0.2) | (cabin_heat > 0.2) | (snowman_heat > 0.2)
    is_snow = inside_dome & (~solid_obj) & (rnd > 0.985)
    snow_heat = np.where(is_snow, 0.65 + 0.35 * np.sin(1.8 * t + rnd * 50.0), 0.0)

    # Combine all heat layers
    heat = np.maximum.reduce([
        aurora_heat,
        moon_heat,
        sky_heat,
        dome * 0.76,
        base_heat,
        ground * 0.84,
        trunk_heat,
        tree_heat,
        cabin_heat,
        smoke_heat,
        snowman_heat,
        gift_heat,
        garland * 1.12,
        orn_heat * 1.15,
        star_heat,
        np.broadcast_to(shock, X.shape),
        snow_heat,
    ])

    on = heat > 0.08
    level = np.clip((heat * 3.4).astype(int), 0, 3)
    char = FILL[level, (hsh + int(t * 4.5)) % 12]

    # Special cute ASCII glyphs for details
    char = np.where(is_snow, np.where(rnd > 0.994, AT["*"], AT["."]), char)
    char = np.where(outside_star, np.where(rnd < 0.0018, AT["+"], AT["."]), char)
    char = np.where(is_orn, AT["0"], char)
    char = np.where(star_heat > 0.55, AT["*"], char)
    char = np.where(in_window & (cabin_reveal > 0.2), AT["#"], char)
    char = np.where(in_eye & (sm_reveal > 0.3), AT["."], char)
    char = np.where(in_nose & (sm_reveal > 0.3), AT[">"], char)
    char = np.where(on, char, AT[" "])

    # Layer-by-layer vibrant color assignment
    tag = np.where(tree_heat > 0.68, NEON_GREEN, DEEP_GREEN)
    tag = np.where(aurora_heat > 0.08, AURORA, tag)
    tag = np.where(trunk_heat > 0.1, WOOD, tag)
    tag = np.where((dome > 0.12) | (ground > 0.12) | is_snow | outside_star, ICE_BLUE, tag)
    tag = np.where(in_base, WOOD, tag)
    tag = np.where(is_plaque, GOLD, tag)
    tag = np.where(in_cabin_wall | in_chimney | in_door, WOOD, tag)
    tag = np.where(in_cabin_roof | (snowman_heat > 0.1), ICE_BLUE, tag)
    tag = np.where(in_window, GOLD, tag)
    tag = np.where(smoke_heat > 0.12, WARM_WHITE, tag)
    tag = np.where(in_scarf | g1_box, CRIMSON, tag)
    tag = np.where(g2_box | g1_rib | g2_rib, GOLD, tag)
    tag = np.where(in_nose, CARROT, tag)
    tag = np.where(garland > 0.25, GOLD, tag)
    tag = np.where(is_orn, np.where((hsh % 2) == 0, CRIMSON, GOLD), tag)
    tag = np.where((star_heat > 0.2) | (shock > 0.15) | (moon_heat > 0.15), WARM_WHITE, tag)
    tag = np.where((star_heat > 0.25) & (star_heat <= 0.85), GOLD, tag)

    lum = np.where(on, np.clip(0.45 + 0.85 * heat, 0.0, 1.35), 0.0)
    count = int((char != AT[" "]).sum())
    return char.astype(int), lum.astype(np.float32), tag.astype(int), {"magic": float(magic_on), "heat": float(heat.max())}, count


# --- Window & Multi-Pass Gaussian Bloom Engine ---
TITLE = "Winter Wonderland Snowglobe"
CW, CH, FONT_PX = 7, 11, 12
W, H = 1080, 960
COLS, ROWS = W // CW, H // CH
ASPECT = (COLS * CW) / (ROWS * CH)
TRAIL = 0.38
COLORS = np.array(TAG_COLOR, np.float32) / 255
DIM, MINT = (110, 124, 120), (110, 255, 185)
MONO = "consolas,menlo,dejavusansmono,couriernew,monospace"

def glyphs():
    font = pygame.font.SysFont(MONO, FONT_PX)
    atlas = []
    for ch in CHARS:
        s = pygame.Surface((CW, CH))
        g = font.render(ch, True, (255, 255, 255))
        s.blit(g, ((CW - g.get_width()) // 2, (CH - g.get_height()) // 2))
        atlas.append(pygame.surfarray.array3d(s)[:, :, 0].T.astype(np.float32) / 255)
    return np.stack(atlas)

class Canvas:
    def __init__(self, atlas):
        self.atlas = (atlas * 255).astype(np.uint8)
        self.shape = pygame.Surface((COLS * CW, ROWS * CH))
        self.trail = pygame.Surface((W, H))
        self.fade = (int(TRAIL * 255),) * 3

    def reset(self):
        self.trail.fill((0, 0, 0))

    def draw(self, t):
        char, lum, tag, info, count = frame(t, COLS, ROWS, ASPECT)
        mask = self.atlas[char.T].transpose(0, 3, 1, 2).reshape(COLS * CW, ROWS * CH)
        pygame.surfarray.blit_array(self.shape, np.repeat(mask[..., None], 3, 2))
        col = np.clip(COLORS[np.clip(tag, 0, len(COLORS) - 1)] * lum[..., None] * 255, 0, 255).astype(np.uint8)
        tint = pygame.transform.scale(pygame.surfarray.make_surface(col.transpose(1, 0, 2)), self.shape.get_size())
        self.shape.blit(tint, (0, 0), special_flags=pygame.BLEND_MULT)
        self.trail.fill(self.fade, special_flags=pygame.BLEND_MULT)
        self.trail.blit(self.shape, (0, 0), special_flags=pygame.BLEND_MAX)
        return self.trail, info, count

def blur(surf, k, radius):
    small = pygame.transform.smoothscale(surf, (W // k, H // k))
    if hasattr(pygame.transform, "gaussian_blur"):
        small = pygame.transform.gaussian_blur(small, max(1, radius // k))
    return pygame.transform.smoothscale(small, (W, H))

def glow_layer(surf, amount):
    layer = surf.copy()
    layer.fill((int(255 * amount),) * 3, special_flags=pygame.BLEND_MULT)
    return layer

def window_size():
    info = pygame.display.Info()
    k = 1.0
    if info.current_w > 0 and info.current_h > 0:
        k = min(1.0, 0.85 * info.current_h / H, 0.95 * info.current_w / W)
    return int(W * k), int(H * k)

def main():
    pygame.init()
    size = window_size()
    window = pygame.display.set_mode(size)
    pygame.display.set_caption(TITLE)
    screen = pygame.Surface((W, H))
    small = pygame.font.SysFont(MONO, 17)
    canvas, clock = Canvas(glyphs()), pygame.time.Clock()
    t, paused = 0.0, False
    art, info, count = canvas.draw(t)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                paused = not paused
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                t = 0.0
                canvas.reset()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_s:
                pygame.image.save(screen, str(Path(__file__).with_name(f"winter_wonderland_{int(time.time())}.png")))

        dt = clock.tick(30) / 1000
        if not paused:
            t += min(dt, 1 / 15)
            if t > LOOP:
                t = 0.0
                canvas.reset()
            art, info, count = canvas.draw(t)

        screen.fill((0, 0, 0))
        screen.blit(art, (0, 0))
        screen.blit(glow_layer(blur(art, 4, 5), 0.78), (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(glow_layer(blur(art, 8, 22), 0.48), (0, 0), special_flags=pygame.BLEND_ADD)

        y = H - 70
        screen.blit(small.render(f"magic {info['magic']:.2f}   glow {info['heat']:.2f}", True, DIM), (64, y))
        screen.blit(small.render(f"letters {count:05,d}", True, DIM), (64, y + 26))
        tt = small.render(f"{'●' if int(t * 2) % 2 == 0 else ' '} t {t:05.2f}s", True, MINT)
        screen.blit(tt, (W - 64 - tt.get_width(), 30))

        window.blit(screen if size == (W, H) else pygame.transform.smoothscale(screen, size), (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    sys.exit(main())
