# core/card.py
import pygame
import math
import random
from config import *
from .effect import EffectRegistry
from abc import ABC, abstractmethod

_card_art_cache = {}

def _generate_monster_art(card_id, name, attack, health, width, height):
    width = max(1, width)
    height = max(1, height)
    key = (card_id, width, height)
    if key in _card_art_cache:
        return _card_art_cache[key]

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    seed = hash(card_id) if card_id else hash(name)
    rng = random.Random(seed)

    bg_hue = rng.randint(0, 360)
    bg_r = int(20 + 15 * math.sin(math.radians(bg_hue)))
    bg_g = int(20 + 15 * math.sin(math.radians(bg_hue + 120)))
    bg_b = int(35 + 20 * math.sin(math.radians(bg_hue + 240)))
    pygame.draw.rect(surf, (bg_r, bg_g, bg_b), (0, 0, width, height))

    for layer in range(3):
        layer_alpha = 30 + layer * 20
        cx = width // 2 + rng.randint(-10, 10)
        cy = height // 2 + rng.randint(-10, 10)
        for ring in range(4, 0, -1):
            r = int(min(width, height) * 0.15 * ring / 4 + min(width, height) * 0.1)
            if r < 1:
                continue
            hue_shift = (bg_hue + ring * 30 + layer * 60) % 360
            cr = int(40 + 40 * math.sin(math.radians(hue_shift)))
            cg = int(40 + 40 * math.sin(math.radians(hue_shift + 120)))
            cb = int(60 + 40 * math.sin(math.radians(hue_shift + 240)))
            ring_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (cr, cg, cb, layer_alpha), (r, r), r)
            surf.blit(ring_surf, (cx - r, cy - r))

    body_r = int(min(width, height) * 0.22)
    body_cx = width // 2
    body_cy = int(height * 0.45)
    body_color = (
        min(255, bg_r + 80 + rng.randint(-20, 20)),
        min(255, bg_g + 60 + rng.randint(-20, 20)),
        min(255, bg_b + 100 + rng.randint(-20, 20))
    )
    pygame.draw.ellipse(surf, body_color, (body_cx - body_r, body_cy - body_r, body_r * 2, int(body_r * 2.2)))
    highlight = (min(255, body_color[0] + 40), min(255, body_color[1] + 40), min(255, body_color[2] + 40))
    if body_r > 4:
        pygame.draw.ellipse(surf, highlight, (body_cx - body_r + 4, body_cy - body_r + 4, body_r - 4, int(body_r * 0.8)))

    eye_r = max(2, body_r // 5)
    eye_color = (255, 255, 200)
    pygame.draw.circle(surf, eye_color, (body_cx - eye_r * 2, body_cy - eye_r), eye_r)
    pygame.draw.circle(surf, eye_color, (body_cx + eye_r * 2, body_cy - eye_r), eye_r)
    pupil_color = (20, 20, 40)
    pygame.draw.circle(surf, pupil_color, (body_cx - eye_r * 2, body_cy - eye_r), max(1, eye_r // 2))
    pygame.draw.circle(surf, pupil_color, (body_cx + eye_r * 2, body_cy - eye_r), max(1, eye_r // 2))

    atk_ratio = min(1.0, attack / 3000)
    hp_ratio = min(1.0, health / 3000)
    if atk_ratio > 0.5:
        horn_h = int(10 + atk_ratio * 20)
        horn_color = (min(255, body_color[0] + 60), min(255, body_color[1] + 30), min(255, body_color[2] + 30))
        pygame.draw.polygon(surf, horn_color, [
            (body_cx - body_r // 2, body_cy - body_r),
            (body_cx - body_r // 2 - 5, body_cy - body_r - horn_h),
            (body_cx - body_r // 2 + 8, body_cy - body_r)
        ])
        pygame.draw.polygon(surf, horn_color, [
            (body_cx + body_r // 2, body_cy - body_r),
            (body_cx + body_r // 2 + 5, body_cy - body_r - horn_h),
            (body_cx + body_r // 2 - 8, body_cy - body_r)
        ])

    if hp_ratio > 0.5:
        shield_r = int(body_r * 0.6)
        if shield_r > 0:
            shield_surf = pygame.Surface((shield_r * 2, shield_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (200, 200, 220, 100), (shield_r, shield_r), shield_r)
            pygame.draw.circle(shield_surf, (220, 220, 240, 150), (shield_r, shield_r), shield_r, 2)
            surf.blit(shield_surf, (body_cx + body_r - shield_r, body_cy + body_r // 2 - shield_r))

    for _ in range(8):
        sx = rng.randint(2, max(3, width - 2))
        sy = rng.randint(2, max(3, height - 2))
        star_r = rng.randint(1, 2)
        star_alpha = rng.randint(100, 220)
        star_surf = pygame.Surface((star_r * 2, star_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(star_surf, (255, 255, 255, star_alpha), (star_r, star_r), star_r)
        surf.blit(star_surf, (sx - star_r, sy - star_r))

    _card_art_cache[key] = surf
    return surf


def _generate_spell_art(card_id, name, width, height):
    width = max(1, width)
    height = max(1, height)
    key = ("spell", card_id, width, height)
    if key in _card_art_cache:
        return _card_art_cache[key]

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rng = random.Random(hash(card_id) if card_id else hash(name))

    pygame.draw.rect(surf, (15, 10, 40), (0, 0, width, height))

    cx, cy = width // 2, height // 2
    for ring in range(5, 0, -1):
        r = int(min(width, height) * 0.35 * ring / 5)
        if r < 1:
            continue
        hue = (hash(card_id) * 37 + ring * 60) % 360
        cr = int(60 + 40 * math.sin(math.radians(hue)))
        cg = int(30 + 30 * math.sin(math.radians(hue + 120)))
        cb = int(100 + 50 * math.sin(math.radians(hue + 240)))
        ring_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (cr, cg, cb, 60 + ring * 20), (r, r), r)
        surf.blit(ring_surf, (cx - r, cy - r))

    core_r = max(3, min(width, height) // 8)
    pygame.draw.circle(surf, (200, 180, 255, 200), (cx, cy), core_r)
    for i in range(6):
        angle = math.pi * 2 / 6 * i
        ex = cx + int(math.cos(angle) * min(width, height) * 0.25)
        ey = cy + int(math.sin(angle) * min(width, height) * 0.25)
        pygame.draw.line(surf, (180, 160, 255, 150), (cx, cy), (ex, ey), 2)

    _card_art_cache[key] = surf
    return surf


def _generate_trap_art(card_id, name, width, height):
    width = max(1, width)
    height = max(1, height)
    key = ("trap", card_id, width, height)
    if key in _card_art_cache:
        return _card_art_cache[key]

    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rng = random.Random(hash(card_id) if card_id else hash(name))

    pygame.draw.rect(surf, (30, 10, 15), (0, 0, width, height))

    cx, cy = width // 2, height // 2
    size = int(min(width, height) * 0.3)
    if size > 0:
        points = []
        for i in range(3):
            angle = math.pi * 2 / 3 * i - math.pi / 2
            points.append((cx + int(math.cos(angle) * size), cy + int(math.sin(angle) * size)))
        pygame.draw.polygon(surf, (180, 50, 50, 180), points)
        pygame.draw.polygon(surf, (220, 80, 80, 220), points, 2)
        inner_size = size // 2
        if inner_size > 0:
            inner_points = []
            for i in range(3):
                angle = math.pi * 2 / 3 * i + math.pi / 2
                inner_points.append((cx + int(math.cos(angle) * inner_size), cy + int(math.sin(angle) * inner_size)))
            pygame.draw.polygon(surf, (220, 80, 80, 150), inner_points)

    for _ in range(5):
        ex = rng.randint(5, max(6, width - 5))
        ey = rng.randint(5, max(6, height - 5))
        spark_surf = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(spark_surf, (255, 100, 100, rng.randint(100, 200)), (3, 3), 2)
        surf.blit(spark_surf, (ex - 3, ey - 3))

    _card_art_cache[key] = surf
    return surf


class Card(ABC):
    def __init__(self, card_id, name, card_type, cost, description, image=None):
        self.id = card_id
        self.name = name
        self.card_type = card_type
        self.cost = cost
        self.description = description
        self.image = image
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.owner = None
        self.location = "deck"
        self.dragging = False
        self.face_up = True
        self.highlight = False
        self.selected = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.home_pos = (0, 0)
        self._art_cache = None

    @abstractmethod
    def can_activate(self, game_state):
        pass

    @abstractmethod
    def activate(self, game_state, target=None):
        pass

    def _get_card_colors(self):
        return {
            "monster": ((25, 30, 55), (60, 80, 140), (80, 120, 200)),
            "spell": ((35, 20, 55), (100, 60, 160), (140, 100, 220)),
            "trap": ((40, 15, 20), (140, 50, 60), (200, 80, 90)),
        }

    def _draw_card_frame(self, surface, bg_color, border_color, accent_color):
        r = self.rect
        pygame.draw.rect(surface, bg_color, r, border_radius=6)
        pygame.draw.rect(surface, border_color, r, 2, border_radius=6)

        art_h = int(r.height * 0.55)
        art_w = r.width - 8
        if art_w > 0 and art_h > 22:
            art_rect = pygame.Rect(r.x + 4, r.y + 22, art_w, art_h - 22)
            art_surf = self._get_art(art_rect.width, art_rect.height)
            if art_surf:
                surface.blit(art_surf, art_rect.topleft)

        divider_y = r.y + art_h + 2
        pygame.draw.line(surface, border_color, (r.x + 4, divider_y), (r.x + r.width - 4, divider_y), 1)

        name_surf = FONT_SMALL.render(self.name, True, WHITE)
        name_x = r.x + (r.width - name_surf.get_width()) // 2
        surface.blit(name_surf, (name_x, r.y + 3))

        cost_r = 11
        cost_cx = r.x + r.width - cost_r - 3
        cost_cy = r.y + cost_r + 3
        pygame.draw.circle(surface, (20, 60, 160), (cost_cx, cost_cy), cost_r)
        pygame.draw.circle(surface, (100, 160, 255), (cost_cx, cost_cy), cost_r, 2)
        cost_surf = FONT_SMALL.render(str(self.cost), True, WHITE)
        surface.blit(cost_surf, (cost_cx - cost_surf.get_width() // 2, cost_cy - cost_surf.get_height() // 2))

    def _get_art(self, width, height):
        return None

    def draw(self, surface):
        colors = self._get_card_colors()
        bg, border, accent = colors.get(self.card_type, colors["monster"])
        self._draw_card_frame(surface, bg, border, accent)

    def update(self):
        pass

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "card_type": self.card_type,
            "cost": self.cost,
            "description": self.description
        }


class MonsterCard(Card):
    def __init__(self, card_id, name, cost, attack, health, description,
                 attack_type="melee", effect=None, **kwargs):
        super().__init__(card_id, name, "monster", cost, description, **kwargs)
        self.attack = attack
        self.max_health = health
        self.health = health
        self.attack_type = attack_type
        self.effect = effect
        self.has_attacked = False
        self.summon_sickness = True

    def can_activate(self, game_state):
        return False

    def activate(self, game_state, target=None):
        pass

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def _get_art(self, width, height):
        return _generate_monster_art(self.id, self.name, self.attack, self.max_health, width, height)

    def draw(self, surface):
        r = self.rect
        colors = self._get_card_colors()
        bg, border, accent = colors["monster"]

        pygame.draw.rect(surface, bg, r, border_radius=6)
        pygame.draw.rect(surface, border, r, 2, border_radius=6)

        art_h = int(r.height * 0.55)
        art_w = r.width - 8
        if art_w > 0 and art_h > 22:
            art_rect = pygame.Rect(r.x + 4, r.y + 22, art_w, art_h - 22)
            art_surf = self._get_art(art_rect.width, art_rect.height)
            if art_surf:
                surface.blit(art_surf, art_rect.topleft)

        divider_y = r.y + art_h + 2
        pygame.draw.line(surface, border, (r.x + 4, divider_y), (r.x + r.width - 4, divider_y), 1)

        name_surf = FONT_SMALL.render(self.name, True, WHITE)
        name_x = r.x + (r.width - name_surf.get_width()) // 2
        surface.blit(name_surf, (name_x, r.y + 3))

        cost_r = 11
        cost_cx = r.x + r.width - cost_r - 3
        cost_cy = r.y + cost_r + 3
        pygame.draw.circle(surface, (20, 60, 160), (cost_cx, cost_cy), cost_r)
        pygame.draw.circle(surface, (100, 160, 255), (cost_cx, cost_cy), cost_r, 2)
        cost_surf = FONT_SMALL.render(str(self.cost), True, WHITE)
        surface.blit(cost_surf, (cost_cx - cost_surf.get_width() // 2, cost_cy - cost_surf.get_height() // 2))

        stats_y = r.y + int(r.height * 0.58) + 4

        atk_bg = pygame.Rect(r.x + 3, r.y + r.height - 22, r.width // 2 - 2, 19)
        hp_bg = pygame.Rect(r.x + r.width // 2 + 1, r.y + r.height - 22, r.width // 2 - 4, 19)
        pygame.draw.rect(surface, (120, 30, 30), atk_bg, border_radius=3)
        pygame.draw.rect(surface, (30, 30, 120), hp_bg, border_radius=3)

        atk_surf = FONT_SMALL.render(f"ATK {self.attack}", True, (255, 200, 200))
        hp_color = (200, 200, 255) if self.health >= self.max_health else (255, 100, 100)
        hp_surf = FONT_SMALL.render(f"HP {self.health}", True, hp_color)
        surface.blit(atk_surf, (atk_bg.x + (atk_bg.width - atk_surf.get_width()) // 2, atk_bg.y + 1))
        surface.blit(hp_surf, (hp_bg.x + (hp_bg.width - hp_surf.get_width()) // 2, hp_bg.y + 1))

        if self.health < self.max_health:
            bar_w = r.width - 8
            bar_h = 4
            bar_y = r.y + r.height - 26
            bar_x = r.x + 4
            ratio = max(0, self.health / self.max_health)
            pygame.draw.rect(surface, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
            if ratio > 0:
                bar_color = (0, 200, 0) if ratio > 0.5 else (255, 165, 0) if ratio > 0.25 else (255, 0, 0)
                pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=2)

        if self.location == "field" and (self.has_attacked or self.summon_sickness):
            shade = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 100))
            surface.blit(shade, r.topleft)
            if self.summon_sickness:
                zz_surf = FONT_SMALL.render("ZZ", True, (150, 150, 200))
                surface.blit(zz_surf, (r.x + r.width // 2 - zz_surf.get_width() // 2, r.y + r.height // 2 - zz_surf.get_height() // 2))

        if self.selected:
            glow_surf = pygame.Surface((r.width + 8, r.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (0, 255, 255, 120), (0, 0, r.width + 8, r.height + 8), border_radius=8)
            pygame.draw.rect(glow_surf, (0, 255, 255, 200), (0, 0, r.width + 8, r.height + 8), 3, border_radius=8)
            surface.blit(glow_surf, (r.x - 4, r.y - 4))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "card_type": "monster",
            "cost": self.cost,
            "description": self.description,
            "attack": self.attack,
            "health": self.max_health
        }


class SpellCard(Card):
    def __init__(self, card_id, name, cost, description, effect=None, **kwargs):
        super().__init__(card_id, name, "spell", cost, description, **kwargs)
        self.effect = effect

    def can_activate(self, game_state):
        player = self.owner
        return player.mana >= self.cost

    def activate(self, game_state, target=None):
        if self.effect:
            self.effect.execute(game_state, self, target)
        self.owner.hand.remove(self)
        self.owner.graveyard.append(self)

    def _get_art(self, width, height):
        return _generate_spell_art(self.id, self.name, width, height)

    def draw(self, surface):
        r = self.rect
        colors = self._get_card_colors()
        bg, border, accent = colors["spell"]
        self._draw_card_frame(surface, bg, border, accent)

        type_surf = FONT_SMALL.render("魔法", True, (200, 160, 255))
        surface.blit(type_surf, (r.x + (r.width - type_surf.get_width()) // 2, r.y + r.height - 20))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "card_type": "spell",
            "cost": self.cost,
            "description": self.description
        }


class TrapCard(Card):
    def __init__(self, card_id, name, cost, description, effect=None, **kwargs):
        super().__init__(card_id, name, "trap", cost, description, **kwargs)
        self.effect = effect
        self.face_up = False

    def can_activate(self, game_state):
        return False

    def activate(self, game_state, target=None):
        if self.effect:
            self.effect.execute(game_state, self, target)
        self.owner.field_traps.remove(self)
        self.owner.graveyard.append(self)

    def _get_art(self, width, height):
        return _generate_trap_art(self.id, self.name, width, height)

    def draw(self, surface):
        r = self.rect
        colors = self._get_card_colors()
        bg, border, accent = colors["trap"]
        self._draw_card_frame(surface, bg, border, accent)

        type_surf = FONT_SMALL.render("陷阱", True, (255, 150, 150))
        surface.blit(type_surf, (r.x + (r.width - type_surf.get_width()) // 2, r.y + r.height - 20))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "card_type": "trap",
            "cost": self.cost,
            "description": self.description
        }
