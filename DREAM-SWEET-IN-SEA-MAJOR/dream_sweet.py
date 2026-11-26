# Dream Sweet in Sea Major — Kobsi · 2026
# Kobsi · @Kobsi17 · 2026. Free for learning and personal projects. See LICENSE.txt.
# Don't repost it or sell it as your own, and don't use it to train AI models.
import math
import sys
import time
from pathlib import Path

import numpy as np
import pygame

SIGN = "Kobsi · 2026"
TITLE = "Hawaii: Part II — Dream Sweet in Sea Major — Kobsi · 2026"
TAU = np.pi * 2.0


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


# --- Synthesized "Dream Sweet in Sea Major" 3/4 Celesta Waltz & Ocean Surf ---
class DreamSweetAudio:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.loop_sound = None
        self.star_chime = None
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.enabled = True
            self._build()
        except Exception:
            self.enabled = False

    def _build(self):
        sr = 44100
        rng = np.random.default_rng(2026)

        # 16 bars of 3/4 waltz = 48 beats @ 112 BPM (~25.71s seamless musical phrase)
        bpm = 112.0
        beat = 60.0 / bpm
        total_beats = 48.0
        dur = total_beats * beat
        n = int(sr * dur)
        tt = np.arange(n, dtype=np.float32) / sr

        # Soft rolling ocean waves with dual-layer surf swell
        white = rng.normal(0.0, 1.0, n).astype(np.float32)
        surf_low = np.convolve(white, np.ones(260, dtype=np.float32) / 260.0, mode="same")
        surf_foam = np.convolve(white, np.ones(65, dtype=np.float32) / 65.0, mode="same")
        swell = 0.55 + 0.45 * np.sin(TAU * (3.0 / dur) * tt)
        buf = surf_low * (0.042 * swell) + surf_foam * (0.012 * (swell ** 2))

        # Warm lush string/organ pad underneath the waltz (Fmaj7 -> Em7 -> Dm7 -> Cmaj7)
        chords = [
            (0,  12, [41, 53, 60, 64, 69]),  # Fmaj7 ("Alone at the edge...")
            (12, 12, [40, 52, 59, 64, 67]),  # Em7   ("...of a universe...")
            (24, 12, [38, 50, 57, 60, 65]),  # Dm7   ("...humming a tune...")
            (36, 12, [36, 48, 55, 60, 64]),  # Cmaj7 ("...dreaming we were snow...")
        ]
        for b0, blen, notes in chords:
            i0 = int(b0 * beat * sr)
            i1 = min(n, int((b0 + blen) * beat * sr))
            seg_t = np.arange(i1 - i0, dtype=np.float32) / sr
            pad_env = np.sin(np.pi * np.clip(seg_t / (blen * beat), 0.0, 1.0)) ** 0.60
            for idx_n, m in enumerate(notes):
                f = 440.0 * (2.0 ** ((m - 69) / 12.0))
                vibrato = 1.0 + 0.0018 * np.sin(TAU * 4.2 * seg_t + idx_n)
                amp = 0.026 if idx_n == 0 else 0.021
                buf[i0:i1] += np.sin(TAU * f * vibrato * seg_t) * pad_env * amp

        # "Dream Sweet in Sea Major" 3/4 celesta & music-box melody
        melody = [
            # Phrase 1: "A - lone at the edge of a u - ni - verse hum - ming a tune"
            (69, 0.0, 1.0), (72, 1.0, 2.0), (76, 3.0, 2.0), (74, 5.0, 1.0),
            (72, 6.0, 1.0), (71, 7.0, 1.0), (72, 8.0, 1.0), (74, 9.0, 2.0), (67, 11.0, 1.0),
            # Phrase 2: "For mere - ly dream - ing we were snow"
            (69, 12.0, 1.0), (72, 13.0, 2.0), (77, 15.0, 2.0), (76, 17.0, 1.0),
            (74, 18.0, 2.0), (72, 20.0, 1.0), (71, 21.0, 3.0),
            # Phrase 3: "A si - ren sounds like the god - dess who pro - mi - ses"
            (72, 24.0, 1.0), (76, 25.0, 2.0), (79, 27.0, 2.0), (77, 29.0, 1.0),
            (76, 30.0, 1.0), (74, 31.0, 1.0), (76, 32.0, 1.0), (77, 33.0, 2.0), (72, 35.0, 1.0),
            # Phrase 4: "End - less a - po - lo - gies of pa - ra - dise"
            (74, 36.0, 1.0), (76, 37.0, 2.0), (74, 39.0, 1.0), (72, 40.0, 1.0), (71, 41.0, 1.0),
            (72, 42.0, 2.0), (67, 44.0, 1.0), (69, 45.0, 3.0),
        ]

        for midi, b_start, b_len in melody:
            i0 = int(b_start * beat * sr)
            ring = min(n - i0, int(sr * (b_len * beat + 1.8)))
            tm = np.arange(ring, dtype=np.float32) / sr
            f = 440.0 * (2.0 ** ((midi - 69) / 12.0))
            env = np.exp(-tm * 1.65) * (1.0 - np.exp(-tm * 150.0))
            celesta = (
                0.72 * np.sin(TAU * f * tm)
                + 0.20 * np.sin(TAU * f * 2.0 * tm) * np.exp(-tm * 4.5)
                + 0.08 * np.sin(TAU * f * 4.0 * tm) * np.exp(-tm * 10.5)
            )
            buf[i0:i0 + ring] += celesta * env * 0.092

        # Gentle 3/4 waltz harp arpeggio
        waltz_bars = [
            (41, 60, 64), (41, 60, 64), (41, 60, 64), (41, 60, 64),
            (40, 59, 64), (40, 59, 64), (40, 59, 64), (40, 59, 64),
            (38, 57, 62), (38, 57, 62), (38, 57, 62), (38, 57, 62),
            (36, 55, 60), (36, 55, 60), (36, 55, 60), (36, 55, 60),
        ]
        for bar_idx, (b1, b2, b3) in enumerate(waltz_bars):
            for sub_b, m_note, amp in ((0.0, b1, 0.052), (1.0, b2, 0.035), (2.0, b3, 0.035)):
                i0 = int((bar_idx * 3.0 + sub_b) * beat * sr)
                ring = min(n - i0, int(sr * 1.25))
                tm = np.arange(ring, dtype=np.float32) / sr
                f = 440.0 * (2.0 ** ((m_note - 69) / 12.0))
                env = np.exp(-tm * 2.4) * (1.0 - np.exp(-tm * 110.0))
                tone = 0.85 * np.sin(TAU * f * tm) + 0.15 * np.sin(TAU * f * 2.0 * tm) * np.exp(-tm * 5.0)
                buf[i0:i0 + ring] += tone * env * amp

        fade = np.linspace(0.0, 1.0, int(sr * 0.35), dtype=np.float32)
        buf[:len(fade)] *= fade
        buf[-len(fade):] *= fade[::-1]

        left = np.clip(buf * 32767, -32767, 32767).astype(np.int16)
        right = np.roll(left, 440)
        self.loop_sound = pygame.sndarray.make_sound(np.column_stack((left, right)))

        # Shooting-star crystalline chime
        c_n = int(sr * 2.4)
        chime = np.zeros(c_n, dtype=np.float32)
        for idx, f in enumerate([659.25, 880.0, 1046.5, 1318.5, 1567.98, 2093.0]):
            d = int(idx * 0.058 * sr)
            tc = np.arange(c_n - d, dtype=np.float32) / sr
            chime[d:] += np.sin(TAU * f * tc) * np.exp(-tc * 2.2) * (1.0 - np.exp(-tc * 150.0)) * 0.072
        ci16 = np.clip(chime * 32767, -32767, 32767).astype(np.int16)
        self.star_chime = pygame.sndarray.make_sound(np.column_stack((ci16, np.roll(ci16, 220))))

    def start(self):
        if self.enabled and self.loop_sound is not None:
            self.loop_sound.play(loops=-1)

    def play_star(self):
        if self.enabled and not self.muted and self.star_chime is not None:
            self.star_chime.play()

    def set_muted(self, mute_state):
        self.muted = mute_state
        if self.enabled and self.loop_sound is not None:
            self.loop_sound.set_volume(0.0 if self.muted else 1.0)


# --- Analytical Sky, Drifting Clouds, Volumetric God-Rays & Fresnel Ocean ---
class BackdropShader:
    def __init__(self, sh_w, sh_h):
        self.sw = sh_w
        self.sh = sh_h
        yy, xx = np.mgrid[0:sh_h, 0:sh_w].astype(np.float32)
        self.nx = xx / sh_w
        self.ny = yy / sh_h
        self.aspect = sh_w / sh_h

        rng = np.random.default_rng(17)
        self.grain = rng.uniform(-0.008, 0.008, size=(sh_h, sh_w)).astype(np.float32)

    def render(self, surf, t, user_yaw, user_pitch, wave_pulse):
        horizon_y = float(np.clip(0.565 + user_pitch * 0.30, 0.42, 0.70))
        cam_shift_x = user_yaw * 0.28

        is_sky = self.ny < horizon_y
        sky_h = np.clip((horizon_y - self.ny) / max(horizon_y, 0.05), 0.0, 1.0)

        # Base vertical gradient: deep obsidian zenith -> misty silver-slate horizon
        base_lum = np.where(
            is_sky,
            0.028 + 0.21 * ((1.0 - sky_h) ** 2.5),
            0.020 + 0.055 * np.exp(-((self.ny - horizon_y) / 0.055) ** 2),
        )

        # Drifting atmospheric night clouds across the upper sky
        cloud_vis = smooth(t / 2.6)
        if cloud_vis > 0.001:
            cx = self.nx * 4.2 + cam_shift_x * 0.6 + t * 0.018
            cy = self.ny * 8.5
            clouds = (
                0.50 * np.sin(cx * 2.1 + np.cos(cy * 1.4))
                + 0.30 * np.cos(cx * 4.3 - cy * 2.2 + t * 0.03)
                + 0.20 * np.sin(cx * 7.8 + cy * 3.9 - t * 0.02)
            )
            clouds = np.clip(clouds * 0.5 + 0.5, 0.0, 1.0) ** 1.8
            cloud_band = np.exp(-((self.ny - (horizon_y - 0.16)) / 0.22) ** 2)
            base_lum += cloud_vis * is_sky * clouds * cloud_band * 0.085

        # Volumetric diagonal god-rays slanting down from top-left (cover-art signature)
        ray_vis = smooth((t - 1.2) / 2.4)
        if ray_vis > 0.001:
            diag = (self.nx - 0.02 - cam_shift_x * 0.4) - (self.ny - 0.02) * 0.78
            b1 = np.exp(-((diag - 0.12) / 0.080) ** 2)
            b2 = 0.82 * np.exp(-((diag - 0.27) / 0.055) ** 2)
            b3 = 0.65 * np.exp(-((diag + 0.04) / 0.068) ** 2)
            b4 = 0.45 * np.exp(-((diag - 0.40) / 0.045) ** 2)
            b5 = 0.30 * np.exp(-((diag - 0.52) / 0.038) ** 2)
            falloff = np.exp(-(self.nx * 0.72 + self.ny * 1.12))
            shimmer = 0.88 + 0.12 * np.sin(17.0 * diag - 0.52 * t)
            rays = ray_vis * is_sky * falloff * shimmer * (b1 + b2 + b3 + b4 + b5) * 0.36
            base_lum += rays

        # Full Moon + Lunar Maria + Atmospheric Corona (Upper Right)
        moon_vis = smooth(t / 2.2)
        mx = 0.655 - cam_shift_x * 0.65
        my = horizon_y - 0.335
        dx_m = (self.nx - mx) * self.aspect
        dy_m = self.ny - my
        dist_m = np.hypot(dx_m, dy_m)
        moon_r = 0.094

        # Multi-layered soft lunar corona
        halo = moon_vis * is_sky * (
            0.28 * np.exp(-(dist_m / 0.22) ** 2)
            + 0.14 * np.exp(-(dist_m / 0.46) ** 2)
        )
        base_lum += halo

        # Crisp moon disc with detailed maria & crater relief
        in_moon = dist_m <= moon_r
        if np.any(in_moon):
            u_m = dx_m / moon_r
            v_m = dy_m / moon_r
            maria = (
                0.11 * np.sin(u_m * 4.0 + 0.6) * np.cos(v_m * 3.6 - 0.4)
                + 0.08 * np.cos((u_m - v_m) * 7.2 + 0.3)
                + 0.05 * np.sin((u_m + v_m) * 13.0)
                + 0.03 * np.cos(u_m * 19.0 - v_m * 16.0)
            )
            limb = np.sqrt(np.clip(1.0 - (dist_m / moon_r) ** 2, 0.0, 1.0)) ** 0.24
            moon_disc = moon_vis * np.clip((0.92 + maria) * limb, 0.66, 1.04)
            base_lum = np.where(in_moon, np.maximum(base_lum, moon_disc), base_lum)

        # Continuous Fresnel Ocean Waves & Shimmering Moonlight Path
        sea_vis = smooth((t - 0.5) / 2.2)
        if sea_vis > 0.001:
            sea_depth = np.clip((self.ny - horizon_y) / max(1.0 - horizon_y, 0.05), 0.002, 1.0)
            z_persp = 1.0 / (sea_depth + 0.042)
            x_persp = (self.nx - 0.5 + cam_shift_x) * z_persp * 0.44

            w1 = np.sin(x_persp * 6.8 + z_persp * 2.5 - 1.45 * t)
            w2 = np.cos(x_persp * 11.5 - z_persp * 3.2 - 1.85 * t)
            w3 = np.sin(z_persp * 4.8 - 2.25 * t + 1.25 * np.sin(x_persp * 3.1))
            wave_slope = 0.44 * w1 + 0.34 * w2 + 0.56 * w3

            if wave_pulse > 0.01:
                r_p = np.hypot((self.nx - 0.48) * self.aspect, (self.ny - 0.74) * 1.8)
                ring_r = (1.0 - wave_pulse) * 0.98
                wave_slope += 1.65 * wave_pulse * np.exp(-((r_p - ring_r) / 0.052) ** 2) * np.sin(46.0 * (r_p - ring_r))

            # Moonlight specular path under the upper-right moon
            moon_col_dist = np.abs(self.nx - mx)
            path_width = 0.048 + 0.145 * sea_depth
            moon_path = np.exp(-((moon_col_dist / path_width) ** 2))
            specular = np.clip(wave_slope, 0.0, 1.9) ** 1.75
            glitter = (np.clip(wave_slope, 0.0, 1.8) ** 4.2) * moon_path * 0.38

            horizon_glow = np.exp(-((self.ny - horizon_y) / 0.005) ** 2) * 0.34
            # Soft horizon sea mist
            sea_mist = np.exp(-((self.ny - horizon_y) / 0.032) ** 2) * 0.065
            ocean_lum = sea_vis * (
                0.018
                + horizon_glow
                + sea_mist
                + (0.040 + 0.24 * moon_path) * specular * (0.35 + 0.65 * sea_depth)
                + glitter
            )
            base_lum = np.where(~is_sky, ocean_lum, base_lum)

        # Painterly silver-slate monochrome with subtle lunar blue-indigo undertone
        lum = np.clip(base_lum + self.grain, 0.0, 1.0)
        rgb = np.empty((self.sh, self.sw, 3), dtype=np.uint8)
        rgb[..., 0] = np.clip(lum * 228.0, 0, 255).astype(np.uint8)
        rgb[..., 1] = np.clip(lum * 238.0, 0, 255).astype(np.uint8)
        rgb[..., 2] = np.clip(lum * 254.0, 0, 255).astype(np.uint8)

        small_surf = pygame.surfarray.make_surface(rgb.transpose(1, 0, 2))
        pygame.transform.smoothscale(small_surf, surf.get_size(), surf)
        return horizon_y, cam_shift_x, (mx, my)


# --- Painterly Foreground: Island, Palms, Orca, Ghostly Anglerfish, Snow & 3D Escher Staircase ---
class PaintedElements:
    def __init__(self):
        rng = np.random.default_rng(2026)

        # 1. Crisp Stars & Drifting Snow/Motes ("For merely dreaming we were snow")
        n_stars = 280
        self.star_nx = rng.uniform(0.01, 0.99, n_stars)
        self.star_ny = rng.uniform(0.01, 0.54, n_stars)
        self.star_r = rng.choice([1, 1, 1, 2], size=n_stars)
        self.star_ph = rng.uniform(0.0, TAU, n_stars)

        n_motes = 130
        self.mote_nx = rng.uniform(0.02, 0.95, n_motes)
        self.mote_ny = rng.uniform(0.03, 0.88, n_motes)
        self.mote_sp = rng.uniform(0.008, 0.024, n_motes)
        self.mote_ph = rng.uniform(0.0, TAU, n_motes)

        # 2. Precompute 20 Sculpted 3D Escher Stair Slabs rising out of the sea mist
        self.slabs = []
        n_slabs = 20
        for k in range(n_slabs):
            frac = k / (n_slabs - 1)  # 0 = foreground bottom-right, 1 = high skyward left
            cx = 0.28 - frac * 1.18 + 0.08 * math.sin(frac * 3.1)
            cy = -0.38 + frac * 0.42
            cz = -0.58 + frac * 1.55
            twist = -0.52 + frac * 0.72 + 0.16 * math.sin(frac * 5.0)
            w = 0.46 - frac * 0.15
            d = 0.12
            h = 0.034

            ct, st = math.cos(twist), math.sin(twist)
            corners_local = [
                (-w * 0.5, 0.0, -d * 0.5),  # 0: front-left top
                ( w * 0.5, 0.0, -d * 0.5),  # 1: front-right top
                ( w * 0.5, 0.0,  d * 0.5),  # 2: back-right top
                (-w * 0.5, 0.0,  d * 0.5),  # 3: back-left top
                (-w * 0.5,  -h, -d * 0.5),  # 4: front-left bottom
                ( w * 0.5,  -h, -d * 0.5),  # 5: front-right bottom
                ( w * 0.5,  -h,  d * 0.5),  # 6: back-right bottom
                (-w * 0.5,  -h,  d * 0.5),  # 7: back-left bottom
            ]
            pts3d = []
            for lx, ly, lz in corners_local:
                wx = cx + lx * ct - lz * st
                wz = cz + lx * st + lz * ct
                wy = cy + ly
                pts3d.append((wx, wy, wz))
            self.slabs.append((frac, pts3d))

    def draw_stars_and_snow(self, screen, t, horizon_y, cam_shift_x, shoot_timer):
        w, h = screen.get_size()
        sky_vis = smooth(t / 2.2)
        if sky_vis <= 0.01:
            return

        for i in range(len(self.star_nx)):
            if self.star_ny[i] >= horizon_y - 0.01:
                continue
            sx = int(((self.star_nx[i] - cam_shift_x * 0.35) % 1.0) * w)
            sy = int(self.star_ny[i] * h)
            tw = (0.48 + 0.52 * math.sin(1.85 * t + self.star_ph[i])) * sky_vis
            val = max(0, min(255, int(245 * tw)))
            r = int(self.star_r[i])
            if r == 1:
                screen.set_at((sx, sy), (val, val, min(255, val + 12)))
            else:
                pygame.draw.circle(screen, (val, val, min(255, val + 14)), (sx, sy), 2)
                if tw > 0.84:
                    pygame.draw.line(screen, (val // 2, val // 2, val // 2), (sx - 4, sy), (sx + 4, sy), 1)
                    pygame.draw.line(screen, (val // 2, val // 2, val // 2), (sx, sy - 4), (sx, sy + 4), 1)

        # Floating snow / luminous dust motes drifting softly through the beams
        mote_vis = smooth((t - 1.5) / 2.5)
        if mote_vis > 0.01:
            mote_layer = pygame.Surface((w, h), pygame.SRCALPHA)
            for i in range(len(self.mote_nx)):
                mx = int(((self.mote_nx[i] + 0.015 * math.sin(0.45 * t + self.mote_ph[i]) - cam_shift_x * 0.25) % 1.0) * w)
                my = int(((self.mote_ny[i] + self.mote_sp[i] * t * 0.4) % 1.0) * h)
                tw = 0.25 + 0.75 * (math.sin(1.5 * t + self.mote_ph[i]) ** 2)
                alpha = int(175 * mote_vis * tw)
                if alpha > 12:
                    pygame.draw.circle(mote_layer, (235, 242, 255, alpha), (mx, my), 1)
            screen.blit(mote_layer, (0, 0))

        # Shooting star streak (auto every ~15s or on right-click)
        auto_cycle = (t % 15.0) / 1.35
        s_prog = shoot_timer if shoot_timer >= 0.0 else (auto_cycle if auto_cycle < 1.0 else -1.0)
        if 0.0 <= s_prog <= 1.0:
            hx = int((0.80 - s_prog * 0.58) * w)
            hy = int((0.09 + s_prog * 0.23) * h)
            tx = int((0.80 - max(0.0, s_prog - 0.18) * 0.58) * w)
            ty = int((0.09 + max(0.0, s_prog - 0.18) * 0.23) * h)
            fade = math.sin(math.pi * s_prog)
            col_head = (int(255 * fade), int(250 * fade), int(230 * fade))
            pygame.draw.line(screen, col_head, (tx, ty), (hx, hy), 2)
            pygame.draw.circle(screen, col_head, (hx, hy), 3)

    def draw_ghost_anglerfish(self, screen, t, moon_uv):
        """Draw the ethereal spectral abyssal anglerfish with glowing esca & needle teeth beside the moon."""
        angler_vis = smooth((t - 5.0) / 3.0)
        if angler_vis <= 0.01:
            return
        w, h = screen.get_size()
        layer = pygame.Surface((w, h), pygame.SRCALPHA)

        mx, my = moon_uv
        drift_x = 0.006 * math.cos(0.48 * t)
        drift_y = 0.009 * math.sin(0.62 * t)
        ox = (mx + 0.042 + drift_x) * w
        oy = (my + 0.015 + drift_y) * h
        sc = h / 860.0

        # Smooth organic spectral cranium & gaping jaw (48-point parametric silhouette)
        def smooth_body(scale_pad=1.0):
            pts = []
            # Upper dome from snout around back of head to tail/neck
            for i in range(28):
                u = i / 27.0
                ang = math.pi * (1.05 - u * 1.45)  # ~190 deg to -72 deg
                rx = 152 * scale_pad
                ry = 148 * scale_pad
                cx = ox + 148 * sc
                cy = oy + 14 * sc
                px = cx + math.cos(ang) * rx * sc
                py = cy - math.sin(ang) * ry * sc
                pts.append((int(px), int(py)))
            # Lower jaw curving forward
            for i in range(16):
                u = i / 15.0
                px = ox + (200 - u * 142) * sc
                py = oy + (152 + 34 * math.sin(u * math.pi) - u * 14) * sc
                pts.append((int(px), int(py)))
            # Inner throat curve back to upper jaw
            for i in range(10):
                u = i / 9.0
                px = ox + (110 + 44 * math.sin(u * math.pi)) * sc
                py = oy + (125 - u * 155) * sc
                pts.append((int(px), int(py)))
            return pts

        pygame.draw.polygon(layer, (186, 200, 224, int(18 * angler_vis)), smooth_body(1.06))
        pygame.draw.polygon(layer, (192, 206, 228, int(28 * angler_vis)), smooth_body(1.0))

        # Translucent pectoral fin rays trailing behind
        for r_i in range(7):
            ang = 0.30 + r_i * 0.13 + 0.04 * math.sin(t * 1.3 + r_i)
            fx0, fy0 = ox + 215 * sc, oy + 38 * sc
            fx1 = fx0 + math.cos(ang) * (82 - r_i * 6) * sc
            fy1 = fy0 + math.sin(ang) * (82 - r_i * 6) * sc
            pygame.draw.aaline(layer, (210, 222, 242, int(44 * angler_vis)), (fx0, fy0), (fx1, fy1))

        # Sunken abyssal eye socket
        eye_x, eye_y = int(ox + 132 * sc), int(oy - 62 * sc)
        pygame.draw.circle(layer, (18, 24, 34, int(78 * angler_vis)), (eye_x, eye_y), int(14 * sc))
        pygame.draw.circle(layer, (218, 228, 244, int(60 * angler_vis)), (eye_x, eye_y), int(14 * sc), 1)

        # Gracefully arched illicium (stalk) & glowing bioluminescent esca (lure)
        stalk_pts = []
        sway = 8.0 * sc * math.sin(1.25 * t)
        for j in range(18):
            u = j / 17.0
            sx = ox + (82 - u * 124) * sc + (u ** 1.6) * sway
            sy = oy + (-102 - math.sin(u * math.pi) * 48 + u * 84) * sc
            stalk_pts.append((int(sx), int(sy)))
        pygame.draw.aalines(layer, (220, 234, 250, int(92 * angler_vis)), False, stalk_pts)
        lure_x, lure_y = stalk_pts[-1]
        lure_pulse = 0.72 + 0.28 * math.sin(2.4 * t)
        pygame.draw.circle(layer, (180, 232, 255, int(46 * angler_vis * lure_pulse)), (lure_x, lure_y), int(16 * sc))
        pygame.draw.circle(layer, (240, 250, 255, int(185 * angler_vis * lure_pulse)), (lure_x, lure_y), int(4 * sc))

        # Curved upper & lower needle-tooth rows
        alpha_tooth = int(130 * angler_vis)
        for idx in range(16):
            u = idx / 15.0
            ux = ox + (24 + u * 134) * sc
            uy = oy + (-34 - 16 * math.sin(u * math.pi)) * sc
            t_len = (20 + 25 * math.sin(u * math.pi)) * sc
            tip_ux = ux + (4 + 8 * u) * sc
            tip_uy = uy + t_len
            pygame.draw.polygon(
                layer,
                (238, 244, 252, alpha_tooth),
                [(int(ux - 1.8 * sc), int(uy)), (int(ux + 1.8 * sc), int(uy)), (int(tip_ux), int(tip_uy))],
            )

            lx = ox + (52 + u * 124) * sc
            ly = oy + (136 + 28 * math.sin(u * math.pi)) * sc
            l_len = (20 + 25 * math.sin(u * math.pi)) * sc
            tip_lx = lx - (5 + 6 * u) * sc
            tip_ly = ly - l_len
            pygame.draw.polygon(
                layer,
                (238, 244, 252, alpha_tooth),
                [(int(lx - 1.8 * sc), int(ly)), (int(lx + 1.8 * sc), int(ly)), (int(tip_lx), int(tip_ly))],
            )

        screen.blit(layer, (0, 0))

    def draw_island_and_orca(self, screen, t, horizon_y, cam_shift_x):
        """Draw the dark volcanic headland under the palms and the sleek orca dorsal fin on the horizon."""
        land_vis = smooth((t - 0.9) / 2.2)
        if land_vis <= 0.01:
            return
        w, h = screen.get_size()
        hy = horizon_y * h + 2
        sc = (h / 860.0) * land_vis

        # Distant volcanic island / spit grounding the two palms
        ix = (0.295 - cam_shift_x * 0.72) * w
        island_pts = [
            (ix - 175 * sc, hy + 2),
            (ix - 125 * sc, hy - 14 * sc),
            (ix - 58 * sc, hy - 28 * sc),
            (ix + 10 * sc, hy - 34 * sc),
            (ix + 82 * sc, hy - 22 * sc),
            (ix + 148 * sc, hy - 8 * sc),
            (ix + 195 * sc, hy + 2),
        ]
        pygame.draw.polygon(screen, (8, 10, 15), [(int(x), int(y)) for x, y in island_pts])

        # Sleek curved orca dorsal fin & back crest on the far-left horizon
        fx = (0.115 - cam_shift_x * 0.5) * w
        bob = 2.2 * math.sin(1.25 * t)
        fin_pts = [
            (fx - 42 * sc, hy + 1),
            (fx - 20 * sc, hy - 6 * sc + bob),
            (fx - 6 * sc, hy - 24 * sc + bob),
            (fx + 3 * sc, hy - 44 * sc + bob),
            (fx + 10 * sc, hy - 42 * sc + bob),
            (fx + 6 * sc, hy - 20 * sc + bob),
            (fx + 16 * sc, hy - 8 * sc + bob),
            (fx + 48 * sc, hy + 1),
        ]
        pygame.draw.polygon(screen, (7, 9, 13), [(int(x), int(y)) for x, y in fin_pts])

    def draw_palms(self, screen, t, horizon_y, cam_shift_x):
        """Draw the two tall silhouetted coconut palms rooted on the island."""
        palm_vis = smooth((t - 1.9) / 2.4)
        if palm_vis <= 0.01:
            return
        w, h = screen.get_size()
        sc = h / 860.0
        col_sil = (6, 8, 12)
        base_y = horizon_y - 0.022

        palms = [
            (0.245 - cam_shift_x * 0.72, base_y, 355 * sc * palm_vis, -46 * sc, 1.05 * sc * palm_vis, 0.0),
            (0.345 - cam_shift_x * 0.72, base_y + 0.004, 275 * sc * palm_vis, 28 * sc, 0.85 * sc * palm_vis, 1.7),
        ]

        for bx_n, by_n, trunk_h, lean, f_scale, ph in palms:
            bx = bx_n * w
            by = by_n * h
            sway = 11.0 * sc * math.sin(1.12 * t + ph)

            left_edge, right_edge = [], []
            steps = 22
            for s_i in range(steps + 1):
                u = s_i / steps
                cx = bx + (u ** 1.55) * lean + (u ** 1.4) * sway
                cy = by - u * trunk_h
                half_w = (9.0 * (1.0 - 0.60 * u)) * sc
                left_edge.append((int(cx - half_w), int(cy)))
                right_edge.append((int(cx + half_w), int(cy)))
            pygame.draw.polygon(screen, col_sil, left_edge + right_edge[::-1])

            tip_x = bx + lean + sway
            tip_y = by - trunk_h

            frond_angles = [-2.75, -2.35, -1.95, -1.55, -1.10, -0.65, -0.25, 0.18, 0.58, 2.95, 3.30]
            for idx_f, base_ang in enumerate(frond_angles):
                ang = base_ang + 0.04 * math.sin(1.35 * t + ph + idx_f)
                f_len = (135 + 18 * math.cos(idx_f * 1.7)) * f_scale
                dir_x = math.cos(ang)
                dir_y = math.sin(ang) * 0.65

                spine = []
                for j in range(15):
                    u = j / 14.0
                    px = tip_x + dir_x * f_len * u
                    py = tip_y + dir_y * f_len * u + (u ** 1.85) * 60.0 * f_scale
                    spine.append((px, py))

                pygame.draw.lines(screen, col_sil, False, [(int(x), int(y)) for x, y in spine], max(2, int(3.0 * sc)))

                for j in range(2, 14):
                    u = j / 14.0
                    px, py = spine[j]
                    lf_len = (33.0 * math.sin(u * math.pi) + 7.0) * f_scale
                    hang_x = px + (6.0 if dir_x >= 0 else -6.0) * f_scale
                    hang_y = py + lf_len
                    pygame.draw.line(screen, col_sil, (int(px), int(py)), (int(hang_x), int(hang_y)), max(1, int(2.0 * sc)))

    def draw_staircase(self, screen, t, user_yaw, user_pitch):
        """Render the twisted 3D Escher staircase and its soft water reflection."""
        stair_prog = smooth((t - 3.0) / 3.4)
        if stair_prog <= 0.001:
            return

        w, h = screen.get_size()
        cx_scr, cy_scr = w * 0.5, h * 0.52
        fov = h * 1.12

        yaw = 0.032 * math.sin(0.18 * t) + user_yaw
        pitch = 0.08 + 0.012 * math.cos(0.22 * t) + user_pitch
        cam_y = 0.22
        cam_z = -1.55
        cy, sy = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)

        def proj(pt):
            rx, ry, rz = pt[0], pt[1] - cam_y, pt[2] - cam_z
            x1 = rx * cy + rz * sy
            z1 = -rx * sy + rz * cy
            y2 = ry * cp - z1 * sp
            z2 = ry * sp + z1 * cp
            if z2 <= 0.15:
                return None
            inv = fov / z2
            return (int(cx_scr + x1 * inv), int(cy_scr - y2 * inv)), z2

        refl_layer = pygame.Surface((w, h), pygame.SRCALPHA)

        for frac, pts3d in reversed(self.slabs):
            if frac > stair_prog:
                continue
            bob = 0.005 * math.sin(1.4 * t - frac * 5.0)
            projected = [proj((x, y + bob, z)) for (x, y, z) in pts3d]
            if any(p is None for p in projected):
                continue
            pts2d = [p[0] for p in projected]

            # Misty atmospheric depth fade as steps climb into the night sky
            fade = 1.0 - 0.42 * frac
            top_col = (int(234 * fade), int(239 * fade), int(248 * fade))
            front_col = (int(56 * fade), int(62 * fade), int(74 * fade))
            side_col = (int(32 * fade), int(36 * fade), int(46 * fade))
            edge_col = (int(250 * fade), int(252 * fade), int(255 * fade))

            # Subtle water reflection for lower steps
            if frac < 0.36:
                refl_alpha = int(42 * (1.0 - frac / 0.36))
                refl_pts = [(px, int(py + (h * 0.14))) for (px, py) in pts2d[:4]]
                pygame.draw.polygon(refl_layer, (190, 210, 235, refl_alpha), refl_pts)

            pygame.draw.polygon(screen, side_col, [pts2d[1], pts2d[2], pts2d[6], pts2d[5]])
            pygame.draw.polygon(screen, side_col, [pts2d[0], pts2d[3], pts2d[7], pts2d[4]])
            pygame.draw.polygon(screen, front_col, [pts2d[0], pts2d[1], pts2d[5], pts2d[4]])
            top_poly = [pts2d[0], pts2d[1], pts2d[2], pts2d[3]]
            pygame.draw.polygon(screen, top_col, top_poly)
            pygame.draw.aalines(screen, edge_col, True, top_poly)

        screen.blit(refl_layer, (0, 0))


def bloom_pass(surf, k, radius, amount):
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // k), max(1, h // k)))
    if hasattr(pygame.transform, "gaussian_blur"):
        small = pygame.transform.gaussian_blur(small, max(1, radius // k))
    glow = pygame.transform.smoothscale(small, (w, h))
    val = int(np.clip(amount * 255, 0, 255))
    glow.fill((val, val, val), special_flags=pygame.BLEND_MULT)
    return glow


def draw_album_emblem(screen, f_en, f_jp, alpha_scale):
    """Draw the signature 'HAWAII: PART II' + rainbow 'ミラクルミュージカル' centerpiece."""
    if alpha_scale <= 0.02:
        return
    w, h = screen.get_size()
    cx, cy = w // 2, int(h * 0.515)

    en_surf = f_en.render("HAWAII: PART II", True, (242, 246, 252))
    en_surf.set_alpha(int(240 * alpha_scale))
    screen.blit(en_surf, (cx - en_surf.get_width() // 2, cy - 30))

    jp_text = "ミラクルミュージカル"
    rainbow = [
        (255, 86, 94),
        (255, 152, 68),
        (252, 218, 76),
        (132, 232, 118),
        (68, 224, 198),
        (78, 178, 255),
        (114, 126, 255),
        (162, 108, 255),
        (214, 102, 248),
        (246, 118, 210),
    ]
    glyph_surfs = [f_jp.render(ch, True, rainbow[i % len(rainbow)]) for i, ch in enumerate(jp_text)]
    total_w = sum(g.get_width() for g in glyph_surfs)
    cur_x = cx - total_w // 2
    for g in glyph_surfs:
        g.set_alpha(int(245 * alpha_scale))
        screen.blit(g, (cur_x, cy + 8))
        cur_x += g.get_width()


def main():
    pygame.init()
    audio = DreamSweetAudio()
    audio.start()

    W, H = 1480, 860
    info = pygame.display.Info()
    scale = min(0.93 * info.current_h / H, 0.96 * info.current_w / W)
    win_size = (int(W * scale), int(H * scale))

    window = pygame.display.set_mode(win_size, pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)

    screen = pygame.Surface((W, H))
    shader = BackdropShader(370, 215)
    elements = PaintedElements()

    mono = "consolas,menlo,dejavusansmono,couriernew,monospace"
    f_hud = pygame.font.SysFont(mono, 15)
    f_sign = pygame.font.SysFont(mono, 16, bold=True)
    f_title = pygame.font.SysFont("georgia,timesnewroman,serif", 21, italic=True)
    f_en = pygame.font.SysFont("arial,helvetica,sans-serif", 34, bold=True)
    f_jp = pygame.font.SysFont("meiryo,msgothic,yugothic,arialunicodems,sans-serif", 29, bold=True)

    clock = pygame.time.Clock()
    t = 0.0
    paused = False
    fullscreen = False
    show_emblem = True
    user_yaw = 0.0
    user_pitch = 0.0
    wave_pulse = 0.0
    shoot_timer = -1.0
    stars_triggered = 0

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
                elif e.key == pygame.K_e:
                    show_emblem = not show_emblem
                elif e.key == pygame.K_r:
                    t = 0.0
                    user_yaw, user_pitch = 0.0, 0.0
                    wave_pulse = 0.0
                    shoot_timer = -1.0
                elif e.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        di = pygame.display.Info()
                        win_size = (di.current_w, di.current_h)
                        window = pygame.display.set_mode(win_size, pygame.FULLSCREEN)
                    else:
                        win_size = (int(W * scale), int(H * scale))
                        window = pygame.display.set_mode(win_size, pygame.RESIZABLE)
                elif e.key == pygame.K_s:
                    stamp = time.strftime("%Y%m%d_%H%M%S")
                    pygame.image.save(screen, str(Path(__file__).with_name(f"dream_sweet_{stamp}.png")))
            elif e.type == pygame.VIDEORESIZE and not fullscreen:
                win_size = (e.w, e.h)
                window = pygame.display.set_mode(win_size, pygame.RESIZABLE)

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                wave_pulse = 1.0
                shoot_timer = 0.0
                stars_triggered += 1
                audio.play_star()

        if pygame.mouse.get_pressed()[0]:
            mdx, mdy = pygame.mouse.get_rel()
            user_yaw = float(np.clip(user_yaw + mdx * 0.0055, -0.55, 0.55))
            user_pitch = float(np.clip(user_pitch + mdy * 0.0040, -0.18, 0.36))
        else:
            pygame.mouse.get_rel()

        dt = clock.tick(30) / 1000.0
        if not paused:
            step = min(dt, 1.0 / 15.0)
            t += step
            if wave_pulse > 0.0:
                wave_pulse = max(0.0, wave_pulse - step * 0.42)
            if shoot_timer >= 0.0:
                shoot_timer += step * 0.85
                if shoot_timer > 1.0:
                    shoot_timer = -1.0

        # 1. Volumetric sky, clouds, god-rays, full moon & Fresnel ocean waves
        horizon_y, cam_shift_x, moon_uv = shader.render(screen, t, user_yaw, user_pitch, wave_pulse)

        # 2. Crisp stars, drifting snow motes & ghostly anglerfish with bioluminescent lure
        elements.draw_stars_and_snow(screen, t, horizon_y, cam_shift_x, shoot_timer)
        elements.draw_ghost_anglerfish(screen, t, moon_uv)

        # 3. Volcanic island, orca dorsal fin, coconut palms & 20-step 3D Escher staircase
        elements.draw_island_and_orca(screen, t, horizon_y, cam_shift_x)
        elements.draw_palms(screen, t, horizon_y, cam_shift_x)
        elements.draw_staircase(screen, t, user_yaw, user_pitch)

        # 4. Multi-pass atmospheric bloom
        screen.blit(bloom_pass(screen, 4, 8, 0.24), (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(bloom_pass(screen, 10, 18, 0.16), (0, 0), special_flags=pygame.BLEND_ADD)

        if show_emblem:
            draw_album_emblem(screen, f_en, f_jp, smooth((t - 4.0) / 2.2))

        # --- MANDATORY BRANDING & HUD ---
        title_surf = f_title.render("Dream Sweet in Sea Major", True, (232, 238, 246))
        time_surf = f_hud.render(f"{'●' if int(t * 2) % 2 == 0 else ' '} t {t:06.2f}s", True, (198, 214, 232))
        screen.blit(title_surf, (W - 48 - title_surf.get_width(), 30))
        screen.blit(time_surf, (W - 48 - time_surf.get_width(), 58))

        hud_y = H - 82
        screen.blit(f_sign.render(SIGN, True, (194, 206, 222)), (48, hud_y - 26))
        telem = f"horizon {horizon_y:.2f}   yaw {math.degrees(user_yaw):+05.1f}°   stars {stars_triggered:02d}"
        screen.blit(f_hud.render(telem, True, (148, 162, 180)), (48, hud_y))
        ctrls = "left-drag orbit · right-click star & wave · [e] emblem · [m] mute · [space] pause · [r] restart · [s] save · [f] fullscreen"
        screen.blit(f_hud.render(ctrls, True, (108, 120, 136)), (48, hud_y + 24))

        window.blit(screen if win_size == (W, H) else pygame.transform.smoothscale(screen, win_size), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    sys.exit(main())
