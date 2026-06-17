# ui/components.py
import pygame
from config import *


class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=None, action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        if hover_color is None:
            self.hover_color = (min(color[0]+50,255), min(color[1]+50,255), min(color[2]+50,255))
        else:
            self.hover_color = hover_color
        self.action = action
        self.rect = pygame.Rect(x, y, width, height)
        self.font = FONT_MID

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        current = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, current, self.rect, border_radius=10)
        pygame.draw.rect(screen, (60,60,90), self.rect, 2, border_radius=10)
        if self.text:
            txt = self.font.render(self.text, True, (255,255,255))
            screen.blit(txt, txt.get_rect(center=self.rect.center))

    # 👇 这是你原来代码必须要的方法，我恢复了！
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_clicked(event.pos):
                if self.action:
                    self.action()

class LogPanel:
    def __init__(self, x, y, w, h, max_lines=10):
        self.rect = pygame.Rect(x, y, w, h)
        self.messages = []
        self.max_lines = max_lines
        self.font = FONT_SMALL

    def add(self, msg):
        self.messages.append(msg)
        if len(self.messages) > self.max_lines:
            self.messages.pop(0)

    def draw(self, surface):
        pygame.draw.rect(surface, (30, 30, 50), self.rect)
        pygame.draw.rect(surface, GRAY, self.rect, 2)
        for i, msg in enumerate(self.messages[-self.max_lines:]):
            text_surf = self.font.render(msg, True, WHITE)
            surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5 + i * 24))