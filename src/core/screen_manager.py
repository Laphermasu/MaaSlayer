from dataclasses import dataclass, field
from typing import List, Dict

class ScreenState:
    def __init__(self, data):
        self.data = data

    @classmethod
    def from_data(cls, data):
        return cls(data)

class ShopScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        shop_data = data.get('shop_items', [])
        return cls(shop_data)

class RestScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        rest_data = data.get('rest_options', [])
        return cls(rest_data)

class MapScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        map_data = data.get('map_details', {})
        return cls(map_data)

class HandSelectScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        hand_data = data.get('hand_options', [])
        return cls(hand_data)

class EventScreenState(ScreenState):
    @classmethod
    def from_data(cls, data):
        event_data = data.get('event_details', {})
        return cls(event_data)

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
        }

        # 获取对应的状态类，如果没有匹配，返回一个默认状态
        state_class = screen_state_classes.get(self.screen_type, ScreenState)
        return state_class.from_data(data)

    def update_screen_state(self, screen_type: str, screen_state_data):
        self.screen_type = screen_type
        self.screen_state = self.create_screen_state(screen_state_data)