from dataclasses import dataclass, field
from typing import List, Dict

class ScreenState:
    def __init__(self, data):
        self.data = data

    # def __str__(self):
    #     return f"{self.__class__.__name__}: {self.data}"

@dataclass
class ShopScreenState(ScreenState):
    pass

@dataclass
class RestScreenState(ScreenState):
    has_rested: bool = True
    rest_options: List[str] = ["SMITH", "REST"]


class MapScreenState(ScreenState):
    pass


class HandSelectScreenState(ScreenState):
    pass


class EventScreenState(ScreenState):
    pass


class ChestScreenState(ScreenState):
    pass


class CombatRewardScreenState(ScreenState):
    pass


class CardRewardScreenState(ScreenState):
    pass


class BossRewardScreenState(ScreenState):
    pass


class GridScreenState(ScreenState):
    pass


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
        return state_class(data)

    def update_screen_type(self, new_type, new_data):
        """更新 screen_type 并重新设置 screen_state。"""
        self.screen_type = new_type
        self.screen_state = self.create_screen_state(new_data)

