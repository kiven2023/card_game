# core/player.py
from config import *
from .field import Field
class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.life = 5000
        self.max_mana = 2
        self.mana = 2
        self.deck = []          # Card 列表
        self.hand = []          # Card 列表
        self.graveyard = []     # Card 列表
        self.field = Field()    # 怪兽区域
        self.traps = []         # 陷阱区域（最多5张）
        self.summoned_this_turn = False

    def draw_card(self, num=1):
        for _ in range(num):
            if self.deck:
                card = self.deck.pop()
                card.owner = self
                card.location = "hand"
                self.hand.append(card)

    def take_damage(self, amount):
        self.life -= amount