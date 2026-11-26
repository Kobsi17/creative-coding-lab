import pygame
import colorsys
import math
import random

pygame.init()
WIDTH, HEIGHT = 780, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spiral Galaxy")
clock = pygame.time.Clock()

random.seed(7)
TILT = 0.45
COS_T, SIN_T = math.cos(TILT), math.sin(TILT)

def glow(h, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1, 0.7, v)
    return (int(r * 255), int(g * 255), int(b * 255))

# Pre-generate all galaxy particles in the exact order your turtle script draws them
particles = []

# 1. Background stars (stationary)
for _ in range(140):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    particles.append((x, y, random.randint(1, 2), (255, 255, 255), True))

# 2. Dust
for _ in range(700):
    r = random.gauss(0, 120)
    a = random.uniform(0, 6.283)
    particles.append((r, a, random.randint(1, 2), glow(0.7, 0.3), False))

# 3. Spiral arms (900 * 4 = 3,600 stars, spiraling outward from center)
for i in range(900):
    for k in range(4):
        d = i / 900
        a = k * math.pi / 2 + d * 5.5
        r = 10 + d * 290
        s = 4 + d * 26
        x = r * math.cos(a) + random.gauss(0, s)
        y = r * math.sin(a) + random.gauss(0, s)
        rad = math.hypot(x, y)
        ang = math.atan2(y, x)
        hue = 0.13 - d * 0.55
        v = random.uniform(0.6, 1)
        particles.append((rad, ang, random.randint(1, 2), glow(hue, v), False))

# 4. Core
for _ in range(260):
    r = random.gauss(0, 26)
    a = random.uniform(0, 6.283)
    particles.append((r, a, random.randint(1, 3), glow(0.12), False))

# 5. Sparkles
for _ in range(40):
    r = random.gauss(0, 150)
    a = random.uniform(0, 6.283)
    particles.append((r, a, random.randint(3, 4), (255, 255, 255), False))

# Animation state
spin = 0.0
visible_count = 0
DRAW_SPEED = 45  # Number of new dots revealed per frame (higher = faster reveal)

running = True
while running:
    screen.fill((3, 3, 11))  # #03030b

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Gradually reveal particles until the full galaxy is drawn
    if visible_count < len(particles):
        visible_count = min(len(particles), visible_count + DRAW_SPEED)

    spin += 0.008

    # Draw only the particles revealed so far
    for rad, ang, size, color, is_bg in particles[:visible_count]:
        if is_bg:
            pygame.draw.circle(screen, color, (rad, ang), size)
        else:
            cur_a = ang + spin
            x = rad * math.cos(cur_a)
            y = rad * math.sin(cur_a) * 0.55
            sx = int(WIDTH / 2 + (x * COS_T - y * SIN_T))
            sy = int(HEIGHT / 2 + (x * SIN_T + y * COS_T))
            pygame.draw.circle(screen, color, (sx, sy), size)

    # Light up the bright center orb right after the core stars appear
    if visible_count >= len(particles) - 40:
        pygame.draw.circle(screen, (255, 243, 196), (WIDTH // 2, HEIGHT // 2), 13)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
