# systems/turn_manager.py
from enum import Enum
from config import *

class Phase(Enum):
    DRAW = 1
    MAIN = 2
    BATTLE = 3
    END = 4

class TurnManager:
    def __init__(self, player1, player2, game):
        self.p1 = player1
        self.p2 = player2
        self.game = game
        self.current_player = player1
        self.phase = Phase.DRAW
        self.turn_count = 1
        self.phase_names = {Phase.DRAW: "抽卡", Phase.MAIN: "主要",
                            Phase.BATTLE: "战斗", Phase.END: "结束"}

    def start_turn(self):
        self.current_player.max_mana = min(10, self.current_player.max_mana + 1)
        self.current_player.mana = self.current_player.max_mana
        self.current_player.summoned_this_turn = False
        for card in self.current_player.field.get_all_monsters():
            card.has_attacked = False
            card.summon_sickness = False
        self.phase = Phase.DRAW

    def next_phase(self):
        if self.phase == Phase.DRAW:
            self.phase = Phase.MAIN
            player = self.current_player
            if len(player.hand) < 10 and player.deck:
                card = player.deck.pop()
                card.owner = player
                card.location = "hand"
                is_ai = player.is_ai
                target_x = 220 + len(player.hand) * 110 + CARD_WIDTH // 2
                target_y = SCREEN_HEIGHT - CARD_HEIGHT - 140
                self.game.start_draw_animation(card, (target_x, target_y), is_ai=is_ai)

        elif self.phase == Phase.MAIN:
            self.phase = Phase.BATTLE
        elif self.phase == Phase.BATTLE:
            self.phase = Phase.END
        elif self.phase == Phase.END:
            self.end_turn()

    def end_turn(self):
        self.current_player = self.p2 if self.current_player == self.p1 else self.p1
        self.turn_count += 1
        self.start_turn()

    def get_enemy(self, player):
        return self.p2 if player == self.p1 else self.p1
