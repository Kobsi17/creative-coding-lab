# 366-Day Birth Flower Particle Studio — Kobsi · 2026
# Kobsi · @Kobsi17 · 2026. Free for learning and personal projects. See LICENSE.txt.
# Don't repost it or sell it as your own, and don't use it to train AI models.
import sys
import time
import datetime
from pathlib import Path
import numpy as np
import pygame

# ==============================================================================
# SET YOUR DATE HERE (e.g. "November 15", "March 21", "July 4", "October 31")
# Or press [D] inside the window to type any date live!
# ==============================================================================
BIRTH_DATE = "January 1"

TAU = np.pi * 2.0
LOOP = 12.0


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


# --- 366-Day Birth Flower Almanac & Botanical DNA ---
EXACT_DATES = {
    (1, 1):   ("Snowdrop", "Hope & Renewal", "bell", "pearl_emerald"),
    (2, 14):  ("Crimson Rose", "Passionate Devotion", "rose", "crimson_velvet"),
    (3, 17):  ("Bells of Ireland", "Good Fortune", "spike", "jade_mint"),
    (3, 21):  ("Daffodil", "New Beginnings", "trumpet", "solar_gold"),
    (4, 15):  ("Sweet Pea", "Blissful Pleasure", "spike", "pastel_orchid"),
    (5, 1):   ("Lily of the Valley", "Return of Happiness", "bell", "ivory_moss"),
    (6, 21):  ("Sunflower", "Radiant Adoration", "daisy", "amber_sun"),
    (7, 4):   ("Larkspur", "Open Heart", "spike", "cobalt_sky"),
    (8, 15):  ("Gladiolus", "Strength of Character", "spike", "coral_flame"),
    (9, 22):  ("Autumn Aster", "Wisdom & Valor", "daisy", "violet_gold"),
    (10, 31): ("Marigold", "Sacred Warmth", "daisy", "tangerine_gold"),
    (11, 15): ("Crown Vetch", "Humility", "umbel", "cream_blush"),
    (12, 25): ("Winter Holly", "Everlasting Protection", "holly", "holly_berry"),
}

MONTHLY_POOLS = {
    1: [
        ("Carnation", "Deep Admiration", "rose", "blush_rose"),
        ("Snowdrop", "Quiet Hope", "bell", "pearl_emerald"),
        ("Winter Jasmine", "Grace & Modesty", "trumpet", "solar_gold"),
        ("Hellebore", "Serenity", "daisy", "plum_ivory"),
    ],
    2: [
        ("Sweet Violet", "Faithfulness", "violet", "royal_violet"),
        ("Primrose", "First Love", "trumpet", "pastel_orchid"),
        ("Iris", "Eloquence & Wisdom", "violet", "cobalt_sky"),
        ("Almond Blossom", "Awakening", "umbel", "cream_blush"),
    ],
    3: [
        ("Daffodil", "Rebirth & Joy", "trumpet", "solar_gold"),
        ("Jonquil", "Affection Returned", "trumpet", "amber_sun"),
        ("Cherry Blossom", "Fleeting Beauty", "umbel", "blush_rose"),
        ("Anemone", "Anticipation", "daisy", "crimson_velvet"),
    ],
    4: [
        ("English Daisy", "Innocence & Purity", "daisy", "cream_blush"),
        ("Sweet Pea", "Gratitude", "spike", "pastel_orchid"),
        ("Tulip", "Perfect Love", "bell", "coral_flame"),
        ("Hyacinth", "Sincerity", "spike", "cobalt_sky"),
    ],
    5: [
        ("Lily of the Valley", "Sweetness & Humility", "bell", "ivory_moss"),
        ("Hawthorn", "Protection & Hope", "umbel", "cream_blush"),
        ("Peony", "Prosperity & Romance", "rose", "blush_rose"),
        ("Bluebell", "Constancy", "bell", "cobalt_sky"),
    ],
    6: [
        ("Garden Rose", "Timeless Love", "rose", "crimson_velvet"),
        ("Honeysuckle", "Devoted Affection", "trumpet", "amber_sun"),
        ("Lavender", "Calm Devotion", "spike", "royal_violet"),
        ("Hydrangea", "Heartfelt Emotion", "umbel", "cobalt_sky"),
    ],
    7: [
        ("Larkspur", "Levity & Grace", "spike", "cobalt_sky"),
        ("Water Lily", "Purity of Heart", "rose", "cream_blush"),
        ("Delphinium", "Boundless Sky", "spike", "royal_violet"),
        ("Coreopsis", "Always Cheerful", "daisy", "solar_gold"),
    ],
    8: [
        ("Gladiolus", "Integrity & Honor", "spike", "coral_flame"),
        ("Poppy", "Imagination", "trumpet", "crimson_velvet"),
        ("Sunflower", "Loyalty & Warmth", "daisy", "amber_sun"),
        ("Hibiscus", "Delicate Beauty", "trumpet", "blush_rose"),
    ],
    9: [
        ("Star Aster", "Patience & Elegance", "daisy", "royal_violet"),
        ("Morning Glory", "Affection", "trumpet", "cobalt_sky"),
        ("Dahlia", "Inner Strength", "rose", "plum_ivory"),
        ("Forget-Me-Not", "True Remembrance", "umbel", "cobalt_sky"),
    ],
    10: [
        ("Marigold", "Creativity & Passion", "daisy", "tangerine_gold"),
        ("Cosmos", "Peace & Harmony", "daisy", "blush_rose"),
        ("Calendula", "Golden Light", "daisy", "amber_sun"),
        ("Dahlia", "Dignity", "rose", "crimson_velvet"),
    ],
    11: [
        ("Chrysanthemum", "Joy & Longevity", "daisy", "amber_sun"),
        ("Crown Vetch", "Humility", "umbel", "cream_blush"),
        ("Camellia", "Admiration", "rose", "blush_rose"),
        ("Goldenrod", "Encouragement", "spike", "solar_gold"),
    ],
    12: [
        ("Holly", "Goodwill & Peace", "holly", "holly_berry"),
        ("Narcissus", "Inner Radiance", "trumpet", "ivory_moss"),
        ("Poinsettia", "Celebration", "daisy", "crimson_velvet"),
        ("Winter Camellia", "Steadfastness", "rose", "cream_blush"),
    ],
}

PALETTES = {
    "cream_blush":    ((0.99, 0.93, 0.84), (0.97, 0.80, 0.83), (0.96, 0.76, 0.42)),
    "crimson_velvet": ((0.96, 0.16, 0.28), (0.72, 0.06, 0.18), (0.98, 0.78, 0.34)),
    "blush_rose":     ((0.99, 0.72, 0.82), (0.94, 0.46, 0.64), (0.98, 0.86, 0.52)),
    "solar_gold":     ((0.99, 0.88, 0.24), (0.96, 0.64, 0.12), (0.99, 0.96, 0.78)),
    "amber_sun":      ((0.99, 0.76, 0.18), (0.92, 0.42, 0.10), (0.42, 0.22, 0.08)),
    "tangerine_gold": ((0.99, 0.52, 0.12), (0.98, 0.82, 0.22), (0.85, 0.24, 0.08)),
    "cobalt_sky":     ((0.36, 0.66, 0.99), (0.58, 0.82, 0.99), (0.96, 0.92, 0.62)),
    "royal_violet":   ((0.68, 0.44, 0.98), (0.46, 0.24, 0.86), (0.98, 0.84, 0.36)),
    "violet_gold":    ((0.66, 0.42, 0.96), (0.86, 0.62, 0.99), (0.98, 0.82, 0.28)),
    "pastel_orchid":  ((0.92, 0.68, 0.98), (0.98, 0.82, 0.92), (0.96, 0.88, 0.56)),
    "plum_ivory":     ((0.78, 0.24, 0.52), (0.96, 0.88, 0.92), (0.96, 0.78, 0.32)),
    "coral_flame":    ((0.99, 0.42, 0.36), (0.99, 0.68, 0.48), (0.98, 0.90, 0.48)),
    "ivory_moss":     ((0.98, 0.98, 0.94), (0.86, 0.95, 0.86), (0.88, 0.92, 0.44)),
    "pearl_emerald":  ((0.96, 0.99, 0.97), (0.74, 0.96, 0.84), (0.42, 0.88, 0.58)),
    "jade_mint":      ((0.46, 0.92, 0.66), (0.72, 0.98, 0.80), (0.94, 0.98, 0.74)),
    "holly_berry":    ((0.96, 0.14, 0.22), (0.99, 0.38, 0.34), (0.98, 0.84, 0.38)),
}


def parse_date_string(text):
    clean = f"{text.strip().replace(',', ' ')} 2024"
    for fmt in ("%B %d %Y", "%b %d %Y", "%m/%d %Y", "%m-%d %Y", "%d %B %Y", "%d %b %Y"):
        try:
            dt = datetime.datetime.strptime(clean, fmt)
            return datetime.date(2024, dt.month, dt.day)
        except ValueError:
            continue
    return datetime.date(2024, 11, 15)


def get_birth_flower(d: datetime.date):
    key = (d.month, d.day)
    if key in EXACT_DATES:
        name, meaning, arch, pal = EXACT_DATES[key]
    else:
        pool = MONTHLY_POOLS[d.month]
        name, meaning, arch, pal = pool[(d.day - 1) % len(pool)]
    seed = d.month * 100 + d.day
    return {
        "date_obj": d,
        "date_label": f"{d.strftime('%B').upper()} {d.day}",
        "name": name,
        "meaning": meaning,
        "arch": arch,
        "palette": PALETTES[pal],
        "seed": seed,
    }


# --- Synthesized Gentle Harp & Breeze Ambience ---
def build_botanical_audio():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
    except Exception:
        return None

    sr = 44100
    dur = 24.0
    n = int(sr * dur)
    tt = np.arange(n, dtype=np.float32) / sr

    pad_freqs = [174.61, 220.00, 261.63, 329.63, 392.00]
    buf = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(pad_freqs):
        lfo = 0.55 + 0.45 * np.sin(TAU * ((i + 1) / dur) * tt + i * 1.1)
        buf += np.sin(TAU * f * tt) * lfo * (0.085 / (1.0 + 0.25 * i))

    notes = [
        523.25, 659.25, 783.99, 987.77, 1046.50, 783.99, 659.25, 880.00, 1174.66,
        987.77, 783.99, 659.25, 587.33, 659.25, 880.00, 1046.50, 783.99, 523.25,
    ]
    for step, f in enumerate(notes):
        start_t = 0.6 + step * 1.25
        idx0 = int(start_t * sr)
        if idx0 >= n:
            break
        ring = min(n - idx0, int(sr * 2.5))
        tc = np.arange(ring, dtype=np.float32) / sr
        env = np.exp(-tc * 2.1) * (1.0 - np.exp(-tc * 110.0))
        plucked = 0.72 * np.sin(TAU * f * tc) + 0.28 * np.sin(TAU * f * 2.0 * tc) * np.exp(-tc * 5.0)
        buf[idx0:idx0 + ring] += plucked * env * 0.10

    fade_len = int(sr * 1.2)
    fade = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
    buf[:fade_len] *= fade
    buf[-fade_len:] *= fade[::-1]

    left = np.clip(buf * 32767, -32767, 32767).astype(np.int16)
    right = np.roll(left, 420)
    return pygame.sndarray.make_sound(np.column_stack((left, right)))


# --- Parametric 3D Botanical Particle Generator (Adapts to Any Birth Flower) ---
def generate_flower_cloud(spec):
    rng = np.random.default_rng(spec["seed"])
    arch = spec["arch"]
    c_main, c_sec, c_core = spec["palette"]

    pts_x, pts_y, pts_z = [], [], []
    cols_r, cols_g, cols_b = [], [], []
    birth_t, flex, kind_id = [], [], []

    def add_particles(x, y, z, r, g, b, bt, flx, k_id):
        n_pts = len(x)
        pts_x.append(np.asarray(x, dtype=np.float32))
        pts_y.append(np.asarray(y, dtype=np.float32))
        pts_z.append(np.asarray(z, dtype=np.float32))
        cols_r.append(np.full(n_pts, r, dtype=np.float32) if np.ndim(r) == 0 else np.asarray(r, dtype=np.float32))
        cols_g.append(np.full(n_pts, g, dtype=np.float32) if np.ndim(g) == 0 else np.asarray(g, dtype=np.float32))
        cols_b.append(np.full(n_pts, b, dtype=np.float32) if np.ndim(b) == 0 else np.asarray(b, dtype=np.float32))
        birth_t.append(np.full(n_pts, bt, dtype=np.float32) if np.ndim(bt) == 0 else np.asarray(bt, dtype=np.float32))
        flex.append(np.full(n_pts, flx, dtype=np.float32) if np.ndim(flx) == 0 else np.asarray(flx, dtype=np.float32))
        kind_id.append(np.full(n_pts, k_id, dtype=np.uint8))

    curve_amp = 0.042 if arch in ("umbel", "bell", "spike") else 0.024
    curve_freq = 4.4 if arch == "umbel" else 3.2

    def stem_pos(u):
        sx = curve_amp * np.sin(u * curve_freq - 0.5) - 0.014 * (u ** 1.6)
        sy = 0.34 - u * 0.65
        sz = 0.024 * np.cos(u * 3.6)
        return sx, sy, sz

    # 1. CENTRAL STEM
    n_stem = 7500
    u_s = rng.random(n_stem)
    sx, sy, sz = stem_pos(u_s)
    rad_s = (0.0072 * (1.0 - 0.55 * u_s)) * np.sqrt(rng.random(n_stem))
    ang_s = rng.uniform(0.0, TAU, n_stem)
    shade = 0.72 + 0.28 * np.cos(ang_s - 0.6)
    stem_g = 0.42 if arch == "holly" else 0.50
    add_particles(
        sx + rad_s * np.cos(ang_s),
        sy + rng.normal(0.0, 0.0012, n_stem),
        sz + rad_s * np.sin(ang_s),
        0.22 * shade + rng.uniform(-0.02, 0.03, n_stem),
        stem_g * shade + rng.uniform(-0.02, 0.04, n_stem),
        0.21 * shade,
        u_s * 4.0,
        (u_s ** 1.35) * 0.85,
        0
    )

    # 2. BRANCHES & FOLIAGE
    flower_anchors = []

    if arch == "umbel":
        branch_specs = [
            (0.16, -1, 0.19, 0.42, False),
            (0.27,  1, 0.21, 0.38, False),
            (0.39, -1, 0.22, 0.44, True),
            (0.51,  1, 0.21, 0.40, True),
            (0.64, -1, 0.19, 0.46, True),
            (0.76,  1, 0.17, 0.42, True),
            (0.88, -1, 0.14, 0.36, True),
        ]
        for b_idx, (u0, side, b_len, upward, has_bloom) in enumerate(branch_specs):
            bx0, by0, bz0 = stem_pos(u0)
            b_start = u0 * 3.9 + 0.35
            z_tilt = 0.28 * np.sin(b_idx * 1.9)

            def branch_pos(v):
                return (
                    bx0 + side * b_len * v,
                    by0 - upward * b_len * (v ** 0.88) + 0.022 * (v ** 2),
                    bz0 + z_tilt * b_len * v,
                )

            nb = 1600
            vb = rng.random(nb)
            bx, by, bz = branch_pos(vb)
            rb = 0.0036 * (1.0 - 0.55 * vb) * np.sqrt(rng.random(nb))
            ab = rng.uniform(0.0, TAU, nb)
            add_particles(
                bx + rb * np.cos(ab), by + rb * np.sin(ab), bz + rng.normal(0.0, 0.001, nb),
                0.28, 0.54 + 0.12 * vb, 0.25,
                b_start + vb * 1.5, (u0 ** 1.2) * 0.85 + vb * 0.35, 0
            )

            for p_i in range(6):
                vp = 0.18 + (p_i / 5.0) * 0.72
                lx0, ly0, lz0 = branch_pos(vp)
                leaf_len = 0.036 * (1.0 - 0.32 * abs(vp - 0.52))
                leaf_wid = 0.0145 * (1.0 - 0.25 * abs(vp - 0.52))
                for l_side in (-1, 1):
                    nl = 380
                    s_l = np.sqrt(rng.random(nl))
                    t_l = rng.uniform(0.0, TAU, nl)
                    u_ov = s_l * np.cos(t_l)
                    v_ov = s_l * np.sin(t_l) * (1.0 - 0.25 * u_ov)
                    ang_l = (0.62 if l_side > 0 else -0.78) + 0.15 * side
                    ca, sa = np.cos(ang_l), np.sin(ang_l)
                    dx = (u_ov + 1.0) * 0.5 * leaf_len * side
                    dy = v_ov * leaf_wid
                    edge_m = s_l > 0.78
                    add_particles(
                        lx0 + dx * ca - dy * sa, ly0 + dx * sa + dy * ca,
                        lz0 + 0.004 * np.sin(s_l * np.pi) * l_side,
                        np.where(edge_m, 0.44, 0.22), np.where(edge_m, 0.74, 0.48), np.where(edge_m, 0.32, 0.19),
                        b_start + vp * 1.4 + s_l * 0.9, (u0 ** 1.2) * 0.85 + vp * 0.45, 0
                    )
                    nh = 110
                    th = rng.uniform(0.0, TAU, nh)
                    sh = rng.uniform(0.95, 1.24, nh)
                    uh = sh * np.cos(th)
                    vh = sh * np.sin(th) * (1.0 - 0.25 * np.clip(uh, -1, 1))
                    hdx = (uh + 1.0) * 0.5 * leaf_len * side
                    hdy = vh * leaf_wid
                    add_particles(
                        lx0 + hdx * ca - hdy * sa, ly0 + hdx * sa + hdy * ca, lz0 + rng.normal(0.0, 0.002, nh),
                        0.56, 0.80, 0.45,
                        b_start + vp * 1.4 + 0.7, (u0 ** 1.2) * 0.85 + vp * 0.55, 1
                    )
            if has_bloom:
                tx, ty, tz = branch_pos(1.0)
                flower_anchors.append((tx, ty, tz, b_start + 1.3, u0, 1.0))
        tx0, ty0, tz0 = stem_pos(0.98)
        flower_anchors.append((tx0, ty0 - 0.015, tz0, 4.3, 1.0, 1.05))

    else:
        n_leaves = 10 if arch in ("holly", "spike") else 8
        for l_i in range(n_leaves):
            u0 = 0.14 + (l_i / (n_leaves - 1)) * 0.62
            side = -1 if (l_i % 2 == 0) else 1
            lx0, ly0, lz0 = stem_pos(u0)
            l_start = u0 * 3.8 + 0.4
            leaf_len = (0.14 if arch in ("daisy", "trumpet", "violet") else 0.11) * (1.05 - 0.35 * u0)
            leaf_wid = (0.068 if arch in ("violet", "holly") else 0.044) * (1.05 - 0.30 * u0)
            tilt = (0.45 if arch == "spike" else 0.28) * side

            nl = 3800
            s_l = np.sqrt(rng.random(nl))
            t_l = rng.uniform(0.0, TAU, nl)
            u_ov = s_l * np.cos(t_l)
            v_ov = s_l * np.sin(t_l)

            serrate = 1.0 + (0.24 * np.cos(7.0 * t_l) if arch == "holly" else 0.06 * np.cos(14.0 * t_l))
            dx = (u_ov + 1.0) * 0.5 * leaf_len * side * serrate
            dy = v_ov * leaf_wid * serrate - 0.03 * ((u_ov + 1.0) ** 2)
            ca, sa = np.cos(tilt), np.sin(tilt)
            rx = dx * ca - dy * sa
            ry = dx * sa + dy * ca
            rz = 0.018 * np.sin(s_l * np.pi) * side + 0.014 * np.cos(l_i * 1.7)

            edge_m = s_l > 0.82
            vein_m = np.abs(v_ov) < 0.10
            base_g = 0.38 if arch == "holly" else 0.48
            add_particles(
                lx0 + rx, ly0 + ry, lz0 + rz,
                np.where(edge_m, 0.36, 0.18) + rng.uniform(-0.02, 0.02, nl),
                np.where(edge_m, base_g + 0.26, np.where(vein_m, base_g + 0.20, base_g)),
                np.where(edge_m, 0.28, 0.18),
                l_start + s_l * 1.3, (u0 ** 1.2) * 0.85 + s_l * 0.35, 0
            )

            nh = 1000
            th = rng.uniform(0.0, TAU, nh)
            sh = rng.uniform(0.96, 1.14, nh)
            ser_h = 1.0 + (0.24 * np.cos(7.0 * th) if arch == "holly" else 0.06 * np.cos(14.0 * th))
            hdx = (sh * np.cos(th) + 1.0) * 0.5 * leaf_len * side * ser_h
            hdy = sh * np.sin(th) * leaf_wid * ser_h - 0.03 * ((sh * np.cos(th) + 1.0) ** 2)
            add_particles(
                lx0 + hdx * ca - hdy * sa, ly0 + hdx * sa + hdy * ca, lz0 + rz[:nh],
                0.48, 0.78, 0.44,
                l_start + 0.9, (u0 ** 1.2) * 0.85 + 0.4, 1
            )

        if arch in ("bell", "spike"):
            n_bl = 9 if arch == "spike" else 7
            for k in range(n_bl):
                ub = 0.44 + (k / (n_bl - 1)) * 0.54
                bx, by, bz = stem_pos(ub)
                side = -1 if (k % 2 == 0) else 1
                off_x = (0.048 if arch == "bell" else 0.026) * side
                flower_anchors.append((bx + off_x, by, bz + 0.015 * side, 3.6 + k * 0.35, ub, 0.82 - 0.22 * (k / n_bl)))
        elif arch == "holly":
            for u_h in (0.35, 0.55, 0.75, 0.92):
                bx, by, bz = stem_pos(u_h)
                flower_anchors.append((bx, by, bz, 3.8 + u_h * 1.5, u_h, 1.0))
        else:
            tx0, ty0, tz0 = stem_pos(0.95)
            flower_anchors.append((tx0, ty0 - 0.02, tz0, 3.8, 1.0, 1.0))

    # 3. BLOSSOM HEADS (kind_id = 2 — stays anchored to the stems)
    for f_idx, (fx, fy, fz, f_start, u_h, sc) in enumerate(flower_anchors):
        if arch == "umbel":
            n_florets = 16
            idx_f = np.arange(n_florets)
            phi_f = np.arccos(1.0 - 2.0 * (idx_f + 0.5) / n_florets)
            theta_f = idx_f * 2.39996323 + f_idx * 0.7
            umbel_r = 0.036 * sc
            for fl_i in range(n_florets):
                dx_c = umbel_r * np.sin(phi_f[fl_i]) * np.cos(theta_f[fl_i])
                dy_c = umbel_r * np.cos(phi_f[fl_i]) * 0.88
                dz_c = umbel_r * np.sin(phi_f[fl_i]) * np.sin(theta_f[fl_i])
                nf = 360
                u_p = rng.random(nf)
                v_p = rng.uniform(0.0, TAU, nf)
                cup = 0.0165 * np.sin(u_p * np.pi) * (0.78 + 0.25 * np.cos(2.0 * v_p))
                is_core = u_p < 0.26
                is_sec = (u_p >= 0.26) & (u_p < 0.62) & ((fl_i % 2) == 0)
                r_f = np.where(is_core, c_core[0], np.where(is_sec, c_sec[0], c_main[0])) + rng.uniform(-0.03, 0.01, nf)
                g_f = np.where(is_core, c_core[1], np.where(is_sec, c_sec[1], c_main[1])) + rng.uniform(-0.03, 0.02, nf)
                b_f = np.where(is_core, c_core[2], np.where(is_sec, c_sec[2], c_main[2])) + rng.uniform(-0.03, 0.03, nf)
                add_particles(
                    fx + dx_c * (0.45 + 0.55 * u_p) + cup * np.cos(v_p),
                    fy + dy_c * (0.45 + 0.55 * u_p) + cup * np.sin(v_p) * 0.85,
                    fz + dz_c * (0.45 + 0.55 * u_p) + 0.012 * (u_p - 0.5),
                    r_f, g_f, b_f,
                    f_start + (fl_i / n_florets) * 1.4 + u_p * 1.1,
                    (u_h ** 1.15) * 0.95, 2
                )

        elif arch == "rose":
            nf = 32000
            u_p = rng.random(nf)
            th = rng.uniform(0.0, TAU * 6.5, nf)
            layer = th / (TAU * 6.5)
            r_rad = (0.018 + 0.145 * (layer ** 0.85)) * np.sqrt(u_p) * sc
            cup_z = -0.11 * (1.0 - layer * 0.72) * np.cos(u_p * np.pi * 0.5) * sc
            curl = 0.018 * np.sin(th * 5.0) * u_p
            px_f = fx + (r_rad + curl) * np.cos(th)
            py_f = fy + cup_z + 0.025 * (r_rad / 0.15) - 0.02
            pz_f = fz + (r_rad + curl) * np.sin(th) * 0.82
            py_t = py_f * 0.86 - pz_f * 0.50
            pz_t = py_f * 0.50 + pz_f * 0.86
            is_core = layer < 0.22
            is_rim = u_p > 0.84
            r_f = np.where(is_core, c_core[0], np.where(is_rim, c_sec[0], c_main[0])) + rng.uniform(-0.03, 0.02, nf)
            g_f = np.where(is_core, c_core[1], np.where(is_rim, c_sec[1], c_main[1])) + rng.uniform(-0.03, 0.02, nf)
            b_f = np.where(is_core, c_core[2], np.where(is_rim, c_sec[2], c_main[2])) + rng.uniform(-0.03, 0.02, nf)
            add_particles(px_f, py_t, pz_t, r_f, g_f, b_f, f_start + layer * 2.2 + u_p * 0.8, 0.95, 2)

        elif arch == "daisy":
            n_disk = 8000
            idx_d = rng.random(n_disk)
            r_d = 0.056 * np.sqrt(idx_d) * sc
            a_d = idx_d * n_disk * 2.39996323
            add_particles(
                fx + r_d * np.cos(a_d),
                fy + r_d * np.sin(a_d) * 0.88 - 0.02,
                fz + 0.022 * np.cos(idx_d * np.pi * 0.5),
                c_core[0] + rng.uniform(-0.04, 0.03, n_disk),
                c_core[1] + rng.uniform(-0.04, 0.03, n_disk),
                c_core[2] + rng.uniform(-0.03, 0.03, n_disk),
                f_start + idx_d * 1.1, 0.95, 2
            )
            n_pet = 24000
            n_rays = 22
            p_id = rng.integers(0, n_rays, n_pet)
            u_p = rng.random(n_pet)
            v_p = rng.uniform(-1.0, 1.0, n_pet)
            ang = (p_id / n_rays) * TAU + (p_id % 2) * 0.04
            p_len = (0.052 + 0.115 * u_p) * sc
            p_wid = 0.015 * np.sin(u_p * np.pi) * v_p * sc
            ca, sa = np.cos(ang), np.sin(ang)
            px_f = fx + p_len * ca - p_wid * sa
            py_f = fy + (p_len * sa + p_wid * ca) * 0.88 - 0.02
            pz_f = fz + 0.024 * np.sin(u_p * np.pi) + (p_id % 2) * 0.008
            is_sec = (u_p > 0.72) | ((p_id % 2) == 1)
            add_particles(
                px_f, py_f, pz_f,
                np.where(is_sec, c_sec[0], c_main[0]) + rng.uniform(-0.03, 0.02, n_pet),
                np.where(is_sec, c_sec[1], c_main[1]) + rng.uniform(-0.03, 0.02, n_pet),
                np.where(is_sec, c_sec[2], c_main[2]) + rng.uniform(-0.03, 0.02, n_pet),
                f_start + 0.6 + u_p * 1.8, 0.95, 2
            )

        elif arch == "trumpet":
            n_outer = 20000
            p_id = rng.integers(0, 6, n_outer)
            u_p = rng.random(n_outer)
            v_p = rng.uniform(-1.0, 1.0, n_outer)
            ang = (p_id / 6.0) * TAU + 0.25
            p_len = (0.03 + 0.135 * u_p) * sc
            p_wid = 0.038 * np.sin(u_p * np.pi) * v_p * sc
            ca, sa = np.cos(ang), np.sin(ang)
            add_particles(
                fx + p_len * ca - p_wid * sa,
                fy + (p_len * sa + p_wid * ca) * 0.88 - 0.02,
                fz + 0.018 * np.sin(u_p * np.pi),
                c_main[0] + rng.uniform(-0.03, 0.02, n_outer),
                c_main[1] + rng.uniform(-0.03, 0.02, n_outer),
                c_main[2] + rng.uniform(-0.03, 0.02, n_outer),
                f_start + 0.4 + u_p * 1.6, 0.95, 2
            )
            n_cup = 12000
            uc = rng.random(n_cup)
            ac = rng.uniform(0.0, TAU, n_cup)
            ruffle = 1.0 + 0.16 * np.sin(12.0 * ac) * (uc ** 1.5)
            rc = (0.024 + 0.028 * uc) * ruffle * sc
            is_rim = uc > 0.82
            add_particles(
                fx + rc * np.cos(ac),
                fy + rc * np.sin(ac) * 0.88 - 0.02,
                fz + 0.015 + 0.068 * uc * sc,
                np.where(is_rim, c_core[0], c_sec[0]),
                np.where(is_rim, c_core[1], c_sec[1]),
                np.where(is_rim, c_core[2], c_sec[2]),
                f_start + 1.0 + uc * 1.4, 0.95, 2
            )

        elif arch == "violet":
            nf = 32000
            p_id = rng.integers(0, 5, nf)
            u_p = rng.random(nf)
            v_p = rng.uniform(-1.0, 1.0, nf)
            angles = np.array([-2.2, -0.94, 0.25, 1.57, 2.89])
            scales = np.array([0.92, 0.92, 0.95, 1.18, 0.95]) * sc
            ang = angles[p_id]
            p_len = (0.02 + 0.125 * u_p) * scales[p_id]
            p_wid = 0.056 * (np.sin(u_p * np.pi) ** 0.7) * v_p * scales[p_id]
            ca, sa = np.cos(ang), np.sin(ang)
            is_eye = u_p < 0.22
            is_blotch = (u_p >= 0.22) & (u_p < 0.55) & (np.abs(v_p) < 0.55)
            add_particles(
                fx + p_len * ca - p_wid * sa,
                fy + (p_len * sa + p_wid * ca) * 0.9 - 0.02,
                fz + 0.02 * np.sin(u_p * np.pi) + p_id * 0.004,
                np.where(is_eye, c_core[0], np.where(is_blotch, c_sec[0], c_main[0])),
                np.where(is_eye, c_core[1], np.where(is_blotch, c_sec[1], c_main[1])),
                np.where(is_eye, c_core[2], np.where(is_blotch, c_sec[2], c_main[2])),
                f_start + 0.5 + u_p * 1.8, 0.95, 2
            )

        elif arch == "holly":
            for b_i in range(5):
                ang_b = b_i * 1.35 + f_idx
                bx = fx + 0.028 * np.cos(ang_b)
                by = fy + 0.022 * np.sin(ang_b * 1.3)
                bz = fz + 0.028 * np.sin(ang_b)
                nb = 1800
                rad_b = 0.022 * (rng.random(nb) ** (1.0 / 3.0))
                th_b = rng.uniform(0.0, TAU, nb)
                ph_b = np.arccos(rng.uniform(-1.0, 1.0, nb))
                px_b = bx + rad_b * np.sin(ph_b) * np.cos(th_b)
                py_b = by + rad_b * np.cos(ph_b)
                pz_b = bz + rad_b * np.sin(ph_b) * np.sin(th_b)
                spec_hi = (px_b - bx > 0.006) & (py_b - by < -0.006)
                add_particles(
                    px_b, py_b, pz_b,
                    np.where(spec_hi, c_core[0], c_main[0]),
                    np.where(spec_hi, c_core[1], c_main[1]),
                    np.where(spec_hi, c_core[2], c_main[2]),
                    f_start + b_i * 0.25, (u_h ** 1.15) * 0.95, 2
                )

        else:
            nf = 4000
            u_b = rng.random(nf)
            a_b = rng.uniform(0.0, TAU, nf)
            if arch == "bell":
                flare = (0.012 + 0.036 * (u_b ** 1.25)) * (1.0 + 0.14 * np.cos(6.0 * a_b) * u_b) * sc
                px_b = fx + flare * np.cos(a_b)
                py_b = fy + 0.056 * u_b * sc
                pz_b = fz + flare * np.sin(a_b)
            else:
                pet = 1.0 + 0.35 * np.cos(5.0 * a_b) * (u_b ** 0.8)
                flare = (0.010 + 0.048 * u_b) * pet * sc
                px_b = fx + flare * np.cos(a_b)
                py_b = fy + flare * np.sin(a_b) * 0.85
                pz_b = fz + 0.025 * (1.0 - u_b)

            is_core = u_b < 0.25
            is_rim = u_b > 0.78
            add_particles(
                px_b, py_b, pz_b,
                np.where(is_core, c_core[0], np.where(is_rim, c_sec[0], c_main[0])),
                np.where(is_core, c_core[1], np.where(is_rim, c_sec[1], c_main[1])),
                np.where(is_core, c_core[2], np.where(is_rim, c_sec[2], c_main[2])),
                f_start + u_b * 1.3, (u_h ** 1.15) * 0.95, 2
            )

    # 4. AMBIENT GOLDEN SPECKS & STARDUST (kind_id = 3 — gentle stationary shimmer)
    n_conf = 1800
    cx = rng.uniform(-0.34, 0.34, n_conf)
    cy = rng.uniform(-0.42, 0.42, n_conf)
    cz = rng.uniform(-0.18, 0.18, n_conf)
    is_gold = rng.random(n_conf) < 0.55
    add_particles(
        cx, cy, cz,
        np.where(is_gold, 0.98, c_main[0]),
        np.where(is_gold, 0.86, c_main[1]),
        np.where(is_gold, 0.44, c_main[2]),
        rng.uniform(5.2, 9.8, n_conf),
        rng.uniform(0.6, 1.4, n_conf),
        3
    )

    return {
        "x": np.concatenate(pts_x),
        "y": np.concatenate(pts_y),
        "z": np.concatenate(pts_z),
        "r": np.concatenate(cols_r),
        "g": np.concatenate(cols_g),
        "b": np.concatenate(cols_b),
        "birth": np.concatenate(birth_t),
        "flex": np.concatenate(flex),
        "kind": np.concatenate(kind_id),
        "phase": rng.uniform(0.0, TAU, sum(len(a) for a in pts_x)).astype(np.float32),
        "n_hairs": int(sum((k == 1).sum() for k in kind_id)),
    }


def render_frame(buf, data, t, yaw, pitch, wind, cw, ch):
    buf.fill(0.0)
    alive = data["birth"] <= t
    if not np.any(alive):
        return 0

    age = t - data["birth"][alive]
    grow = smooth(age / 0.85)

    px = data["x"][alive].copy()
    py = data["y"][alive].copy()
    pz = data["z"][alive].copy()
    flx = data["flex"][alive]
    ph = data["phase"][alive]
    knd = data["kind"][alive]

    # Gentle organic wind sway on stems, leaves & anchored blossoms
    breeze = (0.012 + 0.032 * wind) * np.sin(1.45 * t - py * 4.2 + ph * 0.15) * flx
    px += breeze
    py += 0.004 * np.cos(1.1 * t + ph * 0.2) * flx

    # Gentle stationary hover for ambient golden specks (no falling)
    is_conf = knd == 3
    if np.any(is_conf):
        py[is_conf] += 0.005 * np.sin(1.2 * t + ph[is_conf])
        px[is_conf] += 0.006 * np.cos(1.0 * t + ph[is_conf])

    cos_y, sin_y = float(np.cos(yaw)), float(np.sin(yaw))
    x1 = px * cos_y + pz * sin_y
    z1 = -px * sin_y + pz * cos_y

    cos_p, sin_p = float(np.cos(pitch)), float(np.sin(pitch))
    y2 = py * cos_p - z1 * sin_p
    z2 = py * sin_p + z1 * cos_p

    cam_dist = 1.65
    depth = z2 + cam_dist
    inv_d = 1.0 / np.maximum(depth, 0.35)
    focal = ch * 1.48

    sx = np.round(x1 * inv_d * focal + cw * 0.5).astype(np.int32)
    sy = np.round(y2 * inv_d * focal + ch * 0.52).astype(np.int32)

    valid = (sx >= 1) & (sx < cw - 1) & (sy >= 1) & (sy < ch - 1)
    sx = sx[valid]
    sy = sy[valid]
    g_w = grow[valid] * (1.12 - 0.35 * np.clip(z2[valid] + 0.25, 0.0, 0.6))

    r_val = data["r"][alive][valid] * g_w * 0.78
    g_val = data["g"][alive][valid] * g_w * 0.78
    b_val = data["b"][alive][valid] * g_w * 0.78

    np.add.at(buf[:, :, 0], (sx, sy), r_val)
    np.add.at(buf[:, :, 1], (sx, sy), g_val)
    np.add.at(buf[:, :, 2], (sx, sy), b_val)

    return int(sx.size)


def bloom_pass(surf, scale_div, blur_rad, intensity):
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // scale_div), max(1, h // scale_div)))
    if hasattr(pygame.transform, "gaussian_blur"):
        small = pygame.transform.gaussian_blur(small, max(1, blur_rad // scale_div))
    glow = pygame.transform.smoothscale(small, (w, h))
    glow.fill((int(255 * intensity),) * 3, special_flags=pygame.BLEND_MULT)
    return glow


def main():
    pygame.init()
    audio = build_botanical_audio()
    muted = False
    if audio is not None:
        audio.play(loops=-1)

    W, H = 1480, 880
    STAGE_W, STAGE_H = 540, 820
    STAGE_X = (W - STAGE_W) // 2
    STAGE_Y = (H - STAGE_H) // 2

    info_disp = pygame.display.Info()
    k = min(0.92 * info_disp.current_h / H, 0.95 * info_disp.current_w / W)
    win_size = (int(W * k), int(H * k))

    window = pygame.display.set_mode(win_size)
    screen = pygame.Surface((W, H))
    stage_surf = pygame.Surface((STAGE_W, STAGE_H))
    accum_buf = np.zeros((STAGE_W, STAGE_H, 3), dtype=np.float32)

    mono_name = "consolas,menlo,dejavusansmono,couriernew,monospace"
    serif_name = "georgia,timesnewroman,serif"
    sans_name = "segoeui,helvetica,arial,sans-serif"

    f_label = pygame.font.SysFont(sans_name, 13, bold=True)
    f_val = pygame.font.SysFont(sans_name, 22, bold=True)
    f_top = pygame.font.SysFont(sans_name, 16, bold=True)
    f_sub = pygame.font.SysFont(sans_name, 12, bold=True)
    f_title = pygame.font.SysFont(serif_name, 40, bold=True)
    f_meaning = pygame.font.SysFont(sans_name, 14, bold=True)
    f_hud = pygame.font.SysFont(mono_name, 15)

    txt_bday = f_top.render("H A P P Y   B I R T H D A Y", True, (220, 218, 212))

    def load_date(date_obj):
        spec = get_birth_flower(date_obj)
        pygame.display.set_caption(f"{spec['name']} ({spec['date_label']}) — Kobsi · 2026")
        spaced_date = "   ".join(" ".join(w) for w in spec["date_label"].split())
        spaced_mean = " ".join(spec["meaning"])
        return {
            "spec": spec,
            "data": generate_flower_cloud(spec),
            "txt_date": f_sub.render(spaced_date, True, (185, 142, 112)),
            "txt_flower": f_title.render(spec["name"], True, (245, 242, 236)),
            "txt_meaning": f_meaning.render(spaced_mean, True, (195, 192, 185)),
        }

    current_date = parse_date_string(BIRTH_DATE)
    bundle = load_date(current_date)

    clock = pygame.time.Clock()
    t = 0.0
    paused = False
    fullscreen = False
    typing_date = False
    typed_buf = ""
    user_yaw = 0.0
    user_pitch = 0.0
    wind = 0.25
    fps_smooth = 30.0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                return

            if typing_date:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        typing_date = False
                    elif e.key == pygame.K_RETURN:
                        if typed_buf.strip():
                            current_date = parse_date_string(typed_buf)
                            bundle = load_date(current_date)
                            t = 0.0
                        typing_date = False
                    elif e.key == pygame.K_BACKSPACE:
                        typed_buf = typed_buf[:-1]
                    elif e.unicode and e.unicode.isprintable():
                        typed_buf += e.unicode
                continue

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                elif e.key == pygame.K_SPACE:
                    paused = not paused
                    if audio is not None and not muted:
                        pygame.mixer.pause() if paused else pygame.mixer.unpause()
                elif e.key == pygame.K_m and audio is not None:
                    muted = not muted
                    audio.set_volume(0.0 if muted else 1.0)
                elif e.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        di = pygame.display.Info()
                        win_size = (di.current_w, di.current_h)
                        window = pygame.display.set_mode(win_size, pygame.FULLSCREEN)
                    else:
                        win_size = (int(W * k), int(H * k))
                        window = pygame.display.set_mode(win_size)
                elif e.key == pygame.K_r:
                    t = 0.0
                    user_yaw = 0.0
                    user_pitch = 0.0
                elif e.key == pygame.K_s:
                    slug = bundle["spec"]["name"].lower().replace(" ", "_")
                    pygame.image.save(screen, str(Path(__file__).with_name(f"{slug}_{int(time.time())}.png")))
                elif e.key == pygame.K_d:
                    typing_date = True
                    typed_buf = ""
                elif e.key == pygame.K_UP:
                    current_date += datetime.timedelta(days=1)
                    bundle = load_date(current_date)
                    t = 0.0
                elif e.key == pygame.K_DOWN:
                    current_date -= datetime.timedelta(days=1)
                    bundle = load_date(current_date)
                    t = 0.0
                elif e.key == pygame.K_TAB:
                    next_m = 1 if current_date.month == 12 else current_date.month + 1
                    current_date = datetime.date(2024, next_m, min(current_date.day, 28))
                    bundle = load_date(current_date)
                    t = 0.0

        keys = pygame.key.get_pressed()
        if not typing_date:
            if keys[pygame.K_RIGHT]:
                wind = min(2.0, wind + 0.03)
            if keys[pygame.K_LEFT]:
                wind = max(0.0, wind - 0.03)

        if pygame.mouse.get_pressed()[0]:
            mdx, mdy = pygame.mouse.get_rel()
            user_yaw += mdx * 0.008
            user_pitch = float(np.clip(user_pitch + mdy * 0.006, -0.85, 0.85))
        else:
            pygame.mouse.get_rel()

        dt = clock.tick(30) / 1000.0
        if dt > 0:
            fps_smooth = 0.85 * fps_smooth + 0.15 * (1.0 / dt)

        # Runs continuously until closed (press [R] to replay bloom)
        if not paused:
            t += min(dt, 1.0 / 15.0)

        spec = bundle["spec"]
        data = bundle["data"]

        auto_yaw = 0.18 * np.sin(0.45 * t) + user_yaw
        active_pts = render_frame(accum_buf, data, t, auto_yaw, user_pitch, wind, STAGE_W, STAGE_H)

        rgb_u8 = np.clip(np.power(np.clip(accum_buf, 0.0, 1.0), 0.86) * 255.0, 0, 255).astype(np.uint8)
        pygame.surfarray.blit_array(stage_surf, rgb_u8)

        screen.fill((22, 23, 22))
        pygame.draw.rect(screen, (6, 7, 6), (STAGE_X, STAGE_Y, STAGE_W, STAGE_H))
        pygame.draw.rect(screen, (46, 48, 46), (STAGE_X - 1, STAGE_Y - 1, STAGE_W + 2, STAGE_H + 2), 1)

        screen.blit(stage_surf, (STAGE_X, STAGE_Y))
        screen.blit(bloom_pass(stage_surf, 4, 8, 0.34), (STAGE_X, STAGE_Y), special_flags=pygame.BLEND_ADD)
        screen.blit(bloom_pass(stage_surf, 8, 20, 0.22), (STAGE_X, STAGE_Y), special_flags=pygame.BLEND_ADD)

        text_alpha = int(255 * smooth((t - 0.5) / 1.3))
        for surf_txt, pos in [
            (txt_bday, (STAGE_X + (STAGE_W - txt_bday.get_width()) // 2, STAGE_Y + 42)),
            (bundle["txt_date"], (STAGE_X + (STAGE_W - bundle["txt_date"].get_width()) // 2, STAGE_Y + 70)),
            (bundle["txt_flower"], (STAGE_X + (STAGE_W - bundle["txt_flower"].get_width()) // 2, STAGE_Y + STAGE_H - 102)),
            (bundle["txt_meaning"], (STAGE_X + (STAGE_W - bundle["txt_meaning"].get_width()) // 2, STAGE_Y + STAGE_H - 50)),
        ]:
            tmp = surf_txt.copy()
            tmp.set_alpha(text_alpha)
            screen.blit(tmp, pos)

        # Left Telemetry Column
        lx = STAGE_X - 245
        left_items = [
            ("DATE", f"{current_date.strftime('%b %d')}"),
            ("FORM", spec["arch"]),
            ("WIND", f"{wind:.2f}"),
            ("ROUGH", "0.70"),
            ("THRESH", "10"),
        ]
        for idx, (lbl, val) in enumerate(left_items):
            yy = STAGE_Y + 24 + idx * 96
            screen.blit(f_label.render(lbl, True, (118, 122, 118)), (lx, yy))
            screen.blit(f_val.render(val, True, (232, 232, 226)), (lx, yy + 20))

        # Right Telemetry Column
        rx = STAGE_X + STAGE_W + 48
        frame_num = min(308, int((min(t, LOOP) / LOOP) * 308))
        right_items = [
            ("POINTS", f"{active_pts / 1_000_000:.2f}M"),
            ("HAIRS", f"{data['n_hairs'] // 1000}k"),
            ("FRAME", f"{frame_num:03d} / 308"),
            ("TIME", f"{t:04.1f} s"),
            ("FPS", f"{fps_smooth:04.1f}"),
        ]
        for idx, (lbl, val) in enumerate(right_items):
            yy = STAGE_Y + 24 + idx * 96
            screen.blit(f_label.render(lbl, True, (118, 122, 118)), (rx, yy))
            screen.blit(f_val.render(val, True, (232, 232, 226)), (rx, yy + 20))

        # Bottom-Left HUD & Interactive Date Prompt
        screen.blit(f_hud.render("Kobsi · 2026", True, (158, 164, 156)), (48, H - 72))
        if typing_date:
            prompt = f"Enter date (e.g. May 14): {typed_buf}_"
            screen.blit(f_hud.render(prompt, True, (255, 220, 120)), (48, H - 46))
        else:
            screen.blit(f_hud.render("[D] type date · ↑/↓ day · [Tab] month · drag orbit", True, (104, 108, 104)), (48, H - 46))

        window.blit(screen if win_size == (W, H) else pygame.transform.smoothscale(screen, win_size), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    sys.exit(main())
