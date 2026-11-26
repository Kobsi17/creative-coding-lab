# Kobsi · 2026 — Galactic Star Nursery & Binary Nebula
import sys
import time
from pathlib import Path
import numpy as np
import pygame

TAU = np.pi * 2.0
IGNITE = 4.8


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


# --- 36-Second Evolving Cosmic Synth & Harp Soundscape (Zero External Files) ---
class CosmicAudio:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.pad_sound = None
        self.burst_sound = None
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.enabled = True
            self._build()
        except Exception:
            self.enabled = False

    def _build(self):
        sr = 44100
        dur = 36.0
        n = int(sr * dur)
        tt = np.arange(n, dtype=np.float32) / sr

        # Deep Lydian space drone (C2, G2, D3, E3, F#3, B3, D4)
        freqs = [65.41, 98.00, 146.83, 164.81, 185.00, 246.94, 293.66]
        pad = np.zeros(n, dtype=np.float32)
        for i, f in enumerate(freqs):
            lfo = 0.58 + 0.42 * np.sin(TAU * ((i + 1) / dur) * tt + i * 0.9)
            detune = 1.0 + 0.0022 * np.sin(TAU * (2.0 / dur) * tt + i)
            pad += np.sin(TAU * f * detune * tt) * lfo * (0.095 / (1.0 + 0.24 * i))

        # 36-second celestial harp arpeggio sequence
        scale = [523.25, 587.33, 659.25, 739.99, 783.99, 987.77, 1174.66, 1318.51]
        events = [
            (0.8, 0), (2.4, 2), (4.0, 4), (4.8, 6), (6.6, 5), (8.4, 3), (10.2, 2),
            (12.2, 1), (13.8, 3), (15.4, 4), (17.0, 7), (18.8, 5), (20.6, 4), (22.4, 2),
            (24.4, 0), (26.0, 3), (27.6, 5), (29.2, 6), (31.0, 4), (32.8, 2), (34.4, 0),
        ]
        for t0, deg in events:
            i0 = int(t0 * sr)
            ring = min(n - i0, int(sr * 3.0))
            th = np.arange(ring, dtype=np.float32) / sr
            f = scale[deg]
            env = np.exp(-th * 1.9) * (1.0 - np.exp(-th * 130.0))
            harp = 0.76 * np.sin(TAU * f * th) + 0.24 * np.sin(TAU * f * 2.0 * th) * np.exp(-th * 4.5)
            pad[i0:i0 + ring] += harp * env * 0.075

        fade = np.linspace(0.0, 1.0, int(sr * 1.6), dtype=np.float32)
        pad[:len(fade)] *= fade
        pad[-len(fade):] *= fade[::-1]

        left = np.clip(pad * 32767, -32767, 32767).astype(np.int16)
        right = np.roll(left, 620)
        self.pad_sound = pygame.sndarray.make_sound(np.column_stack((left, right)))

        # Supernova / pulsar chime burst
        b_len = int(sr * 2.6)
        tb = np.arange(b_len, dtype=np.float32) / sr
        boom = np.sin(TAU * (88.0 * np.exp(-tb * 1.6) + 34.0) * tb) * np.exp(-tb * 1.9) * 0.26
        for idx, f in enumerate([523.25, 783.99, 987.77, 1174.66, 1567.98]):
            d = int(idx * 0.075 * sr)
            ts = np.arange(b_len - d, dtype=np.float32) / sr
            boom[d:] += np.sin(TAU * f * ts) * np.exp(-ts * 2.2) * (1.0 - np.exp(-ts * 150.0)) * 0.11
        b_i16 = np.clip(boom * 32767, -32767, 32767).astype(np.int16)
        self.burst_sound = pygame.sndarray.make_sound(np.column_stack((b_i16, np.roll(b_i16, 190))))

    def start(self):
        if self.enabled and self.pad_sound is not None:
            self.pad_sound.play(loops=-1)

    def trigger_burst(self):
        if self.enabled and not self.muted and self.burst_sound is not None:
            self.burst_sound.play()

    def set_muted(self, mute_state):
        self.muted = mute_state
        if self.enabled and self.pad_sound is not None:
            self.pad_sound.set_volume(0.0 if self.muted else 1.0)


# --- Procedural 3D Nebula Cloud & Star Cluster Generator ---
def generate_universe():
    rng = np.random.default_rng(2026)

    px, py, pz = [], [], []
    cr, cg, cb = [], [], []
    birth, weight, kind = [], [], []

    def add(x, y, z, r, g, b, bt, w, k):
        n = len(x)
        px.append(np.asarray(x, dtype=np.float32))
        py.append(np.asarray(y, dtype=np.float32))
        pz.append(np.asarray(z, dtype=np.float32))
        cr.append(np.full(n, r, dtype=np.float32) if np.ndim(r) == 0 else np.asarray(r, dtype=np.float32))
        cg.append(np.full(n, g, dtype=np.float32) if np.ndim(g) == 0 else np.asarray(g, dtype=np.float32))
        cb.append(np.full(n, b, dtype=np.float32) if np.ndim(b) == 0 else np.asarray(b, dtype=np.float32))
        birth.append(np.full(n, bt, dtype=np.float32) if np.ndim(bt) == 0 else np.asarray(bt, dtype=np.float32))
        weight.append(np.full(n, w, dtype=np.float32) if np.ndim(w) == 0 else np.asarray(w, dtype=np.float32))
        kind.append(np.full(n, k, dtype=np.uint8))

    # 1. DEEP-SPACE BACKGROUND STARFIELD (4,500 crisp stars)
    n_bg = 4500
    bx = rng.uniform(-1.45, 1.45, n_bg)
    by = rng.uniform(-0.95, 0.95, n_bg)
    bz = rng.uniform(-1.10, 1.10, n_bg)
    tint = rng.random(n_bg)
    add(
        bx, by, bz,
        np.where(tint < 0.3, 0.72, np.where(tint < 0.7, 0.96, 1.0)),
        np.where(tint < 0.3, 0.86, np.where(tint < 0.7, 0.96, 0.85)),
        np.where(tint < 0.3, 1.00, np.where(tint < 0.7, 1.00, 0.68)),
        rng.uniform(0.0, 1.8, n_bg),
        rng.uniform(0.45, 1.15, n_bg),
        0
    )

    # 2. VOLUMETRIC 3D NEBULA FILAMENTS & IONIZED GAS PILLARS (33,600 points)
    lobes = [
        (-0.34,  0.14, -0.08, 0.24, 0.14, (0.34, 0.16, 0.72), 1.4),  # Deep Indigo Ridge
        (-0.18,  0.06,  0.06, 0.20, 0.12, (0.86, 0.22, 0.58), 1.8),  # Ionized Magenta Core
        ( 0.02, -0.02,  0.00, 0.22, 0.13, (0.16, 0.72, 0.88), 2.1),  # Cyan-Teal Nursery Cavity
        ( 0.22, -0.10, -0.06, 0.23, 0.14, (0.94, 0.54, 0.22), 2.4),  # Golden Amber Dust Pillar
        ( 0.38, -0.18,  0.08, 0.22, 0.13, (0.48, 0.24, 0.82), 2.7),  # Violet Outer Veil
        (-0.08, -0.16,  0.12, 0.18, 0.10, (0.22, 0.84, 0.76), 2.3),  # Emerald-Cyan Wisp
        ( 0.12,  0.16, -0.12, 0.19, 0.11, (0.92, 0.32, 0.64), 2.5),  # Rose Emission Cloud
    ]

    for lx, ly, lz, sx, sy, col, t_start in lobes:
        nl = 4800
        u = rng.normal(0.0, 1.0, nl)
        v = rng.normal(0.0, 1.0, nl)
        w = rng.normal(0.0, 1.0, nl)
        swirl = 0.065 * np.sin(3.2 * u + 2.4 * v)
        x = lx + u * sx + swirl
        y = ly + v * sy - 0.38 * u * sx + 0.045 * np.cos(2.8 * w)
        z = lz + w * (sx * 0.75) + swirl * 0.8

        dist = np.sqrt(u * u + v * v + w * w)
        fade = np.exp(-0.32 * dist * dist)
        add(
            x, y, z,
            col[0] + rng.uniform(-0.05, 0.05, nl),
            col[1] + rng.uniform(-0.05, 0.05, nl),
            col[2] + rng.uniform(-0.05, 0.05, nl),
            t_start + np.clip(dist * 0.55, 0.0, 1.8),
            0.22 * fade,
            1
        )

    # 3. EMBEDDED OPEN STAR CLUSTERS & PROTOSTARS (8,500 bright points)
    n_cl = 8500
    rad_c = np.abs(rng.normal(0.0, 0.24, n_cl))
    ang_c = rng.uniform(0.0, TAU, n_cl)
    inc_c = rng.normal(0.0, 0.11, n_cl)
    cx = rad_c * np.cos(ang_c) * 1.35
    cy = rad_c * np.sin(ang_c) * 0.55 - 0.32 * cx + inc_c
    cz = rad_c * np.sin(ang_c) * 0.85

    is_hot_blue = rng.random(n_cl) < 0.48
    add(
        cx, cy, cz,
        np.where(is_hot_blue, 0.68, 1.00),
        np.where(is_hot_blue, 0.88, 0.88),
        np.where(is_hot_blue, 1.00, 0.62),
        rng.uniform(2.2, 4.6, n_cl),
        rng.uniform(0.55, 1.25, n_cl),
        2
    )

    # 4. SPIRALING ACCRETION RIBBON AROUND THE BINARY HEART (4,500 points)
    n_acc = 4500
    t_a = rng.random(n_acc)
    arm = rng.integers(0, 2, n_acc)
    ang_a = arm * np.pi + t_a * 4.6 + rng.normal(0.0, 0.18, n_acc)
    r_a = 0.075 + t_a * 0.26 + rng.normal(0.0, 0.014, n_acc)
    ax = r_a * np.cos(ang_a)
    ay = rng.normal(0.0, 0.012, n_acc) + 0.015 * np.sin(ang_a * 2.0)
    az = r_a * np.sin(ang_a)
    add(
        ax, ay, az,
        1.0 - 0.45 * t_a,
        0.78 + 0.12 * t_a,
        0.42 + 0.56 * t_a,
        3.4 + t_a * 1.4,
        0.52 * (1.0 - 0.45 * t_a),
        3
    )

    all_x = np.concatenate(px)
    return {
        "x": all_x,
        "y": np.concatenate(py),
        "z": np.concatenate(pz),
        "r": np.concatenate(cr),
        "g": np.concatenate(cg),
        "b": np.concatenate(cb),
        "birth": np.concatenate(birth),
        "weight": np.concatenate(weight),
        "kind": np.concatenate(kind),
        "phase": rng.uniform(0.0, TAU, len(all_x)).astype(np.float32),
        "n_total": len(all_x),
    }


def render_cosmos(buf, data, t, yaw, pitch, warp_z, shock_t, cw, ch):
    buf.fill(0.0)
    alive = data["birth"] <= t
    if not np.any(alive):
        return 0

    age = t - data["birth"][alive]
    reveal = smooth(age / 1.1)

    px = data["x"][alive].copy()
    py = data["y"][alive].copy()
    pz = data["z"][alive].copy()
    ph = data["phase"][alive]
    knd = data["kind"][alive]
    w_base = data["weight"][alive] * reveal

    # Rotate central accretion ribbon (kind == 3)
    is_acc = knd == 3
    if np.any(is_acc):
        ca_s, sa_s = np.cos(0.65 * t), np.sin(0.65 * t)
        ax, az = px[is_acc], pz[is_acc]
        px[is_acc] = ax * ca_s - az * sa_s
        pz[is_acc] = ax * sa_s + az * ca_s

    # Gentle warp-flight z-loop on background stars when warp mode is active
    is_bg = knd == 0
    if warp_z != 0.0 and np.any(is_bg):
        pz[is_bg] = ((pz[is_bg] + warp_z + 1.1) % 2.2) - 1.1

    # 3D Camera Orbit Rotation (using cos_y, sin_y to avoid collision with screen sy)
    cos_y, sin_y = float(np.cos(yaw)), float(np.sin(yaw))
    x1 = px * cos_y + pz * sin_y
    z1 = -px * sin_y + pz * cos_y

    cos_p, sin_p = float(np.cos(pitch)), float(np.sin(pitch))
    y2 = py * cos_p - z1 * sin_p
    z2 = py * sin_p + z1 * cos_p

    cam_dist = 1.45
    depth = z2 + cam_dist
    valid_z = depth > 0.22
    inv_d = np.where(valid_z, 1.0 / np.maximum(depth, 0.22), 0.0)
    focal = ch * 1.18

    sx = np.round(x1 * inv_d * focal + cw * 0.5).astype(np.int32)
    sy = np.round(y2 * inv_d * focal + ch * 0.5).astype(np.int32)

    valid = valid_z & (sx >= 2) & (sx < cw - 2) & (sy >= 2) & (sy < ch - 2)
    sx = sx[valid]
    sy = sy[valid]
    k_v = knd[valid]
    ph_v = ph[valid]

    twinkle = np.where((k_v == 0) | (k_v == 2), 0.72 + 0.34 * np.sin(2.6 * t + ph_v), 1.0)
    w_v = w_base[valid] * twinkle * np.clip(1.25 - 0.32 * depth[valid], 0.25, 1.35)

    r_v = data["r"][alive][valid] * w_v
    g_v = data["g"][alive][valid] * w_v
    b_v = data["b"][alive][valid] * w_v

    np.add.at(buf[:, :, 0], (sx, sy), r_v)
    np.add.at(buf[:, :, 1], (sx, sy), g_v)
    np.add.at(buf[:, :, 2], (sx, sy), b_v)

    # Soft 2x2 volumetric splat on nebula gas particles (kind == 1) for cloudy depth
    gas = k_v == 1
    if np.any(gas):
        gx, gy = sx[gas], sy[gas]
        gr, gg, gb = r_v[gas] * 0.55, g_v[gas] * 0.55, b_v[gas] * 0.55
        for ox, oy in ((1, 0), (0, 1), (1, 1)):
            np.add.at(buf[:, :, 0], (gx + ox, gy + oy), gr)
            np.add.at(buf[:, :, 1], (gx + ox, gy + oy), gg)
            np.add.at(buf[:, :, 2], (gx + ox, gy + oy), gb)

    # --- ORBITING BINARY STARS + PLASMA BRIDGE + DIFFRACTION SPIKES ---
    star_vis = float(smooth((t - 3.6) / 1.4))
    if star_vis > 0.01:
        orb_a = 0.85 * t
        sep = 0.068 * star_vis
        stars_3d = [
            (float(np.cos(orb_a) * sep),  float(0.012 * np.sin(orb_a)), float(np.sin(orb_a) * sep), (0.45, 0.88, 1.00), 1.05),
            (float(-np.cos(orb_a) * sep), float(-0.012 * np.sin(orb_a)), float(-np.sin(orb_a) * sep), (1.00, 0.82, 0.38), 1.00),
        ]

        # Plasma bridge points between the two stars
        for u_b in np.linspace(-1.0, 1.0, 48):
            u_val = float(u_b)
            bx_b = float(np.cos(orb_a)) * sep * u_val
            by_b = float(0.012 * np.sin(orb_a)) * u_val + float(0.010 * np.sin(u_val * np.pi + t * 4.0))
            bz_b = float(np.sin(orb_a)) * sep * u_val
            x_b = bx_b * cos_y + bz_b * sin_y
            z_b = -bx_b * sin_y + bz_b * cos_y
            y_b2 = by_b * cos_p - z_b * sin_p
            z_b2 = by_b * sin_p + z_b * cos_p
            d_b = z_b2 + cam_dist
            if d_b > 0.25:
                px_b = int(round(x_b / d_b * focal + cw * 0.5))
                py_b = int(round(y_b2 / d_b * focal + ch * 0.5))
                if 2 <= px_b < cw - 2 and 2 <= py_b < ch - 2:
                    t_mix = 0.5 * (u_val + 1.0)
                    br = (0.45 * (1.0 - t_mix) + 1.00 * t_mix) * 0.45 * star_vis
                    bg = (0.88 * (1.0 - t_mix) + 0.82 * t_mix) * 0.45 * star_vis
                    bb = (1.00 * (1.0 - t_mix) + 0.38 * t_mix) * 0.45 * star_vis
                    buf[px_b - 1:px_b + 2, py_b - 1:py_b + 2, 0] += br
                    buf[px_b - 1:px_b + 2, py_b - 1:py_b + 2, 1] += bg
                    buf[px_b - 1:px_b + 2, py_b - 1:py_b + 2, 2] += bb

        for bx0, by0, bz0, scol, s_mag in stars_3d:
            x_s = bx0 * cos_y + bz0 * sin_y
            z_s = -bx0 * sin_y + bz0 * cos_y
            y_s2 = by0 * cos_p - z_s * sin_p
            z_s2 = by0 * sin_p + z_s * cos_p
            d_s = z_s2 + cam_dist
            if d_s <= 0.25:
                continue
            cx0 = int(round(x_s / d_s * focal + cw * 0.5))
            cy0 = int(round(y_s2 / d_s * focal + ch * 0.5))
            rad = 26
            x0, x1 = max(0, cx0 - rad), min(cw, cx0 + rad + 1)
            y0, y1 = max(0, cy0 - rad), min(ch, cy0 + rad + 1)
            if x1 <= x0 or y1 <= y0:
                continue
            gx_g, gy_g = np.meshgrid(np.arange(x0, x1) - cx0, np.arange(y0, y1) - cy0, indexing="ij")
            r2 = gx_g * gx_g + gy_g * gy_g
            core = np.exp(-r2 / 10.0) * 1.35 * star_vis * s_mag
            halo = np.exp(-r2 / 140.0) * 0.42 * star_vis * s_mag
            spike_x = np.exp(-(gy_g * gy_g) / 1.6) * np.exp(-np.abs(gx_g) / 11.0) * 0.85 * star_vis
            spike_y = np.exp(-(gx_g * gx_g) / 1.6) * np.exp(-np.abs(gy_g) / 11.0) * 0.85 * star_vis
            tot = core + halo + spike_x + spike_y

            buf[x0:x1, y0:y1, 0] += tot * scol[0] + core * 0.55
            buf[x0:x1, y0:y1, 1] += tot * scol[1] + core * 0.55
            buf[x0:x1, y0:y1, 2] += tot * scol[2] + core * 0.55

    # --- SUPERNOVA / PULSAR SHOCKWAVE RING (Triggered at t=4.8s or Right-Click) ---
    if 0.0 <= shock_t < 2.2:
        ring_r = (0.04 + shock_t * 0.34) * focal / cam_dist
        ring_fade = float(np.exp(-shock_t * 1.65) * 0.75)
        n_ring = 420
        ang_r = np.linspace(0.0, TAU, n_ring, endpoint=False)
        rx = np.round(cw * 0.5 + np.cos(ang_r) * ring_r).astype(np.int32)
        ry = np.round(ch * 0.5 + np.sin(ang_r) * ring_r * (0.45 + 0.55 * abs(cos_p))).astype(np.int32)
        ok = (rx >= 1) & (rx < cw - 1) & (ry >= 1) & (ry < ch - 1)
        rx, ry = rx[ok], ry[ok]
        np.add.at(buf[:, :, 0], (rx, ry), ring_fade * 0.65)
        np.add.at(buf[:, :, 1], (rx, ry), ring_fade * 0.90)
        np.add.at(buf[:, :, 2], (rx, ry), ring_fade * 1.00)

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
    audio = CosmicAudio()
    audio.start()

    W, H = 1480, 860
    SIM_W, SIM_H = 740, 430

    info = pygame.display.Info()
    k = min(0.92 * info.current_h / H, 0.95 * info.current_w / W)
    win_size = (int(W * k), int(H * k))

    window = pygame.display.set_mode(win_size)
    pygame.display.set_caption("Galactic Star Nursery — Kobsi · 2026")
    screen = pygame.Surface((W, H))
    sim_surf = pygame.Surface((SIM_W, SIM_H))
    accum_buf = np.zeros((SIM_W, SIM_H, 3), dtype=np.float32)

    data = generate_universe()

    mono_name = "consolas,menlo,dejavusansmono,couriernew,monospace"
    f_hud = pygame.font.SysFont(mono_name, 16)
    f_title = pygame.font.SysFont("georgia,timesnewroman,serif", 22, italic=True)

    clock = pygame.time.Clock()
    t = 0.0
    paused = False
    fullscreen = False
    ignited = False
    warp_active = False
    warp_z = 0.0
    shock_t = -1.0
    user_yaw = 0.0
    user_pitch = 0.14
    fps_smooth = 60.0

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    paused = not paused
                    if audio.enabled and not audio.muted:
                        pygame.mixer.pause() if paused else pygame.mixer.unpause()
                elif e.key == pygame.K_m:
                    audio.set_muted(not audio.muted)
                elif e.key == pygame.K_w:
                    warp_active = not warp_active
                elif e.key == pygame.K_r:
                    t = 0.0
                    ignited = False
                    shock_t = -1.0
                    warp_z = 0.0
                    user_yaw = 0.0
                    user_pitch = 0.14
                elif e.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        di = pygame.display.Info()
                        win_size = (di.current_w, di.current_h)
                        window = pygame.display.set_mode(win_size, pygame.FULLSCREEN)
                    else:
                        win_size = (int(W * k), int(H * k))
                        window = pygame.display.set_mode(win_size)
                elif e.key == pygame.K_s:
                    pygame.image.save(screen, str(Path(__file__).with_name(f"galactic_nursery_{int(time.time())}.png")))

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                shock_t = 0.0
                audio.trigger_burst()

        if pygame.mouse.get_pressed()[0]:
            mdx, mdy = pygame.mouse.get_rel()
            user_yaw += mdx * 0.007
            user_pitch = float(np.clip(user_pitch + mdy * 0.005, -1.15, 1.15))
        else:
            pygame.mouse.get_rel()

        dt = clock.tick(60) / 1000.0
        if dt > 0:
            fps_smooth = 0.88 * fps_smooth + 0.12 * (1.0 / dt)

        if not paused:
            step_dt = min(dt, 1.0 / 20.0)
            t += step_dt
            if t >= IGNITE and not ignited:
                ignited = True
                shock_t = 0.0
                audio.trigger_burst()
            if shock_t >= 0.0:
                shock_t += step_dt
            if warp_active:
                warp_z += step_dt * 0.42

        auto_yaw = 0.12 * t + user_yaw
        active_pts = render_cosmos(accum_buf, data, t, auto_yaw, user_pitch, warp_z, shock_t, SIM_W, SIM_H)

        rgb_u8 = np.clip(accum_buf * 255.0, 0, 255).astype(np.uint8)
        pygame.surfarray.blit_array(sim_surf, rgb_u8)

        pygame.transform.smoothscale(sim_surf, (W, H), screen)
        screen.blit(bloom_pass(screen, 5, 10, 0.42), (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(bloom_pass(screen, 10, 24, 0.28), (0, 0), special_flags=pygame.BLEND_ADD)

        # Kobsi · 2026 Studio HUD
        if t > 0.3:
            screen.blit(f_hud.render("Kobsi · 2026", True, (176, 206, 232)), (44, H - 86))
            screen.blit(
                f_hud.render(
                    f"stars {active_pts:05,d}   warp {'on' if warp_active else 'off'}   fps {fps_smooth:04.1f}",
                    True,
                    (118, 152, 184),
                ),
                (44, H - 62),
            )
            screen.blit(
                f_hud.render(
                    "drag orbit 3D · right-click pulsar shockwave · [W] star warp · [M] mute",
                    True,
                    (92, 118, 146),
                ),
                (44, H - 38),
            )
            title_surf = f_title.render("Galactic Star Nursery", True, (206, 226, 246))
            screen.blit(title_surf, (W - 44 - title_surf.get_width(), 32))

        window.blit(screen if win_size == (W, H) else pygame.transform.smoothscale(screen, win_size), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    sys.exit(main())