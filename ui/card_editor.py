# ui/card_editor.py
import pygame
from config import *
from ui.components import Button
from core.card import MonsterCard, SpellCard, TrapCard


class CardEditor:
    def __init__(self, screen):
        self.screen = screen
        self.active = False
        self.current_card = None
        self.card_type = "monster"  # 默认创建怪兽卡

        # 输入框状态
        self.inputs = {
            "name": {"text": "", "rect": pygame.Rect(400, 150, 300, 40), "active": False},
            "id": {"text": "", "rect": pygame.Rect(400, 200, 300, 40), "active": False},
            "cost": {"text": "", "rect": pygame.Rect(400, 250, 300, 40), "active": False},
            "attack": {"text": "", "rect": pygame.Rect(400, 300, 300, 40), "active": False},
            "health": {"text": "", "rect": pygame.Rect(400, 350, 300, 40), "active": False},
            "description": {"text": "", "rect": pygame.Rect(400, 400, 300, 80), "active": False},
        }

        # 按钮
        self.buttons = {
            "save": Button(400, 500, 140, 50, "保存卡牌", GREEN),
            "cancel": Button(550, 500, 140, 50, "取消", RED),
            "monster": Button(300, 100, 100, 40, "怪兽卡", BLUE),
            "spell": Button(410, 100, 100, 40, "魔法卡", BLUE),
            "trap": Button(520, 100, 100, 40, "陷阱卡", BLUE),
        }

    def handle_events(self, event):
        if not self.active:
            return None

        # 输入框事件
        for key, input_data in self.inputs.items():
            if event.type == pygame.MOUSEBUTTONDOWN:
                input_data["active"] = input_data["rect"].collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and input_data["active"]:
                if event.key == pygame.K_BACKSPACE:
                    input_data["text"] = input_data["text"][:-1]
                elif event.unicode.isprintable():
                    input_data["text"] += event.unicode

        # 按钮事件
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # 卡牌类型选择
            if self.buttons["monster"].is_clicked(pos):
                self.card_type = "monster"
            elif self.buttons["spell"].is_clicked(pos):
                self.card_type = "spell"
            elif self.buttons["trap"].is_clicked(pos):
                self.card_type = "trap"
            # 保存卡牌
            elif self.buttons["save"].is_clicked(pos):
                return self.create_card_from_inputs()
            # 取消
            elif self.buttons["cancel"].is_clicked(pos):
                self.active = False
                self.clear_inputs()
                return None

        return None

    def create_card_from_inputs(self):
        """根据输入创建卡牌"""
        try:
            card_id = self.inputs["id"]["text"]
            name = self.inputs["name"]["text"]
            cost = int(self.inputs["cost"]["text"]) if self.inputs["cost"]["text"] else 0
            description = self.inputs["description"]["text"]

            if self.card_type == "monster":
                attack = int(self.inputs["attack"]["text"]) if self.inputs["attack"]["text"] else 0
                health = int(self.inputs["health"]["text"]) if self.inputs["health"]["text"] else 0
                card = MonsterCard(card_id, name, cost, attack, health, description)
            elif self.card_type == "spell":
                card = SpellCard(card_id, name, cost, description)
            elif self.card_type == "trap":
                card = TrapCard(card_id, name, cost, description)
            else:
                return None

            self.active = False
            self.clear_inputs()
            return card
        except:
            return None

    def clear_inputs(self):
        """清空输入框"""
        for input_data in self.inputs.values():
            input_data["text"] = ""
            input_data["active"] = False

    def draw(self):
        if not self.active:
            return

        # 半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # 编辑器面板
        panel_rect = pygame.Rect(250, 50, 600, 600)
        pygame.draw.rect(self.screen, DARK_BLUE, panel_rect)
        pygame.draw.rect(self.screen, WHITE, panel_rect, 3)

        # 标题
        title = FONT_BIG.render("卡牌编辑器", True, WHITE)
        self.screen.blit(title, (panel_rect.centerx - title.get_width() // 2, 60))

        # 卡牌类型按钮
        self.buttons["monster"].color = GREEN if self.card_type == "monster" else BLUE
        self.buttons["spell"].color = GREEN if self.card_type == "spell" else BLUE
        self.buttons["trap"].color = GREEN if self.card_type == "trap" else BLUE
        self.buttons["monster"].draw(self.screen)
        self.buttons["spell"].draw(self.screen)
        self.buttons["trap"].draw(self.screen)

        # 绘制输入框
        labels = {
            "name": "卡牌名称:",
            "id": "卡牌ID:",
            "cost": "消耗法力:",
            "attack": "攻击力:",
            "health": "生命值:",
            "description": "卡牌描述:"
        }

        y_offset = 150
        for key, input_data in self.inputs.items():
            # 隐藏怪兽卡特有属性（非怪兽卡时）
            if self.card_type != "monster" and key in ["attack", "health"]:
                continue

            # 标签
            label = FONT_MID.render(labels[key], True, WHITE)
            self.screen.blit(label, (300, y_offset + 5))

            # 输入框
            rect = input_data["rect"]
            color = LIGHT_BLUE if input_data["active"] else GRAY
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 2)

            # 输入文本
            text = FONT_MID.render(input_data["text"], True, WHITE)
            self.screen.blit(text, (rect.x + 5, rect.y + 5))

            y_offset += 50 if key != "description" else 90

        # 按钮
        self.buttons["save"].draw(self.screen)
        self.buttons["cancel"].draw(self.screen)

        # 预览卡牌
        preview_rect = pygame.Rect(750, 150, CARD_WIDTH, CARD_HEIGHT)
        if self.card_type == "monster":
            preview_card = MonsterCard(
                "preview", self.inputs["name"]["text"] or "预览卡",
                int(self.inputs["cost"]["text"]) if self.inputs["cost"]["text"] else 0,
                int(self.inputs["attack"]["text"]) if self.inputs["attack"]["text"] else 0,
                int(self.inputs["health"]["text"]) if self.inputs["health"]["text"] else 0,
                           self.inputs["description"]["text"] or "预览描述"
            )
            preview_card.rect = preview_rect
            preview_card.draw(self.screen)