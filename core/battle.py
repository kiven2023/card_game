# core/battle.py
from config import SCREEN_HEIGHT
from ui.animations import FloatingText, SlashEffect


class AttackResult:
    def __init__(self, attacker, defender=None, damage=0, defender_destroyed=False,
                 direct_attack=False, target_pos=None):
        self.attacker = attacker
        self.defender = defender
        self.damage = damage
        self.defender_destroyed = defender_destroyed
        self.direct_attack = direct_attack
        self.target_pos = target_pos


class BattleManager:
    @staticmethod
    def can_attack(attacker, defender=None):
        if attacker.has_attacked:
            return False, "已经攻击过"
        if attacker.summon_sickness:
            return False, "召唤回合不能攻击"
        return True, ""

    @staticmethod
    def can_direct_attack(attacker, enemy):
        for i in range(4):
            if enemy.field.melee_slots[i] is not None:
                return False
            if enemy.field.ranged_slots[i] is not None:
                return False
        return True

    @staticmethod
    def perform_attack(attacker, defender, game_state):
        can, reason = BattleManager.can_attack(attacker, defender)
        if not can:
            return None

        if defender is None:
            enemy = game_state.turn_manager.get_enemy(attacker.owner)
            if not BattleManager.can_direct_attack(attacker, enemy):
                game_state.log_panel.add("对方场上有怪兽，不能直接攻击玩家！")
                return None

        damage = attacker.attack

        if defender:
            defender.take_damage(damage)
            game_state.log_panel.add(f"{attacker.name} 对 {defender.name} 造成 {damage} 点伤害")

            target_x = defender.rect.centerx
            target_y = defender.rect.centery
            defender_destroyed = defender.health <= 0

            if hasattr(game_state, 'particles'):
                game_state.particles.emit_burst(
                    target_x, target_y,
                    colors=[(255, 200, 100), (255, 150, 50), (255, 255, 200)],
                    count=15, speed=5, gravity=0.1, life=25
                )
                game_state.particles.emit_ring(
                    target_x, target_y,
                    color=(255, 180, 80),
                    count=12, radius=20, speed=3, life=20
                )

            if hasattr(game_state, 'slash_effects'):
                game_state.slash_effects.append(SlashEffect(target_x, target_y, (255, 255, 200)))

            if hasattr(game_state, 'floating_texts'):
                game_state.floating_texts.append(
                    FloatingText(f"-{damage}", target_x, target_y - 20, color=(255, 80, 80), size=32, duration=50)
                )

            if defender_destroyed:
                game_state.log_panel.add(f"{defender.name} 被破坏！")
                if hasattr(game_state, 'particles'):
                    game_state.particles.emit_burst(
                        target_x, target_y,
                        colors=[(100, 100, 100), (150, 150, 150), (80, 80, 120)],
                        count=25, speed=4, gravity=0.15, life=35
                    )
                defender.owner.field.remove(defender)
                if defender not in defender.owner.graveyard:
                    defender.owner.graveyard.append(defender)

            attacker.has_attacked = True
            return AttackResult(attacker, defender, damage, defender_destroyed,
                                target_pos=(target_x, target_y))

        else:
            enemy = game_state.turn_manager.get_enemy(attacker.owner)
            enemy.life -= damage
            game_state.log_panel.add(f"{attacker.name} 直接攻击玩家，造成 {damage} 点伤害！")

            if attacker.owner == game_state.p1 and hasattr(game_state, 'ai_avatar_rect'):
                target_x = game_state.ai_avatar_rect.centerx
                target_y = game_state.ai_avatar_rect.centery
            elif hasattr(game_state, 'p1_info_pos'):
                target_x, target_y = game_state.p1_info_pos
            else:
                target_x = 145
                target_y = SCREEN_HEIGHT - 280

            if hasattr(game_state, 'particles'):
                game_state.particles.emit_burst(
                    target_x, target_y,
                    colors=[(255, 50, 50), (255, 100, 50), (255, 200, 100)],
                    count=30, speed=6, gravity=0.1, life=30
                )

            if hasattr(game_state, 'floating_texts'):
                game_state.floating_texts.append(
                    FloatingText(f"-{damage}", target_x, target_y - 20, color=(255, 50, 50), size=40, duration=60)
                )
            if hasattr(game_state, 'shake'):
                game_state.shake.trigger(10, decay=1)

            attacker.has_attacked = True
            return AttackResult(attacker, None, damage, direct_attack=True,
                                target_pos=(target_x, target_y))

    @staticmethod
    def get_opposite_slot(attacker, enemy):
        for i in range(4):
            if attacker.owner.field.melee_slots[i] == attacker:
                return enemy.field.melee_slots[i]
            if attacker.owner.field.ranged_slots[i] == attacker:
                return enemy.field.ranged_slots[i]
        return None

    @staticmethod
    def get_attack_target(attacker, enemy):
        opposite = BattleManager.get_opposite_slot(attacker, enemy)
        if opposite is not None:
            return opposite
        if BattleManager.can_direct_attack(attacker, enemy):
            return None
        return "blocked"
