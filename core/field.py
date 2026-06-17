# core/field.py
from config import *
class Field:
    def __init__(self):
        self.melee_slots = [None] * 4   # 前排近战
        self.ranged_slots = [None] * 4   # 后排远程

    def get_all_monsters(self):
        return [m for m in self.melee_slots + self.ranged_slots if m]

    def is_full(self, slot_type=None):
        if slot_type == "melee":
            return all(self.melee_slots)
        elif slot_type == "ranged":
            return all(self.ranged_slots)
        return all(self.melee_slots) and all(self.ranged_slots)

    def place_card(self, card, slot_index, slot_type="melee"):
        if slot_type == "melee" and not self.melee_slots[slot_index]:
            self.melee_slots[slot_index] = card
            card.location = "field"
            return True
        elif slot_type == "ranged" and not self.ranged_slots[slot_index]:
            self.ranged_slots[slot_index] = card
            card.location = "field"
            return True
        return False

    def remove(self, card):
        for i in range(4):
            if self.melee_slots[i] == card:
                self.melee_slots[i] = None
                return
            if self.ranged_slots[i] == card:
                self.ranged_slots[i] = None
                return