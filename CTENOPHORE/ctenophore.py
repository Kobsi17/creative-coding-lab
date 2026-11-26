# Ctenophore — The Living Prism — Kobsi · 2026
# Kobsi · @Kobsi17 · 2026. Free for learning and personal projects. See LICENSE.txt.
# Don't repost it or sell it as your own, and don't use it to train AI models.
# Interactive 3D ASCII bioluminescent comb jelly with direct swimming, fluid plankton,
# sonar ripples, iridescent comb rows, and live procedural chimes.
#
# run:   pip install numpy pygame-ce
#        python ctenophore.py
# move:  W/S or Up/Down swim · A/D or Left/Right steer · Q/E dive/ascend · Shift surge
#        C toggle follow-cursor autopilot · Space prism pulse
# mouse: Left-click sonar ripple · Left-drag stir water & gather plankton · Right-drag orbit camera
# other: 1/2/3 sea state · P pause · R reset · S screenshot · F fullscreen · M mute · Esc quit

import sys
import time
from pathlib import Path
import numpy as np
import pygame

TAU = np.pi * 2.0
DRONE_DUR = 18.0

# Density-ramped character pool (dark/delicate -> dense/bright)
POOLS = ["1il!;:", "rtfjcvxz=+", "aeoun0{}[]<>", "08B$#&%Q"]
CHARS = " .,:~+*^01|/\\-_#()x" + "".join(POOLS)
AT = {c: i for i, c in enumerate(CHARS)}
FILL = np.array([[AT[p[k % len(p)]] for k in range(12)] for p in POOLS])

# Color tags: deep abyssal cobalt -> electric cyan -> iridescent prism violet/teal -> pearl
(
    DEEP_WATER,
    DUSK_BLUE,
    COBALT_BODY,
    CYAN_COMB,
    PRISM_TEAL,
    PRISM_VIOLET,
    ICE_GLOW,
    PEARL_PULSE,
    SNOW_DIM,
) = range(9)

PALETTES = {
    0: np.array([  # 1: Abyssal Calm
        [12, 42, 92],     # DEEP_WATER
        [22, 86, 174],    # DUSK_BLUE
        [44, 146, 238],   # COBALT_BODY
        [78, 218, 255],   # CYAN_COMB
        [72, 238, 218],   # PRISM_TEAL
        [152, 138, 255],  # PRISM_VIOLET
        [174, 242, 255],  # ICE_GLOW
        [244, 252, 255],  # PEARL_PULSE
        [96, 152, 214],   # SNOW_DIM
    ], dtype=np.float32) / 255.0,
    1: np.array([  # 2: Prismatic Bloom
        [14, 38, 96],
        [32, 94, 192],
        [54, 162, 246],
        [90, 232, 255],
        [88, 252, 212],
        [192, 136, 255],
        [196, 246, 255],
        [250, 252, 255],
        [118, 176, 236],
    ], dtype=np.float32) / 255.0,
    2: np.array([  # 3: Midnight Surge
        [8, 28, 72],
        [18, 68, 156],
        [36, 128, 228],
        [68, 204, 255],
        [56, 216, 238],
        [124, 118, 248],
        [168, 236, 255],
        [240, 250, 255],
        [82, 134, 198],
    ], dtype=np.float32) / 255.0,
}
STATE_NAMES = ["ABYSSAL CALM", "PRISMATIC BLOOM", "MIDNIGHT SURGE"]


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def rot_x(p, a):
    c, s = np.cos(a), np.sin(a)
    return np.stack([p[:, 0], c * p[:, 1] - s * p[:, 2], s * p[:, 1] + c * p[:, 2]], axis=1)


def rot_y(p, a):
    c, s = np.cos(a), np.sin(a)
    return np.stack([c * p[:, 0] + s * p[:, 2], p[:, 1], -s * p[:, 0] + c * p[:, 2]], axis=1)


def rot_z(p, a):
    c, s = np.cos(a), np.sin(a)
    return np.stack([c * p[:, 0] - s * p[:, 1], s * p[:, 0] + c * p[:, 1], p[:, 2]], axis=1)


# --- Synthesized Deep-Ocean Drone & Live Crystalline Chimes ---
def build_audio():
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
        pygame.mixer.set_num_channels(16)
    except Exception:
        return None, []

    sr = 44100
    n = int(sr * DRONE_DUR)
    tt = np.arange(n, dtype=np.float32) / sr

    # Sub-aquatic C#m9 drone (C#2, G#2, E3, B3, D#4)
    freqs = [69.30, 103.83, 164.81, 246.94, 311.13]
    buf = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        lfo = 0.55 + 0.45 * np.sin(TAU * (0.055 * (i + 1)) * tt + i * 1.2)
        drift = 1.0 + 0.002 * np.sin(TAU * 0.11 * tt + i)
        buf += np.sin(TAU * f * drift * tt) * lfo * (0.10 / (1.0 + 0.25 * i))

    fade_len = int(sr * 1.2)
    fade = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
    buf[:fade_len] *= fade
    buf[-fade_len:] *= fade[::-1]

    left = np.clip(buf * 32767, -32767, 32767).astype(np.int16)
    right = np.roll(left, 580)
    drone = pygame.sndarray.make_sound(np.column_stack((left, right)))

    # Interactive crystalline glass-harp chimes (C# minor pentatonic / 9th)
    chime_freqs = [415.30, 493.88, 554.37, 622.25, 659.25, 830.61, 987.77, 1108.73]
    chimes = []
    cn = int(sr * 2.4)
    tc = np.arange(cn, dtype=np.float32) / sr
    for idx, f in enumerate(chime_freqs):
        env = np.exp(-tc * 2.0) * (1.0 - np.exp(-tc * 110.0))
        tone = (
            0.72 * np.sin(TAU * f * tc)
            + 0.22 * np.sin(TAU * f * 2.0 * tc) * np.exp(-tc * 4.2)
            + 0.06 * np.sin(TAU * f * 3.0 * tc) * np.exp(-tc * 7.5)
        )
        wave = np.clip(tone * env * 0.16 * 32767, -32767, 32767).astype(np.int16)
        pan_shift = 220 + (idx % 4) * 140
        chimes.append(pygame.sndarray.make_sound(np.column_stack((wave, np.roll(wave, pan_shift)))))

    return drone, chimes


# --- Parametric 3D Ctenophore Morphology ---
rng = np.random.default_rng(17)

# Main lobate bell surface: u around circumference, v from aboral apex (0.02) to oral lobes (1.0)
U_BODY, V_BODY = np.meshgrid(np.linspace(0.0, TAU, 136, endpoint=False), np.linspace(0.02, 1.0, 46))
U_BODY, V_BODY = U_BODY.ravel(), V_BODY.ravel()

# 8 comb rows (ctenes): dense cilia plates along 8 meridians
N_COMBS = 8
COMB_U = np.linspace(0.0, TAU, N_COMBS, endpoint=False)
S_COMB = np.linspace(0.08, 0.92, 54)
COMB_U_GRID, COMB_S_GRID = np.meshgrid(COMB_U, S_COMB)
COMB_U_FLAT, COMB_S_FLAT = COMB_U_GRID.ravel(), COMB_S_GRID.ravel()
COMB_IDX_FLAT = np.tile(np.arange(N_COMBS), len(S_COMB))

# Internal statocyst & glowing digestive canals
U_CORE, V_CORE = np.meshgrid(np.linspace(0.0, TAU, 20, endpoint=False), np.linspace(0.05, 0.95, 10))
U_CORE, V_CORE = U_CORE.ravel(), V_CORE.ravel()

# 2 primary lacy feeding tentacles + fine side-filaments (tentilla)
S_TENT = np.linspace(0.0, 1.0, 68)
N_TENTILLA = 18
TENTILLA_ANCHORS = np.linspace(0.18, 0.96, N_TENTILLA)
S_TENTILLA = np.linspace(0.0, 1.0, 10)

# Interactive 3D bioluminescent plankton field
N_PLANKTON = 460


def outline_letter(gx, gy):
    ax, ay = np.abs(gx), np.abs(gy)
    diag = (ax > 0) & (ay > 0)
    horiz = ay >= ax
    ch = np.full(gx.shape, AT["|"], dtype=int)
    ch = np.where(horiz & (gy < 0), AT["-"], ch)
    ch = np.where(horiz & (gy > 0), AT["_"], ch)
    ch = np.where(diag & (gx * gy < 0), AT["/"], ch)
    ch = np.where(diag & (gx * gy > 0), AT["\\"], ch)
    return ch


class CtenophoreWorld:
    """Self-contained 3D ctenophore kinematics, fluid plankton, and sonar ripples."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.t = 0.0
        self.pos = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.vel = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.yaw = 0.25
        self.pitch = 0.08
        self.bank = 0.0
        self.yaw_rate = 0.0
        self.pitch_rate = 0.0
        self.surge = 0.0
        self.feed_glow = 0.0

        self.cam_yaw = -0.42
        self.cam_pitch = 0.22
        self.autopilot = False
        self.sea_state = 0
        self.pulse_count = 0

        # Active expanding bioluminescent pulses along the creature: (start_time, strength)
        self.pulses = [(0.0, 0.9)]
        # Active 3D sonar ripples in water: [x, y, z, start_time, radius_speed]
        self.ripples = []

        # Plankton state (wrapped in a local chamber around the creature)
        self.p_pos = np.c_[
            rng.uniform(-2.8, 2.8, N_PLANKTON),
            rng.uniform(-2.1, 2.1, N_PLANKTON),
            rng.uniform(-2.4, 2.0, N_PLANKTON),
        ].astype(np.float32)
        self.p_vel = np.zeros((N_PLANKTON, 3), dtype=np.float32)
        self.p_phase = rng.uniform(0.0, TAU, N_PLANKTON).astype(np.float32)
        self.p_energy = rng.uniform(0.25, 0.75, N_PLANKTON).astype(np.float32)

        # Tentacle trailing lag state (2 tentacles, each with S_TENT segments in world space)
        self.tent_pts = [np.zeros((len(S_TENT), 3), dtype=np.float32) for _ in range(2)]
        self._init_tentacles()

    def _init_tentacles(self):
        fwd, right, up = self.basis()
        for side_idx, sign in enumerate((-1.0, 1.0)):
            anchor = self.pos + right * (0.36 * sign) - up * 0.24
            for k, s in enumerate(S_TENT):
                self.tent_pts[side_idx][k] = anchor - fwd * (s * 2.15) - up * (s * 0.55)

    def basis(self):
        """Returns (forward, right, up) unit vectors of the ctenophore in world space."""
        cy, sy = np.cos(self.yaw), np.sin(self.yaw)
        cp, sp = np.cos(self.pitch), np.sin(self.pitch)
        fwd = np.array([sy * cp, sp, -cy * cp], dtype=np.float32)
        world_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        right = np.cross(fwd, world_up)
        n = np.linalg.norm(right)
        right = right / n if n > 1e-5 else np.array([1.0, 0.0, 0.0], dtype=np.float32)
        up = np.cross(right, fwd)
        return fwd, right, up

    def trigger_pulse(self, strength=1.0):
        self.pulses.append((self.t, strength))
        if len(self.pulses) > 8:
            self.pulses.pop(0)
        self.pulse_count += 1

    def spawn_ripple(self, ndc_x, ndc_y, aspect):
        """Spawn a 3D sonar ripple near the creature's depth plane."""
        wx = self.pos[0] + ndc_x * 1.9 * aspect
        wy = self.pos[1] - ndc_y * 1.9
        wz = self.pos[2]
        self.ripples.append([wx, wy, wz, self.t, 1.85, False])
        if len(self.ripples) > 6:
            self.ripples.pop(0)

    def stir_water(self, ndc_x, ndc_y, dx_ndc, dy_ndc, aspect, gather=False):
        """Inject fluid swirl & gather plankton near cursor."""
        wx = self.pos[0] + ndc_x * 1.9 * aspect
        wy = self.pos[1] - ndc_y * 1.9
        wz = self.pos[2]
        cursor = np.array([wx, wy, wz], dtype=np.float32)
        diff = self.p_pos - cursor
        dist2 = np.sum(diff * diff, axis=1) + 0.08
        falloff = np.exp(-dist2 * 1.35)

        # Tangential vortex + drag wake
        vortex = np.c_[-diff[:, 1], diff[:, 0], np.zeros_like(diff[:, 0])]
        wake = np.array([dx_ndc * 4.5, -dy_ndc * 4.5, 0.0], dtype=np.float32)
        self.p_vel += (vortex * 1.6 + wake) * falloff[:, None]
        if gather:
            self.p_vel -= diff * (1.8 * falloff[:, None])
        self.p_energy = np.clip(self.p_energy + 0.35 * falloff, 0.2, 1.35)

    def step(self, dt, controls, cursor_ndc, aspect, chimes, muted):
        self.t += dt

        thrust = controls["thrust"]
        turn = controls["turn"]
        elev = controls["elev"]
        boost = controls["boost"]

        # Optional follow-cursor autopilot
        if self.autopilot and cursor_ndc is not None:
            nx, ny = cursor_ndc
            target_yaw = self.cam_yaw + nx * 1.35
            target_pitch = np.clip(-ny * 0.95, -0.75, 0.75)
            dyaw = (target_yaw - self.yaw + np.pi) % TAU - np.pi
            turn = np.clip(dyaw * 1.6, -1.0, 1.0)
            elev = np.clip((target_pitch - self.pitch) * 1.8, -1.0, 1.0)
            dist_center = np.hypot(nx, ny)
            thrust = max(thrust, np.clip(0.35 + dist_center * 0.85, 0.35, 1.0))

        self.surge = self.surge * np.exp(-dt * 4.5) + (1.0 if boost else 0.0) * (1.0 - np.exp(-dt * 6.0))
        self.yaw_rate = self.yaw_rate * np.exp(-dt * 6.0) + turn * 1.65 * (1.0 - np.exp(-dt * 6.0))
        self.pitch_rate = self.pitch_rate * np.exp(-dt * 6.0) + elev * 1.15 * (1.0 - np.exp(-dt * 6.0))

        self.yaw += self.yaw_rate * dt
        self.pitch = float(np.clip(self.pitch + self.pitch_rate * dt, -0.95, 0.95))
        target_bank = -self.yaw_rate * 0.42
        self.bank = self.bank * np.exp(-dt * 5.0) + target_bank * (1.0 - np.exp(-dt * 5.0))

        fwd, right, up = self.basis()
        cilia_beat = 0.24 + 0.16 * np.sin(self.t * (2.6 + self.surge * 3.8))
        accel_mag = thrust * (1.35 + 1.45 * self.surge) + cilia_beat * 0.35
        self.vel += fwd * (accel_mag * dt)
        self.vel *= np.exp(-dt * 1.85)  # viscous deep-water drag
        self.pos += self.vel * dt

        # Update trailing tentacles in world space with smooth spring-follow + water wave
        for side_idx, sign in enumerate((-1.0, 1.0)):
            pts = self.tent_pts[side_idx]
            anchor = self.pos + right * (0.34 * sign) - up * 0.22 - fwd * 0.18
            pts[0] = anchor
            seg_len = 0.036
            for k in range(1, len(S_TENT)):
                s = S_TENT[k]
                wave = (
                    right * (0.012 * np.sin(self.t * 3.2 - s * 7.5 + side_idx * 1.8))
                    + up * (0.009 * np.cos(self.t * 2.5 - s * 6.2 + side_idx * 0.9))
                )
                target = pts[k - 1] - fwd * seg_len + wave * (0.4 + s)
                follow = np.exp(-dt * (18.0 - 9.0 * s))
                pts[k] = pts[k] * follow + target * (1.0 - follow)
                # Enforce max segment stretch so tentacles stay silky
                d = pts[k] - pts[k - 1]
                dist = np.linalg.norm(d)
                if dist > seg_len * 1.45:
                    pts[k] = pts[k - 1] + d * (seg_len * 1.45 / dist)

        # Update plankton field (keep wrapped in a 5.6 x 4.2 x 4.4 box centered on creature)
        drift = np.c_[
            0.03 * np.sin(self.t * 0.6 + self.p_phase),
            0.05 + 0.02 * np.cos(self.t * 0.4 + self.p_phase),
            0.02 * np.sin(self.t * 0.5 - self.p_phase),
        ].astype(np.float32)

        # Creature swimming displaces nearby plankton
        rel = self.p_pos - self.pos
        r2 = np.sum(rel * rel, axis=1) + 0.05
        near_body = np.exp(-r2 * 2.8)
        self.p_vel += (rel * 0.45 + self.vel * 0.35) * near_body[:, None] * dt * 4.0
        self.p_energy = np.clip(self.p_energy + near_body * dt * 1.4, 0.25, 1.4)

        # Feeding glow when swimming through dense plankton
        feed_hit = float(np.sum(near_body))
        self.feed_glow = self.feed_glow * np.exp(-dt * 2.5) + min(1.0, feed_hit * 0.08) * (1.0 - np.exp(-dt * 4.0))

        self.p_vel *= np.exp(-dt * 1.9)
        self.p_pos += (self.p_vel + drift) * dt
        self.p_energy = self.p_energy * np.exp(-dt * 0.35) + 0.35 * (1.0 - np.exp(-dt * 0.35))

        # Wrap plankton seamlessly relative to creature position
        rel = self.p_pos - self.pos
        rel[:, 0] = (rel[:, 0] + 2.8) % 5.6 - 2.8
        rel[:, 1] = (rel[:, 1] + 2.1) % 4.2 - 2.1
        rel[:, 2] = (rel[:, 2] + 2.2) % 4.4 - 2.2
        self.p_pos = self.pos + rel

        # Check sonar ripples hitting the creature
        alive = []
        for rip in self.ripples:
            rx, ry, rz, t0, spd, triggered = rip
            age = self.t - t0
            radius = age * spd
            if age < 2.2:
                if not triggered:
                    dist_c = np.linalg.norm(self.pos - np.array([rx, ry, rz], dtype=np.float32))
                    if abs(radius - dist_c) < 0.32:
                        rip[5] = True
                        self.trigger_pulse(strength=0.95)
                        if chimes and not muted:
                            chimes[self.pulse_count % len(chimes)].play()
                alive.append(rip)
        self.ripples = alive

        # Prune old pulses
        self.pulses = [(t0, st) for (t0, st) in self.pulses if (self.t - t0) < 3.6]

    def _pulse_intensity(self, s_norm):
        """Evaluate combined bioluminescent wave intensity along body coordinate s_norm in [0, 1]."""
        val = np.zeros_like(s_norm)
        for t0, strength in self.pulses:
            age = self.t - t0
            head = age * 0.85
            d = np.abs(s_norm - head)
            val += strength * np.exp(-d * d * 42.0) * np.exp(-age * 0.65)
        return np.clip(val, 0.0, 1.5)

    def render_frame(self, cols, rows, aspect):
        t = self.t
        speed = float(np.linalg.norm(self.vel))
        cilia_hz = 8.5 + speed * 4.2 + self.surge * 9.0

        # --- 1. Lobate Ctenophore Body Surface (local frame: +z forward, +y up) ---
        breath = 1.0 + 0.055 * np.sin(t * 2.4) - 0.07 * self.surge
        # Lobate hourglass profile with 8 subtle flutes
        flute = 1.0 + 0.065 * np.cos(8.0 * U_BODY)
        # Flattened biradial symmetry (oval cross-section)
        rx_scale = 1.18 * breath
        ry_scale = 0.82 * breath
        profile = np.sin(np.pi * V_BODY) ** 0.72
        # Oral lobes flare near v > 0.72
        lobe = np.where(V_BODY > 0.65, 0.14 * smooth((V_BODY - 0.65) / 0.35) * (0.5 + 0.5 * np.cos(2.0 * U_BODY)), 0.0)
        rad = (0.34 * profile + lobe) * flute

        bx = rad * rx_scale * np.cos(U_BODY)
        by = rad * ry_scale * np.sin(U_BODY)
        bz = (0.52 - V_BODY) * 1.08  # +0.50 at aboral apex, -0.54 at oral lobes
        body_local = np.stack([bx, by, bz], axis=1)

        # Normals in local frame
        nx = np.cos(U_BODY) / rx_scale
        ny = np.sin(U_BODY) / ry_scale
        nz = -0.35 * np.cos(np.pi * V_BODY)
        body_n = np.stack([nx, ny, nz], axis=1)
        body_n /= np.linalg.norm(body_n, axis=1, keepdims=True) + 1e-6

        pulse_body = self._pulse_intensity(V_BODY)
        rim = np.power(1.0 - np.abs(body_n[:, 2]), 1.6)
        body_shade = 0.14 + 0.28 * rim + 0.36 * pulse_body + 0.18 * self.feed_glow + 0.16 * self.surge
        body_tag = np.where(
            pulse_body > 0.78,
            PEARL_PULSE,
            np.where(pulse_body > 0.35, ICE_GLOW, np.where(rim > 0.55, COBALT_BODY, DUSK_BLUE)),
        )
        body_kind = np.full(len(U_BODY), 1, dtype=int)

        # --- 2. 8 Iridescent Comb Rows (Ctenes) ---
        c_flute = 1.08
        c_prof = np.sin(np.pi * COMB_S_FLAT) ** 0.72
        c_rad = 0.355 * c_prof * c_flute
        cx = c_rad * rx_scale * np.cos(COMB_U_FLAT)
        cy = c_rad * ry_scale * np.sin(COMB_U_FLAT)
        cz = (0.52 - COMB_S_FLAT) * 1.08
        comb_local = np.stack([cx, cy, cz], axis=1)

        # Metachronal cilia wave + prism diffraction
        wave_phase = COMB_S_FLAT * 14.0 - t * (3.8 + self.surge * 5.2 + speed * 1.8) + COMB_IDX_FLAT * 0.45
        cilia_wave = 0.5 + 0.5 * np.sin(wave_phase)
        pulse_comb = self._pulse_intensity(COMB_S_FLAT)
        comb_shade = 0.55 + 0.48 * (cilia_wave ** 2) + 0.55 * pulse_comb + 0.28 * self.surge + 0.25 * self.feed_glow

        prism_band = (COMB_S_FLAT * 3.0 - t * 0.85 + COMB_IDX_FLAT * 0.125) % 1.0
        comb_tag = np.where(
            pulse_comb > 0.72,
            PEARL_PULSE,
            np.where(
                prism_band < 0.33,
                CYAN_COMB,
                np.where(prism_band < 0.66, PRISM_TEAL, PRISM_VIOLET),
            ),
        )
        comb_kind = np.full(len(COMB_S_FLAT), 2, dtype=int)

        # --- 3. Internal Statocyst & Canals ---
        core_rad = 0.085 * np.sin(np.pi * V_CORE)
        core_local = np.stack([
            core_rad * np.cos(U_CORE),
            core_rad * np.sin(U_CORE) * 0.85,
            (0.45 - V_CORE * 0.75),
        ], axis=1)
        core_pulse = 0.65 + 0.35 * np.sin(t * 3.5) + self._pulse_intensity(V_CORE * 0.5)
        core_shade = 0.50 + 0.45 * core_pulse
        core_tag = np.where(core_pulse > 0.95, PEARL_PULSE, ICE_GLOW)
        core_kind = np.full(len(U_CORE), 3, dtype=int)

        # Transform local creature geometry to world space
        local_xyz = np.vstack([body_local, comb_local, core_local])
        local_xyz = rot_z(local_xyz, self.bank)
        local_xyz = rot_x(local_xyz, self.pitch)
        local_xyz = rot_y(local_xyz, -self.yaw)
        creature_world = local_xyz + self.pos

        # --- 4. Two Lacy Tentacles + Tentilla (already in world space) ---
        tent_xyz_list = []
        tent_shade_list = []
        tent_tag_list = []
        tent_kind_list = []

        fwd, right, up = self.basis()
        for side_idx, sign in enumerate((-1.0, 1.0)):
            pts = self.tent_pts[side_idx]
            p_t = self._pulse_intensity(0.5 + S_TENT * 0.5)
            s_t = (1.0 - S_TENT * 0.55) * (0.48 + 0.55 * p_t + 0.25 * self.surge)
            tg_t = np.where(p_t > 0.65, PEARL_PULSE, np.where(p_t > 0.25, CYAN_COMB, COBALT_BODY))
            tent_xyz_list.append(pts)
            tent_shade_list.append(s_t)
            tent_tag_list.append(tg_t)
            tent_kind_list.append(np.full(len(S_TENT), -1, dtype=int))

            # Fine side-filaments (tentilla) hanging off the main tentacle
            for a_idx, anc in enumerate(TENTILLA_ANCHORS):
                seg_i = int(anc * (len(S_TENT) - 1))
                base = pts[seg_i]
                curtain = (
                    right * (0.09 * sign * S_TENTILLA[:, None])
                    - up * (0.14 * (S_TENTILLA[:, None] ** 1.25))
                    + right * (0.03 * np.sin(t * 3.6 - a_idx * 0.7 + S_TENTILLA * 4.0)[:, None])
                )
                fil = base + curtain
                p_f = self._pulse_intensity(np.full(len(S_TENTILLA), 0.55 + anc * 0.45))
                s_f = (1.0 - S_TENTILLA * 0.65) * (0.36 + 0.48 * p_f)
                tg_f = np.where(p_f > 0.5, ICE_GLOW, PRISM_TEAL)
                tent_xyz_list.append(fil)
                tent_shade_list.append(s_f)
                tent_tag_list.append(tg_f)
                tent_kind_list.append(np.full(len(S_TENTILLA), -1, dtype=int))

        # --- 5. Combine all 3D points & Transform to Camera Space ---
        all_world = np.vstack([creature_world] + tent_xyz_list + [self.p_pos])
        all_shade = np.concatenate([body_shade, comb_shade, core_shade] + tent_shade_list + [self.p_energy * (0.55 + 0.35 * np.sin(t * 2.2 + self.p_phase))])
        all_tag = np.concatenate([body_tag, comb_tag, core_tag] + tent_tag_list + [np.full(N_PLANKTON, SNOW_DIM, dtype=int)])
        all_kind = np.concatenate([body_kind, comb_kind, core_kind] + tent_kind_list + [np.full(N_PLANKTON, -2, dtype=int)])

        # Camera orbits around the ctenophore's position
        rel_cam = all_world - self.pos
        rel_cam = rot_y(rel_cam, self.cam_yaw)
        rel_cam = rot_x(rel_cam, self.cam_pitch)

        z = rel_cam[:, 2] + 2.30
        fov = 2.45
        ok = z > 0.35
        sx = (rel_cam[:, 0] * fov) / (z * aspect)
        sy = -(rel_cam[:, 1] * fov) / z
        ix = ((sx * 0.5 + 0.5) * cols).astype(int)
        iy = ((sy * 0.5 + 0.5) * rows).astype(int)
        ok &= (ix >= 0) & (ix < cols) & (iy >= 0) & (iy < rows)

        depth = np.full((rows, cols), 1e9, dtype=np.float32)
        lum = np.zeros((rows, cols), dtype=np.float32)
        tag = np.zeros((rows, cols), dtype=int)
        part = np.full((rows, cols), -1, dtype=int)

        # Solid/translucent body & comb rows (kind > 0)
        solid = ok & (all_kind > 0)
        if np.any(solid):
            si, sj, sz, ss, st, sk = (a[solid] for a in (iy, ix, z, all_shade, all_tag, all_kind))
            order = np.argsort(-sz)
            si, sj, sz, ss, st, sk = si[order], sj[order], sz[order], ss[order], st[order], sk[order]
            depth[si, sj] = sz
            lum[si, sj] = ss
            tag[si, sj] = st
            part[si, sj] = sk

        # Silhouette edge detection
        body = part > 0
        pp = np.pad(part, 1, constant_values=-1)
        pd = np.pad(depth, 1, constant_values=1e9)
        gx = np.zeros((rows, cols), dtype=int)
        gy = np.zeros((rows, cols), dtype=int)
        edge = np.zeros((rows, cols), dtype=bool)
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
        level = np.clip((lum * 2.5).astype(int), 0, 3)
        inside = FILL[level, (h + (t * 5.2 + h % 11).astype(int)) % 12]
        char = np.where(body, np.where(edge, outline_letter(gx, gy), inside), 0)
        char = np.where(body & (tag == PEARL_PULSE), AT["*"], char)
        lum = np.where(body, np.where(edge, np.maximum(0.72, lum), np.clip(lum, 0.16, 1.32)), 0.0)

        # Fine tentacles (kind == -1) & plankton (kind == -2)
        fx = ok & (all_kind < 0) & (all_shade > 0.05)
        hidden = body[iy[fx], ix[fx]] & (depth[iy[fx], ix[fx]] < z[fx])
        fi, fj, fs, ft, fk = (a[fx][~hidden] for a in (iy, ix, all_shade, all_tag, all_kind))

        tent_ch = np.where(fs > 0.78, AT["*"], np.where(fs > 0.48, AT["+"], np.where(fs > 0.30, AT[":"], AT["."])))
        snow_ch = np.where(fs > 0.62, AT["*"], np.where(fs > 0.42, AT["+"], AT["."]))
        char[fi, fj] = np.where(fk == -1, tent_ch, snow_ch)
        lum[fi, fj] = np.clip(fs, 0.0, 1.25)
        tag[fi, fj] = ft

        # Expanding sonar ripple rings in ASCII space
        for rx, ry, rz, t0, spd, _ in self.ripples:
            age = t - t0
            radius = age * spd
            fade_r = np.exp(-age * 1.15)
            rel_r = np.array([rx, ry, rz], dtype=np.float32) - self.pos
            rel_r = rot_y(rel_r[None, :], self.cam_yaw)[0]
            rel_r = rot_x(rel_r[None, :], self.cam_pitch)[0]
            rz_cam = rel_r[2] + 2.30
            if rz_cam > 0.4:
                cx_ndc = (rel_r[0] * fov) / (rz_cam * aspect)
                cy_ndc = -(rel_r[1] * fov) / rz_cam
                rc_x = (cx_ndc * 0.5 + 0.5) * cols
                rc_y = (cy_ndc * 0.5 + 0.5) * rows
                rad_cells = (radius * fov / rz_cam) * 0.5 * rows
                dist_grid = np.hypot((c - rc_x) * (CW / CH), (r - rc_y))
                ring_mask = (np.abs(dist_grid - rad_cells) < 0.55) & (char == 0)
                char = np.where(ring_mask, AT["~"], char)
                lum = np.where(ring_mask, 0.52 * fade_r, lum)
                tag = np.where(ring_mask, CYAN_COMB, tag)

        # Subtle abyssal water shimmer in empty background cells
        bg = (char == 0) & ((h % 19) == 0)
        shimmer = 0.13 + 0.09 * np.sin(t * 1.4 + r * 0.18 + c * 0.09)
        char = np.where(bg, AT["."], char)
        lum = np.where(bg, shimmer * smooth(t / 1.5), lum)
        tag = np.where(bg, DEEP_WATER, tag)

        depth_m = 1420.0 - self.pos[1] * 18.5
        temp_c = np.clip(2.8 + (1420.0 - depth_m) * 0.012, 1.4, 8.5)
        info = {
            "depth": depth_m,
            "temp": temp_c,
            "cilia": cilia_hz,
            "speed": speed,
            "pulses": self.pulse_count,
            "plankton": N_PLANKTON,
            "mode": "AUTOPILOT" if self.autopilot else "MANUAL",
            "state": STATE_NAMES[self.sea_state],
        }
        count = int((char != 0).sum())
        return char.astype(int), lum.astype(np.float32), tag.astype(int), info, count


# --- Widescreen Window, Horizontal Scanline Glow & Multi-Pass Bloom ---
TITLE = "CTENOPHORE · THE LIVING PRISM · Kobsi"
SIGN = "Kobsi · 2026"
CW, CH, FONT_PX = 7, 11, 12
W, H = 1480, 860
COLS, ROWS = W // CW, H // CH
ASPECT = (COLS * CW) / (ROWS * CH)
TRAIL = 0.46
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

    def draw(self, world):
        char, lum, tag, info, count = world.render_frame(COLS, ROWS, ASPECT)
        palette = PALETTES[world.sea_state]
        mask = self.atlas[char.T].transpose(0, 3, 1, 2).reshape(COLS * CW, ROWS * CH)
        pygame.surfarray.blit_array(self.shape, np.repeat(mask[..., None], 3, 2))
        col = (palette[np.clip(tag, 0, len(palette) - 1)] * np.clip(lum, 0, 1.25)[..., None] * 255).clip(0, 255).astype(np.uint8)
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
    overhead_light = np.exp(-1.7 * x**2 - 4.6 * y)
    pixels = np.array([2, 5, 16]) + overhead_light[..., None] * np.array([5, 19, 34])
    return pygame.transform.smoothscale(pygame.surfarray.make_surface(pixels.astype(np.uint8)), (W, H))


def compose_frame(screen, background, art, small, info, count):
    screen.blit(background, (0, 0))
    screen.blit(art, (0, 0), special_flags=pygame.BLEND_ADD)
    screen.blit(blur_anisotropic(art, 14, 1, 0.34), (0, 0), special_flags=pygame.BLEND_ADD)
    screen.blit(blur_anisotropic(art, 5, 5, 0.24), (0, 0), special_flags=pygame.BLEND_ADD)

    top_left = (
        f"depth {info['depth']:,.1f} m · {info['temp']:.1f} °C · "
        f"cilia {info['cilia']:.1f} Hz · {info['mode']}"
    )
    top_right = f"v {info['speed']:.2f} m/s · {info['state']}"
    bot_stats = f"pulses {info['pulses']:02d}   plankton {info['plankton']}   letters {count:,}"
    bot_hint = "wasd/arrows swim · q/e dive · shift surge · space pulse · c autopilot · click ripple · drag stir · right-drag orbit"

    screen.blit(small.render(top_left, True, CYAN), (58, 22))
    tr = small.render(top_right, True, CYAN)
    screen.blit(tr, (W - 58 - tr.get_width(), 22))
    screen.blit(small.render(SIGN, True, DIM), (58, H - 96))
    screen.blit(small.render(bot_stats, True, CYAN), (58, H - 68))
    screen.blit(small.render(bot_hint, True, DIM), (58, H - 40))


def main():
    pygame.init()
    drone, chimes = build_audio()
    muted = False
    if drone is not None:
        drone.play(loops=-1)

    size = window_size()
    window = pygame.display.set_mode(size)
    pygame.display.set_caption(TITLE)
    screen = pygame.Surface((W, H))
    background = abyss_background()
    small = pygame.font.SysFont(MONO, 16)
    canvas, clock = Canvas(glyphs()), pygame.time.Clock()
    world = CtenophoreWorld()

    paused, fullscreen = False, False
    left_down, right_down = False, False
    prev_mouse = (0, 0)
    art, info, count = canvas.draw(world)

    while True:
        redraw = False
        dt = min(clock.tick(30) / 1000.0, 0.05)

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    paused = not paused
                elif e.key == pygame.K_SPACE:
                    world.trigger_pulse(strength=1.15)
                    if chimes and not muted:
                        chimes[world.pulse_count % len(chimes)].play()
                    redraw = True
                elif e.key == pygame.K_c:
                    world.autopilot = not world.autopilot
                    redraw = True
                elif e.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    world.sea_state = e.key - pygame.K_1
                    redraw = True
                elif e.key == pygame.K_r:
                    world.reset()
                    canvas.reset()
                    redraw = True
                elif e.key == pygame.K_m and drone is not None:
                    muted = not muted
                    drone.set_volume(0.0 if muted else 1.0)
                elif e.key == pygame.K_f:
                    fullscreen = not fullscreen
                    window = pygame.display.set_mode((0, 0) if fullscreen else size, pygame.FULLSCREEN if fullscreen else 0)
                elif e.key == pygame.K_s:
                    out = Path(__file__).parent / f"ctenophore_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    pygame.image.save(screen, str(out))
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                win_w, win_h = window.get_size()
                ndc_x = (mx / max(1, win_w)) * 2.0 - 1.0
                ndc_y = (my / max(1, win_h)) * 2.0 - 1.0
                if e.button == 1:
                    left_down = True
                    prev_mouse = e.pos
                    world.spawn_ripple(ndc_x, ndc_y, ASPECT)
                    if chimes and not muted:
                        chimes[(world.pulse_count + 2) % len(chimes)].play()
                    redraw = True
                elif e.button == 3:
                    right_down = True
                    prev_mouse = e.pos
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    left_down = False
                elif e.button == 3:
                    right_down = False
            elif e.type == pygame.MOUSEMOTION:
                mx, my = e.pos
                dx, dy = mx - prev_mouse[0], my - prev_mouse[1]
                prev_mouse = e.pos
                win_w, win_h = window.get_size()
                ndc_x = (mx / max(1, win_w)) * 2.0 - 1.0
                ndc_y = (my / max(1, win_h)) * 2.0 - 1.0
                if right_down:
                    world.cam_yaw += dx * 0.008
                    world.cam_pitch = float(np.clip(world.cam_pitch + dy * 0.006, -1.1, 1.1))
                    redraw = True
                elif left_down:
                    world.stir_water(ndc_x, ndc_y, dx / max(1, win_w), dy / max(1, win_h), ASPECT, gather=True)

        keys = pygame.key.get_pressed()
        controls = {
            "thrust": (1.0 if (keys[pygame.K_w] or keys[pygame.K_UP]) else 0.0) - (0.6 if (keys[pygame.K_s] or keys[pygame.K_DOWN]) else 0.0),
            "turn": (1.0 if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) else 0.0) - (1.0 if (keys[pygame.K_a] or keys[pygame.K_LEFT]) else 0.0),
            "elev": (1.0 if keys[pygame.K_e] else 0.0) - (1.0 if keys[pygame.K_q] else 0.0),
            "boost": bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]),
        }

        mx, my = pygame.mouse.get_pos()
        win_w, win_h = window.get_size()
        cursor_ndc = ((mx / max(1, win_w)) * 2.0 - 1.0, (my / max(1, win_h)) * 2.0 - 1.0)

        if not paused:
            world.step(dt, controls, cursor_ndc, ASPECT, chimes, muted)
            art, info, count = canvas.draw(world)
        elif redraw:
            art, info, count = canvas.draw(world)

        compose_frame(screen, background, art, small, info, count)
        window.blit(pygame.transform.smoothscale(screen, window.get_size()), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main()
