# core/ai.py
import random
from config import *

class AIController:
    def __init__(self, player, game_state):
        self.player = player
        self.game = game_state
        self.action_queue = []
        self.action_timer = 0
        self.action_delay = 15

    def take_turn(self):
        self.action_queue = []
        self.action_queue.append(("draw", None))
        self._plan_summon()
        self._plan_attack()
        self.action_queue.append(("end_turn", None))
        self.action_timer = 0

    def _plan_summon(self):
        player = self.player
        hand_monsters = [c for c in player.hand if c.card_type == "monster"]
        hand_monsters.sort(key=lambda c: c.cost, reverse=True)

        for card in hand_monsters:
            if player.mana >= card.cost:
                placed = False
                for i in range(4):
                    if player.field.melee_slots[i] is None:
                        self.action_queue.append(("summon", (card, i, "melee")))
                        placed = True
                        break
                if placed:
                    continue
                for i in range(4):
                    if player.field.ranged_slots[i] is None:
                        self.action_queue.append(("summon", (card, i, "ranged")))
                        break

    def _plan_attack(self):
        enemy = self.game.turn_manager.get_enemy(self.player)
        my_monsters = self.player.field.get_all_monsters()

        for m in my_monsters:
            if m.has_attacked or m.summon_sickness:
                continue
            target = self.game.battle_manager.get_attack_target(m, enemy)
            if target == "blocked":
                continue
            self.action_queue.append(("attack", (m, target)))

    def update(self):
        if not self.action_queue:
            return False

        self.action_timer += 1
        if self.action_timer < self.action_delay:
            return True

        self.action_timer = 0
        action, data = self.action_queue.pop(0)

        if action == "draw":
            self._do_draw()
        elif action == "summon":
            card, slot_idx, slot_type = data
            self._do_summon(card, slot_idx, slot_type)
        elif action == "attack":
            attacker, target = data
            self._do_attack(attacker, target)
        elif action == "end_turn":
            self.game.turn_manager.end_turn()
            self.game.log_panel.add("AI 回合结束")
            return False

        return True

    def _do_draw(self):
        player = self.player
        if len(player.hand) < 10 and player.deck:
            card = player.deck.pop()
            card.owner = player
            card.location = "hand"
            player.hand.append(card)
            self.game.log_panel.add("AI 抽了一张牌")

    def _do_summon(self, card, slot_idx, slot_type):
        player = self.player
        if card not in player.hand or player.mana < card.cost:
            return
        ok, msg = self.game.summon_manager.summon(player, card, slot_idx, slot_type, self.game)
        if ok:
            self.game.log_panel.add(f"AI 召唤 {card.name} ({'近战' if slot_type == 'melee' else '远程'})")
            target_pos = (380 + slot_idx * 100, 100 if slot_type == "melee" else 240)
            if hasattr(self.game, 'trigger_summon_effect'):
                self.game.trigger_summon_effect(card, target_pos)
        else:
            self.game.log_panel.add(f"AI 召唤失败: {msg}")

    def _do_attack(self, attacker, target):
        if attacker.has_attacked or attacker.summon_sickness:
            return
        result = self.game.battle_manager.perform_attack(attacker, target, self.game)
        if result is None:
            self.game.log_panel.add("AI 攻击无效")
