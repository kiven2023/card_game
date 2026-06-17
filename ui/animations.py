import pygame
import random
import math
from config import *

_font_cache = {}

def _get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


class Particle:
    def __init__(self, x, y, color, vel_x=None, vel_y=None, size=None, life=None, gravity=0, shrink=True):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x if vel_x is not None else random.uniform(-3, 3)
        self.vel_y = vel_y if vel_y is not None else random.uniform(-5, -1)
        self.size = size if size is not None else random.uniform(2, 5)
        self.life = life if life is not None else random.randint(20, 40)
        self.max_life = self.life
        self.gravity = gravity
        self.shrink = shrink

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        r = max(1, int(self.size * (self.life / self.max_life))) if self.shrink else max(1, int(self.size))
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        c = (*self.color[:3], alpha)
        pygame.draw.circle(surf, c, (r, r), r)
        screen.blit(surf, (int(self.x - r), int(self.y - r)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=10, **kwargs):
        for _ in range(count):
            self.particles.append(Particle(x + random.uniform(-5, 5), y + random.uniform(-5, 5), color, **kwargs))

    def emit_burst(self, x, y, colors, count=20, speed=4, **kwargs):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(1, speed)
            color = random.choice(colors)
            self.particles.append(Particle(
                x, y, color,
                vel_x=math.cos(angle) * spd,
                vel_y=math.sin(angle) * spd,
                **kwargs
            ))

    def emit_ring(self, x, y, color, count=16, radius=30, speed=2, **kwargs):
        for i in range(count):
            angle = (math.pi * 2 / count) * i
            self.particles.append(Particle(
                x + math.cos(angle) * radius * 0.3,
                y + math.sin(angle) * radius * 0.3,
                color,
                vel_x=math.cos(angle) * speed,
                vel_y=math.sin(angle) * speed,
                **kwargs
            ))

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

    def clear(self):
        self.particles.clear()


class FloatingText:
    def __init__(self, text, x, y, color=WHITE, size=28, duration=60, bounce=True):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = duration
        self.max_life = duration
        self.bounce = bounce
        self.scale = 0.0
        self.font = _get_font(size)

    def update(self):
        self.life -= 1
        if self.bounce:
            if self.life > self.max_life * 0.8:
                self.scale = min(1.0, self.scale + 0.15)
            elif self.life < self.max_life * 0.3:
                self.y -= 0.5
        else:
            self.y -= 1
        return self.life > 0

    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int(255 * min(1.0, self.life / (self.max_life * 0.4)))
        text_surf = self.font.render(self.text, True, self.color)

        if self.bounce and self.scale < 1.0:
            w = max(1, int(text_surf.get_width() * self.scale))
            h = max(1, int(text_surf.get_height() * self.scale))
            text_surf = pygame.transform.scale(text_surf, (w, h))

        outline_surf = self.font.render(self.text, True, BLACK)
        if self.bounce and self.scale < 1.0:
            w = max(1, int(outline_surf.get_width() * self.scale))
            h = max(1, int(outline_surf.get_height() * self.scale))
            outline_surf = pygame.transform.scale(outline_surf, (w, h))

        cx = self.x - text_surf.get_width() // 2
        cy = self.y - text_surf.get_height() // 2

        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            outline_copy = outline_surf.copy()
            outline_copy.set_alpha(alpha)
            screen.blit(outline_copy, (cx + dx, cy + dy))

        text_surf.set_alpha(alpha)
        screen.blit(text_surf, (cx, cy))


class ShakeEffect:
    def __init__(self):
        self.power = 0
        self.decay = 1

    def trigger(self, power=5, decay=1):
        self.power = power
        self.decay = decay

    def apply(self):
        if self.power <= 0:
            return (0, 0)
        dx = random.randint(-int(self.power), int(self.power))
        dy = random.randint(-int(self.power), int(self.power))
        self.power = max(0, self.power - self.decay)
        return (dx, dy)


class AttackAnimation:
    def __init__(self, attacker, defender, target_pos, is_direct=False):
        self.attacker = attacker
        self.defender = defender
        self.start_pos = (attacker.rect.centerx, attacker.rect.centery)
        self.target_pos = target_pos
        self.is_direct = is_direct
        self.progress = 0.0
        self.speed = 0.08
        self.phase = "lunge"
        self.done = False

    def update(self):
        if self.phase == "lunge":
            self.progress += self.speed
            if self.progress >= 1.0:
                self.progress = 1.0
                self.phase = "return"
        elif self.phase == "return":
            self.progress -= self.speed * 1.5
            if self.progress <= 0.0:
                self.progress = 0.0
                self.done = True
                self.attacker.rect.center = self.start_pos
                return
        t = self.progress
        ease = t * (2 - t) if self.phase == "lunge" else t * (2 - t)
        cx = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * ease
        cy = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * ease
        self.attacker.rect.center = (int(cx), int(cy))

    def draw(self, screen):
        pass


class SummonAnimation:
    def __init__(self, card, target_pos):
        self.card = card
        self.target_pos = target_pos
        self.progress = 0.0
        self.speed = 0.06
        self.done = False

    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.progress = 1.0
            self.done = True

    def draw(self, screen):
        if self.done:
            return
        alpha = int(255 * min(1.0, self.progress * 2))
        scale = 0.5 + 0.5 * min(1.0, self.progress * 1.5)
        w = int(CARD_WIDTH * scale)
        h = int(CARD_HEIGHT * scale)
        glow_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
        glow_alpha = int(180 * (1.0 - self.progress))
        pygame.draw.rect(glow_surf, (100, 200, 255, glow_alpha), (0, 0, w + 20, h + 20), border_radius=8)
        cx = self.target_pos[0] + CARD_WIDTH // 2
        cy = self.target_pos[1] + CARD_HEIGHT // 2
        screen.blit(glow_surf, (cx - (w + 20) // 2, cy - (h + 20) // 2))


class DrawCardAnimation:
    def __init__(self, card, target_pos, is_ai=False):
        self.card = card
        self.target_pos = target_pos
        self.is_ai = is_ai
        self.start_x = SCREEN_WIDTH + 20
        self.start_y = SCREEN_HEIGHT // 2
        self.progress = 0.0
        self.speed = 0.04
        self.done = False
        self.flip_progress = 0.0

    def update(self):
        self.progress += self.speed
        self.flip_progress = min(1.0, self.progress * 2.5)
        if self.progress >= 1.0:
            self.progress = 1.0
            self.done = True

    def draw(self, screen):
        if self.done:
            return
        t = self.progress
        ease = 1 - (1 - t) ** 3
        cx = self.start_x + (self.target_pos[0] - self.start_x) * ease
        cy = self.start_y + (self.target_pos[1] - self.start_y) * ease

        flip = abs(math.sin(self.flip_progress * math.pi))
        if flip < 0.05:
            flip = 0.05
        w = max(1, int(CARD_WIDTH * flip))
        h = CARD_HEIGHT

        card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        if self.is_ai or flip < 0.5:
            pygame.draw.rect(card_surf, (40, 40, 80), (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=6)
            pygame.draw.rect(card_surf, (80, 80, 140), (0, 0, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=6)
            pattern_y = 20
            for py_off in range(0, CARD_HEIGHT - 40, 20):
                pygame.draw.line(card_surf, (60, 60, 110), (10, pattern_y + py_off), (CARD_WIDTH - 10, pattern_y + py_off), 1)
        else:
            saved_rect = self.card.rect.copy()
            self.card.rect.topleft = (0, 0)
            self.card.draw(card_surf)
            self.card.rect = saved_rect

        scaled = pygame.transform.scale(card_surf, (w, h))
        glow_alpha = int(120 * (1.0 - self.progress))
        if glow_alpha > 0:
            glow = pygame.Surface((w + 16, h + 16), pygame.SRCALPHA)
            pygame.draw.rect(glow, (100, 180, 255, glow_alpha), (0, 0, w + 16, h + 16), border_radius=10)
            screen.blit(glow, (int(cx - (w + 16) // 2), int(cy - (h + 16) // 2)))

        screen.blit(scaled, (int(cx - w // 2), int(cy - h // 2)))


class SlashEffect:
    def __init__(self, x, y, color=(255, 255, 200)):
        self.x = x
        self.y = y
        self.color = color
        self.life = 15
        self.max_life = 15
        self.angles = [random.uniform(-0.5, 0.5) for _ in range(3)]

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        progress = 1.0 - (self.life / self.max_life)
        length = 40 + progress * 30

        for angle_off in self.angles:
            angle = -math.pi / 4 + angle_off + progress * 0.3
            surf = pygame.Surface((int(length * 2), int(length * 2)), pygame.SRCALPHA)
            cx, cy = length, length
            x1 = cx + math.cos(angle) * length * 0.8
            y1 = cy + math.sin(angle) * length * 0.8
            x2 = cx - math.cos(angle) * length * 0.3
            y2 = cy - math.sin(angle) * length * 0.3
            width = max(1, int(4 * (self.life / self.max_life)))
            c = (*self.color[:3], alpha)
            pygame.draw.line(surf, c, (int(x1), int(y1)), (int(x2), int(y2)), width)
            screen.blit(surf, (int(self.x - length), int(self.y - length)))


class GlowPulse:
    def __init__(self, x, y, radius=40, color=(100, 200, 255), duration=30):
        self.x = x
        self.y = y
        self.max_radius = radius
        self.color = color
        self.life = duration
        self.max_life = duration

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        if self.life <= 0:
            return
        progress = 1.0 - (self.life / self.max_life)
        alpha = int(150 * (self.life / self.max_life))
        r = int(self.max_radius * (0.5 + 0.5 * progress))
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        for ring in range(3):
            ring_r = max(1, r - ring * 5)
            ring_alpha = max(0, alpha - ring * 40)
            pygame.draw.circle(surf, (*self.color[:3], ring_alpha), (r, r), ring_r, 2)
        screen.blit(surf, (int(self.x - r), int(self.y - r)))


class PhaseBanner:
    def __init__(self, text, color=(255, 255, 255)):
        self.text = text
        self.color = color
        self.life = 45
        self.max_life = 45

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        if self.life <= 0:
            return
        progress = 1.0 - (self.life / self.max_life)
        if progress < 0.15:
            alpha = int(255 * (progress / 0.15))
        elif progress > 0.7:
            alpha = int(255 * (1.0 - (progress - 0.7) / 0.3))
        else:
            alpha = 255

        scale = 1.0 + 0.3 * max(0, 1.0 - progress * 5)
        font = _get_font(72)
        text_surf = font.render(self.text, True, self.color)
        w = max(1, int(text_surf.get_width() * scale))
        h = max(1, int(text_surf.get_height() * scale))
        text_surf = pygame.transform.scale(text_surf, (w, h))
        text_surf.set_alpha(alpha)

        bg_surf = pygame.Surface((w + 60, h + 20), pygame.SRCALPHA)
        bg_alpha = min(alpha, 160)
        pygame.draw.rect(bg_surf, (0, 0, 0, bg_alpha), (0, 0, w + 60, h + 20), border_radius=12)
        border_alpha = min(alpha, 200)
        pygame.draw.rect(bg_surf, (*self.color[:3], border_alpha), (0, 0, w + 60, h + 20), 3, border_radius=12)

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2 - 50
        screen.blit(bg_surf, (cx - (w + 60) // 2, cy - (h + 20) // 2))
        screen.blit(text_surf, (cx - w // 2, cy - h // 2))
