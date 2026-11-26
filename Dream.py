# Kobsi · 2026 — Hawaii: Part II (Dream Sweet in Sea Major — Volumetric Shader & 3D Art)
import sys
import time
from pathlib import Path
import numpy as np
import pygame

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

        # Soft rolling ocean waves
        white = rng.normal(0.0, 1.0, n).astype(np.float32)
        surf = np.convolve(white, np.ones(200, dtype=np.float32) / 200.0, mode="same")
        surf_env = 0.036 * (0.55 + 0.45 * np.sin(TAU * (1.0 / (dur / 3.0)) * tt))
        buf = surf * surf_env

        # Warm lush string/organ pad underneath the waltz
        chords = [
            (0,  12, [53, 60, 64, 69]),  # Fmaj7 ("Alone at the edge...")
            (12, 12, [52, 59, 64, 67]),  # Em7   ("...of a universe...")
            (24, 12, [50, 57, 60, 65]),  # Dm7   ("...humming a tune...")
            (36, 12, [48, 55, 60, 64]),  # Cmaj7 ("...dreaming we were snow...")
        ]
        for b0, blen, notes in chords:
            i0 = int(b0 * beat * sr)
            i1 = min(n, int((b0 + blen) * beat * sr))
            seg_t = np.arange(i1 - i0, dtype=np.float32) / sr
            pad_env = np.sin(np.pi * np.clip(seg_t / (blen * beat), 0.0, 1.0)) ** 0.65
            for m in notes:
                f = 440.0 * (2.0 ** ((m - 69) / 12.0))
                vibrato = 1.0 + 0.0018 * np.sin(TAU * 4.5 * seg_t)
                buf[i0:i1] += np.sin(TAU * f * vibrato * seg_t) * pad_env * 0.024

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
            ring = min(n - i0, int(sr * (b_len * beat + 1.5)))
            tm = np.arange(ring, dtype=np.float32) / sr
            f = 440.0 * (2.0 ** ((midi - 69) / 12.0))
            env = np.exp(-tm * 1.75) * (1.0 - np.exp(-tm * 150.0))
            celesta = (
                0.74 * np.sin(TAU * f * tm)
                + 0.19 * np.sin(TAU * f * 2.0 * tm) * np.exp(-tm * 4.8)
                + 0.07 * np.sin(TAU * f * 4.0 * tm) * np.exp(-tm * 11.0)
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
            for sub_b, m_note, amp in ((0.0, b1, 0.055), (1.0, b2, 0.036), (2.0, b3, 0.036)):
                i0 = int((bar_idx * 3.0 + sub_b) * beat * sr)
                ring = min(n - i0, int(sr * 1.15))
                tm = np.arange(ring, dtype=np.float32) / sr
                f = 440.0 * (2.0 ** ((m_note - 69) / 12.0))
                env = np.exp(-tm * 2.6) * (1.0 - np.exp(-tm * 110.0))
                buf[i0:i0 + ring] += np.sin(TAU * f * tm) * env * amp

        fade = np.linspace(0.0, 1.0, int(sr * 0.35), dtype=np.float32)
        buf[:len(fade)] *= fade
        buf[-len(fade):] *= fade[::-1]

        left = np.clip(buf * 32767, -32767, 32767).astype(np.int16)
        right = np.roll(left, 420)
        self.loop_sound = pygame.sndarray.make_sound(np.column_stack((left, right)))

        # Shooting-star crystalline chime
        c_n = int(sr * 2.2)
        chime = np.zeros(c_n, dtype=np.float32)
        for idx, f in enumerate([659.25, 880.0, 1046.5, 1318.5, 1567.98]):
            d = int(idx * 0.065 * sr)
            tc = np.arange(c_n - d, dtype=np.float32) / sr
            chime[d:] += np.sin(TAU * f * tc) * np.exp(-tc * 2.4) * (1.0 - np.exp(-tc * 150.0)) * 0.085
        ci16 = np.clip(chime * 32767, -32767, 32767).astype(np.int16)
        self.star_chime = pygame.sndarray.make_sound(np.column_stack((ci16, np.roll(ci16, 200))))

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


# --- Analytical Sky, Volumetric God-Rays & Ocean Wave Pixel Shader ---
class BackdropShader:
    def __init__(self, sh_w, sh_h):
        self.sw = sh_w
        self.sh = sh_h
        yy, xx = np.mgrid[0:sh_h, 0:sh_w].astype(np.float32)
        self.nx = xx / sh_w
        self.ny = yy / sh_h
        self.aspect = sh_w / sh_h

        # Precompute crater texture for the full moon
        self.crater_seed_x = xx * 0.19
        self.crater_seed_y = yy * 0.19

    def render(self, surf, t, user_yaw, user_pitch, wave_pulse):
        horizon_y = float(np.clip(0.565 + user_pitch * 0.32, 0.42, 0.70))
        cam_shift_x = user_yaw * 0.28

        # Sky vs. Ocean masks with soft atmospheric horizon blend
        is_sky = self.ny < horizon_y
        sky_h = np.clip((horizon_y - self.ny) / max(horizon_y, 0.05), 0.0, 1.0)

        # Base vertical gradient: deep obsidian zenith -> misty silver-slate horizon
        base_lum = np.where(
            is_sky,
            0.035 + 0.19 * ((1.0 - sky_h) ** 2.6),
            0.025 + 0.05 * np.exp(-((self.ny - horizon_y) / 0.06) ** 2),
        )

        # Volumetric diagonal god-rays slanting down from top-left (matching cover art)
        ray_vis = smooth((t - 1.2) / 2.4)
        if ray_vis > 0.001:
            diag = (self.nx - 0.03 - cam_shift_x * 0.4) - (self.ny - 0.02) * 0.76
            b1 = np.exp(-((diag - 0.13) / 0.085) ** 2)
            b2 = 0.78 * np.exp(-((diag - 0.28) / 0.058) ** 2)
            b3 = 0.62 * np.exp(-((diag + 0.03) / 0.072) ** 2)
            b4 = 0.40 * np.exp(-((diag - 0.41) / 0.048) ** 2)
            falloff = np.exp(-((self.nx * 0.75 + self.ny * 1.15)))
            shimmer = 0.90 + 0.10 * np.sin(18.0 * diag - 0.55 * t)
            rays = ray_vis * is_sky * falloff * shimmer * (b1 + b2 + b3 + b4) * 0.36
            base_lum += rays

        # Full Moon + Lunar Maria Craters + Atmospheric Halo (Upper Right)
        moon_vis = smooth(t / 2.2)
        mx = 0.645 - cam_shift_x * 0.65
        my = horizon_y - 0.335
        dx_m = (self.nx - mx) * self.aspect
        dy_m = self.ny - my
        dist_m = np.hypot(dx_m, dy_m)
        moon_r = 0.092

        # Soft outer lunar corona
        halo = moon_vis * is_sky * (0.26 * np.exp(-(dist_m / 0.24) ** 2) + 0.12 * np.exp(-(dist_m / 0.45) ** 2))
        base_lum += halo

        # Crisp moon disc with subtle crater shading
        in_moon = dist_m <= moon_r
        if np.any(in_moon):
            u_m = dx_m / moon_r
            v_m = dy_m / moon_r
            maria = (
                0.10 * np.sin(u_m * 4.2 + 0.6) * np.cos(v_m * 3.8 - 0.4)
                + 0.07 * np.cos((u_m - v_m) * 7.5)
                + 0.05 * np.sin((u_m + v_m) * 12.0)
            )
            limb = np.sqrt(np.clip(1.0 - (dist_m / moon_r) ** 2, 0.0, 1.0)) ** 0.22
            moon_disc = moon_vis * np.clip((0.92 + maria) * limb, 0.68, 1.04)
            base_lum = np.where(in_moon, np.maximum(base_lum, moon_disc), base_lum)

        # Continuous Fresnel Ocean Waves & Shimmering Moonlight Path
        sea_vis = smooth((t - 0.5) / 2.2)
        if sea_vis > 0.001:
            sea_depth = np.clip((self.ny - horizon_y) / max(1.0 - horizon_y, 0.05), 0.002, 1.0)
            # Perspective-foreshortened wave coordinates (tighter ripples near horizon, wider in foreground)
            z_persp = 1.0 / (sea_depth + 0.045)
            x_persp = (self.nx - 0.5 + cam_shift_x) * z_persp * 0.42

            w1 = np.sin(x_persp * 6.5 + z_persp * 2.4 - 1.5 * t)
            w2 = np.cos(x_persp * 11.0 - z_persp * 3.1 - 1.9 * t)
            w3 = np.sin(z_persp * 4.6 - 2.3 * t + 1.2 * np.sin(x_persp * 3.0))
            wave_slope = 0.45 * w1 + 0.35 * w2 + 0.55 * w3

            if wave_pulse > 0.01:
                r_p = np.hypot((self.nx - 0.45) * self.aspect, (self.ny - 0.74) * 1.8)
                ring_r = (1.0 - wave_pulse) * 0.95
                wave_slope += 1.6 * wave_pulse * np.exp(-((r_p - ring_r) / 0.055) ** 2) * np.sin(45.0 * (r_p - ring_r))

            # Moonlight specular path under the upper-right moon
            moon_col_dist = np.abs(self.nx - mx)
            path_width = 0.055 + 0.14 * sea_depth
            moon_path = np.exp(-((moon_col_dist / path_width) ** 2))
            specular = np.clip(wave_slope, 0.0, 1.8) ** 1.7

            # Crisp horizon silver line + dark obsidian swells with silver crests
            horizon_glow = np.exp(-((self.ny - horizon_y) / 0.006) ** 2) * 0.32
            ocean_lum = sea_vis * (
                0.022
                + horizon_glow
                + (0.045 + 0.24 * moon_path) * specular * (0.35 + 0.65 * sea_depth)
            )
            base_lum = np.where(~is_sky, ocean_lum, base_lum)

        # Subtle cool monochrome blue-silver tint
        lum = np.clip(base_lum, 0.0, 1.0)
        rgb = np.empty((self.sh, self.sw, 3), dtype=np.uint8)
        rgb[..., 0] = np.clip(lum * 238.0, 0, 255).astype(np.uint8)
        rgb[..., 1] = np.clip(lum * 244.0, 0, 255).astype(np.uint8)
        rgb[..., 2] = np.clip(lum * 255.0, 0, 255).astype(np.uint8)

        small_surf = pygame.surfarray.make_surface(rgb.transpose(1, 0, 2))
        pygame.transform.smoothscale(small_surf, surf.get_size(), surf)
        return horizon_y, cam_shift_x, (mx, my)


# --- 3D Twisted Escher Staircase Polygons, Silhouetted Palms & Ghostly Anglerfish ---
class PaintedElements:
    def __init__(self):
        rng = np.random.default_rng(2026)

        # 1. Crisp Stars & Dust Motes in the Light Beams
        n_stars = 260
        self.star_nx = rng.uniform(0.01, 0.99, n_stars)
        self.star_ny = rng.uniform(0.01, 0.54, n_stars)
        self.star_r = rng.choice([1, 1, 1, 2], size=n_stars)
        self.star_ph = rng.uniform(0.0, TAU, n_stars)

        n_motes = 95
        self.mote_nx = rng.uniform(0.04, 0.62, n_motes)
        self.mote_ny = rng.uniform(0.04, 0.52, n_motes)
        self.mote_ph = rng.uniform(0.0, TAU, n_motes)

        # 2. Precompute 13 Twisted 3D Stair Slabs (each slab is a 3D rectangular prism)
        self.slabs = []
        n_slabs = 13
        for k in range(n_slabs):
            frac = k / (n_slabs - 1)  # 0 = foreground bottom-right, 1 = midground left
            cx = 0.24 - frac * 1.18
            cy = -0.35 + frac * 0.345
            cz = -0.52 + frac * 1.38
            twist = -0.46 + frac * 0.60 + 0.14 * np.sin(frac * 5.2)
            w = 0.46 - frac * 0.12
            d = 0.135
            h = 0.038

            ct, st = np.cos(twist), np.sin(twist)
            # 4 top corners & 4 bottom corners in 3D
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

    def draw_stars_and_motes(self, screen, t, horizon_y, cam_shift_x, shoot_timer):
        w, h = screen.get_size()
        sky_vis = smooth(t / 2.2)
        if sky_vis <= 0.01:
            return

        for i in range(len(self.star_nx)):
            if self.star_ny[i] >= horizon_y - 0.01:
                continue
            sx = int(((self.star_nx[i] - cam_shift_x * 0.35) % 1.0) * w)
            sy = int(self.star_ny[i] * h)
            tw = (0.50 + 0.50 * np.sin(1.9 * t + self.star_ph[i])) * sky_vis
            val = max(0, min(255, int(245 * tw)))
            r = int(self.star_r[i])
            if r == 1:
                screen.set_at((sx, sy), (val, val, min(255, val + 10)))
            else:
                pygame.draw.circle(screen, (val, val, min(255, val + 12)), (sx, sy), 2)
                if tw > 0.85:
                    pygame.draw.line(screen, (val // 2, val // 2, val // 2), (sx - 4, sy), (sx + 4, sy), 1)
                    pygame.draw.line(screen, (val // 2, val // 2, val // 2), (sx, sy - 4), (sx, sy + 4), 1)

        # Floating dust motes drifting inside the diagonal light rays
        ray_vis = smooth((t - 1.5) / 2.5)
        if ray_vis > 0.01:
            for i in range(len(self.mote_nx)):
                mx = int((self.mote_nx[i] + 0.012 * np.sin(0.5 * t + self.mote_ph[i])) * w)
                my = int((self.mote_ny[i] + 0.010 * np.cos(0.4 * t + self.mote_ph[i])) * h)
                if my >= int(horizon_y * h):
                    continue
                b = int(175 * ray_vis * (0.35 + 0.65 * np.sin(1.6 * t + self.mote_ph[i]) ** 2))
                pygame.draw.circle(screen, (b, b, min(255, b + 15)), (mx, my), 1)

        # Shooting star streak
        auto_cycle = (t % 15.0) / 1.35
        s_prog = shoot_timer if shoot_timer >= 0.0 else (auto_cycle if auto_cycle < 1.0 else -1.0)
        if 0.0 <= s_prog <= 1.0:
            hx = int((0.78 - s_prog * 0.56) * w)
            hy = int((0.10 + s_prog * 0.22) * h)
            tx = int((0.78 - max(0.0, s_prog - 0.16) * 0.56) * w)
            ty = int((0.10 + max(0.0, s_prog - 0.16) * 0.22) * h)
            fade = np.sin(np.pi * s_prog)
            col_head = (int(255 * fade), int(248 * fade), int(220 * fade))
            pygame.draw.line(screen, col_head, (tx, ty), (hx, hy), 2)
            pygame.draw.circle(screen, col_head, (hx, hy), 3)

    def draw_ghost_anglerfish(self, screen, t, moon_uv, horizon_y):
        """Draw the translucent ghostly abyssal anglerfish jaws & needle teeth beside the moon."""
        angler_vis = smooth((t - 5.2) / 3.2)
        if angler_vis <= 0.01:
            return
        w, h = screen.get_size()
        layer = pygame.Surface((w, h), pygame.SRCALPHA)

        mx, my = moon_uv
        drift_x = 0.005 * np.cos(0.55 * t)
        drift_y = 0.008 * np.sin(0.70 * t)
        ox = (mx + 0.045 + drift_x) * w
        oy = (my + 0.020 + drift_y) * h
        sc = h / 860.0

        alpha_body = int(42 * angler_vis)
        alpha_rim = int(78 * angler_vis)
        alpha_tooth = int(125 * angler_vis)

        # Soft translucent head & open maw silhouette
        skull_poly = [
            (ox + 15 * sc, oy - 35 * sc),
            (ox + 85 * sc, oy - 115 * sc),
            (ox + 185 * sc, oy - 135 * sc),
            (ox + 265 * sc, oy - 75 * sc),
            (ox + 285 * sc, oy + 45 * sc),
            (ox + 235 * sc, oy + 145 * sc),
            (ox + 145 * sc, oy + 185 * sc),
            (ox + 55 * sc, oy + 140 * sc),
            (ox + 115 * sc, oy + 85 * sc),
            (ox + 145 * sc, oy + 10 * sc),
            (ox + 105 * sc, oy - 35 * sc),
        ]
        pygame.draw.polygon(layer, (185, 195, 210, alpha_body), [(int(x), int(y)) for x, y in skull_poly])
        pygame.draw.aalines(layer, (215, 224, 238, alpha_rim), False, [(int(x), int(y)) for x, y in skull_poly[:7]])

        # Faint sunken eye socket
        pygame.draw.circle(layer, (28, 32, 40, int(65 * angler_vis)), (int(ox + 135 * sc), int(oy - 62 * sc)), int(14 * sc))
        pygame.draw.circle(layer, (215, 224, 238, int(55 * angler_vis)), (int(ox + 135 * sc), int(oy - 62 * sc)), int(14 * sc), 1)

        # Curved upper & lower needle-tooth rows (signature cover detail)
        for idx in range(15):
            u = idx / 14.0
            # Upper jaw teeth curving downward
            ux = ox + (24 + u * 135) * sc
            uy = oy + (-34 - 16 * np.sin(u * np.pi)) * sc
            t_len = (24 + 22 * np.sin(u * np.pi)) * sc
            tip_ux = ux + (4 + 8 * u) * sc
            tip_uy = uy + t_len
            pygame.draw.polygon(
                layer,
                (235, 240, 248, alpha_tooth),
                [(int(ux - 2.2 * sc), int(uy)), (int(ux + 2.2 * sc), int(uy)), (int(tip_ux), int(tip_uy))],
            )

            # Lower jaw teeth curving upward
            lx = ox + (52 + u * 125) * sc
            ly = oy + (135 + 28 * np.sin(u * np.pi)) * sc
            l_len = (24 + 24 * np.sin(u * np.pi)) * sc
            tip_lx = lx - (5 + 6 * u) * sc
            tip_ly = ly - l_len
            pygame.draw.polygon(
                layer,
                (235, 240, 248, alpha_tooth),
                [(int(lx - 2.2 * sc), int(ly)), (int(lx + 2.2 * sc), int(ly)), (int(tip_lx), int(tip_ly))],
            )

        screen.blit(layer, (0, 0))

    def draw_orca_fin(self, screen, t, horizon_y, cam_shift_x):
        """Draw the dark orca dorsal fin silhouette on the far-left horizon."""
        fin_vis = smooth((t - 1.0) / 2.2)
        if fin_vis <= 0.01:
            return
        w, h = screen.get_size()
        fx = (0.145 - cam_shift_x * 0.5) * w
        fy = horizon_y * h + 2
        sc = (h / 860.0) * fin_vis
        bob = 2.0 * np.sin(1.3 * t)

        fin_pts = [
            (fx - 34 * sc, fy),
            (fx - 12 * sc, fy - 8 * sc + bob),
            (fx - 2 * sc, fy - 38 * sc + bob),
            (fx + 6 * sc, fy - 36 * sc + bob),
            (fx + 14 * sc, fy - 10 * sc + bob),
            (fx + 46 * sc, fy),
        ]
        pygame.draw.polygon(screen, (8, 10, 14), [(int(x), int(y)) for x, y in fin_pts])

    def draw_palms(self, screen, t, horizon_y, cam_shift_x):
        """Draw the two tall silhouetted coconut palms on the left with feathered fronds."""
        palm_vis = smooth((t - 2.0) / 2.4)
        if palm_vis <= 0.01:
            return
        w, h = screen.get_size()
        sc = h / 860.0
        col_sil = (7, 9, 13)

        # Two palms matching the album cover placement
        palms = [
            # (base_nx, base_ny, height_px, lean_px, crown_scale, phase)
            (0.245 - cam_shift_x * 0.75, 0.72, 465 * sc * palm_vis, -42 * sc, 1.05 * sc * palm_vis, 0.0),
            (0.355 - cam_shift_x * 0.70, 0.71, 375 * sc * palm_vis,  26 * sc, 0.85 * sc * palm_vis, 1.7),
        ]

        for bx_n, by_n, trunk_h, lean, f_scale, ph in palms:
            bx = bx_n * w
            by = by_n * h
            sway = 11.0 * sc * np.sin(1.15 * t + ph)

            # Build tapered curved trunk polygon
            left_edge, right_edge = [], []
            steps = 22
            for s_i in range(steps + 1):
                u = s_i / steps
                cx = bx + (u ** 1.55) * lean + (u ** 1.4) * sway
                cy = by - u * trunk_h
                half_w = (9.5 * (1.0 - 0.58 * u)) * sc
                left_edge.append((int(cx - half_w), int(cy)))
                right_edge.append((int(cx + half_w), int(cy)))
            trunk_poly = left_edge + right_edge[::-1]
            pygame.draw.polygon(screen, col_sil, trunk_poly)

            tip_x = bx + lean + sway
            tip_y = by - trunk_h

            # 11 lush drooping palm fronds with individual hanging leaflets
            frond_angles = [-2.75, -2.35, -1.95, -1.55, -1.10, -0.65, -0.25, 0.18, 0.58, 2.95, 3.30]
            for idx_f, base_ang in enumerate(frond_angles):
                ang = base_ang + 0.04 * np.sin(1.4 * t + ph + idx_f)
                f_len = (138 + 18 * np.cos(idx_f * 1.7)) * f_scale
                dir_x = np.cos(ang)
                dir_y = np.sin(ang) * 0.65

                # Spine of the frond
                spine = []
                for j in range(15):
                    u = j / 14.0
                    px = tip_x + dir_x * f_len * u
                    py = tip_y + dir_y * f_len * u + (u ** 1.85) * 62.0 * f_scale
                    spine.append((px, py))

                pygame.draw.lines(screen, col_sil, False, [(int(x), int(y)) for x, y in spine], max(2, int(3.2 * sc)))

                # Hanging feather leaflets along each frond
                for j in range(2, 14):
                    u = j / 14.0
                    px, py = spine[j]
                    lf_len = (34.0 * np.sin(u * np.pi) + 8.0) * f_scale
                    hang_x = px + (6.0 if dir_x >= 0 else -6.0) * f_scale
                    hang_y = py + lf_len
                    pygame.draw.line(screen, col_sil, (int(px), int(py)), (int(hang_x), int(hang_y)), max(1, int(2.2 * sc)))

    def draw_staircase(self, screen, t, user_yaw, user_pitch):
        """Render the twisted foreground Escher staircase as solid, depth-sorted 3D polygons."""
        stair_prog = smooth((t - 3.2) / 3.4)
        if stair_prog <= 0.001:
            return

        w, h = screen.get_size()
        cx_scr, cy_scr = w * 0.5, h * 0.52
        fov = h * 1.12

        yaw = 0.035 * np.sin(0.18 * t) + user_yaw
        pitch = 0.08 + 0.012 * np.cos(0.22 * t) + user_pitch
        cam_y = 0.22
        cam_z = -1.55
        cy, sy = np.cos(yaw), np.sin(yaw)
        cp, sp = np.cos(pitch), np.sin(pitch)

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

        # Draw slabs back-to-front (highest frac = farthest in midground -> lowest frac = closest foreground)
        for frac, pts3d in reversed(self.slabs):
            if frac > stair_prog:
                continue
            bob = 0.005 * np.sin(1.5 * t - frac * 5.0)
            projected = [proj((x, y + bob, z)) for (x, y, z) in pts3d]
            if any(p is None for p in projected):
                continue
            pts2d = [p[0] for p in projected]

            # Tone shifts gently from misty horizon distance to crisp foreground ivory
            fade = 1.0 - 0.36 * frac
            top_col = (int(232 * fade), int(236 * fade), int(244 * fade))
            front_col = (int(58 * fade), int(64 * fade), int(74 * fade))
            side_col = (int(34 * fade), int(38 * fade), int(46 * fade))
            edge_col = (int(248 * fade), int(250 * fade), int(255 * fade))

            # Side thickness faces
            pygame.draw.polygon(screen, side_col, [pts2d[1], pts2d[2], pts2d[6], pts2d[5]])
            pygame.draw.polygon(screen, side_col, [pts2d[0], pts2d[3], pts2d[7], pts2d[4]])
            # Front riser face
            pygame.draw.polygon(screen, front_col, [pts2d[0], pts2d[1], pts2d[5], pts2d[4]])
            # Top luminous ivory tread
            top_poly = [pts2d[0], pts2d[1], pts2d[2], pts2d[3]]
            pygame.draw.polygon(screen, top_col, top_poly)
            pygame.draw.aalines(screen, edge_col, True, top_poly)


def bloom_pass(surf, k, radius, amount):
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // k), max(1, h // k)))
    if hasattr(pygame.transform, "gaussian_blur"):
        small = pygame.transform.gaussian_blur(small, max(1, radius // k))
    glow = pygame.transform.smoothscale(small, (w, h))
    glow.fill((int(255 * amount),) * 3, special_flags=pygame.BLEND_MULT)
    return glow


def draw_album_emblem(screen, f_en, f_jp, alpha_scale):
    """Draw the signature 'HAWAII: PART II' + rainbow 'ミラクルミュージカル' centerpiece."""
    if alpha_scale <= 0.02:
        return
    w, h = screen.get_size()
    cx, cy = w // 2, int(h * 0.515)

    en_surf = f_en.render("HAWAII: PART II", True, (242, 245, 250))
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

    window = pygame.display.set_mode(win_size)
    pygame.display.set_caption("Hawaii: Part II — Dream Sweet in Sea Major — Kobsi · 2026")

    screen = pygame.Surface((W, H))
    shader = BackdropShader(370, 215)
    elements = PaintedElements()

    mono = "consolas,menlo,dejavusansmono,couriernew,monospace"
    f_hud = pygame.font.SysFont(mono, 16)
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
                        window = pygame.display.set_mode(win_size)
                elif e.key == pygame.K_s:
                    pygame.image.save(screen, str(Path(__file__).with_name(f"hawaii_part_ii_{int(time.time())}.png")))

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                wave_pulse = 1.0
                shoot_timer = 0.0
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
            t += step  # Runs continuously until you close the window or press [R]
            if wave_pulse > 0.0:
                wave_pulse = max(0.0, wave_pulse - step * 0.42)
            if shoot_timer >= 0.0:
                shoot_timer += step * 0.85
                if shoot_timer > 1.0:
                    shoot_timer = -1.0

        # 1. Smooth volumetric sky, god-rays, full moon & Fresnel ocean waves
        horizon_y, cam_shift_x, moon_uv = shader.render(screen, t, user_yaw, user_pitch, wave_pulse)

        # 2. Crisp stars, dust motes & ghostly anglerfish beside the moon
        elements.draw_stars_and_motes(screen, t, horizon_y, cam_shift_x, shoot_timer)
        elements.draw_ghost_anglerfish(screen, t, moon_uv, horizon_y)

        # 3. Orca dorsal fin, silhouetted coconut palms & solid 3D twisted staircase
        elements.draw_orca_fin(screen, t, horizon_y, cam_shift_x)
        elements.draw_palms(screen, t, horizon_y, cam_shift_x)
        elements.draw_staircase(screen, t, user_yaw, user_pitch)

        # 4. Soft atmospheric bloom pass
        screen.blit(bloom_pass(screen, 4, 10, 0.28), (0, 0), special_flags=pygame.BLEND_ADD)

        if show_emblem:
            draw_album_emblem(screen, f_en, f_jp, smooth((t - 4.0) / 2.2))

        # Kobsi · 2026 HUD
        sign_surf = f_hud.render("Kobsi · 2026", True, (186, 196, 210))
        ctrl_surf = f_hud.render("drag orbit · right-click star · [E] emblem · [M] mute · [S] save", True, (124, 134, 148))
        title_surf = f_title.render("Dream Sweet in Sea Major", True, (232, 238, 246))
        time_surf = f_hud.render(f"{'●' if int(t * 2) % 2 == 0 else ' '} t {t:05.2f}s", True, (198, 214, 232))

        screen.blit(sign_surf, (48, H - 64))
        screen.blit(ctrl_surf, (48, H - 38))
        screen.blit(title_surf, (W - 48 - title_surf.get_width(), 30))
        screen.blit(time_surf, (W - 48 - time_surf.get_width(), 60))

        window.blit(screen if win_size == (W, H) else pygame.transform.smoothscale(screen, win_size), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    sys.exit(main())