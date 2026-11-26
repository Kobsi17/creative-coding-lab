# Spiral Galaxy — Kobsi · 2026
# Kobsi · @Kobsi17 · 2026. Free for learning and personal projects. See LICENSE.txt.
# Don't repost it or sell it as your own, and don't use it to train AI models.
import colorsys
import math
import random
import time
from pathlib import Path

import pygame

WIDTH, HEIGHT = 780, 480
TILT = 0.45
COS_T, SIN_T = math.cos(TILT), math.sin(TILT)
PARTICLES_PER_SECOND = 2700
ROTATION_SPEED = 0.48
CENTER = (WIDTH // 2, HEIGHT // 2)


def glow(h, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1, 0.7, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def build_particles():
    rng = random.Random(7)
    particles = []

    # Background stars store screen coordinates. The moving particles store
    # a radius and angle in the galaxy's plane.

    # 1. Background stars (stationary)
    for _ in range(140):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT)
        size = rng.randint(1, 2)
        tint = ((95, 115, 157), (155, 172, 206), (180, 151, 133))[x % 3]
        particles.append((x, y, size if x % 7 == 0 else 1, tint, True))

    # 2. Dust
    for _ in range(700):
        r = rng.gauss(0, 120)
        a = rng.uniform(0, 6.283)
        particles.append((r, a, rng.randint(1, 2), glow(0.7, 0.3), False))

    # 3. Spiral arms (900 * 4 = 3,600 stars, spiraling outward from center)
    for i in range(900):
        for k in range(4):
            d = i / 900
            a = k * math.pi / 2 + d * 5.5
            r = 10 + d * 290
            s = 4 + d * 26
            x = r * math.cos(a) + rng.gauss(0, s)
            y = r * math.sin(a) + rng.gauss(0, s)
            rad = math.hypot(x, y)
            ang = math.atan2(y, x)
            hue = 0.13 - d * 0.55
            v = rng.uniform(0.6, 1)
            size = rng.randint(1, 2)
            particles.append((rad, ang, size if v > 0.84 else 1, glow(hue, v), False))

    # 4. Core
    for _ in range(260):
        r = rng.gauss(0, 26)
        a = rng.uniform(0, 6.283)
        particles.append((r, a, rng.randint(1, 3), glow(0.12), False))

    # 5. Sparkles
    for _ in range(40):
        r = rng.gauss(0, 150)
        a = rng.uniform(0, 6.283)
        size = rng.randint(3, 4)
        particles.append((r, a, size - 2, (221, 233, 255), False))

    return particles


def main():
    pygame.display.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Spiral Galaxy")
        clock = pygame.time.Clock()
        particles = build_particles()
        light = pygame.Surface((WIDTH // 4, HEIGHT // 4))
        elapsed = 0.0
        paused = False

        while True:
            dt = min(clock.tick(60) / 1000, 0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        elapsed = 0.0
                        paused = False
                    elif event.key == pygame.K_s:
                        path = Path(__file__).with_name(f"spiral-galaxy_{time.time_ns()}.png")
                        pygame.image.save(screen, str(path))

            if not paused:
                elapsed += dt
            spin = elapsed * ROTATION_SPEED
            visible_count = min(len(particles), int(elapsed * PARTICLES_PER_SECOND))

            screen.fill((3, 3, 11))
            light.fill((0, 0, 0))

            # Draw only the particles revealed so far
            for first, second, size, color, is_background in particles[:visible_count]:
                if is_background:
                    pygame.draw.circle(screen, color, (first, second), size)
                else:
                    radius, angle = first, second
                    rotated_angle = angle + spin
                    x = radius * math.cos(rotated_angle)
                    y = radius * math.sin(rotated_angle) * 0.55
                    sx = int(CENTER[0] + x * COS_T - y * SIN_T)
                    sy = int(CENTER[1] + x * SIN_T + y * COS_T)
                    pygame.draw.circle(screen, color, (sx, sy), size)
                    if size > 1:
                        pygame.draw.circle(light, tuple(channel // 5 for channel in color), (sx // 4, sy // 4), 1)

            # Grow the central light as the core particles are revealed.
            core_start = len(particles) - 300
            core_light = min(1.0, max(0.0, (visible_count - core_start) / 260))
            if core_light:
                source = (CENTER[0] // 4, CENTER[1] // 4)
                for radius, color in ((14, (14, 5, 8)), (9, (40, 16, 12)),
                                      (5, (90, 44, 25)), (2, (150, 95, 50))):
                    pygame.draw.circle(light, tuple(int(channel * core_light) for channel in color), source, radius)
                pygame.draw.circle(screen, (255, 237, 190), CENTER, max(1, int(3 * core_light)))

            screen.blit(pygame.transform.smoothscale(light, screen.get_size()), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            pygame.display.flip()
    finally:
        pygame.display.quit()


if __name__ == "__main__":
    main()
