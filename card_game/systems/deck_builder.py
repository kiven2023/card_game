import pygame
from config import *

# 墓地系统（带滚轮）
class GraveyardSystem:
    def __init__(self, game):
        self.game = game
        self.show_graveyard = False
        self.graveyard_rect = pygame.Rect(700, 100, 680, 400)
        self.close_btn_rect = pygame.Rect(1300, 110, 40, 40)
        self.graveyard_clickable_cards = {}
        self.scroll_y = 0  # 滚动偏移
        self.max_scroll = 0

    def draw_graveyard_button(self):
        if self.game.in_menu or self.game.game_over:
            return
        # 1. 再往下移，完全避开日志面板
        self.game.graveyard_btn_rect = pygame.Rect(20, 500, 70, 90)

        # 2. PVZ风格墓碑（石头质感+深色边框）
        pygame.draw.rect(self.game.screen, (100, 100, 110), self.game.graveyard_btn_rect)
        pygame.draw.rect(self.game.screen, (60, 60, 70), self.game.graveyard_btn_rect, 3)

        # 3. 十字居中，不再被文字挡住
        pygame.draw.line(self.game.screen, (220, 220, 220), (55, 510), (55, 560), 4)
        pygame.draw.line(self.game.screen, (220, 220, 220), (40, 535), (70, 535), 4)

        # 4. 文字放在墓碑下方，不遮挡十字
        grave_text = FONT_SMALL.render("墓地", True, WHITE)
        text_rect = grave_text.get_rect(
            center=(self.game.graveyard_btn_rect.centerx, self.game.graveyard_btn_rect.bottom + 15))
        self.game.screen.blit(grave_text, text_rect)

    def draw_graveyard_window(self):
        if not self.show_graveyard:
            return

        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 120))
        self.game.screen.blit(surf, (0, 0))

        pygame.draw.rect(self.game.screen, (20, 20, 40), self.graveyard_rect)
        pygame.draw.rect(self.game.screen, WHITE, self.graveyard_rect, 3)

        title = FONT_MID.render("玩家墓地", True, WHITE)
        self.game.screen.blit(title, (self.graveyard_rect.x + 20, self.graveyard_rect.y + 20))

        pygame.draw.rect(self.game.screen, (200, 0, 0), self.close_btn_rect)
        pygame.draw.rect(self.game.screen, WHITE, self.close_btn_rect, 2)
        x_text = FONT_MID.render("X", True, WHITE)
        self.game.screen.blit(x_text, (self.close_btn_rect.centerx - 8, self.close_btn_rect.centery - 12))

        card_height = 40
        start_y = self.graveyard_rect.y + 80 + self.scroll_y
        self.graveyard_clickable_cards = {}
        visible_cards = []

        for i, card in enumerate(self.game.p1.graveyard):
            cy = start_y + i * card_height
            card_rect = pygame.Rect(self.graveyard_rect.x + 20, cy, 640, card_height - 4)
            if card_rect.bottom > self.graveyard_rect.top + 70 and card_rect.top < self.graveyard_rect.bottom:
                visible_cards.append((card_rect, card, i))

        total_height = len(self.game.p1.graveyard) * card_height
        self.max_scroll = max(0, total_height - 300)

        for card_rect, card, i in visible_cards:
            pygame.draw.rect(self.game.screen, (40, 40, 70), card_rect)
            pygame.draw.rect(self.game.screen, WHITE, card_rect, 1)
            txt = FONT_SMALL.render(f"{card.name}    ATK:{getattr(card,'attack','-')}    HP:{getattr(card,'max_health','-')}", True, WHITE)
            self.game.screen.blit(txt, (card_rect.x + 10, card_rect.y + 8))
            self.graveyard_clickable_cards[i] = (card_rect, card)

    def handle_wheel(self, event):
        if self.show_graveyard:
            self.scroll_y += event.y * 30
            self.scroll_y = min(0, max(-self.max_scroll, self.scroll_y))

    def handle_click(self, e):
        if self.game.in_menu or self.game.game_over:
            return

        if e.type == pygame.MOUSEBUTTONDOWN:
            pos = e.pos
            if hasattr(self.game, 'graveyard_btn_rect') and self.game.graveyard_btn_rect.collidepoint(pos):
                self.show_graveyard = True
                self.scroll_y = 0
                return

            if self.show_graveyard:
                if self.close_btn_rect.collidepoint(pos):
                    self.show_graveyard = False
                    return
                if not self.graveyard_rect.collidepoint(pos):
                    self.show_graveyard = False
                    return
                for idx, (rect, card) in self.graveyard_clickable_cards.items():
                    if rect.collidepoint(pos):
                        self.game.log_panel.add(f"选中墓地：{card.name}（可复活）")
                        return

    def close(self):
        self.show_graveyard = False

# 卡组查看系统（带滚轮）
class DeckViewer:
    def __init__(self, game):
        self.game = game
        self.show_deck = False
        self.deck_rect = pygame.Rect(700, 520, 680, 380)
        self.close_btn_rect = pygame.Rect(1300, 530, 40, 40)
        self.deck_clickable_cards = {}
        self.scroll_y = 0
        self.max_scroll = 0

    def draw_deck_button(self):
        if self.game.in_menu or self.game.game_over:
            return
        # 卡牌大小按钮，放在右下角
        self.game.deck_btn_rect = pygame.Rect(
            SCREEN_WIDTH - CARD_WIDTH - 20,
            SCREEN_HEIGHT - CARD_HEIGHT - 20,
            CARD_WIDTH, CARD_HEIGHT
        )
        pygame.draw.rect(self.game.screen, (40, 40, 60), self.game.deck_btn_rect)
        pygame.draw.rect(self.game.screen, (90, 90, 120), self.game.deck_btn_rect, 2)
        txt = FONT_SMALL.render(f"卡组\n{len(self.game.p1.deck)}", True, WHITE)
        self.game.screen.blit(txt, txt.get_rect(center=self.game.deck_btn_rect.center))

    def draw_deck_window(self):
        if not self.show_deck:
            return

        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 120))
        self.game.screen.blit(surf, (0, 0))

        pygame.draw.rect(self.game.screen, (20, 30, 50), self.deck_rect)
        pygame.draw.rect(self.game.screen, WHITE, self.deck_rect, 3)

        title = FONT_MID.render("卡组剩余卡牌", True, WHITE)
        self.game.screen.blit(title, (self.deck_rect.x + 20, self.deck_rect.y + 20))

        pygame.draw.rect(self.game.screen, (200, 0, 0), self.close_btn_rect)
        pygame.draw.rect(self.game.screen, WHITE, self.close_btn_rect, 2)
        x_text = FONT_MID.render("X", True, WHITE)
        self.game.screen.blit(x_text, (self.close_btn_rect.centerx - 8, self.close_btn_rect.centery - 12))

        card_height = 38
        start_y = self.deck_rect.y + 80 + self.scroll_y
        self.deck_clickable_cards = {}
        visible = []

        for i, card in enumerate(self.game.p1.deck):
            cy = start_y + i * card_height
            cr = pygame.Rect(self.deck_rect.x + 20, cy, 640, card_height - 4)
            if cr.bottom > self.deck_rect.top + 70 and cr.top < self.deck_rect.bottom:
                visible.append((cr, card, i))

        total_h = len(self.game.p1.deck) * card_height
        self.max_scroll = max(0, total_h - 280)

        for cr, card, i in visible:
            pygame.draw.rect(self.game.screen, (50, 50, 80), cr)
            pygame.draw.rect(self.game.screen, WHITE, cr, 1)
            atk = getattr(card, "attack", "-")
            hp = getattr(card, "max_health", "-")
            txt = FONT_SMALL.render(f"{card.name}    ATK:{atk}    HP:{hp}", True, WHITE)
            self.game.screen.blit(txt, (cr.x + 10, cr.y + 8))
            self.deck_clickable_cards[i] = (cr, card)

    def handle_wheel(self, event):
        if self.show_deck:
            self.scroll_y += event.y * 30
            self.scroll_y = min(0, max(-self.max_scroll, self.scroll_y))

    def handle_click(self, e):
        if self.game.in_menu or self.game.game_over:
            return

        if e.type == pygame.MOUSEBUTTONDOWN:
            pos = e.pos
            if hasattr(self.game, 'deck_btn_rect') and self.game.deck_btn_rect.collidepoint(pos):
                self.show_deck = True
                self.scroll_y = 0
                return

            if self.show_deck:
                if self.close_btn_rect.collidepoint(pos):
                    self.show_deck = False
                    return
                if not self.deck_rect.collidepoint(pos):
                    self.show_deck = False
                    return

                for idx, (rect, card) in self.deck_clickable_cards.items():
                    if rect.collidepoint(pos):
                        self.game.log_panel.add(f"选中卡组：{card.name}（可特殊召唤）")
                        return