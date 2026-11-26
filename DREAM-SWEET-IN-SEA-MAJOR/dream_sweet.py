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
            buf[i0:i0 + ring] += celesta * env * 0.095

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


# --- Analytical Cover-Art Shader: Diagonal Rainbow Prism, Full Moon & Rippling Sea ---
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
        horizon_y = float(np.clip(0.575 + user_pitch * 0.28, 0.44, 0.70))
        cam_shift_x = user_yaw * 0.26

        is_sky = self.ny < horizon_y
        sky_h = np.clip((horizon_y - self.ny) / max(horizon_y, 0.05), 0.0, 1.0)

        # Deep charcoal-black sky with soft silver horizon mist
        base_lum = np.where(
            is_sky,
            0.024 + 0.165 * ((1.0 - sky_h) ** 2.8),
            0.014 + 0.040 * np.exp(-((self.ny - horizon_y) / 0.045) ** 2),
        )

        # Subtle monochrome RGB channels
        r_ch = base_lum * 0.96
        g_ch = base_lum * 0.98
        b_ch = base_lum * 1.02

        # Diagonal Rainbow Prism Beam slanting from top-left toward center horizon (exact cover motif)
        ray_vis = smooth((t - 1.0) / 2.2)
        if ray_vis > 0.001:
            # Distance perpendicular to the diagonal axis from (0.04, 0.0) to (0.60, 0.58)
            u_diag = (self.nx - 0.03 - cam_shift_x * 0.35) - self.ny * 0.96
            beam_env = np.exp(-((u_diag - 0.035) / 0.095) ** 2)
            falloff = np.exp(-(self.nx * 0.85 + self.ny * 1.05)) * (0.90 + 0.10 * np.sin(14.0 * u_diag - 0.45 * t))

            # Spectral dispersion across the beam width (red -> yellow -> green -> cyan -> blue)
            spec_pos = np.clip((u_diag + 0.065) / 0.20, 0.0, 1.0)
            spec_r = np.exp(-((spec_pos - 0.80) / 0.24) ** 2) + 0.45 * np.exp(-((spec_pos - 0.62) / 0.22) ** 2)
            spec_g = np.exp(-((spec_pos - 0.52) / 0.25) ** 2)
            spec_b = np.exp(-((spec_pos - 0.24) / 0.24) ** 2)

            rainbow_strength = ray_vis * is_sky * beam_env * falloff * 0.26
            r_ch += rainbow_strength * (0.38 + 0.85 * spec_r)
            g_ch += rainbow_strength * (0.38 + 0.82 * spec_g)
            b_ch += rainbow_strength * (0.40 + 0.90 * spec_b)

            # Soft secondary monochrome rays
            ray2 = ray_vis * is_sky * np.exp(-((u_diag + 0.12) / 0.065) ** 2) * falloff * 0.14
            r_ch += ray2
            g_ch += ray2
            b_ch += ray2 * 1.04

        # Full Moon + Detailed Lunar Maria + Soft Corona (Upper Right)
        moon_vis = smooth(t / 2.0)
        mx = 0.670 - cam_shift_x * 0.60
        my = horizon_y - 0.365
        dx_m = (self.nx - mx) * self.aspect
        dy_m = self.ny - my
        dist_m = np.hypot(dx_m, dy_m)
        moon_r = 0.095

        halo = moon_vis * is_sky * (
            0.22 * np.exp(-(dist_m / 0.20) ** 2)
            + 0.10 * np.exp(-(dist_m / 0.42) ** 2)
        )
        r_ch += halo * 0.96
        g_ch += halo * 0.98
        b_ch += halo * 1.02

        in_moon = dist_m <= moon_r
        if np.any(in_moon):
            u_m = dx_m / moon_r
            v_m = dy_m / moon_r
            maria = (
                0.13 * np.sin(u_m * 3.8 + 0.7) * np.cos(v_m * 3.4 - 0.5)
                + 0.09 * np.cos((u_m - v_m) * 6.8 + 0.4)
                + 0.06 * np.sin((u_m + v_m) * 12.5)
                + 0.04 * np.cos(u_m * 18.0 - v_m * 15.0)
            )
            limb = np.sqrt(np.clip(1.0 - (dist_m / moon_r) ** 2, 0.0, 1.0)) ** 0.22
            moon_disc = moon_vis * np.clip((0.91 + maria) * limb, 0.64, 1.04)
            r_ch = np.where(in_moon, np.maximum(r_ch, moon_disc * 0.98), r_ch)
            g_ch = np.where(in_moon, np.maximum(g_ch, moon_disc * 0.99), g_ch)
            b_ch = np.where(in_moon, np.maximum(b_ch, moon_disc * 1.00), b_ch)

        # Dark Rippling Ocean with Fine Silver Moonlight Path
        sea_vis = smooth((t - 0.4) / 2.0)
        if sea_vis > 0.001:
            sea_depth = np.clip((self.ny - horizon_y) / max(1.0 - horizon_y, 0.05), 0.002, 1.0)
            z_persp = 1.0 / (sea_depth + 0.036)
            x_persp = (self.nx - 0.5 + cam_shift_x) * z_persp * 0.46

            w1 = np.sin(x_persp * 7.5 + z_persp * 2.8 - 1.45 * t)
            w2 = np.cos(x_persp * 13.0 - z_persp * 3.6 - 1.85 * t)
            w3 = np.sin(z_persp * 5.2 - 2.30 * t + 1.4 * np.sin(x_persp * 3.4))
            wave_slope = 0.44 * w1 + 0.34 * w2 + 0.58 * w3

            if wave_pulse > 0.01:
                r_p = np.hypot((self.nx - 0.55) * self.aspect, (self.ny - 0.74) * 1.8)
                ring_r = (1.0 - wave_pulse) * 0.98
                wave_slope += 1.65 * wave_pulse * np.exp(-((r_p - ring_r) / 0.050) ** 2) * np.sin(46.0 * (r_p - ring_r))

            moon_col_dist = np.abs(self.nx - mx)
            path_width = 0.052 + 0.16 * sea_depth
            moon_path = np.exp(-((moon_col_dist / path_width) ** 2))
            # Fine crisp horizontal wave glints
            specular = np.clip(wave_slope, 0.0, 1.9) ** 2.2
            glints = (np.clip(wave_slope, 0.0, 1.8) ** 5.0) * moon_path * 0.48

            # Dark left shore shadow under the staircase
            left_shadow = smooth(np.clip((self.nx - 0.08) / 0.38, 0.0, 1.0))
            horizon_line = np.exp(-((self.ny - horizon_y) / 0.004) ** 2) * 0.24

            ocean_lum = sea_vis * (
                0.014
                + horizon_line
                + left_shadow * ((0.032 + 0.25 * moon_path) * specular * (0.35 + 0.65 * sea_depth) + glints)
            )
            r_ch = np.where(~is_sky, ocean_lum * 0.95, r_ch)
            g_ch = np.where(~is_sky, ocean_lum * 0.97, g_ch)
            b_ch = np.where(~is_sky, ocean_lum * 1.01, b_ch)

        rgb = np.empty((self.sh, self.sw, 3), dtype=np.uint8)
        rgb[..., 0] = np.clip((r_ch + self.grain) * 255.0, 0, 255).astype(np.uint8)
        rgb[..., 1] = np.clip((g_ch + self.grain) * 255.0, 0, 255).astype(np.uint8)
        rgb[..., 2] = np.clip((b_ch + self.grain) * 255.0, 0, 255).astype(np.uint8)

        small_surf = pygame.surfarray.make_surface(rgb.transpose(1, 0, 2))
        pygame.transform.smoothscale(small_surf, surf.get_size(), surf)
        return horizon_y, cam_shift_x, (mx, my)


# --- Cover Elements: Stars, Floating Musical Notes, Anglerfish, Orca, Palms & Twisted Staircase ---
class PaintedElements:
    def __init__(self):
        rng = np.random.default_rng(2026)

        # 1. Dense Milky-Way-style starfield
        n_stars = 460
        self.star_nx = rng.uniform(0.01, 0.99, n_stars)
        self.star_ny = rng.uniform(0.01, 0.56, n_stars)
        self.star_r = rng.choice([1, 1, 1, 1, 2], size=n_stars)
        self.star_ph = rng.uniform(0.0, TAU, n_stars)

        # 2. Floating "Dream Sweet in Sea Major" musical notes drifting in the background
        self.note_glyphs = ["♪", "♫"]
        n_notes = 28
        self.note_nx = rng.uniform(0.06, 0.94, n_notes)
        self.note_ny = rng.uniform(0.06, 0.52, n_notes)
        self.note_sp = rng.uniform(0.008, 0.020, n_notes)
        self.note_ph = rng.uniform(0.0, TAU, n_notes)
        self.note_idx = rng.integers(0, len(self.note_glyphs), size=n_notes)

        # 3. Top-left prism shards (signature geometric shards from top-left of the cover)
        self.shards = [
            [(0.0, 0.0), (0.14, 0.0), (0.04, 0.16)],
            [(0.0, 0.06), (0.11, 0.02), (0.0, 0.22)],
            [(0.12, 0.0), (0.24, 0.0), (0.08, 0.12)],
            [(0.0, 0.14), (0.09, 0.08), (0.02, 0.28)],
        ]

        # 4. Twisted Escher Staircase (rising from bottom-right/center up toward left horizon)
        self.steps = []
        n_steps = 11
        for k in range(n_steps):
            frac = k / (n_steps - 1)  # 0 = bottom-right foreground, 1 = left horizon
            cx = 0.56 - frac * 0.55
            cy = 0.96 - frac * 0.37
            w = 0.22 - frac * 0.13
            d = 0.052 - frac * 0.024
            h = 0.048 - frac * 0.022
            # Alternating Escher twist angle
            skew = (0.055 if k % 2 == 0 else -0.042) * (1.0 - 0.55 * frac)
            self.steps.append((frac, cx, cy, w, d, h, skew))

    def draw_prism_shards(self, screen, t):
        vis = smooth((t - 0.8) / 2.0)
        if vis <= 0.01:
            return
        w, h = screen.get_size()
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        for idx, poly in enumerate(self.shards):
            pts = [(int(px * w), int(py * h)) for px, py in poly]
            alpha = int((26 - idx * 4) * vis)
            pygame.draw.polygon(layer, (215, 224, 238, alpha), pts)
        screen.blit(layer, (0, 0))

    def draw_stars_and_notes(self, screen, t, horizon_y, cam_shift_x, shoot_timer, f_note):
        w, h = screen.get_size()
        sky_vis = smooth(t / 2.2)
        if sky_vis <= 0.01:
            return

        # Crisp starry night sky
        for i in range(len(self.star_nx)):
            if self.star_ny[i] >= horizon_y - 0.01:
                continue
            sx = int(((self.star_nx[i] - cam_shift_x * 0.35) % 1.0) * w)
            sy = int(self.star_ny[i] * h)
            tw = (0.45 + 0.55 * math.sin(1.8 * t + self.star_ph[i])) * sky_vis
            val = max(0, min(255, int(242 * tw)))
            if self.star_r[i] == 1:
                screen.set_at((sx, sy), (val, val, min(255, val + 10)))
            else:
                pygame.draw.circle(screen, (val, val, min(255, val + 12)), (sx, sy), 1)
                if tw > 0.85:
                    pygame.draw.line(screen, (val // 2, val // 2, val // 2), (sx - 3, sy), (sx + 3, sy), 1)
                    pygame.draw.line(screen, (val // 2, val // 2, val // 2), (sx, sy - 3), (sx, sy + 3), 1)

        # Subtle glowing Dream Sweet in Sea Major musical notes drifting in the background
        note_vis = smooth((t - 2.0) / 2.5)
        if note_vis > 0.01:
            for i in range(len(self.note_nx)):
                nx = ((self.note_nx[i] + 0.018 * math.sin(0.4 * t + self.note_ph[i]) - cam_shift_x * 0.25) % 1.0)
                ny = ((self.note_ny[i] - self.note_sp[i] * t * 0.35) % max(horizon_y - 0.04, 0.2))
                pulse = 0.30 + 0.70 * (math.sin(1.3 * t + self.note_ph[i]) ** 2)
                alpha = int(115 * note_vis * pulse)
                if alpha > 14:
                    g_surf = f_note.render(self.note_glyphs[self.note_idx[i]], True, (215, 230, 250))
                    g_surf.set_alpha(alpha)
                    screen.blit(g_surf, (int(nx * w), int(ny * h)))

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
        """Draw the misty, textured abyssal anglerfish jaws & needle teeth lurking beside the moon."""
        angler_vis = smooth((t - 4.2) / 3.0)
        if angler_vis <= 0.01:
            return
        w, h = screen.get_size()
        layer = pygame.Surface((w, h), pygame.SRCALPHA)

        mx, my = moon_uv
        drift_x = 0.004 * math.cos(0.45 * t)
        drift_y = 0.006 * math.sin(0.60 * t)
        ox = (mx + 0.045 + drift_x) * w
        oy = (my + 0.060 + drift_y) * h
        sc = h / 860.0

        # Misty organic head & brow shading (smooth 48-point curve, fading softly into the night sky)
        def angler_curve(pad=1.0):
            pts = []
            for i in range(28):
                u = i / 27.0
                ang = math.pi * (1.05 - u * 1.45)
                px = ox + (135 + math.cos(ang) * 148 * pad) * sc
                py = oy + (16 - math.sin(ang) * 158 * pad) * sc
                pts.append((int(px), int(py)))
            for i in range(14):
                u = i / 13.0
                px = ox + (195 - u * 135) * sc
                py = oy + (152 + 30 * math.sin(u * math.pi)) * sc
                pts.append((int(px), int(py)))
            for i in range(10):
                u = i / 9.0
                px = ox + (108 + 38 * math.sin(u * math.pi)) * sc
                py = oy + (125 - u * 155) * sc
                pts.append((int(px), int(py)))
            return pts

        pygame.draw.polygon(layer, (172, 184, 204, int(14 * angler_vis)), angler_curve(1.06))
        pygame.draw.polygon(layer, (176, 188, 208, int(20 * angler_vis)), angler_curve(1.0))

        # Textured brow ridge & cheek highlights (matching the ghostly cover texture)
        brow_pts = [
            (ox + 18 * sc, oy - 38 * sc),
            (ox + 58 * sc, oy - 72 * sc),
            (ox + 112 * sc, oy - 95 * sc),
            (ox + 165 * sc, oy - 82 * sc),
        ]
        pygame.draw.aalines(layer, (215, 224, 238, int(65 * angler_vis)), False, [(int(x), int(y)) for x, y in brow_pts])

        # Sunken dark eye socket
        eye_x, eye_y = int(ox + 102 * sc), int(oy - 58 * sc)
        pygame.draw.circle(layer, (12, 16, 22, int(85 * angler_vis)), (eye_x, eye_y), int(10 * sc))
        pygame.draw.circle(layer, (200, 212, 228, int(50 * angler_vis)), (eye_x, eye_y), int(10 * sc), 1)

        # Jagged, curved needle-tooth rows (varied length & organic angle like the cover)
        for idx in range(20):
            u = idx / 19.0
            # Upper jaw teeth
            ux = ox + (8 + u * 142) * sc
            uy = oy + (-28 - 14 * math.sin(u * math.pi)) * sc
            t_len = (26 + 34 * math.sin(u * math.pi) + 8 * math.sin(idx * 2.3)) * sc
            tip_ux = ux + (3 + 7 * u) * sc
            tip_uy = uy + t_len
            alpha_t = int((145 - 55 * u) * angler_vis)
            pygame.draw.polygon(
                layer,
                (232, 238, 246, alpha_t),
                [(int(ux - 2.0 * sc), int(uy)), (int(ux + 2.0 * sc), int(uy)), (int(tip_ux), int(tip_uy))],
            )

            # Lower jaw teeth
            lx = ox + (58 + u * 125) * sc
            ly = oy + (142 + 24 * math.sin(u * math.pi)) * sc
            l_len = (24 + 32 * math.sin(u * math.pi) + 7 * math.cos(idx * 2.1)) * sc
            tip_lx = lx - (4 + 6 * u) * sc
            tip_ly = ly - l_len
            pygame.draw.polygon(
                layer,
                (226, 232, 242, alpha_t),
                [(int(lx - 2.0 * sc), int(ly)), (int(lx + 2.0 * sc), int(ly)), (int(tip_lx), int(tip_ly))],
            )

        # Soft misty fade on the right/bottom edges
        screen.blit(layer, (0, 0))

    def draw_orca(self, screen, t, horizon_y, cam_shift_x):
        """Draw the dark orca back & curved dorsal fin on the far-left horizon."""
        fin_vis = smooth((t - 0.9) / 2.2)
        if fin_vis <= 0.01:
            return
        w, h = screen.get_size()
        fx = (0.125 - cam_shift_x * 0.5) * w
        fy = horizon_y * h + 2
        sc = (h / 860.0) * fin_vis
        bob = 2.0 * math.sin(1.25 * t)

        fin_pts = [
            (fx - 70 * sc, fy + 1),
            (fx - 34 * sc, fy - 5 * sc + bob),
            (fx - 15 * sc, fy - 14 * sc + bob),
            (fx - 10 * sc, fy - 42 * sc + bob),
            (fx - 3 * sc, fy - 44 * sc + bob),
            (fx + 6 * sc, fy - 18 * sc + bob),
            (fx + 35 * sc, fy - 8 * sc + bob),
            (fx + 88 * sc, fy + 1),
        ]
        pygame.draw.polygon(screen, (6, 8, 12), [(int(x), int(y)) for x, y in fin_pts])

    def draw_palms(self, screen, t, horizon_y, cam_shift_x):
        """Draw the two tall silhouetted coconut palms rising from the left horizon/staircase."""
        palm_vis = smooth((t - 1.8) / 2.4)
        if palm_vis <= 0.01:
            return
        w, h = screen.get_size()
        sc = h / 860.0
        col_sil = (5, 7, 10)

        # Two tall palms positioned exactly as in the cover (left-of-center, rising high)
        palms = [
            (0.245 - cam_shift_x * 0.72, 0.74, 520 * sc * palm_vis, -46 * sc, 1.15 * sc * palm_vis, 0.0),
            (0.325 - cam_shift_x * 0.70, 0.71, 415 * sc * palm_vis,  28 * sc, 0.92 * sc * palm_vis, 1.7),
        ]

        for bx_n, by_n, trunk_h, lean, f_scale, ph in palms:
            bx = bx_n * w
            by = by_n * h
            sway = 9.0 * sc * math.sin(1.10 * t + ph)

            left_edge, right_edge = [], []
            steps = 24
            for s_i in range(steps + 1):
                u = s_i / steps
                cx = bx + (u ** 1.55) * lean + (u ** 1.4) * sway
                cy = by - u * trunk_h
                half_w = (8.5 * (1.0 - 0.62 * u)) * sc
                left_edge.append((int(cx - half_w), int(cy)))
                right_edge.append((int(cx + half_w), int(cy)))
            pygame.draw.polygon(screen, col_sil, left_edge + right_edge[::-1])

            tip_x = bx + lean + sway
            tip_y = by - trunk_h

            frond_angles = [-2.75, -2.35, -1.95, -1.55, -1.10, -0.65, -0.25, 0.18, 0.58, 2.95, 3.30]
            for idx_f, base_ang in enumerate(frond_angles):
                ang = base_ang + 0.035 * math.sin(1.30 * t + ph + idx_f)
                f_len = (142 + 18 * math.cos(idx_f * 1.7)) * f_scale
                dir_x = math.cos(ang)
                dir_y = math.sin(ang) * 0.66

                spine = []
                for j in range(15):
                    u = j / 14.0
                    px = tip_x + dir_x * f_len * u
                    py = tip_y + dir_y * f_len * u + (u ** 1.85) * 64.0 * f_scale
                    spine.append((px, py))

                pygame.draw.lines(screen, col_sil, False, [(int(x), int(y)) for x, y in spine], max(2, int(3.0 * sc)))

                for j in range(2, 14):
                    u = j / 14.0
                    px, py = spine[j]
                    lf_len = (36.0 * math.sin(u * np.pi) + 8.0) * f_scale
                    hang_x = px + (6.0 if dir_x >= 0 else -6.0) * f_scale
                    hang_y = py + lf_len
                    pygame.draw.line(screen, col_sil, (int(px), int(py)), (int(hang_x), int(hang_y)), max(1, int(2.2 * sc)))

    def draw_staircase(self, screen, t, user_yaw, user_pitch):
        """Draw the signature twisted Escher staircase climbing from bottom-center toward the left horizon."""
        stair_prog = smooth((t - 2.6) / 3.0)
        if stair_prog <= 0.001:
            return

        w, h = screen.get_size()
        layer = pygame.Surface((w, h), pygame.SRCALPHA)

        shift_x = user_yaw * 0.12
        shift_y = user_pitch * 0.10

        # Draw from top-left (farthest) to bottom-right (closest)
        for frac, cx, cy, sw, sd, sh, skew in reversed(self.steps):
            if frac > stair_prog:
                continue
            bob = 0.002 * math.sin(1.4 * t - frac * 4.5)
            px = (cx - shift_x * (1.0 - frac * 0.5)) * w
            py = (cy + bob + shift_y * (1.0 - frac * 0.5)) * h
            half_w = sw * w
            d_px = sd * h
            h_px = sh * h
            sk_px = skew * w

            # Top tread trapezoid/wedge (twisted Escher ribbon)
            tl = (int(px - half_w - sk_px), int(py - d_px))
            tr = (int(px + half_w - sk_px), int(py - d_px * 0.72))
            br = (int(px + half_w + sk_px), int(py))
            bl = (int(px - half_w + sk_px), int(py + d_px * 0.25))

            # Riser bottom corners
            bl_b = (bl[0], int(bl[1] + h_px))
            br_b = (br[0], int(br[1] + h_px))
            tl_b = (tl[0], int(tl[1] + h_px))

            fade = 1.0 - 0.22 * frac
            alpha = int(225 - 40 * frac)
            top_col = (int(225 * fade), int(230 * fade), int(238 * fade), alpha)
            front_col = (int(24 * fade), int(28 * fade), int(35 * fade), min(255, alpha + 20))
            side_col = (int(12 * fade), int(15 * fade), int(20 * fade), min(255, alpha + 20))

            # Left shadow side + front riser + luminous top tread
            pygame.draw.polygon(layer, side_col, [tl, bl, bl_b, tl_b])
            pygame.draw.polygon(layer, front_col, [bl, br, br_b, bl_b])
            pygame.draw.polygon(layer, top_col, [tl, tr, br, bl])
            pygame.draw.aalines(layer, (245, 248, 255, alpha), True, [tl, tr, br, bl])

        screen.blit(layer, (0, 0))


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
    cx, cy = w // 2, int(h * 0.495)

    en_surf = f_en.render("HAWAII: PART II", True, (244, 246, 250))
    en_surf.set_alpha(int(245 * alpha_scale))
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
    f_note = pygame.font.SysFont("seguisymbol,arialunicodems,dejavusans,sans-serif", 20)
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

        # 1. Cover-art sky, diagonal rainbow prism, full moon & rippling dark sea
        horizon_y, cam_shift_x, moon_uv = shader.render(screen, t, user_yaw, user_pitch, wave_pulse)

        # 2. Top-left prism shards, crisp stars, drifting Dream Sweet notes & ghostly anglerfish
        elements.draw_prism_shards(screen, t)
        elements.draw_stars_and_notes(screen, t, horizon_y, cam_shift_x, shoot_timer, f_note)
        elements.draw_ghost_anglerfish(screen, t, moon_uv)

        # 3. Orca fin, tall coconut palms & signature twisted Escher staircase
        elements.draw_orca(screen, t, horizon_y, cam_shift_x)
        elements.draw_palms(screen, t, horizon_y, cam_shift_x)
        elements.draw_staircase(screen, t, user_yaw, user_pitch)

        # 4. Multi-pass atmospheric bloom
        screen.blit(bloom_pass(screen, 4, 8, 0.22), (0, 0), special_flags=pygame.BLEND_ADD)
        screen.blit(bloom_pass(screen, 10, 18, 0.14), (0, 0), special_flags=pygame.BLEND_ADD)

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
