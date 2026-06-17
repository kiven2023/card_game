import pygame
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from core.card import MonsterCard, SpellCard, TrapCard
from core.player import Player
from core.effect import EffectRegistry
from systems.turn_manager import TurnManager, Phase
from systems.summon_manager import SummonManager
from core.battle import BattleManager
from ui.components import Button, LogPanel
from ui.animations import (
    FloatingText, ShakeEffect, ParticleSystem,
    AttackAnimation, SummonAnimation, DrawCardAnimation,
    SlashEffect, GlowPulse, PhaseBanner
)
from core.ai import AIController
from core.data_manager import load_custom_cards, save_custom_cards, load_custom_decks, save_custom_decks, get_card_by_id
from ui.card_editor import CardEditor
from ui.deck_editor import DeckEditor
from systems.deck_builder import GraveyardSystem, DeckViewer
from ui.windows import EndBattleWindow, VictoryWindow

class Game:
    def __init__(self, screen, mode="ai"):
        self.screen = screen
        self.mode = mode
        self.p1 = Player("玩家")
        self.p2 = Player("AI", is_ai=(mode == "ai"))
        self.ai_avatar_rect = pygame.Rect(20, 20, 250, 80)
        self.ai_turn_in_progress = False
        self.selected_attacker = None
        self.turn_manager = TurnManager(self.p1, self.p2, self)
        self.summon_manager = SummonManager()
        self.battle_manager = BattleManager()
        self.ai_controller = AIController(self.p2, self) if mode == "ai" else None

        self.particles = ParticleSystem()
        self.floating_texts = []
        self.slash_effects = []
        self.glow_pulses = []
        self.phase_banners = []
        self.attack_anims = []
        self.summon_anims = []
        self.draw_card_anims = []
        self.shake = ShakeEffect()
        self.dragged_card = None

        self.custom_cards = load_custom_cards()
        self.custom_decks = load_custom_decks()

        self.card_editor = CardEditor(screen)
        self.deck_editor = DeckEditor(screen, self.custom_cards)
        self.deck_editor.set_decks(self.custom_decks)

        self.menu_buttons = {
            "edit_card": Button(SCREEN_WIDTH//2 - 110, 400, 220, 60, "编辑卡牌", BLUE),
            "edit_deck": Button(SCREEN_WIDTH//2 - 110, 480, 220, 60, "编辑卡组", BLUE),
            "start_game": Button(SCREEN_WIDTH//2 - 120, 580, 240, 70, "开始游戏", (0, 220, 100)),
        }

        self.log_panel = LogPanel(20, 120, 300, 330, max_lines=12)
        self.end_battle_window = EndBattleWindow(self.screen)
        self.victory_window = VictoryWindow(self.screen)

        self.in_menu = True
        self.phase_btn = Button(1080, 500, 180, 50, "")
        self.update_phase_button_text()
        self.init_test_deck()

        self.game_over = False
        self.winner = None

        self.graveyard_sys = GraveyardSystem(self)
        self.deck_viewer = DeckViewer(self)

        self.menu_bg = None
        self._build_menu_bg()

    def _build_menu_bg(self):
        self.menu_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            r = int(12 + y * 0.03)
            g = int(15 + y * 0.03)
            b = int(45 + y * 0.05)
            pygame.draw.line(self.menu_bg, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def start_draw_animation(self, card, target_pos, is_ai=False):
        self.draw_card_anims.append(DrawCardAnimation(card, target_pos, is_ai))

    def trigger_summon_effect(self, card, target_pos):
        self.summon_anims.append(SummonAnimation(card, target_pos))
        self.particles.emit_burst(
            target_pos[0] + CARD_WIDTH // 2, target_pos[1] + CARD_HEIGHT // 2,
            colors=[(100, 200, 255), (150, 220, 255), (80, 160, 220)],
            count=20, speed=4, gravity=0.05, life=30
        )
        self.glow_pulses.append(GlowPulse(
            target_pos[0] + CARD_WIDTH // 2, target_pos[1] + CARD_HEIGHT // 2,
            radius=50, color=(100, 200, 255), duration=25
        ))

    def update_draw_animation(self):
        remaining = []
        for anim in self.draw_card_anims:
            anim.update()
            if anim.done:
                if not anim.is_ai:
                    self.p1.hand.append(anim.card)
                else:
                    self.p2.hand.append(anim.card)
            else:
                remaining.append(anim)
        self.draw_card_anims = remaining

    def init_test_deck(self):
        self.p1.deck.clear()
        self.p2.deck.clear()

    def back_to_main_menu(self):
        self.__init__(self.screen, self.mode)
        self.in_menu = True
        self.game_over = False

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if self.card_editor.active:
                new_card = self.card_editor.handle_events(e)
                if new_card:
                    self.custom_cards.append(new_card.to_dict())
                    save_custom_cards(self.custom_cards)
                    self.deck_editor.set_cards(self.custom_cards)
                return

            if self.deck_editor.active:
                deck_action = self.deck_editor.handle_events(e)
                if deck_action:
                    if deck_action["type"] == "save":
                        self.custom_decks = deck_action["decks"]
                        save_custom_decks(self.custom_decks)
                    elif deck_action["type"] == "back":
                        self.deck_editor.active = False
                        self.in_menu = True
                    elif deck_action["type"] == "set_active":
                        self.active_deck = deck_action["deck_name"]
                return

            if self.in_menu:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.menu_buttons["edit_card"].is_clicked(pos):
                        self.card_editor.active = True
                    elif self.menu_buttons["edit_deck"].is_clicked(pos):
                        self.deck_editor.active = True
                        self.deck_editor.set_cards(self.custom_cards)
                        self.deck_editor.set_decks(self.custom_decks)
                    elif self.menu_buttons["start_game"].is_clicked(pos):
                        self.in_menu = False
                        self.init_custom_deck()
                continue

            if e.type == pygame.MOUSEWHEEL:
                self.graveyard_sys.handle_wheel(e)
                self.deck_viewer.handle_wheel(e)

            if self.game_over:
                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.back_to_main_menu()
                continue

            self.graveyard_sys.handle_click(e)
            self.deck_viewer.handle_click(e)

            if self.graveyard_sys.show_graveyard or self.deck_viewer.show_deck:
                continue

            if e.type == pygame.MOUSEBUTTONDOWN:
                if self.end_battle_window.handle_click(e.pos, self):
                    return

            self.handle_drag_events(e)

            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = e.pos
                if self.phase_btn.is_clicked(pos):
                    if not self.turn_manager.current_player.is_ai:
                        old_phase = self.turn_manager.phase
                        self.turn_manager.next_phase()
                        self.update_phase_button_text()
                        new_phase = self.turn_manager.phase
                        if new_phase != old_phase:
                            self._show_phase_banner(new_phase)
                    return

                if self.turn_manager.phase == Phase.BATTLE and not self.turn_manager.current_player.is_ai:
                    player = self.turn_manager.current_player
                    enemy = self.turn_manager.get_enemy(player)

                    if self.selected_attacker is None:
                        for c in self.p1.field.get_all_monsters():
                            c.selected = False

                        for card in player.field.get_all_monsters():
                            if card.rect.collidepoint(pos) and not card.has_attacked and not card.summon_sickness:
                                target = self.battle_manager.get_attack_target(card, enemy)
                                if target == "blocked":
                                    self.log_panel.add(f"{card.name} 没有可攻击的目标")
                                    return
                                self.selected_attacker = card
                                card.selected = True
                                self.log_panel.add(f"选中 {card.name}")
                                return
                    else:
                        attacker = self.selected_attacker
                        opposite = self.battle_manager.get_opposite_slot(attacker, enemy)
                        target = None

                        for card in enemy.field.get_all_monsters():
                            if card.rect.collidepoint(pos):
                                if opposite is not None and card != opposite:
                                    self.log_panel.add("必须攻击正前方的敌人！")
                                    self.selected_attacker.selected = False
                                    self.selected_attacker = None
                                    return
                                target = card
                                break

                        if target is None and self.ai_avatar_rect.collidepoint(pos):
                            if not self.battle_manager.can_direct_attack(attacker, enemy):
                                self.log_panel.add("对方场上有怪兽，不能直接攻击玩家！")
                                self.selected_attacker.selected = False
                                self.selected_attacker = None
                                return

                        if target is not None or self.ai_avatar_rect.collidepoint(pos):
                            self.battle_manager.perform_attack(attacker, target, self)
                            self.selected_attacker.selected = False
                            self.selected_attacker = None
                        else:
                            self.log_panel.add("取消选中")
                            self.selected_attacker.selected = False
                            self.selected_attacker = None

    def _show_phase_banner(self, phase):
        banners = {
            Phase.DRAW: ("抽卡阶段", (100, 180, 255)),
            Phase.MAIN: ("主要阶段", (100, 255, 150)),
            Phase.BATTLE: ("战斗阶段！", (255, 100, 80)),
            Phase.END: ("结束回合", (200, 200, 200)),
        }
        text, color = banners.get(phase, ("", WHITE))
        if text:
            self.phase_banners.append(PhaseBanner(text, color))

    def init_custom_deck(self):
        self.p1.deck.clear()
        self.p2.deck.clear()

        deck_name = getattr(self, "active_deck", "main")
        if self.custom_decks and deck_name not in self.custom_decks:
            deck_name = "main" if "main" in self.custom_decks else next(iter(self.custom_decks))
        if self.custom_decks and deck_name in self.custom_decks:
            main_deck_ids = self.custom_decks[deck_name]
            self.custom_cards = load_custom_cards()
            for card_id in main_deck_ids:
                card_data = get_card_by_id(card_id, self.custom_cards)
                if not card_data:
                    continue

                card_type = card_data.get("card_type", "monster")
                if card_type == "monster":
                    new_card = MonsterCard(
                        card_data["id"],
                        card_data.get("name", "未知怪兽"),
                        card_data.get("cost", 1),
                        card_data.get("attack", 1000),
                        card_data.get("health", 1000),
                        card_data.get("description", "")
                    )
                    self.p1.deck.append(new_card)
                elif card_type == "spell":
                    new_card = SpellCard(
                        card_data["id"],
                        card_data.get("name", "未知魔法"),
                        card_data.get("cost", 1),
                        card_data.get("description", "")
                    )
                    self.p1.deck.append(new_card)
                elif card_type == "trap":
                    new_card = TrapCard(
                        card_data["id"],
                        card_data.get("name", "未知陷阱"),
                        card_data.get("cost", 1),
                        card_data.get("description", "")
                    )
                    self.p1.deck.append(new_card)

        for _ in range(10):
            self.p2.deck.append(MonsterCard("ai001", "AI怪兽", 2, 300, 400, "测试"))

        if self.p1.deck:
            random.shuffle(self.p1.deck)
            self.p1.draw_card(5)
        self.p2.draw_card(5)

    def handle_drag_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for card in reversed(self.turn_manager.current_player.hand):
                if card.rect.collidepoint(event.pos):
                    self.dragged_card = card
                    card.dragging = True
                    self.drag_offset_x = event.pos[0] - card.rect.x
                    self.drag_offset_y = event.pos[1] - card.rect.y
                    if card.home_pos == (0, 0):
                        card.home_pos = (card.rect.x, card.rect.y)
                    break
        elif event.type == pygame.MOUSEMOTION:
            if self.dragged_card and self.dragged_card.dragging:
                self.dragged_card.rect.x = event.pos[0] - self.drag_offset_x
                self.dragged_card.rect.y = event.pos[1] - self.drag_offset_y
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragged_card:
                card = self.dragged_card
                player = self.turn_manager.current_player
                success = False
                if (self.turn_manager.phase == Phase.MAIN and not player.is_ai and card.card_type == "monster" and not player.summoned_this_turn):
                    mx, my = event.pos
                    for i in range(4):
                        rect = pygame.Rect(380 + i * 100, 400, CARD_WIDTH, CARD_HEIGHT)
                        if rect.collidepoint(mx, my):
                            ok, msg = self.summon_manager.summon(player, card, i, "melee", self)
                            if ok:
                                success = True
                                self.log_panel.add(f"召唤成功：{card.name}")
                                self.trigger_summon_effect(card, (380 + i * 100, 400))
                            else:
                                self.log_panel.add(msg)
                            break
                    if not success:
                        for i in range(4):
                            rect = pygame.Rect(380 + i * 100, 540, CARD_WIDTH, CARD_HEIGHT)
                            if rect.collidepoint(mx, my):
                                ok, msg = self.summon_manager.summon(player, card, i, "ranged", self)
                                if ok:
                                    success = True
                                    self.log_panel.add(f"召唤成功：{card.name}")
                                    self.trigger_summon_effect(card, (380 + i * 100, 540))
                                else:
                                    self.log_panel.add(msg)
                                break
                card.dragging = False
                if not success:
                    card.rect.x, card.rect.y = card.home_pos
                self.dragged_card = None

    def update_phase_button_text(self):
        phase_names = {Phase.DRAW: "结束抽卡", Phase.MAIN: "结束主要", Phase.BATTLE: "结束战斗", Phase.END: "结束回合"}
        self.phase_btn.text = phase_names.get(self.turn_manager.phase, "下一阶段")

    def update(self):
        if not self.game_over:
            if self.p1.life <= 0:
                self.game_over = True
                self.winner = self.p2
                self.log_panel.add("你输了！")
            elif self.p2.life <= 0:
                self.game_over = True
                self.winner = self.p1
                self.log_panel.add("你胜利了！")

        self.particles.update()
        self.floating_texts = [ft for ft in self.floating_texts if ft.update()]
        self.slash_effects = [s for s in self.slash_effects if s.update()]
        self.glow_pulses = [g for g in self.glow_pulses if g.update()]
        self.phase_banners = [b for b in self.phase_banners if b.update()]
        self.attack_anims = [a for a in self.attack_anims if (a.update() or True) and not a.done]

        remaining_summon = []
        for anim in self.summon_anims:
            anim.update()
            if not anim.done:
                remaining_summon.append(anim)
        self.summon_anims = remaining_summon

        self.update_draw_animation()

        if self.turn_manager.current_player.is_ai and not self.ai_turn_in_progress and not self.game_over:
            self.ai_turn_in_progress = True
            self.phase_btn.enabled = False
            self.ai_controller.take_turn()

        if self.ai_turn_in_progress and self.ai_controller:
            still_running = self.ai_controller.update()
            if not still_running:
                self.ai_turn_in_progress = False
                self.phase_btn.enabled = True
                self.update_phase_button_text()

        current_player = self.turn_manager.current_player
        hand_start_x = 200
        hand_start_y = 730
        card_spacing = 100
        max_per_row = 10
        for i, card in enumerate(current_player.hand):
            if not card.dragging:
                row = i // max_per_row
                col = i % max_per_row
                card.rect.x = hand_start_x + col * card_spacing
                card.rect.y = hand_start_y - row * 40
                card.home_pos = (card.rect.x, card.rect.y)

        for i in range(4):
            if self.p1.field.melee_slots[i]:
                self.p1.field.melee_slots[i].rect.topleft = (380 + i * 100, 400)
            if self.p1.field.ranged_slots[i]:
                self.p1.field.ranged_slots[i].rect.topleft = (380 + i * 100, 540)
            if self.p2.field.melee_slots[i]:
                self.p2.field.melee_slots[i].rect.topleft = (380 + i * 100, 100)
            if self.p2.field.ranged_slots[i]:
                self.p2.field.ranged_slots[i].rect.topleft = (380 + i * 100, 240)

    def draw(self):
        self.screen.fill(DARK_BLUE)

        if self.in_menu:
            self.screen.blit(self.menu_bg, (0, 0))

            title_txt = "卡牌游戏 - 主菜单"
            glow = FONT_BIG.render(title_txt, True, (90, 90, 180))
            cx = SCREEN_WIDTH // 2
            ty = 150
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    self.screen.blit(glow, (cx - glow.get_width() // 2 + dx, ty + dy))
            title = FONT_BIG.render(title_txt, True, (245, 245, 255))
            self.screen.blit(title, (cx - title.get_width() // 2, ty))

            for btn in self.menu_buttons.values():
                btn.draw(self.screen)

            card_count = FONT_MID.render(f"自定义卡牌: {len(self.custom_cards)}", True, (230, 200, 90))
            deck_count = FONT_MID.render(f"自定义卡组: {len(self.custom_decks)}", True, (230, 200, 90))
            self.screen.blit(card_count, (100, 800))
            self.screen.blit(deck_count, (100, 850))
        else:
            self._draw_game_field()
            self._draw_game_ui()

        self.graveyard_sys.draw_graveyard_button()
        self.graveyard_sys.draw_graveyard_window()
        self.deck_viewer.draw_deck_button()
        self.deck_viewer.draw_deck_window()

        self.card_editor.draw()
        self.deck_editor.draw()
        self.victory_window.draw_victory_screen(self)

        pygame.display.flip()

    def _draw_game_field(self):
        field_bg = pygame.Surface((640, 580), pygame.SRCALPHA)
        pygame.draw.rect(field_bg, (15, 15, 35, 180), (0, 0, 640, 580), border_radius=10)
        self.screen.blit(field_bg, (360, 80))

        label_font = FONT_SMALL
        ai_melee_label = label_font.render("敌方近战", True, (180, 180, 200))
        self.screen.blit(ai_melee_label, (380, 82))
        ai_ranged_label = label_font.render("敌方远程", True, (180, 180, 200))
        self.screen.blit(ai_ranged_label, (380, 222))
        p_melee_label = label_font.render("我方近战", True, (180, 200, 180))
        self.screen.blit(p_melee_label, (380, 382))
        p_ranged_label = label_font.render("我方远程", True, (180, 200, 180))
        self.screen.blit(p_ranged_label, (380, 522))

        divider_y = 340
        pygame.draw.line(self.screen, (60, 60, 100), (370, divider_y), (990, divider_y), 2)
        vs_surf = FONT_MID.render("VS", True, (100, 100, 150))
        self.screen.blit(vs_surf, (SCREEN_WIDTH // 2 - vs_surf.get_width() // 2 - 20, divider_y - vs_surf.get_height() // 2))

        ai = self.p2
        for i in range(4):
            rect = pygame.Rect(380 + i * 100, 100, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, (40, 40, 70), rect, border_radius=4)
            pygame.draw.rect(self.screen, (70, 70, 110), rect, 1, border_radius=4)
            if ai.field.melee_slots[i]:
                card = ai.field.melee_slots[i]
                card.rect.topleft = rect.topleft
                card.draw(self.screen)
            rect2 = pygame.Rect(380 + i * 100, 240, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, (40, 40, 70), rect2, border_radius=4)
            pygame.draw.rect(self.screen, (70, 70, 110), rect2, 1, border_radius=4)
            if ai.field.ranged_slots[i]:
                card = ai.field.ranged_slots[i]
                card.rect.topleft = rect2.topleft
                card.draw(self.screen)

        for i in range(4):
            rect = pygame.Rect(380 + i * 100, 400, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, (40, 50, 40), rect, border_radius=4)
            pygame.draw.rect(self.screen, (70, 110, 70), rect, 1, border_radius=4)
            if self.p1.field.melee_slots[i]:
                card = self.p1.field.melee_slots[i]
                card.rect.topleft = rect.topleft
                card.draw(self.screen)
            rect2 = pygame.Rect(380 + i * 100, 540, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, (40, 50, 40), rect2, border_radius=4)
            pygame.draw.rect(self.screen, (70, 110, 70), rect2, 1, border_radius=4)
            if self.p1.field.ranged_slots[i]:
                card = self.p1.field.ranged_slots[i]
                card.rect.topleft = rect2.topleft
                card.draw(self.screen)

    def _draw_game_ui(self):
        ai = self.p2
        status_rect = pygame.Rect(20, 20, 250, 80)
        pygame.draw.rect(self.screen, (30, 30, 50), status_rect, border_radius=6)
        pygame.draw.rect(self.screen, (80, 80, 120), status_rect, 2, border_radius=6)
        life_surf = FONT_MID.render(f"AI 生命: {ai.life}", True, RED)
        self.screen.blit(life_surf, (30, 30))
        mana_surf = FONT_SMALL.render(f"法力: {ai.mana}/{ai.max_mana}", True, BLUE)
        self.screen.blit(mana_surf, (30, 60))
        hand_surf = FONT_SMALL.render(f"手牌: {len(ai.hand)}", True, WHITE)
        self.screen.blit(hand_surf, (200, 60))

        phase_surf = FONT_MID.render(f"当前阶段: {self.turn_manager.phase.name}", True, WHITE)
        self.screen.blit(phase_surf, (SCREEN_WIDTH // 2 - 80, 20))
        turn_text = "你的回合" if not self.turn_manager.current_player.is_ai else "AI回合"
        turn_color = GREEN if not self.turn_manager.current_player.is_ai else RED
        turn_surf = FONT_MID.render(turn_text, True, turn_color)
        self.screen.blit(turn_surf, (SCREEN_WIDTH // 2 - 60, 50))

        player = self.p1
        info_rect = pygame.Rect(20, SCREEN_HEIGHT - 290, 300, 35)
        pygame.draw.rect(self.screen, (30, 30, 50), info_rect, border_radius=6)
        info_surf = FONT_MID.render(f"生命: {player.life}  法力: {player.mana}/{player.max_mana}", True, YELLOW)
        self.screen.blit(info_surf, (30, SCREEN_HEIGHT - 285))

        self.particles.draw(self.screen)
        for s in self.slash_effects:
            s.draw(self.screen)
        for g in self.glow_pulses:
            g.draw(self.screen)
        for anim in self.summon_anims:
            anim.draw(self.screen)
        for anim in self.draw_card_anims:
            anim.draw(self.screen)

        self.phase_btn.draw(self.screen)
        self.log_panel.draw(self.screen)

        for ft in self.floating_texts:
            ft.draw(self.screen)

        for banner in self.phase_banners:
            banner.draw(self.screen)

        hand_start_x = 110
        hand_y = SCREEN_HEIGHT - CARD_HEIGHT - 50
        spacing = 110

        for i, card in enumerate(self.p1.hand):
            if i >= HAND_MAX:
                break
            is_animating = any(a.card == card for a in self.draw_card_anims)
            if not card.dragging and not is_animating:
                card.rect.topleft = (hand_start_x + i * spacing, hand_y)
                card.draw(self.screen)

        if self.dragged_card:
            self.dragged_card.draw(self.screen)

        offset = self.shake.apply()
        if offset != (0, 0):
            final_surf = self.screen.copy()
            self.screen.fill(DARK_BLUE)
            self.screen.blit(final_surf, offset)

        self.end_battle_window.draw()


def main():
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
    pygame.display.set_caption("卡牌游戏")
    clock = pygame.time.Clock()
    game = Game(screen, mode="ai")

    while True:
        clock.tick(60)
        game.handle_events()
        game.update()
        game.draw()

if __name__ == "__main__":
    main()
