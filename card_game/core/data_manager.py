import json
import os
from core.card import MonsterCard, SpellCard, TrapCard

DATA_PATH = "user_data"
CARD_FILE = os.path.join(DATA_PATH, "custom_cards.json")
DECK_FILE = os.path.join(DATA_PATH, "custom_decks.json")

# 确保文件夹存在
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

def save_custom_cards(cards):
    """保存卡牌列表为JSON，兼容对象和字典"""
    try:
        serializable = []
        for c in cards:
            if hasattr(c, "to_dict"):
                serializable.append(c.to_dict())
            elif isinstance(c, dict):
                serializable.append(c)
        with open(CARD_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("保存卡牌失败:", e)

def load_custom_cards():
    """读取JSON卡牌，返回字典列表"""
    if not os.path.exists(CARD_FILE):
        return []
    try:
        with open(CARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("读取卡牌失败:", e)
        return []

def save_custom_decks(decks):
    """保存卡组列表为JSON"""
    try:
        with open(DECK_FILE, "w", encoding="utf-8") as f:
            json.dump(decks, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("保存卡组失败:", e)

def load_custom_decks():
    """读取卡组JSON"""
    if not os.path.exists(DECK_FILE):
        return {"main": []}
    try:
        with open(DECK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("读取卡组失败:", e)
        return {"main": []}

def get_card_by_id(card_id, all_cards):
    """根据ID从卡牌列表中获取卡牌字典"""
    for c in all_cards:
        if isinstance(c, dict) and c.get("id") == card_id:
            return c
    return None