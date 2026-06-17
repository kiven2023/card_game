# core/effect.py
from abc import ABC, abstractmethod
from config import *
class Effect(ABC):
    """效果基类"""
    def __init__(self, effect_id, name, timing="activate"):
        self.id = effect_id
        self.name = name
        self.timing = timing      # "on_summon", "on_attack", "on_turn_start", etc.

    @abstractmethod
    def execute(self, game_state, source, target=None):
        pass


class EffectRegistry:
    """效果注册表，方便从JSON加载效果"""
    _effects = {}

    @classmethod
    def register(cls, name, effect_class):
        cls._effects[name] = effect_class

    @classmethod
    def create(cls, name, **kwargs):
        if name in cls._effects:
            return cls._effects[name](**kwargs)
        return None


# 示例效果
class HealEffect(Effect):
    def __init__(self, amount=500):
        super().__init__("heal", "治疗")
        self.amount = amount

    def execute(self, game_state, source, target):
        source.owner.life += self.amount

EffectRegistry.register("heal", HealEffect)


class DamageEffect(Effect):
    def __init__(self, amount=300):
        super().__init__("damage", "伤害")
        self.amount = amount

    def execute(self, game_state, source, target):
        if target:
            target.take_damage(self.amount)

EffectRegistry.register("damage", DamageEffect)