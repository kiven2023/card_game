import pygame
from config import *
from ui.components import Button

class DeckEditor:
    def __init__(self, screen, all_cards):
        self.screen = screen
        self.all_cards = all_cards or []
        self.decks = {"main": []}
        self.current_deck = "main"
        self.main_card_ids = []

        self.active = False
        self.selected_card_id = None

        # 新增：设置为出战卡组按钮
        self.buttons = {
            "back": Button(1200, 800, 140, 50, "返回菜单", RED),
            "save": Button(1030, 800, 140, 50, "保存卡组", GREEN),
            "set_active": Button(860, 800, 140, 50, "设为出战", (255, 215, 0)),
            "new_deck": Button(690, 800, 140, 50, "新建卡组", BLUE),
            "del_deck": Button(520, 800, 140, 50, "删除卡组", (180,20,20)),
            "remove_one": Button(350, 800, 140, 50, "移除单张", ORANGE),
        }

        self.left_rect = pygame.Rect(30, 100, 520, 650)
        self.right_rect = pygame.Rect(580, 100, 520, 650)
        self.cards_per_row = 4
        self.cards_per_col = 3

    def set_cards(self, cards):
        self.all_cards = cards or []

    def set_decks(self, decks):
        self.decks = decks
        if self.current_deck not in self.decks and self.decks:
            self.current_deck = list(self.decks.keys())[0]
        self.main_card_ids = self.decks.get(self.current_deck, [])

    def get_card_by_id(self, cid):
        for c in self.all_cards:
            if isinstance(c, dict) and c.get("id") == cid:
                return c
        return None

    def handle_events(self, e):
        if not self.active:
            return None

        if e.type == pygame.MOUSEBUTTONDOWN:
            pos = e.pos

            # 1. 按钮事件
            if self.buttons["back"].is_clicked(pos):
                return {"type": "back"}
            if self.buttons["save"].is_clicked(pos):
                self.decks[self.current_deck] = self.main_card_ids.copy()
                return {"type": "save", "decks": self.decks}
            if self.buttons["set_active"].is_clicked(pos):
                return {"type": "set_active", "deck_name": self.current_deck}
            if self.buttons["new_deck"].is_clicked(pos):
                new_name = f"deck_{len(self.decks)+1}"
                self.decks[new_name] = []
                self.current_deck = new_name
                self.main_card_ids = []
                self.selected_card_id = None
            if self.buttons["del_deck"].is_clicked(pos):
                if len(self.decks) > 1:
                    del self.decks[self.current_deck]
                    self.current_deck = list(self.decks.keys())[0]
                    self.main_card_ids = self.decks[self.current_deck].copy()
                    self.selected_card_id = None
            if self.buttons["remove_one"].is_clicked(pos):
                if self.selected_card_id in self.main_card_ids:
                    self.main_card_ids.remove(self.selected_card_id)
                self.selected_card_id = None

            # 2. 左侧卡牌添加
            if self.left_rect.collidepoint(pos):
                idx = self._get_card_idx(pos, self.left_rect, self.all_cards)
                if idx is not None:
                    cid = self.all_cards[idx]["id"]
                    if cid not in self.main_card_ids:
                        self.main_card_ids.append(cid)

            # 3. 右侧卡组选中
            if self.right_rect.collidepoint(pos):
                deck_cards = [self.get_card_by_id(cid) for cid in self.main_card_ids]
                idx = self._get_card_idx(pos, self.right_rect, deck_cards)
                if idx is not None:
                    self.selected_card_id = self.main_card_ids[idx]

        # 滚轮切换卡组
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 4 or e.button == 5:
                deck_list = list(self.decks.keys())
                idx = deck_list.index(self.current_deck)
                new_idx = (idx + 1) % len(deck_list) if e.button == 4 else (idx - 1) % len(deck_list)
                self.current_deck = deck_list[new_idx]
                self.main_card_ids = self.decks[self.current_deck].copy()
                self.selected_card_id = None

        return None

    def _get_card_idx(self, pos, rect, card_list):
        if not rect.collidepoint(pos):
            return None
        x0, y0 = rect.x + 10, rect.y + 10
        cw, ch = CARD_WIDTH + 20, CARD_HEIGHT + 20
        max_idx = self.cards_per_row * self.cards_per_col

        for i, _ in enumerate(card_list):
            if i >= max_idx:
                continue
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            cx = x0 + col * cw
            cy = y0 + row * ch
            if pygame.Rect(cx, cy, CARD_WIDTH, CARD_HEIGHT).collidepoint(pos):
                return i
        return None

    def draw_card_list(self, rect, card_list, is_deck=False):
        pygame.draw.rect(self.screen, (25,25,55), rect)
        pygame.draw.rect(self.screen, WHITE, rect, 2)

        title = "当前卡组内容" if is_deck else "所有自定义卡牌"
        t = FONT_MID.render(title, True, WHITE)
        self.screen.blit(t, (rect.x, rect.y - 30))

        x0, y0 = rect.x + 10, rect.y + 10
        cw, ch = CARD_WIDTH + 20, CARD_HEIGHT + 20
        max_idx = self.cards_per_row * self.cards_per_col

        for i, card in enumerate(card_list):
            if not card or i >= max_idx:
                continue
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            x = x0 + col * cw
            y = y0 + row * ch

            pygame.draw.rect(self.screen, (50,50,110), (x,y,CARD_WIDTH,CARD_HEIGHT))
            pygame.draw.rect(self.screen, WHITE, (x,y,CARD_WIDTH,CARD_HEIGHT), 1)

            if is_deck and card.get("id") == self.selected_card_id:
                pygame.draw.rect(self.screen, GREEN, (x,y,CARD_WIDTH,CARD_HEIGHT), 3)

            name = card.get("name", "?")
            cost = str(card.get("cost", 0))
            t1 = FONT_SMALL.render(name[:8], True, WHITE)
            t2 = FONT_SMALL.render(f"Cost:{cost}", True, WHITE)
            self.screen.blit(t1, (x+5, y+5))
            self.screen.blit(t2, (x+5, y+28))

    def draw(self):
        if not self.active:
            return
        self.screen.fill((15,15,35))

        # 顶部标题 + 卡组信息
        title = FONT_BIG.render("卡组编辑器", True, WHITE)
        self.screen.blit(title, (30, 20))
        deck_txt = FONT_MID.render(f"当前卡组：{self.current_deck}  (滚轮可切换)", True, (220,220,100))
        count_txt = FONT_MID.render(f"卡牌总数：{len(self.main_card_ids)}/40", True, (150,220,150))
        self.screen.blit(deck_txt, (30, 70))
        self.screen.blit(count_txt, (30, 100))

        # 绘制卡牌列表
        self.draw_card_list(self.left_rect, self.all_cards, is_deck=False)
        deck_cards = [self.get_card_by_id(cid) for cid in self.main_card_ids]
        self.draw_card_list(self.right_rect, deck_cards, is_deck=True)

        # 绘制按钮
        for btn in self.buttons.values():
            btn.draw(self.screen)

        pygame.display.flip()