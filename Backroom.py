# Kobsi · 2026 — The Backrooms: Level 0 (3D Vectorized Raycaster & Field Shader)
import sys
import time
from pathlib import Path
import numpy as np
import pygame

TAU = np.pi * 2
LOOP = 32.0
SURGE_TIME = 7.5  # moment an eerie fluorescent power surge ripples down the hall

# ASCII character ramp from delicate/dark to dense/bright
POOLS = ["1il!;:", "rtfjcvxz=+", "aeoun0{}[]<>", "08B$#&%Q"]
CHARS = " .,:~+*^01|/\\-_#()x" + "".join(POOLS)
AT = {c: i for i, c in enumerate(CHARS)}
FILL = np.array([[AT[p[k % len(p)]] for k in range(12)] for p in POOLS])


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


# Palette: Deep Umber Shadow, Classic Backrooms Yellow, Damp Carpet Mustard, Acoustic Cream, Fluorescent White, Eerie Exit Green
TAG_COLOR = [
    [76, 62, 22],      # 0: SHADOW_UMBER (far hallway shadows & baseboards)
    [224, 194, 58],    # 1: BACKROOM_YELLOW (iconic damask wallpaper)
    [164, 130, 36],    # 2: CARPET_MUSTARD (moist textured floor)
    [196, 184, 134],   # 3: TILE_CREAM (drop-ceiling grid tiles)
    [255, 252, 218],   # 4: FLUORESCENT_GLOW (overhead light panels & reflections)
    [46, 235, 138],    # 5: EXIT_EMERALD (distant liminal exit sign glow)
]
SHADOW_UMBER, BACKROOM_YELLOW, CARPET_MUSTARD, TILE_CREAM, FLUORESCENT_GLOW, EXIT_EMERALD = range(6)


# --- Synthesized 60Hz Fluorescent Ballast Hum & Liminal Drone (Zero External Files) ---
def build_backrooms_audio():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    except Exception:
        return None, None

    sr = 44100
    dur = 16.0
    n = int(sr * dur)
    tt = np.arange(n, dtype=np.float32) / sr

    # Classic 60Hz + 120Hz + 240Hz fluorescent ballast hum with subtle electrical flutter
    flutter = 0.85 + 0.15 * np.sin(TAU * 7.5 * tt) * np.cos(TAU * 3.1 * tt)
    hum = (
        0.48 * np.sin(TAU * 60.0 * tt)
        + 0.34 * np.sin(TAU * 120.0 * tt)
        + 0.14 * np.sin(TAU * 240.0 * tt)
        + 0.04 * np.sin(TAU * 360.0 * tt)
    ) * flutter * 0.13

    # Deep liminal "breathing" room resonance (F1 + C2 + G2)
    for idx, f in enumerate([43.65, 65.41, 98.00]):
        lfo = 0.60 + 0.40 * np.sin(TAU * (0.0625 * (idx + 1)) * tt + idx)
        hum += np.sin(TAU * f * tt) * lfo * 0.08

    # 1. Continuous HVAC air-vent rumble + subtle analog room hiss
    rng = np.random.default_rng(2026)
    noise = rng.normal(0.0, 1.0, n).astype(np.float32)
    hvac_kernel = np.ones(220, dtype=np.float32) / 220.0
    hvac_rumble = np.convolve(noise, hvac_kernel, mode="same") * 0.32
    tape_hiss = noise * 0.014
    buzz_env = (np.maximum(0.0, np.sin(TAU * 0.375 * tt + 0.4)) ** 12.0) * 0.045
    hum += hvac_rumble + tape_hiss + (noise * buzz_env)

    # 2. Distant echoing metallic pipe/vent groans
    for groan_t, base_f in [(3.4, 148.0), (10.8, 112.0)]:
        g0 = int(groan_t * sr)
        g_len = min(n - g0, int(sr * 2.2))
        tg = np.arange(g_len, dtype=np.float32) / sr
        glide_f = base_f * (1.0 - 0.14 * np.sin(np.pi * tg / 2.2))
        g_env = np.sin(np.pi * tg / 2.2) ** 2.0
        hum[g0:g0 + g_len] += np.sin(TAU * glide_f * tg) * g_env * 0.028

    # 3. Soft muffled footsteps on damp carpet (alternating L/R stereo)
    step_l = np.zeros(n, dtype=np.float32)
    step_r = np.zeros(n, dtype=np.float32)
    step_times = np.arange(0.8, dur - 0.8, 1.14)
    for s_idx, st in enumerate(step_times):
        i0 = int(st * sr)
        s_len = min(n - i0, int(sr * 0.28))
        ts = np.arange(s_len, dtype=np.float32) / sr
        # Muffled low-end carpet thud + soft fabric brush
        thud = np.sin(TAU * (58.0 * np.exp(-ts * 12.0) + 26.0) * ts) * np.exp(-ts * 18.0)
        brush = np.convolve(rng.normal(0.0, 1.0, s_len).astype(np.float32), np.ones(45, dtype=np.float32) / 45.0, mode="same") * np.exp(-ts * 22.0)
        foot = (thud * 0.11 + brush * 0.06) * (0.85 + 0.15 * np.sin(s_idx * 1.7))
        if s_idx % 2 == 0:
            step_l[i0:i0 + s_len] += foot * 1.15
            step_r[i0:i0 + s_len] += foot * 0.75
        else:
            step_l[i0:i0 + s_len] += foot * 0.75
            step_r[i0:i0 + s_len] += foot * 1.15

    fade_len = int(sr * 1.2)
    fade = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
    hum[:fade_len] *= fade
    hum[-fade_len:] *= fade[::-1]

    left = np.clip((hum + step_l) * 32767, -32767, 32767).astype(np.int16)
    right = np.clip((np.roll(hum, 340) + step_r) * 32767, -32767, 32767).astype(np.int16)
    drone_sound = pygame.sndarray.make_sound(np.column_stack((left, right)))

    # Sharp fluorescent starter flicker zap
    z_len = int(sr * 0.85)
    tz = np.arange(z_len, dtype=np.float32) / sr
    zap_env = np.exp(-tz * 6.5) * (0.5 + 0.5 * np.sign(np.sin(TAU * 28.0 * tz)))
    zap = (0.5 * np.sin(TAU * 120.0 * tz) + 0.35 * np.sin(TAU * 480.0 * tz) + 0.25 * rng.normal(0.0, 1.0, z_len)) * zap_env * 0.18
    z_i16 = np.clip(zap * 32767, -32767, 32767).astype(np.int16)
    zap_sound = pygame.sndarray.make_sound(np.column_stack((z_i16, np.roll(z_i16, 95))))

    return drone_sound, zap_sound


# --- Procedural Level 0 Architectural Maze & Precomputed Grid ---
_cache = {}
def backrooms_assets(cols, rows):
    key = (cols, rows)
    if key not in _cache:
        rng = np.random.default_rng(2026)
        rnd = rng.random((rows, cols))
        hsh = rng.integers(0, 12, (rows, cols))

        # Build a 48x48 repeating Level 0 hall & pillar grid
        # Main corridor runs along X = 24 with periodic cross-halls, side alcoves & pillars
        M = 48
        maze = np.zeros((M, M), dtype=int)
        maze[0, :] = 1
        maze[-1, :] = 1
        maze[:, 0] = 1
        maze[:, -1] = 1

        # Partition walls creating endless interconnected rooms & hallways
        for z in range(4, M - 3, 6):
            # Left & right dividing walls with open doorways
            maze[10:21, z] = 1
            maze[28:39, z] = 1
            # Carve doorways into side rooms
            maze[14:17, z] = 0
            maze[32:35, z] = 0

        # Outer side walls
        maze[9, :] = 1
        maze[39, :] = 1
        # Open cross-corridor passages along the outer walls
        for z in range(6, M - 4, 12):
            maze[9, z:z + 3] = 0
            maze[39, z:z + 3] = 0

        # Iconic square structural pillars down the wide hall
        for z in range(7, M - 4, 12):
            maze[21, z] = 1
            maze[27, z] = 1

        # Keep the central walking lane (X = 22..26) completely unobstructed
        maze[22:27, :] = 0

        # Tag one distant alcove wall with an eerie green EXIT sign (wall type 2)
        maze[18, 34] = 2

        col_idx = np.arange(cols, dtype=np.float32)
        row_idx = np.arange(rows, dtype=np.float32)
        cam_plane_x = (2.0 * col_idx / cols) - 1.0  # [-1, 1] across screen width

        _cache[key] = {
            "rnd": rnd, "hsh": hsh,
            "maze": maze, "M": M,
            "cam_plane_x": cam_plane_x,
            "row_idx": row_idx,
        }
    return _cache[key]


def cast_rays_dda(pos_x, pos_z, dir_x, dir_z, plane_x, plane_z, cam_x, maze, M):
    """Vectorized 3D DDA wall raycaster across all screen columns simultaneously."""
    ray_dx = dir_x + plane_x * cam_x
    ray_dz = dir_z + plane_z * cam_x

    map_x = np.floor(pos_x).astype(int)
    map_z = np.floor(pos_z).astype(int)
    map_x = np.full_like(cam_x, map_x, dtype=int)
    map_z = np.full_like(cam_x, map_z, dtype=int)

    delta_dx = np.where(np.abs(ray_dx) < 1e-6, 1e6, np.abs(1.0 / np.where(np.abs(ray_dx) < 1e-6, 1e-6, ray_dx)))
    delta_dz = np.where(np.abs(ray_dz) < 1e-6, 1e6, np.abs(1.0 / np.where(np.abs(ray_dz) < 1e-6, 1e-6, ray_dz)))

    step_x = np.where(ray_dx < 0, -1, 1)
    step_z = np.where(ray_dz < 0, -1, 1)

    side_dx = np.where(ray_dx < 0, (pos_x - map_x) * delta_dx, (map_x + 1.0 - pos_x) * delta_dx)
    side_dz = np.where(ray_dz < 0, (pos_z - map_z) * delta_dz, (map_z + 1.0 - pos_z) * delta_dz)

    hit = np.zeros(len(cam_x), dtype=bool)
    side = np.zeros(len(cam_x), dtype=int)
    wall_type = np.zeros(len(cam_x), dtype=int)

    for _ in range(36):
        active = ~hit
        if not np.any(active):
            break
        step_in_x = active & (side_dx < side_dz)
        step_in_z = active & (~step_in_x)

        side_dx = np.where(step_in_x, side_dx + delta_dx, side_dx)
        map_x = np.where(step_in_x, map_x + step_x, map_x)
        side = np.where(step_in_x, 0, side)

        side_dz = np.where(step_in_z, side_dz + delta_dz, side_dz)
        map_z = np.where(step_in_z, map_z + step_z, map_z)
        side = np.where(step_in_z, 1, side)

        cell_val = maze[map_x % M, map_z % M]
        newly_hit = active & (cell_val > 0)
        hit |= newly_hit
        wall_type = np.where(newly_hit, cell_val, wall_type)

    perp_dist = np.where(side == 0, side_dx - delta_dx, side_dz - delta_dz)
    perp_dist = np.maximum(perp_dist, 0.12)

    wall_u = np.where(side == 0, pos_z + perp_dist * ray_dz, pos_x + perp_dist * ray_dx)
    wall_u -= np.floor(wall_u)
    return perp_dist, wall_u, side, wall_type, ray_dx, ray_dz


def frame(t, cols, rows, aspect, user_yaw=0.0, user_pitch=0.0, surge_boost=0.0):
    A = backrooms_assets(cols, rows)
    rnd, hsh, maze, M = A["rnd"], A["hsh"], A["maze"], A["M"]
    cam_x = A["cam_plane_x"]
    row_idx = A["row_idx"]

    # Progressive entrance reveal (0.0s -> 4.2s)
    lights_reveal = smooth(t / 2.0)
    arch_reveal = smooth((t - 0.8) / 2.8)
    detail_reveal = smooth((t - 2.0) / 2.2)

    # Periodic electrical fluorescent light flicker + power surge at SURGE_TIME
    surge = np.exp(-((t - SURGE_TIME) / 0.35) ** 2) + 0.85 * surge_boost
    flicker_raw = np.sin(23.0 * t) * np.cos(37.0 * t + 1.1)
    bad_ballast = np.where(flicker_raw > 0.72, 0.25, 1.0) * (1.0 - 0.45 * surge)

    # First-person camera gliding endlessly down the Level 0 corridor
    pos_x = 24.5 + 0.65 * np.sin(0.28 * t)
    pos_z = 2.0 + 1.35 * t
    yaw = 0.14 * np.sin(0.24 * t) + user_yaw
    head_bob = 0.025 * np.sin(2.7 * t)
    horizon = rows * (0.50 + 0.28 * user_pitch) + head_bob * rows * 0.15

    dir_x, dir_z = np.sin(yaw), np.cos(yaw)
    fov = 0.82 * (aspect / 1.72)
    plane_x, plane_z = np.cos(yaw) * fov, -np.sin(yaw) * fov

    perp_dist, wall_u, side, wall_type, ray_dx, ray_dz = cast_rays_dda(
        pos_x, pos_z, dir_x, dir_z, plane_x, plane_z, cam_x, maze, M
    )

    # --- 1. 3D CEILING & FLOOR PERSPECTIVE PROJECTION ---
    # Row distance from horizon line (rows above horizon = ceiling, below = floor)
    dy_row = row_idx[:, None] - horizon
    abs_dy = np.maximum(np.abs(dy_row), 0.35)
    pos_z_eye = rows * 0.52
    row_dist = pos_z_eye / abs_dy

    world_x = pos_x + row_dist * ray_dx[None, :]
    world_z = pos_z + row_dist * ray_dz[None, :]

    is_ceiling = dy_row < 0.0
    is_floor = ~is_ceiling

    # Ceiling acoustic grid tiles (1.0 x 1.0 unit grid) & recessed fluorescent panels
    gx_frac = world_x - np.floor(world_x)
    gz_frac = world_z - np.floor(world_z)
    tile_seam = (gx_frac < 0.045) | (gx_frac > 0.955) | (gz_frac < 0.045) | (gz_frac > 0.955)

    # Fluorescent light panels placed every 4 units along Z and every 4 units along X
    cell_ix = np.floor(world_x).astype(int)
    cell_iz = np.floor(world_z).astype(int)
    has_fixture = ((cell_ix % 4) == 0) & ((cell_iz % 4) == 2)
    in_panel = has_fixture & (gx_frac > 0.22) & (gx_frac < 0.78) & (gz_frac > 0.14) & (gz_frac < 0.86)

    # One specific fixture row flickers erratically like a dying ballast
    is_flicker_lamp = ((cell_iz % 12) == 6) & ((cell_ix % 8) == 0)
    lamp_power = np.where(is_flicker_lamp, bad_ballast, 1.0) * lights_reveal

    ceil_fog = np.exp(-row_dist * 0.115)
    ceil_heat = np.where(
        in_panel,
        lamp_power * (1.28 + 0.22 * surge) * np.exp(-row_dist * 0.065),
        arch_reveal * ceil_fog * np.where(tile_seam, 0.32, 0.56),
    )

    # Floor damp mustard carpet + soft light pools cast down from ceiling fixtures
    carpet_grain = 0.52 + 0.22 * np.sin(world_x * 16.0) * np.cos(world_z * 16.0) + 0.16 * np.sin(world_x * 38.0 + world_z * 29.0)
    damp_stain = np.exp(-(((gx_frac - 0.5) ** 2 + (gz_frac - 0.5) ** 2) / 0.16)) * 0.18
    light_pool = np.where(has_fixture, 0.42 * lamp_power * np.exp(-(((gx_frac - 0.5) ** 2 + (gz_frac - 0.5) ** 2) / 0.24)), 0.0)
    floor_fog = np.exp(-row_dist * 0.12)
    floor_heat = arch_reveal * floor_fog * np.clip(carpet_grain - damp_stain + light_pool, 0.18, 1.25)

    # --- 2. 3D WALLS, DAMASK WALLPAPER STRIPES, BASEBOARDS & EXIT SIGN ---
    wall_h = (rows * 0.96) / perp_dist[None, :]
    wall_top = horizon - wall_h * 0.5
    wall_bot = horizon + wall_h * 0.5
    in_wall = (row_idx[:, None] >= wall_top) & (row_idx[:, None] <= wall_bot)

    # Normalized vertical wall coordinate v_wall: 0.0 (ceiling molding) -> 1.0 (floor baseboard)
    v_wall = np.clip((row_idx[:, None] - wall_top) / np.maximum(wall_h, 1.0), 0.0, 1.0)
    u_wall = np.broadcast_to(wall_u[None, :], in_wall.shape)
    d_wall = np.broadcast_to(perp_dist[None, :], in_wall.shape)
    s_wall = np.broadcast_to(side[None, :], in_wall.shape)
    t_wall = np.broadcast_to(wall_type[None, :], in_wall.shape)

    # Iconic Level 0 vertical wallpaper stripes + subtle damask diamond pattern
    stripe = 0.5 + 0.5 * np.cos(u_wall * TAU * 6.0)
    damask = (np.sin(u_wall * TAU * 6.0) * np.sin(v_wall * TAU * 8.0)) > 0.45
    is_baseboard = (v_wall > 0.91) | (v_wall < 0.045)
    is_corner = (u_wall < 0.03) | (u_wall > 0.97)

    # Side-shading gives crisp 3D corner contrast between X-walls and Z-walls
    side_shade = np.where(s_wall == 1, 0.78, 1.0)
    wall_fog = np.exp(-d_wall * 0.105)
    wall_pat = 0.56 + 0.26 * stripe + 0.18 * damask * detail_reveal
    wall_pat = np.where(is_baseboard, 0.44, wall_pat)
    wall_pat = np.where(is_corner, 0.38, wall_pat)
    wall_heat = arch_reveal * wall_fog * side_shade * wall_pat * (0.92 + 0.12 * bad_ballast)

    # Glowing emerald EXIT sign mounted high on the distant alcove wall (wall_type == 2)
    is_exit = in_wall & (t_wall == 2) & (v_wall > 0.14) & (v_wall < 0.28) & (u_wall > 0.28) & (u_wall < 0.72)
    wall_heat = np.where(is_exit, 1.28 * detail_reveal, wall_heat)

    # --- 3. FLOATING LIMINAL DUST MOTES IN LIGHT SHAFTS ---
    dust_y = ((row_idx[:, None] / rows + 0.04 * t + rnd) % 1.0)
    is_dust = (rnd > 0.9945) & (dust_y > 0.15) & (dust_y < 0.85) & (~in_wall) & (detail_reveal > 0.3)
    dust_heat = detail_reveal * np.where(is_dust, 0.65 + 0.35 * np.sin(2.5 * t + rnd * 60.0), 0.0)

    # Combine ceiling, floor, and wall depths
    heat = np.where(is_ceiling, ceil_heat, floor_heat)
    heat = np.where(in_wall, wall_heat, heat)
    heat = np.maximum(heat, dust_heat)

    on = heat > 0.07
    level = np.clip((heat * 3.3).astype(int), 0, 3)
    char = FILL[level, (hsh + int(t * 3.0)) % 12]

    # Architectural ASCII detailing
    char = np.where(is_ceiling & in_panel, AT["0"], char)
    char = np.where(is_ceiling & tile_seam & (~in_panel), AT["+"], char)
    char = np.where(in_wall & is_baseboard, AT["="], char)
    char = np.where(in_wall & is_corner, AT["|"], char)
    char = np.where(in_wall & damask & (~is_baseboard) & (d_wall < 8.5), AT[":"], char)
    char = np.where(is_exit, AT["#"], char)
    char = np.where(is_dust, AT["."], char)
    char = np.where(on, char, AT[" "])

    # Color tags for walls, carpet, ceiling & fluorescent lights
    tag = np.where(is_ceiling, TILE_CREAM, CARPET_MUSTARD)
    tag = np.where(is_ceiling & in_panel, FLUORESCENT_GLOW, tag)
    tag = np.where(is_floor & (light_pool > 0.16), BACKROOM_YELLOW, tag)
    tag = np.where(in_wall, BACKROOM_YELLOW, tag)
    tag = np.where(in_wall & (is_baseboard | is_corner | (d_wall > 10.5)), SHADOW_UMBER, tag)
    tag = np.where(is_exit, EXIT_EMERALD, tag)
    tag = np.where(is_dust, FLUORESCENT_GLOW, tag)

    lum = np.where(on, np.clip(0.38 + 0.88 * heat, 0.0, 1.38), 0.0)
    count = int((char != AT[" "]).sum())
    hz_val = float(60.0 + 1.8 * np.sin(19.0 * t) + 14.0 * surge)
    return char.astype(int), lum.astype(np.float32), tag.astype(int), {"depth": float(pos_z), "hz": hz_val}, count


# --- Widescreen Window & Multi-Pass Gaussian Bloom Engine ---
TITLE = "The Backrooms: Level 0 - Kobsi"
SIGN = "Kobsi · 2026"
CW, CH, FONT_PX = 7, 11, 12
W, H = 1480, 860
COLS, ROWS = W // CW, H // CH
ASPECT = (COLS * CW) / (ROWS * CH)
TRAIL = 0.34
COLORS = np.array(TAG_COLOR, np.float32) / 255
DIM, MUSTARD = (128, 118, 84), (242, 212, 74)
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

    def draw(self, t, user_yaw, user_pitch, surge_boost):
        char, lum, tag, info, count = frame(t, COLS, ROWS, ASPECT, user_yaw, user_pitch, surge_boost)
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
    k = min(0.94 * info.current_h / H, 0.96 * info.current_w / W)
    return int(W * k), int(H * k)


def main():
    pygame.init()
    drone_sound, zap_sound = build_backrooms_audio()
    muted = False
    if drone_sound is not None:
        drone_sound.play(loops=-1)

    size = window_size()
    window = pygame.display.set_mode(size)
    pygame.display.set_caption(TITLE)
    screen = pygame.Surface((W, H))
    small = pygame.font.SysFont(MONO, 17)
    canvas, clock = Canvas(glyphs()), pygame.time.Clock()
    t, paused, surged, fullscreen = 0.0, False, False, False
    user_yaw, user_pitch, surge_boost = 0.0, 0.0, 0.0
    art, info, count = canvas.draw(t, user_yaw, user_pitch, surge_boost)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                paused = not paused
                if drone_sound is not None and not muted:
                    pygame.mixer.pause() if paused else pygame.mixer.unpause()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_m and drone_sound is not None:
                muted = not muted
                drone_sound.set_volume(0.0 if muted else 1.0)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    d_info = pygame.display.Info()
                    size = (d_info.current_w, d_info.current_h)
                    window = pygame.display.set_mode(size, pygame.FULLSCREEN)
                else:
                    size = window_size()
                    window = pygame.display.set_mode(size)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                t, surged = 0.0, False
                user_yaw, user_pitch, surge_boost = 0.0, 0.0, 0.0
                canvas.reset()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_s:
                pygame.image.save(screen, str(Path(__file__).with_name(f"backrooms_lvl0_{int(time.time())}.png")))

        # Left-click + drag to look around the 3D corridors; hold right-click to trigger a fluorescent power flicker
        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            mdx, mdy = pygame.mouse.get_rel()
            user_yaw += mdx * 0.008
            user_pitch = float(np.clip(user_pitch - mdy * 0.005, -0.55, 0.55))
        else:
            pygame.mouse.get_rel()

        if buttons[2]:
            if surge_boost < 0.2 and zap_sound is not None and not muted:
                zap_sound.play()
            surge_boost = min(1.0, surge_boost + 0.14)
        else:
            surge_boost = max(0.0, surge_boost - 0.08)

        dt = clock.tick(30) / 1000
        if not paused:
            t += min(dt, 1 / 15)
            if t >= SURGE_TIME and not surged:
                surged = True
                if zap_sound is not None and not muted:
                    zap_sound.play()
            if t >= LOOP:
                t, surged = 0.0, False
                canvas.reset()
            art, info, count = canvas.draw(t, user_yaw, user_pitch, surge_boost)

        screen.fill((0, 0, 0))
        screen.blit(art, (0, 0))
        screen.blit(glow_layer(blur(art, 4, 5), 0.72), (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(glow_layer(blur(art, 8, 22), 0.44), (0, 0), special_flags=pygame.BLEND_ADD)

        y = H - 70
        screen.blit(small.render(SIGN, True, (148, 138, 96)), (64, y - 26))
        screen.blit(small.render(f"hall {info['depth']:05.1f}m   hum {info['hz']:.1f}Hz", True, DIM), (64, y))
        screen.blit(small.render(f"letters {count:05,d}", True, DIM), (64, y + 26))
        tt = small.render(f"{'●' if int(t * 2) % 2 == 0 else ' '} t {t:05.2f}s", True, MUSTARD)
        screen.blit(tt, (W - 64 - tt.get_width(), 30))

        window.blit(screen if size == (W, H) else pygame.transform.smoothscale(screen, size), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    sys.exit(main())