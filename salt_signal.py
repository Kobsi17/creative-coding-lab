"""Salt Signal, an animated ASCII lighthouse on a storm coast."""

import math
import time
from pathlib import Path

import numpy as np
import pygame

COLS, ROWS = 176, 88
CELL_W, CELL_H = 6, 10
WIDTH, HEIGHT = COLS * CELL_W, ROWS * CELL_H
GLYPHS = " .,:;+=ox%#@/\\|-_"
RAMP = " .,:;+=ox%#@"
LANTERN = (0.382, 0.335)
SEA = 0.65


class Coast:
    def __init__(self):
        row, col = np.indices((ROWS, COLS))
        self.x, self.y = (col + 0.5) / COLS, (row + 0.5) / ROWS
        x, y = self.x, self.y
        rng = np.random.default_rng(27)
        self.grain = rng.random((ROWS, COLS))
        self.rain = rng.uniform([0, -1, 0.5], [1, 1, 1.6], size=(80, 3))
        self.rock_line = (
            0.86 - 0.32 * np.exp(-((x - 0.30) / 0.22) ** 2)
            + 0.018 * np.sin(64 * x) + 0.01 * np.sin(125 * x)
        )
        self.rock = (x < 0.66) & (y >= self.rock_line)
        taper = 0.019 + 0.032 * np.clip((y - 0.35) / 0.24, 0, 1)
        self.tower = (y >= 0.355) & (y < 0.59) & (abs(x - LANTERN[0]) < taper)
        self.roof = (y >= 0.278) & (y < 0.308) & (abs(x - LANTERN[0]) < (y - 0.275) * 1.2)
        self.light = (abs(y - LANTERN[1]) < 0.027) & (abs(x - LANTERN[0]) < 0.029)

    def frame(self, t, aim=None):
        x, y = self.x, self.y
        dx = x - LANTERN[0]
        dy = y - LANTERN[1]
        angle = -0.03 + 0.27 * math.sin(t * 0.57) if aim is None else aim
        distance = np.hypot(dx, dy)
        fog = 0.50 + 0.23 * np.sin(10 * x + 27 * y - 0.48 * t)
        fog += 0.20 * np.sin(20 * x - 14 * y + 0.31 * t)
        fog += 0.13 * np.sin(34 * x + 38 * y + 0.21 * t)
        fog = np.clip(fog, 0, 1)
        sky = (0.06 + 0.13 * fog + 0.06 * self.grain) * (0.45 + y)
        beam = np.exp(-((dy - dx * math.tan(angle)) / (0.016 + 0.095 * abs(dx))) ** 2)
        beam *= (dx > 0) * np.exp(-1.6 * np.maximum(dx, 0)) * (0.12 + 0.67 * fog)
        halo = 0.62 * np.exp(-distance * 30)
        gold = (beam + halo) * (y < SEA)
        sea_depth = np.maximum(y - SEA, 0)
        wave = np.sin(210 * np.log1p(7 * sea_depth) + 8 * np.sin(6 * x) - 5 * t)
        chop = 0.5 + 0.5 * np.sin(x * (52 - 65 * sea_depth) - t * 2 + y * 29)
        foam = np.maximum(wave, 0) ** 6 * chop * (0.18 + 1.25 * sea_depth)
        reflection_center = LANTERN[0] + 0.24 + 0.50 * angle
        reflection = np.exp(-((x - reflection_center) / (0.038 + sea_depth * 0.6)) ** 2)
        water = y >= SEA
        gold = np.where(water, reflection * foam * 1.6, gold)
        value = np.where(water, 0.10 + foam + 0.04 * self.grain, sky)
        rock_rim = np.exp(-np.maximum(y - self.rock_line, 0) * 85)
        rock_value = 0.03 + 0.11 * self.grain + 0.05 * np.sin(x * 88 + y * 65)
        value = np.where(self.rock, rock_value + 0.22 * rock_rim, value)
        gold *= ~self.rock

        # Stripes and shadow give the tower volume at glyph resolution.
        stripes = np.sin((y - 0.36) * 64) > 0
        tower_shade = np.where(stripes, 0.39, 0.21) + 3.1 * dx + 0.12 * self.grain
        rim = np.maximum(dx, 0) / 0.06
        value = np.where(self.tower, tower_shade, value)
        gold = np.where(self.tower, 0.19 * rim, gold)
        value = np.where(self.roof, 0.32 + 0.09 * self.grain, value)
        gold = np.where(self.light, 0.83 + 0.15 * self.grain, gold)
        level = (np.clip(value + gold, 0, 1) * (len(RAMP) - 1)).astype(int)
        glyphs = level.copy()
        glyphs[self.roof] = np.where(dx[self.roof] < 0, GLYPHS.index("/"), GLYPHS.index("\\"))
        mullions = self.light & (np.abs(dx) > 0.020)
        glyphs[mullions] = GLYPHS.index("|")
        glyphs[self.light & ~mullions] = GLYPHS.index("@")
        breakers = water & ~self.rock & (foam > 0.17) & (self.grain > 0.45)
        glyphs[breakers] = GLYPHS.index("_")

        rain_x = ((self.rain[:, 0] - 0.12 * t * self.rain[:, 2]) % 1 * COLS).astype(int)
        rain_y = ((self.rain[:, 1] + 0.39 * t * self.rain[:, 2]) % 1 * ROWS).astype(int)
        open_air = ~(self.rock | self.roof | self.tower | self.light)[rain_y, rain_x]
        rain_y, rain_x = rain_y[open_air], rain_x[open_air]
        glyphs[rain_y, rain_x] = GLYPHS.index("/")
        value[rain_y, rain_x] = 0.23

        cool = np.array([34, 112, 141]) * (0.38 + 1.65 * value[..., None])
        warm = np.array([255, 172, 78])
        glow = np.clip(gold * 1.65, 0, 1)[..., None]
        color = (cool * (1 - glow) + warm * glow).clip(0, 255).astype(np.uint8)
        return glyphs, color


class GlyphCanvas:
    def __init__(self):
        font = pygame.font.SysFont("consolas,dejavusansmono,monospace", 12)
        tiles = []
        for char in GLYPHS:
            tile = pygame.Surface((CELL_W, CELL_H))
            glyph = font.render(char, True, (255, 255, 255))
            tile.blit(glyph, glyph.get_rect(center=tile.get_rect().center))
            tiles.append(pygame.surfarray.array3d(tile)[:, :, 0])
        self.atlas = np.stack(tiles)
        self.surface = pygame.Surface((WIDTH, HEIGHT))

    def draw(self, glyphs, color):
        mask = self.atlas[glyphs.T].transpose(0, 2, 1, 3).reshape(WIDTH, HEIGHT)
        pygame.surfarray.blit_array(self.surface, np.repeat(mask[..., None], 3, axis=2))
        tint = pygame.surfarray.make_surface(color.transpose(1, 0, 2))
        self.surface.blit(pygame.transform.scale(tint, self.surface.get_size()), (0, 0),
                          special_flags=pygame.BLEND_RGB_MULT)
        return self.surface


def main():
    pygame.display.init()
    pygame.font.init()
    try:
        desktop = pygame.display.get_desktop_sizes()[0]
        scale = min(1, desktop[0] * 0.94 / WIDTH, desktop[1] * 0.88 / HEIGHT)
        size = (int(WIDTH * scale), int(HEIGHT * scale))
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Salt Signal | Creative Coding Lab")
        art = pygame.Surface((WIDTH, HEIGHT))
        font = pygame.font.SysFont("consolas,dejavusansmono,monospace", 16)
        title = font.render("S A L T   S I G N A L", True, (226, 196, 148))
        signature = font.render("Kobsi", True, (105, 155, 169))
        coast, canvas, clock = Coast(), GlyphCanvas(), pygame.time.Clock()
        t = 0.0
        paused = False

        while True:
            dt = min(clock.tick(30) / 1000, 0.1)
            save = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        t, paused = 0.0, False
                    elif event.key == pygame.K_s:
                        save = True

            if not paused:
                t += dt
            aim = None
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                aim = math.atan2(my / size[1] - LANTERN[1], max(0.08, mx / size[0] - LANTERN[0]))
                aim = max(-0.55, min(0.55, aim))

            layer = canvas.draw(*coast.frame(t, aim))
            art.fill((3, 12, 20))
            art.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            glow = pygame.transform.smoothscale(layer, (WIDTH // 12, HEIGHT // 12))
            soft_glow = pygame.transform.smoothscale(glow, art.get_size())
            soft_glow.fill((95, 95, 95), special_flags=pygame.BLEND_RGB_MULT)
            art.blit(soft_glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            art.blit(title, (36, 27))
            art.blit(signature, (36, HEIGHT - 46))
            if save:
                path = Path(__file__).with_name(f"salt-signal_{time.time_ns()}.png")
                pygame.image.save(art, str(path))
            screen.blit(art if size == art.get_size() else pygame.transform.smoothscale(art, size), (0, 0))
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
