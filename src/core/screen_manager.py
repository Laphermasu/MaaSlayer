from dataclasses import dataclass, field
from typing import List, Dict

# ScreenState 基类
class ScreenState:
    def __init__(self, data):
        self.data = data

    @classmethod
    def from_data(cls, data):
        return cls(data)

# 暂时依靠pipeline
class ShopScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        shop_data = data.get('shop_items', [])
        return cls(shop_data)

# 暂时依靠pipeline
class RestScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        rest_data = data.get('rest_options', [])
        return cls(rest_data)

# 暂时禁用地图获取
class MapScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        map_data = data.get('map_details', {})
        return cls(map_data)

# 需要实现
class HandSelectScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        # 解析手牌data
        hand_data = data.get()
        return cls(hand_data)

#需要实现
class EventScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        # 解析事件data
        event_data = data.get()
        return cls(event_data)
    
class ChestScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        # 解析宝箱data
        chest_data = data.get()
        return cls(chest_data)
    
class CombatRewardScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        # 解析战斗奖励data
        combat_reward_data = data.get()
        return cls(combat_reward_data)
    
class CardRewardScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        # 解析卡牌奖励data
        card_reward_data = data.get()
        return cls(card_reward_data)

class BossRewardScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        # 解析boss奖励data
        boss_reward_data = data.get()
        return cls(boss_reward_data)
    
class GridScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        # 解析手牌data
        grid_data = data.get()
        return cls(grid_data) 

# Screen管理类
class ScreenManager:
    def __init__(self, screen_type="NONE", screen_state_data=None):
        self.screen_type = screen_type
        self.screen_state = self.create_screen_state(screen_state_data)

    def create_screen_state(self, data):
        """根据 screen_type 创建相应的 screen_state 对象。"""
        screen_state_classes = {
            "SHOP_SCREEN": ShopScreenState,
            "REST": RestScreenState,
            "MAP": MapScreenState,
            "HAND_SELECT": HandSelectScreenState,
            "EVENT": EventScreenState,
            "CHEST": ChestScreenState,
            "COMBAT_REWARD": CombatRewardScreenState,
            "CARD_REWARD": CardRewardScreenState,
            "BOSS_REWARD": BossRewardScreenState,
            "GRID": GridScreenState,
        }

        # 获取对应的状态类，如果没有匹配，返回一个默认状态
        state_class = screen_state_classes.get(self.screen_type, ScreenState)
        return state_class.from_data(data)

    def update_screen_state(self, screen_type: str, screen_state_data):
        self.screen_type = screen_type
        self.screen_state = self.create_screen_state(screen_state_data)