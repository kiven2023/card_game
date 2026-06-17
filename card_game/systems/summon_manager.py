# systems/summon_manager.py
class SummonManager:
    @staticmethod
    def can_summon(player, card, slot_index, slot_type):
        if card.card_type != "monster":
            return False, "不是怪兽卡"
        if player.mana < card.cost:
            return False, "费用不足"
        if slot_type == "melee" and player.field.melee_slots[slot_index] is not None:
            return False, "格子已占用"
        if slot_type == "ranged" and player.field.ranged_slots[slot_index] is not None:
            return False, "格子已占用"
        return True, ""

    @staticmethod
    def summon(player, card, slot_index, slot_type, game_state):
        can, reason = SummonManager.can_summon(player, card, slot_index, slot_type)
        if not can:
            return False, reason

        player.mana -= card.cost
        player.hand.remove(card)
        player.field.place_card(card, slot_index, slot_type)
        card.summon_sickness = True

        if hasattr(card, 'effect') and card.effect:
            card.effect.execute(game_state, card, None)

        return True, "召唤成功"
