import colorsys
import math
import random

import pygame

WIDTH, HEIGHT = 780, 480
TILT = 0.45
COS_T, SIN_T = math.cos(TILT), math.sin(TILT)
PARTICLES_PER_FRAME = 45


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
        particles.append((x, y, rng.randint(1, 2), (255, 255, 255), True))

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
            particles.append((rad, ang, rng.randint(1, 2), glow(hue, v), False))

    # 4. Core
    for _ in range(260):
        r = rng.gauss(0, 26)
        a = rng.uniform(0, 6.283)
        particles.append((r, a, rng.randint(1, 3), glow(0.12), False))

    # 5. Sparkles
    for _ in range(40):
        r = rng.gauss(0, 150)
        a = rng.uniform(0, 6.283)
        particles.append((r, a, rng.randint(3, 4), (255, 255, 255), False))

    return particles


def main():
    pygame.display.init()
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Spiral Galaxy")
        clock = pygame.time.Clock()
        particles = build_particles()
        spin = 0.0
        visible_count = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            screen.fill((3, 3, 11))  # #03030b

            # Gradually reveal particles until the full galaxy is drawn
            if visible_count < len(particles):
                visible_count = min(len(particles), visible_count + PARTICLES_PER_FRAME)

            spin += 0.008

            # Draw only the particles revealed so far
            for first, second, size, color, is_background in particles[:visible_count]:
                if is_background:
                    pygame.draw.circle(screen, color, (first, second), size)
                else:
                    radius, angle = first, second
                    rotated_angle = angle + spin
                    x = radius * math.cos(rotated_angle)
                    y = radius * math.sin(rotated_angle) * 0.55
                    sx = int(WIDTH / 2 + (x * COS_T - y * SIN_T))
                    sy = int(HEIGHT / 2 + (x * SIN_T + y * COS_T))
                    pygame.draw.circle(screen, color, (sx, sy), size)

            # Light up the bright center orb right after the core stars appear
            if visible_count >= len(particles) - 40:
                pygame.draw.circle(screen, (255, 243, 196), (WIDTH // 2, HEIGHT // 2), 13)

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.display.quit()


if __name__ == "__main__":
    main()
