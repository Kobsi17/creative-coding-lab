# Salt Signal — Kobsi · 2026
# Self-contained procedural ASCII storm lighthouse with procedural coastal audio
#
# run:   pip install numpy pygame-ce
#        python salt_signal.py
# keys:  Space pause · R restart · S screenshot · F fullscreen · M mute · Esc quit
# mouse: Left-drag steer lighthouse beam · Right-click storm surge & horn blast

import math
import sys
import time
from pathlib import Path

import numpy as np
import pygame

SIGN = "Kobsi · 2026"
TITLE = "Salt Signal — Kobsi · 2026"

# High-craft Widescreen resolution
WIDTH, HEIGHT = 1480, 860
COLS, ROWS = 185, 86
CELL_W = WIDTH // COLS    # 8
CELL_H = HEIGHT // ROWS   # 10
RENDER_W = COLS * CELL_W  # 1480
RENDER_H = ROWS * CELL_H  # 860

LANTERN = (0.34, 0.35)
SEA_LEVEL = 0.64
TAU = np.pi * 2.0

# ASCII character pool matching Kobsi studio standards
POOLS = ["1il!;:", "rtfjcvxz=+", "aeoun0{}[]<>", "08B$#&%Q"]
GLYPHS = " .,:~+*^01|/\\-_#()x@=" + "".join(POOLS)
AT = {c: i for i, c in enumerate(GLYPHS)}
RAMP = " .,:;+=ox%#@"


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def blur_anisotropic(surf, kw, kh, amount=1.0):
    """Multi-pass anisotropic bloom for atmospheric beam and horizon glow."""
    tw = max(1, surf.get_width() // kw)
    th = max(1, surf.get_height() // kh)
    small = pygame.transform.smoothscale(surf, (tw, th))
    if hasattr(pygame.transform, "gaussian_blur"):
        small = pygame.transform.gaussian_blur(small, max(1, min(kw, kh) // 2))
    layer = pygame.transform.smoothscale(small, surf.get_size())
    if amount < 0.999:
        val = int(np.clip(amount * 255, 0, 255))
        layer.fill((val, val, val), special_flags=pygame.BLEND_RGB_MULT)
    return layer


# --- Procedural Audio Synthesis: Coastal Gale, Rolling Waves, Foghorn & Celesta ---
class CoastalAudio:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.sound = None
        self.horn = None
        self.horn_channel = None
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.enabled = True
            self._build_audio()
        except Exception:
            self.enabled = False

    def _build_audio(self):
        sr = 44100
        dur = 32.0  # continuous seamless musical phrase
        n = int(sr * dur)
        tt = np.arange(n, dtype=np.float32) / sr
        rng = np.random.default_rng(2026)

        # 1. Coastal Wind & Ocean Gale Drone (bandpass filtered noise + resonance)
        noise = rng.normal(0.0, 1.0, n).astype(np.float32)
        wind_kernel = np.ones(320, dtype=np.float32) / 320.0
        wind = np.convolve(noise, wind_kernel, mode="same")
        gust = 0.5 + 0.5 * np.sin(TAU * 0.06 * tt) + 0.3 * np.sin(TAU * 0.14 * tt + 1.2)
        wind_buf = wind * (0.05 + 0.06 * gust)

        # 2. Rhythmic Sea Swell / Waves Breakers
        wave_lfo = np.maximum(0.0, np.sin(TAU * 0.125 * tt)) ** 2.5
        wave_kernel = np.ones(120, dtype=np.float32) / 120.0
        surf = np.convolve(noise, wave_kernel, mode="same") * (wave_lfo * 0.07)

        # 3. Sub-bass Ambient Drone in D-minor (D1, A1, D2, F2)
        drone_freqs = [36.71, 55.00, 73.42, 87.31]
        drone_buf = np.zeros(n, dtype=np.float32)
        for i, f in enumerate(drone_freqs):
            drift = 1.0 + 0.0015 * np.sin(TAU * 0.08 * tt + i)
            amp = 0.045 / (1.0 + 0.4 * i)
            drone_buf += np.sin(TAU * f * drift * tt) * amp

        # 4. Melancholic Celesta / Harp Chimes (D, F, A, C, E)
        chimes = np.zeros(n, dtype=np.float32)
        notes = [
            (2.0, 293.66),   # D4
            (5.5, 349.23),   # F4
            (9.0, 440.00),   # A4
            (13.0, 523.25),  # C5
            (17.5, 440.00),  # A4
            (21.0, 392.00),  # G4
            (25.5, 349.23),  # F4
            (29.0, 329.63),  # E4
        ]
        for start_t, freq in notes:
            idx0 = int(start_t * sr)
            if idx0 < n:
                ring_len = min(n - idx0, int(sr * 4.5))
                tc = np.arange(ring_len, dtype=np.float32) / sr
                env = np.exp(-tc * 1.4) * (1.0 - np.exp(-tc * 80.0))
                chime_tone = 0.7 * np.sin(TAU * freq * tc) + 0.3 * np.sin(TAU * freq * 2.0 * tc) * np.exp(-tc * 2.5)
                chimes[idx0:idx0 + ring_len] += chime_tone * env * 0.038

        master = wind_buf + surf + drone_buf + chimes
        master = np.clip(master, -0.95, 0.95)

        # Stereo field
        stereo = np.zeros((n, 2), dtype=np.int16)
        stereo[:, 0] = (master * 0.92 * 32767.0).astype(np.int16)
        stereo[:, 1] = (master * 1.05 * 32767.0).astype(np.int16)
        self.sound = pygame.sndarray.make_sound(stereo)

        # Procedural Deep Foghorn Sound for Right-Click
        horn_n = int(sr * 3.8)
        horn_t = np.arange(horn_n, dtype=np.float32) / sr
        horn_env = np.sin(np.pi * np.clip(horn_t / 3.8, 0.0, 1.0)) ** 0.55
        h_freq = 58.27  # Bb1 / deep nautical foghorn
        horn_wave = (
            0.65 * np.sin(TAU * h_freq * horn_t)
            + 0.35 * np.sin(TAU * h_freq * 2.0 * horn_t)
            + 0.18 * np.sin(TAU * h_freq * 3.0 * horn_t)
            + 0.08 * np.sin(TAU * h_freq * 4.0 * horn_t)
        )
        sub_rumble = rng.normal(0.0, 0.08, horn_n).astype(np.float32)
        horn_master = np.clip((horn_wave + sub_rumble) * horn_env * 0.42, -0.95, 0.95)
        horn_stereo = np.zeros((horn_n, 2), dtype=np.int16)
        horn_stereo[:, 0] = (horn_master * 32767.0).astype(np.int16)
        horn_stereo[:, 1] = (horn_master * 32767.0).astype(np.int16)
        self.horn = pygame.sndarray.make_sound(horn_stereo)

    def play(self):
        if self.enabled and self.sound is not None:
            self.sound.play(loops=-1)

    def trigger_horn(self):
        if self.enabled and self.horn is not None and not self.muted:
            self.horn.play()

    def set_mute(self, muted):
        self.muted = muted
        if self.enabled and self.sound is not None:
            self.sound.set_volume(0.0 if muted else 1.0)
            if self.horn is not None:
                self.horn.set_volume(0.0 if muted else 1.0)

    def pause(self):
        if self.enabled:
            pygame.mixer.pause()

    def unpause(self):
        if self.enabled:
            pygame.mixer.unpause()


# --- Coast Field & Procedural Rendering Simulation ---
class Coast:
    def __init__(self):
        row, col = np.indices((ROWS, COLS))
        self.x = (col + 0.5) / COLS
        self.y = (row + 0.5) / ROWS
        x, y = self.x, self.y

        rng = np.random.default_rng(2026)
        self.grain = rng.random((ROWS, COLS))
        self.stars_mask = (rng.random((ROWS, COLS)) > 0.978) & (y < 0.46)
        self.stars_brightness = rng.uniform(0.4, 1.0, size=(ROWS, COLS))

        # Rain particles (x, y, speed, length)
        self.n_rain = 140
        self.rain = rng.uniform([0.0, -0.8, 0.6], [1.0, 1.0, 1.8], size=(self.n_rain, 3))

        # Dramatic basalt cliff contours
        self.rock_line = (
            0.88 - 0.36 * np.exp(-((x - 0.28) / 0.24) ** 2)
            + 0.024 * np.sin(58.0 * x)
            + 0.012 * np.sin(116.0 * x)
        )
        self.rock = (x < 0.62) & (y >= self.rock_line)

        # Architectural lighthouse proportions
        taper = 0.022 + 0.038 * np.clip((y - 0.34) / 0.28, 0.0, 1.0)
        self.tower = (y >= 0.35) & (y < 0.63) & (abs(x - LANTERN[0]) < taper)
        self.roof = (y >= 0.28) & (y < 0.315) & (abs(x - LANTERN[0]) < (y - 0.276) * 1.35)
        self.light = (abs(y - LANTERN[1]) < 0.030) & (abs(x - LANTERN[0]) < 0.032)
        self.gallery = (abs(y - 0.345) < 0.007) & (abs(x - LANTERN[0]) < 0.042)
        self.foundation = (y >= 0.62) & (y < 0.66) & (abs(x - LANTERN[0]) < 0.065) & self.rock

    def frame(self, t, aim=None, surge=0.0):
        x, y = self.x, self.y
        dx = x - LANTERN[0]
        dy = y - LANTERN[1]

        # Progressive entrance choreography (0 to 7 seconds)
        entrance_sky = smooth(t / 2.5)
        entrance_structure = smooth((t - 1.8) / 2.8)
        entrance_beam = smooth((t - 4.2) / 2.6)

        # Continuous non-looping motion
        angle = -0.04 + 0.28 * math.sin(t * 0.52) + 0.06 * math.sin(t * 0.19) if aim is None else aim
        distance = np.hypot(dx, dy)

        # Multi-scale drifting marine fog & coastal clouds
        fog = 0.50 + 0.24 * np.sin(9.0 * x + 24.0 * y - 0.45 * t)
        fog += 0.20 * np.sin(18.0 * x - 12.0 * y + 0.28 * t)
        fog += 0.14 * np.sin(32.0 * x + 36.0 * y + 0.18 * t)
        fog = np.clip(fog, 0.0, 1.0)

        # Sky background with twinkling stars
        sky = (0.05 + 0.12 * fog + 0.05 * self.grain) * (0.35 + 0.85 * y) * entrance_sky
        twinkle = 0.7 + 0.3 * np.sin(t * 3.5 + self.grain * 20.0)
        stars = self.stars_mask * self.stars_brightness * twinkle * (1.0 - fog * 0.75) * entrance_sky
        sky += stars * 0.45

        # Volumetric Lighthouse Beam with atmospheric dust scattering
        beam_dist = np.maximum(dx, 0.0)
        beam_width = 0.015 + 0.09 * beam_dist + 0.02 * surge
        beam_center = dx * math.tan(angle)
        beam = np.exp(-((dy - beam_center) / beam_width) ** 2)
        beam *= (dx > 0) * np.exp(-1.45 * beam_dist) * (0.15 + 0.72 * fog + 0.45 * surge)

        # Lantern halo / Fresnel bulb bloom
        halo = (0.75 + 0.55 * surge) * np.exp(-distance * 28.0)
        gold = (beam + halo) * (y < SEA_LEVEL) * entrance_beam

        # Dynamic Ocean Waves & Storm Breakers
        sea_depth = np.maximum(y - SEA_LEVEL, 0.0)
        water = y >= SEA_LEVEL
        wave_freq = 200.0 * np.log1p(7.0 * sea_depth) + 8.0 * np.sin(6.0 * x) - 4.6 * t
        wave = np.sin(wave_freq)
        chop = 0.5 + 0.5 * np.sin(x * (48.0 - 55.0 * sea_depth) - t * 2.2 + y * 32.0)
        foam = np.maximum(wave, 0.0) ** 5.0 * chop * (0.20 + 1.35 * sea_depth + 0.6 * surge)

        # Water specular beam reflection
        reflection_center = LANTERN[0] + 0.22 + 0.52 * angle
        reflection = np.exp(-((x - reflection_center) / (0.045 + sea_depth * 0.7)) ** 2)
        reflection *= (0.25 + 0.75 * np.sin(x * 110.0 + t * 4.0) ** 2)

        water_val = 0.08 + foam * 1.1 + 0.04 * self.grain
        gold = np.where(water, reflection * (foam + 0.35) * (1.8 + surge * 1.2) * entrance_beam, gold)
        value = np.where(water, water_val * entrance_structure, sky)

        # Basalt cliff face & wet rock highlights
        rock_rim = np.exp(-np.maximum(y - self.rock_line, 0.0) * 75.0)
        rock_texture = 0.03 + 0.12 * self.grain + 0.06 * np.sin(x * 82.0 + y * 60.0)
        rock_val = (rock_texture + 0.28 * rock_rim) * entrance_structure
        value = np.where(self.rock, rock_val, value)
        gold *= ~self.rock

        # Architectural Lighthouse Rendering (stripes, shadow, gallery rail)
        stripes = np.sin((y - 0.35) * 58.0) > 0.0
        tower_shade = np.where(stripes, 0.42, 0.23) + 2.8 * dx + 0.12 * self.grain
        rim = np.maximum(dx, 0.0) / 0.055
        value = np.where(self.tower, tower_shade * entrance_structure, value)
        gold = np.where(self.tower, 0.22 * rim * entrance_beam, gold)
        value = np.where(self.roof, (0.34 + 0.10 * self.grain) * entrance_structure, value)
        value = np.where(self.gallery, 0.55 * entrance_structure, value)
        value = np.where(self.foundation, 0.18 + 0.15 * self.grain, value)
        gold = np.where(self.light, (0.92 + 0.18 * self.grain + surge * 0.4) * entrance_beam, gold)

        # ASCII character mapping
        level = (np.clip(value + gold, 0.0, 1.0) * (len(RAMP) - 1)).astype(int)
        glyphs = level.copy()

        # Structural & natural glyph styling
        glyphs[self.roof] = np.where(dx[self.roof] < 0, GLYPHS.index("/"), GLYPHS.index("\\"))
        mullions = self.light & (np.abs(dx) > 0.019)
        glyphs[mullions] = GLYPHS.index("|")
        glyphs[self.light & ~mullions] = GLYPHS.index("@")
        glyphs[self.gallery] = GLYPHS.index("=")

        breakers = water & ~self.rock & (foam > 0.18) & (self.grain > 0.40)
        glyphs[breakers] = GLYPHS.index("~")

        # Drifting rain streaks
        rain_speed = self.rain[:, 2] * (1.0 + 0.5 * surge)
        rain_x = ((self.rain[:, 0] - 0.14 * t * rain_speed) % 1.0 * COLS).astype(int)
        rain_y = ((self.rain[:, 1] + 0.42 * t * rain_speed) % 1.0 * ROWS).astype(int)
        open_air = ~(self.rock | self.roof | self.tower | self.light)[rain_y, rain_x]
        rain_y, rain_x = rain_y[open_air], rain_x[open_air]
        glyphs[rain_y, rain_x] = GLYPHS.index("/")
        value[rain_y, rain_x] = 0.28

        # Dual-tone oceanic atmosphere: Deep abyssal petrol/cyan + incandescent amber gold
        cool_ambient = np.array([28.0, 95.0, 130.0], dtype=np.float32) * (0.32 + 1.70 * value[..., None])
        warm_lamp = np.array([255.0, 185.0, 85.0], dtype=np.float32)
        glow_weight = np.clip(gold * 1.75, 0.0, 1.0)[..., None]
        color = (cool_ambient * (1.0 - glow_weight) + warm_lamp * glow_weight).clip(0.0, 255.0).astype(np.uint8)

        active_glyphs = int(np.count_nonzero(level > 0))
        telemetry = {
            "beam_angle": math.degrees(angle),
            "wind_knots": 24.0 + 12.0 * math.sin(t * 0.3) + surge * 20.0,
            "tide_m": 2.4 + 0.6 * math.sin(t * 0.08),
            "surge": surge,
            "active_glyphs": active_glyphs,
        }
        return glyphs, color, telemetry


# --- Glyph Canvas & Downsampled Atmospheric Bloom ---
class GlyphCanvas:
    def __init__(self):
        font = pygame.font.SysFont("consolas,dejavusansmono,monospace", 14)
        tiles = []
        for char in GLYPHS:
            tile = pygame.Surface((CELL_W, CELL_H))
            glyph = font.render(char, True, (255, 255, 255))
            tile.blit(glyph, glyph.get_rect(center=tile.get_rect().center))
            tiles.append(pygame.surfarray.array3d(tile)[:, :, 0])
        self.atlas = np.stack(tiles)  # shape: (len(GLYPHS), CELL_W, CELL_H)
        self.surface = pygame.Surface((RENDER_W, RENDER_H))
        self.trail = pygame.Surface((RENDER_W, RENDER_H))
        self.trail.fill((0, 0, 0))

    def reset(self):
        self.trail.fill((0, 0, 0))

    def draw(self, glyphs, color):
        # Vectorized atlas mapping to surface
        mask = self.atlas[glyphs.T].transpose(0, 2, 1, 3).reshape(RENDER_W, RENDER_H)
        pygame.surfarray.blit_array(self.surface, np.repeat(mask[..., None], 3, axis=2))
        tint = pygame.surfarray.make_surface(color.transpose(1, 0, 2))
        self.surface.blit(pygame.transform.scale(tint, self.surface.get_size()), (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # Fading trail buffer for smooth beam motion
        self.trail.fill((210, 210, 210), special_flags=pygame.BLEND_RGB_MULT)
        self.trail.blit(self.surface, (0, 0), special_flags=pygame.BLEND_RGB_MAX)
        return self.trail


def get_scaled_window():
    di = pygame.display.Info()
    sw, sh = di.current_w, di.current_h
    scale = min(1.0, (sw * 0.94) / WIDTH, (sh * 0.88) / HEIGHT)
    return int(WIDTH * scale), int(HEIGHT * scale)


def main():
    pygame.init()
    audio = CoastalAudio()
    audio.play()

    size = get_scaled_window()
    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)

    canvas_surf = pygame.Surface((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    coast = Coast()
    glyph_renderer = GlyphCanvas()

    font_hud = pygame.font.SysFont("consolas,dejavusansmono,monospace", 15)
    font_title = pygame.font.SysFont("consolas,dejavusansmono,monospace", 17, bold=True)

    t = 0.0
    paused = False
    fullscreen = False
    muted = False
    surge = 0.0

    while True:
        dt = min(clock.tick(30) / 1000.0, 0.1)
        save = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return sys.exit(0)
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    audio.pause() if paused else audio.unpause()
                elif event.key == pygame.K_r:
                    t = 0.0
                    surge = 0.0
                    glyph_renderer.reset()
                elif event.key == pygame.K_s:
                    save = True
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        di = pygame.display.Info()
                        screen = pygame.display.set_mode((di.current_w, di.current_h), pygame.FULLSCREEN)
                    else:
                        size = get_scaled_window()
                        screen = pygame.display.set_mode(size, pygame.RESIZABLE)
                elif event.key == pygame.K_m:
                    muted = not muted
                    audio.set_mute(muted)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                surge = 1.0
                audio.trigger_horn()
            elif event.type == pygame.VIDEORESIZE and not fullscreen:
                size = (event.w, event.h)
                screen = pygame.display.set_mode(size, pygame.RESIZABLE)

        if not paused:
            t += dt
            if surge > 0.0:
                surge = max(0.0, surge - dt * 0.45)

        # Interactive steering via left click drag
        aim = None
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            cur_w, cur_h = screen.get_size()
            aim = math.atan2(my / cur_h - LANTERN[1], max(0.06, mx / cur_w - LANTERN[0]))
            aim = max(-0.55, min(0.55, aim))

        glyphs, color, telemetry = coast.frame(t, aim, surge)
        art = glyph_renderer.draw(glyphs, color)

        # High-craft composite rendering: Abyssal background + additive glow & bloom passes
        canvas_surf.fill((2, 8, 16))
        canvas_surf.blit(art, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # Multi-pass downsampled Gaussian bloom
        canvas_surf.blit(blur_anisotropic(art, 8, 4, 0.65), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        canvas_surf.blit(blur_anisotropic(art, 16, 8, 0.42), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        canvas_surf.blit(blur_anisotropic(art, 32, 16, 0.25), (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        # --- MANDATORY BRANDING & HUD ---
        # Top-left Title & Status
        title_lbl = font_title.render("S A L T   S I G N A L", True, (240, 205, 140))
        canvas_surf.blit(title_lbl, (52, 34))

        # Top-right live telemetry
        live_dot = "●" if int(t * 2) % 2 == 0 else " "
        tr_text = f"{live_dot} t {t:06.2f}s · beam {telemetry['beam_angle']:+05.1f}° · gale {telemetry['wind_knots']:.1f} kt"
        tr_surf = font_hud.render(tr_text, True, (140, 195, 215))
        canvas_surf.blit(tr_surf, (WIDTH - 52 - tr_surf.get_width(), 36))

        # Bottom-left Kobsi branding & HUD
        hud_y = HEIGHT - 84
        canvas_surf.blit(font_title.render(SIGN, True, (135, 178, 205)), (52, hud_y - 28))
        telemetry_str = f"tide {telemetry['tide_m']:.2f} m   glyphs {telemetry['active_glyphs']:,d}   surge {telemetry['surge']:.2f}"
        canvas_surf.blit(font_hud.render(telemetry_str, True, (100, 145, 168)), (52, hud_y))
        controls_str = "left-drag steer beam · right-click horn surge · space pause · r restart · s save · m mute · f fullscreen"
        canvas_surf.blit(font_hud.render(controls_str, True, (72, 108, 128)), (52, hud_y + 24))

        if save:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            save_path = Path(__file__).with_name(f"salt_signal_{stamp}.png")
            pygame.image.save(canvas_surf, str(save_path))

        # Scale canvas to screen
        screen.blit(pygame.transform.smoothscale(canvas_surf, screen.get_size()), (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main()
