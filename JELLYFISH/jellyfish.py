# Jellyfish — Speaking in Light — Kobsi · 2026
# Kobsi · @Kobsi17 · 2026. Free for learning and personal projects. See LICENSE.txt.
# Don't repost it or sell it as your own, and don't use it to train AI models.
# Self-contained procedural 3D ASCII bioluminescent jellyfish with nerve-pulse rings & sonar audio
#
# run:   pip install numpy pygame-ce
#        python jellyfish2.py
# keys:  Space pause · R restart · S screenshot · F fullscreen · M mute · Esc quit
# mouse: Left-drag orbit camera · Right-click trigger bioluminescent nerve pulse

import sys
import time
from pathlib import Path
import numpy as np
import pygame

TAU = np.pi * 2.0
DUR = 20.0  # loop duration in seconds

# Density-ramped character pool (dark/delicate -> dense/bright)
POOLS = ["1il!;:", "rtfjcvxz=+", "aeoun0{}[]<>", "08B$#&%Q"]
CHARS = " .,:~+*^01|/\\-_#()x" + "".join(POOLS)
AT = {c: i for i, c in enumerate(CHARS)}
FILL = np.array([[AT[p[k % len(p)]] for k in range(12)] for p in POOLS])

# Color palette matching the icy cobalt / electric cyan / pearl white bioluminescence
(DEEP_WATER, DUSK_BLUE, COBALT_BELL, CYAN_RIB, ICE_GLOW, PEARL_PULSE, ORAL_TEAL, SNOW_DIM) = range(8)
TAG_COLOR = [
    [14, 46, 98],     # 0: DEEP_WATER
    [24, 92, 178],    # 1: DUSK_BLUE (translucent bell body)
    [42, 148, 238],   # 2: COBALT_BELL (bell ribs & tentacles)
    [82, 210, 255],   # 3: CYAN_RIB (radial nerve stripes & oral ruffles)
    [168, 240, 255],  # 4: ICE_GLOW (crown & active nerve pulse)
    [242, 252, 255],  # 5: PEARL_PULSE (peak flash & bright nodes)
    [54, 178, 224],   # 6: ORAL_TEAL (central lacy arms)
    [95, 145, 205],   # 7: SNOW_DIM (drifting deep-sea plankton)
]


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def rot_y(p, a):
    c, s = np.cos(a), np.sin(a)
    return np.stack([c * p[:, 0] + s * p[:, 2], p[:, 1], -s * p[:, 0] + c * p[:, 2]], axis=1)


def rot_z(p, a):
    c, s = np.cos(a), np.sin(a)
    return np.stack([c * p[:, 0] - s * p[:, 1], s * p[:, 0] + c * p[:, 1], p[:, 2]], axis=1)


# --- Synthesized Deep-Ocean Sonar & Bioluminescent Pulse Audio ---
def build_abyss_audio():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    except Exception:
        return None

    sr = 44100
    n = int(sr * DUR)
    tt = np.arange(n, dtype=np.float32) / sr

    # Sub-aquatic C-minor 9th drone (C2, G2, Eb3, Bb3, D4)
    freqs = [65.41, 98.00, 155.56, 233.08, 293.66]
    buf = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        lfo = 0.55 + 0.45 * np.sin(TAU * (0.05 * (i + 1)) * tt + i * 1.1)
        drift = 1.0 + 0.002 * np.sin(TAU * 0.1 * tt + i)
        buf += np.sin(TAU * f * drift * tt) * lfo * (0.11 / (1.0 + 0.25 * i))

    # Crystalline nerve-pulse chimes timed to the bioluminescent flashes
    pulse_times = [2.4, 6.2, 10.0, 12.2, 15.8, 18.4]
    pulse_freqs = [523.25, 622.25, 783.99, 1046.50, 932.33, 622.25]
    for st, f in zip(pulse_times, pulse_freqs):
        i0 = int(st * sr)
        ring = min(n - i0, int(sr * 2.6))
        tc = np.arange(ring, dtype=np.float32) / sr
        env = np.exp(-tc * 1.85) * (1.0 - np.exp(-tc * 95.0))
        bell_tone = 0.75 * np.sin(TAU * f * tc) + 0.25 * np.sin(TAU * f * 2.0 * tc) * np.exp(-tc * 4.5)
        buf[i0:i0 + ring] += bell_tone * env * 0.10

    fade_len = int(sr * 1.2)
    fade = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
    buf[:fade_len] *= fade
    buf[-fade_len:] *= fade[::-1]

    left = np.clip(buf * 32767, -32767, 32767).astype(np.int16)
    right = np.roll(left, 620)
    return pygame.sndarray.make_sound(np.column_stack((left, right)))


# --- Parametric Jellyfish Morphology & Kinematics (Hero + Background Jelly) ---
rng = np.random.default_rng(42)

# Pre-sample bell surface grid (u around circumference, v from apex 0.02 to margin 1.0)
U_BELL, V_BELL = np.meshgrid(np.linspace(0.0, TAU, 130, endpoint=False), np.linspace(0.02, 1.0, 44))
U_BELL, V_BELL = U_BELL.ravel(), V_BELL.ravel()

# 4 Oral arms (lacy central ribbons)
U_ARM, S_ARM = np.meshgrid(np.linspace(-1.0, 1.0, 9), np.linspace(0.0, 1.0, 72))
U_ARM, S_ARM = U_ARM.ravel(), S_ARM.ravel()

# 24 Trailing outer tentacles
N_TENT = 24
TENT_ANGLES = np.linspace(0.0, TAU, N_TENT, endpoint=False)
TENT_PHASE = rng.uniform(0.0, TAU, N_TENT)
TENT_LEN = rng.uniform(0.85, 1.28, N_TENT)
S_TENT = np.linspace(0.0, 1.0, 64)

# Deep-sea marine snow (drifting plankton motes)
N_SNOW = 380
SNOW_XYZ = np.c_[rng.uniform(-2.6, 2.6, N_SNOW), rng.uniform(-2.2, 2.2, N_SNOW), rng.uniform(-2.4, 1.6, N_SNOW)]
SNOW_SPEED = rng.uniform(0.04, 0.11, N_SNOW)
SNOW_PHASE = rng.uniform(0.0, TAU, N_SNOW)

HERO = {
    "id": 10,
    "scale": 1.0,
    "pos": np.array([-0.08, 0.12, 0.0]),
    "tilt": -0.36,
    "yaw0": 0.25,
    "speed": 1.0,
    "phase0": 0.0,
    "dim": 1.0,
}

BACK = {
    "id": 20,
    "scale": 0.44,
    "pos": np.array([0.88, -0.18, -1.35]),
    "tilt": 0.28,
    "yaw0": 1.8,
    "speed": 0.85,
    "phase0": 2.1,
    "dim": 0.52,
}

JELLIES = [HERO, BACK]


def bell_cycle(t, speed=1.0, phase0=0.0):
    # Asymmetric contraction & slow glide recovery (matching jellyfish2.py kinematics)
    cy = (t * 0.42 * speed + phase0) % 1.0
    # Quick power stroke (0..0.32), smooth relaxation (0.32..1.0)
    contract = np.where(
        cy < 0.32,
        smooth(cy / 0.32),
        1.0 - smooth((cy - 0.32) / 0.68),
    )
    lift = np.sin(cy * TAU) * 0.045
    return contract, lift, cy


def nerve_wave(t, v_pos, manual_boost=0.0):
    # Bioluminescent light wave sweeping down the 8 radial stripes from apex to rim
    beat_period = 3.8
    local_t = t % beat_period
    # Double-beat around t = 11.5..13.5s like the reel ("speaking in light")
    special = smooth((t - 11.2) / 0.4) * (1.0 - smooth((t - 13.8) / 0.5))
    wave_pos = (local_t / 1.45) - 0.15
    ring = np.exp(-((v_pos - wave_pos) / 0.14) ** 2) * (local_t < 1.8)
    surge = np.exp(-((v_pos - ((t - 11.4) / 1.3)) / 0.18) ** 2) * special * 1.35
    manual = np.exp(-((v_pos - (manual_boost * 1.3)) / 0.18) ** 2) * (manual_boost > 0.01) * 1.4
    return np.clip(ring + surge + manual, 0.0, 1.5)


def build_jelly_points(jelly, t, manual_boost=0.0):
    sc = jelly["scale"]
    dim = jelly["dim"]
    jid = jelly["id"]
    contract, lift, _ = bell_cycle(t, jelly["speed"], jelly["phase0"])

    # Gentle swimming drift path
    drift_x = jelly["pos"][0] + 0.08 * np.sin(t * 0.35 + jelly["phase0"])
    drift_y = jelly["pos"][1] + lift + 0.06 * np.sin(t * 0.28 + jelly["phase0"])
    drift_z = jelly["pos"][2] + 0.12 * np.cos(t * 0.30 + jelly["phase0"])
    center = np.array([drift_x, drift_y, drift_z])
    yaw = jelly["yaw0"] + t * 0.18 * jelly["speed"]

    P_list, N_list, T_list, K_list, S_list = [], [], [], [], []

    # 1. TRANSLUCENT BELL DOME + 8 RADIAL NERVE STRIPES
    u, v = U_BELL, V_BELL
    # Contraction narrows the lower margin and deepens the dome height
    squeeze = 1.0 - 0.24 * contract * (v ** 1.35)
    scallop = 1.0 + 0.042 * np.cos(16.0 * u) * (v ** 2.2)
    r_bell = 0.54 * np.sin(v * np.pi * 0.56) * squeeze * scallop * sc
    y_bell = (0.34 - 0.44 * (v ** 1.28) * (1.0 + 0.16 * contract)) * sc

    pb = np.c_[r_bell * np.cos(u), y_bell, r_bell * np.sin(u)]
    # Outward normals for silhouette / Fresnel rim glow
    nb = np.c_[np.cos(u) * np.sin(v * 1.3), np.cos(v * 1.3), np.sin(u) * np.sin(v * 1.3)]
    nb /= np.linalg.norm(nb, axis=1, keepdims=True) + 1e-8

    # 8 radial glowing nerve channels + milky crown
    stripe = np.clip(np.cos(8.0 * u), 0.0, 1.0) ** 6
    crown = np.exp(-((v - 0.14) / 0.14) ** 2)
    rim = v > 0.90
    pulse = nerve_wave(t + jelly["phase0"] * 0.5, v, manual_boost if jid == 10 else 0.0)

    sh_bell = (0.32 + 0.34 * crown + 0.42 * stripe * (0.35 + 0.65 * v) + 0.35 * rim + 0.85 * pulse * (0.35 + 0.85 * stripe)) * dim
    tg_bell = np.where(
        (pulse > 0.45) & (stripe > 0.45), PEARL_PULSE,
        np.where(pulse > 0.25, ICE_GLOW,
        np.where(rim | (stripe > 0.62), CYAN_RIB,
        np.where(crown > 0.55, ICE_GLOW, DUSK_BLUE)))
    )
    P_list.append(pb)
    N_list.append(nb)
    T_list.append(tg_bell)
    K_list.append(np.full(len(pb), jid, dtype=int))
    S_list.append(sh_bell)

    # 2. FOUR LACY TWISTING ORAL ARMS (Central ruffled ribbons)
    for arm_i in range(4):
        a0 = arm_i * (TAU / 4.0) + 0.4
        s = S_ARM
        u_w = U_ARM
        # Delayed wave propagation down the arm
        c_lag, _, _ = bell_cycle(t - s * 0.55, jelly["speed"], jelly["phase0"])
        twist = a0 + s * 2.4 + 0.35 * np.sin(t * 0.9 + arm_i)
        ribbon_w = (0.075 * (1.0 - 0.62 * s) + 0.018 * np.sin(s * 24.0 - t * 3.0)) * sc
        ruffle = 0.022 * np.sin(s * 28.0 + u_w * 3.0 - t * 2.5) * (1.0 - 0.4 * s) * sc

        sway_r = (0.055 + 0.09 * s * (1.0 - 0.25 * c_lag)) * sc
        cx = sway_r * np.cos(a0 + 0.3 * np.sin(s * 3.5 - t * 1.4))
        cz = sway_r * np.sin(a0 + 0.3 * np.sin(s * 3.5 - t * 1.4))
        cy = (-0.02 - s * 0.92 * (1.0 + 0.06 * c_lag)) * sc

        px = cx + (u_w * ribbon_w) * (-np.sin(twist)) + ruffle * np.cos(twist)
        pz = cz + (u_w * ribbon_w) * np.cos(twist) + ruffle * np.sin(twist)
        py = cy + 0.012 * u_w * np.cos(s * 14.0) * sc

        pa = np.c_[px, py, pz]
        na = np.c_[np.cos(twist), np.full_like(twist, 0.15), np.sin(twist)]
        arm_pulse = nerve_wave(t + jelly["phase0"] * 0.5, 1.0 + s * 0.7, manual_boost if jid == 10 else 0.0)
        frill_edge = np.abs(u_w) > 0.72
        sh_arm = (0.48 + 0.35 * frill_edge + 0.30 * (1.0 - s) + 0.65 * arm_pulse) * dim
        tg_arm = np.where(arm_pulse > 0.35, ICE_GLOW, np.where(frill_edge, CYAN_RIB, ORAL_TEAL))

        P_list.append(pa)
        N_list.append(na)
        T_list.append(tg_arm)
        K_list.append(np.full(len(pa), jid + 1 + arm_i, dtype=int))
        S_list.append(sh_arm)

    # 3. TWENTY-FOUR FINE TRAILING TENTACLES (Delayed sinusoidal follow-through)
    rim_r_base = 0.54 * np.sin(np.pi * 0.56) * sc
    for ti in range(N_TENT):
        ang = TENT_ANGLES[ti]
        ph = TENT_PHASE[ti]
        tlen = TENT_LEN[ti] * sc
        s = S_TENT

        # Root follows the bell margin contraction; tip trails behind with phase lag
        c_lag, l_lag, _ = bell_cycle(t - s * 0.85, jelly["speed"], jelly["phase0"])
        r_cur = rim_r_base * (1.0 - 0.24 * c_lag)
        wave_rad = 0.065 * (s ** 1.3) * np.sin(s * 6.5 - t * 2.1 + ph) * sc
        wave_tan = 0.048 * (s ** 1.2) * np.cos(s * 5.2 - t * 1.7 + ph) * sc

        tx = (r_cur + wave_rad) * np.cos(ang) - wave_tan * np.sin(ang)
        tz = (r_cur + wave_rad) * np.sin(ang) + wave_tan * np.cos(ang)
        ty = (-0.09 - s * tlen + l_lag * 0.5) * sc

        pt = np.c_[tx, ty, tz]
        nt = np.tile([np.cos(ang), 0.0, np.sin(ang)], (len(pt), 1))
        t_pulse = nerve_wave(t + jelly["phase0"] * 0.5, 1.0 + s * 0.85, manual_boost if jid == 10 else 0.0)
        node = np.sin(s * 26.0 - t * 4.0 + ph) > 0.84
        sh_tent = ((0.42 + 0.45 * (1.0 - s)) + 0.45 * node + 0.70 * t_pulse) * dim
        tg_tent = np.where((t_pulse > 0.35) | node, ICE_GLOW, COBALT_BELL)

        P_list.append(pt)
        N_list.append(nt)
        T_list.append(tg_tent)
        K_list.append(np.full(len(pt), -1, dtype=int))  # rendered as delicate filament particles
        S_list.append(sh_tent)

    P = np.concatenate(P_list)
    N = np.concatenate(N_list)
    P = rot_z(rot_y(P, yaw), jelly["tilt"]) + center
    N = rot_z(rot_y(N, yaw), jelly["tilt"])
    return P, N, np.concatenate(T_list), np.concatenate(K_list), np.concatenate(S_list)


def camera(t, user_yaw=0.0, user_pitch=0.0):
    # Cinematic slow sweep from low 3/4 view to close bioluminescent inspection
    u = smooth(t / DUR)
    eye = np.array([
        0.15 * np.sin(t * 0.22) + user_yaw * 1.8,
        -0.25 + 0.22 * np.cos(t * 0.18) + user_pitch * 1.4,
        3.25 - 0.38 * np.sin(u * np.pi),
    ])
    target = np.array([0.05, -0.14, 0.0])
    fwd = (target - eye) / np.linalg.norm(target - eye)
    right = np.cross(fwd, [0.0, 1.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return eye, fwd, right, up


def outline_letter(gx, gy):
    ax, ay = np.abs(gx), np.abs(gy)
    c = np.where(
        ax > 2 * ay, AT["|"],
        np.where(ay > 2 * ax, np.where(gy > 0, AT["_"], AT["-"]),
        np.where(gx * gy > 0, AT["/"], AT["\\"]))
    )
    return np.where((ax + ay) == 0, AT["+"], c)


def frame(t, cols, rows, aspect, user_yaw=0.0, user_pitch=0.0, manual_boost=0.0):
    eye, fwd, right, up = camera(t, user_yaw, user_pitch)
    view_dir = -fwd

    Ps, Ts, Ks, Ss = [], [], [], []
    for jelly in JELLIES:
        P, N, T, K, S = build_jelly_points(jelly, t, manual_boost)
        # Fresnel translucent rim lighting: grazing edges glow bright, front center stays airy
        facing = np.clip(np.abs(N @ view_dir), 0.0, 1.0)
        fresnel = (1.0 - facing) ** 1.45
        S = S * (0.48 + 0.95 * fresnel)
        T = np.where((K == jelly["id"]) & (fresnel > 0.68) & (S > 0.55), ICE_GLOW, T)
        Ps.append(P)
        Ts.append(T)
        Ks.append(K)
        Ss.append(S)

    # Drifting deep-sea marine snow
    snow_y = ((SNOW_XYZ[:, 1] - t * SNOW_SPEED + 2.2) % 4.4) - 2.2
    snow_x = SNOW_XYZ[:, 0] + 0.06 * np.sin(t * 0.7 + SNOW_PHASE)
    snow_p = np.c_[snow_x, snow_y, SNOW_XYZ[:, 2]]
    snow_s = (0.28 + 0.38 * np.sin(t * 1.9 + SNOW_PHASE * 3.0)) * smooth(t / 1.5)

    Ps.append(snow_p)
    Ts.append(np.full(N_SNOW, SNOW_DIM, dtype=int))
    Ks.append(np.full(N_SNOW, -2, dtype=int))
    Ss.append(snow_s)

    P = np.concatenate(Ps)
    T = np.concatenate(Ts)
    K = np.concatenate(Ks)
    shade = np.concatenate(Ss) * smooth(t / 1.4)

    # Project 3D points onto the ASCII grid
    F = 2.12
    rel = P - eye
    x, y, z = rel @ right, rel @ up, rel @ fwd
    # Distant specimens and snow lose brightness as they recede into the water.
    shade *= np.exp(-0.23 * np.maximum(z - 2.0, 0.0))
    zz = np.maximum(z, 0.25)
    sx = (0.5 + x / zz * F * 0.5) * cols
    sy = (0.5 - y / zz * F * 0.5 * aspect) * rows

    order = np.argsort(-z)  # painter's order (far to near)
    sx, sy, z, shade, T, K = sx[order], sy[order], z[order], shade[order], T[order], K[order]
    ix, iy = sx.astype(int), sy.astype(int)
    ok = (ix >= 0) & (ix < cols) & (iy >= 0) & (iy < rows) & (z > 0.25)

    part = np.full((rows, cols), -1)
    depth = np.full((rows, cols), 99.0)
    lum = np.zeros((rows, cols))
    tag = np.zeros((rows, cols), int)

    b = ok & (K >= 0)
    part[iy[b], ix[b]] = K[b]
    depth[iy[b], ix[b]] = z[b]
    lum[iy[b], ix[b]] = shade[b]
    tag[iy[b], ix[b]] = T[b]
    body = part >= 0

    # Silhouette & depth-edge contour detection
    pp = np.pad(part, 1, constant_values=-1)
    pd = np.pad(depth, 1, constant_values=99.0)
    edge = np.zeros_like(body)
    gx = np.zeros((rows, cols))
    gy = np.zeros((rows, cols))
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nb = pp[1 + dy:rows + 1 + dy, 1 + dx:cols + 1 + dx]
            nz = pd[1 + dy:rows + 1 + dy, 1 + dx:cols + 1 + dx]
            out = body & ((nb < 0) | ((nb != part) & (nz > depth + 0.04)))
            gx += dx * out
            gy += dy * out
            if dx == 0 or dy == 0:
                edge |= out

    r, c = np.mgrid[0:rows, 0:cols]
    h = (r * 7919 + c * 104729) % 9973
    level = np.clip((lum * 3.3).astype(int), 0, 3)
    inside = FILL[level, (h + (t * 4.5 + h % 11).astype(int)) % 12]
    char = np.where(body, np.where(edge, outline_letter(gx, gy), inside), 0)
    char = np.where(body & (tag == PEARL_PULSE), AT["*"], char)
    lum = np.where(body, np.where(edge, np.maximum(0.68, lum), np.clip(lum, 0.18, 1.25)), 0.0)

    # Fine trailing tentacles (K == -1) & marine snow (K == -2)
    fx = ok & (K < 0) & (shade > 0.04)
    hidden = body[iy[fx], ix[fx]] & (depth[iy[fx], ix[fx]] < z[fx])
    fi, fj, fs, ft, fk = (a[fx][~hidden] for a in (iy, ix, shade, T, K))

    tent_ch = np.where(fs > 0.78, AT["*"], np.where(fs > 0.52, AT["+"], np.where(fs > 0.34, AT[":"], AT["."])))
    snow_ch = np.where(fs > 0.45, AT["+"], AT["."])
    char[fi, fj] = np.where(fk == -1, tent_ch, snow_ch)
    lum[fi, fj] = np.clip(fs, 0.0, 1.2)
    tag[fi, fj] = ft

    # Subtle abyssal water shimmer in empty background cells
    bg = (char == 0) & ((h % 19) == 0)
    shimmer = 0.14 + 0.10 * np.sin(t * 1.4 + r * 0.18 + c * 0.09)
    char = np.where(bg, AT["."], char)
    lum = np.where(bg, shimmer * smooth(t / 2.0), lum)
    tag = np.where(bg, DEEP_WATER, tag)

    contract, _, _ = bell_cycle(t)
    info = {
        "depth": 842.05 - 1.85 * np.sin(t * 0.25),
        "temp": 4.2,
        "bell": 8.60 - 1.45 * float(contract),
        "beats": int(t / 3.8) + 1,
        "tentacles": N_TENT,
    }
    count = int((char != 0).sum())
    return char.astype(int), lum.astype(np.float32), tag.astype(int), info, count


# --- Widescreen Window, Horizontal Scanline Glow & Multi-Pass Bloom ---
TITLE = "JELLYFISH SERIES 2 · Kobsi"
SIGN = "Kobsi · 2026"
CW, CH, FONT_PX = 7, 11, 12
W, H = 1480, 860
COLS, ROWS = W // CW, H // CH
ASPECT = (COLS * CW) / (ROWS * CH)
TRAIL = 0.46
COLOR = np.array(TAG_COLOR, np.float32) / 255.0
DIM, CYAN = (96, 132, 174), (120, 224, 255)
MONO = "consolas,menlo,dejavusansmono,couriernew,monospace"


def glyphs():
    font = pygame.font.SysFont(MONO, FONT_PX)
    atlas = []
    for ch in CHARS:
        s = pygame.Surface((CW, CH))
        g = font.render(ch, True, (255, 255, 255))
        s.blit(g, ((CW - g.get_width()) // 2, (CH - g.get_height()) // 2))
        atlas.append(pygame.surfarray.array3d(s)[:, :, 0].T.astype(np.float32) / 255.0)
    return np.stack(atlas)


class Canvas:
    def __init__(self, atlas):
        self.atlas = (atlas * 255).astype(np.uint8)
        self.shape = pygame.Surface((COLS * CW, ROWS * CH))
        self.trail = pygame.Surface((W, H))
        self.fade = (int(TRAIL * 255),) * 3

    def reset(self):
        self.trail.fill((0, 0, 0))

    def draw(self, t, user_yaw, user_pitch, manual_boost):
        char, lum, tag, info, count = frame(t, COLS, ROWS, ASPECT, user_yaw, user_pitch, manual_boost)
        mask = self.atlas[char.T].transpose(0, 3, 1, 2).reshape(COLS * CW, ROWS * CH)
        pygame.surfarray.blit_array(self.shape, np.repeat(mask[..., None], 3, 2))
        col = (COLOR[np.clip(tag, 0, len(COLOR) - 1)] * np.clip(lum, 0, 1.2)[..., None] * 255).clip(0, 255).astype(np.uint8)
        tint = pygame.transform.scale(pygame.surfarray.make_surface(col.transpose(1, 0, 2)), self.shape.get_size())
        self.shape.blit(tint, (0, 0), special_flags=pygame.BLEND_MULT)
        self.trail.fill(self.fade, special_flags=pygame.BLEND_MULT)
        self.trail.blit(self.shape, (0, 0), special_flags=pygame.BLEND_MAX)
        return self.trail, info, count


def blur_anisotropic(surf, kx, ky, amount):
    small = pygame.transform.smoothscale(surf, (max(1, W // kx), max(1, H // ky)))
    if hasattr(pygame.transform, "gaussian_blur"):
        small = pygame.transform.gaussian_blur(small, 2)
    layer = pygame.transform.smoothscale(small, (W, H))
    layer.fill((int(255 * amount),) * 3, special_flags=pygame.BLEND_MULT)
    return layer


def window_size():
    info = pygame.display.Info()
    k = min(0.94 * info.current_h / H, 0.96 * info.current_w / W)
    return int(W * k), int(H * k)


def abyss_background():
    x, y = np.mgrid[-1:1:64j, 0:1:48j]
    overhead_light = np.exp(-1.8 * x**2 - 4.8 * y)
    pixels = np.array([2, 5, 16]) + overhead_light[..., None] * np.array([4, 17, 28])
    return pygame.transform.smoothscale(pygame.surfarray.make_surface(pixels.astype(np.uint8)), (W, H))


def main():
    pygame.init()
    audio = build_abyss_audio()
    muted = False
    if audio is not None:
        audio.play(loops=-1)

    size = window_size()
    window = pygame.display.set_mode(size)
    pygame.display.set_caption(TITLE)
    screen = pygame.Surface((W, H))
    background = abyss_background()
    small = pygame.font.SysFont(MONO, 16)
    canvas, clock = Canvas(glyphs()), pygame.time.Clock()

    t, paused, fullscreen = 0.0, False, False
    user_yaw, user_pitch = 0.0, 0.0
    manual_boost = 0.0
    art, info, count = canvas.draw(t, user_yaw, user_pitch, manual_boost)

    while True:
        redraw = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                paused = not paused
                if audio is not None:
                    pygame.mixer.pause() if paused else pygame.mixer.unpause()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_m and audio is not None:
                muted = not muted
                audio.set_volume(0.0 if muted else 1.0)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    di = pygame.display.Info()
                    size = (di.current_w, di.current_h)
                    window = pygame.display.set_mode(size, pygame.FULLSCREEN)
                else:
                    size = window_size()
                    window = pygame.display.set_mode(size)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                t, user_yaw, user_pitch, manual_boost = 0.0, 0.0, 0.0, 0.0
                canvas.reset()
                redraw = True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_s:
                pygame.image.save(screen, str(Path(__file__).with_name(f"jellyfish2_{int(time.time())}.png")))
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                manual_boost = 0.05  # trigger bioluminescent nerve surge
                redraw = True

        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            mdx, mdy = pygame.mouse.get_rel()
            user_yaw += mdx * 0.008
            user_pitch = float(np.clip(user_pitch + mdy * 0.006, -0.9, 0.9))
            redraw = redraw or bool(mdx or mdy)
        else:
            pygame.mouse.get_rel()

        dt = clock.tick(30) / 1000.0
        if not paused:
            t += min(dt, 1.0 / 15.0)
            if manual_boost > 0.0:
                manual_boost += dt * 0.85
                if manual_boost > 1.2:
                    manual_boost = 0.0
            if t > DUR:
                t = 0.0
                canvas.reset()
        elif redraw:
            canvas.reset()

        if not paused or redraw:
            art, info, count = canvas.draw(t, user_yaw, user_pitch, manual_boost)

        # Deep abyssal midnight navy background + horizontal scanline & volumetric bloom
        screen.blit(background, (0, 0))
        screen.blit(art, (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(blur_anisotropic(art, 12, 3, 0.65), (0, 0), special_flags=pygame.BLEND_ADD)  # horizontal light streaks
        screen.blit(blur_anisotropic(art, 6, 6, 0.55), (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(blur_anisotropic(art, 14, 14, 0.40), (0, 0), special_flags=pygame.BLEND_ADD)

        # Top-left ocean telemetry & bottom-left Kobsi watermark HUD
        top_hud = f"depth {info['depth']:6.2f} m · {info['temp']:.1f} °C · bell ø {info['bell']:.2f} m"
        screen.blit(small.render(top_hud, True, DIM), (56, 28))

        y = H - 72
        screen.blit(small.render(SIGN, True, (112, 152, 198)), (56, y - 26))
        screen.blit(small.render(f"beats {info['beats']:02d}   tentacles {info['tentacles']:02d}   letters {count:05,d}", True, DIM), (56, y))
        screen.blit(small.render("drag orbit · right-click nerve pulse · space pause · r restart", True, (74, 102, 136)), (56, y + 26))

        tt = small.render(f"{'●' if int(t * 2) % 2 == 0 else ' '} t {t:05.2f}s", True, CYAN)
        screen.blit(tt, (W - 56 - tt.get_width(), 28))

        window.blit(screen if size == (W, H) else pygame.transform.smoothscale(screen, size), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    sys.exit(main())
