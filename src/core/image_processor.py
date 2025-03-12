from maa.toolkit import Toolkit
from maa.tasker import Tasker
from maa.custom_recognition import CustomRecognition
from maa.resource import Resource
from typing import List
from src.custom_recognition.monster_recognition import MonsterRecognition
from .data_models import Monster, Player, MapNode, Shop, GameState

class ImageProcessor:
    def __init__(self, resource: Resource,tasker: Tasker):
        self.resource = resource
        self.tasker = tasker

    # def recognize_map(self) -> List[MapNode]:
    #     # 使用图像识别获取地图节点信息
    #     result = self.context.run_recognition("MapRecognition")
    #     # 解析识别结果并返回 MapNode 列表
    #     return []
    #
    def recognize_monsters(self) -> List[Monster]:
        monsters = []
        # 注册自定义识别
        self.resource.register_custom_recognition("MonsterRecognition", MonsterRecognition())
        # 获取屏幕裁图
        img = self.tasker.controller.post_screencap().wait().get()
        pipeline_override = {
            "MyRecongitionEntry": {"recognition": "custom", "custom_recognition": "MonsterRecognition"},
        }

        monster_exist = True
        while monster_exist:
            # 进行识别
            task_detail = self.tasker.post_task("MyRecongitionEntry", pipeline_override).wait().get()
            # 获得识别到的怪物信息
            name = task_detail.nodes[0].recognition.best_result.detail
            # 如果不存在识别结果停止循环
            if name == "Unknown":
                monster_exist = False
            else:
                # 添加怪物信息
                monsters.append(name)
                # 消除img中识别过的区域
                x, y, w, h = task_detail.nodes[0].recognition.best_result.box
                img[y:y + h, x:x + w] = 0  # 将匹配区域设置为黑色
        return monsters
    #
    # def recognize_player(self) -> Player:
    #     # 使用图像识别获取玩家信息
    #     result = self.context.run_recognition("PlayerRecognition")
    #     # 解析识别结果并返回 Player 对象
    #     return Player(health=0, energy=0, powers=[], hand_cards=[], relics=[], potions=[])
    #
    # def recognize_current_node(self) -> MapNode:
    #     # 使用图像识别获取当前节点信息
    #     result = self.context.run_recognition("NodeRecognition")
    #     # 解析识别结果并返回 MapNode 对象
    #     return MapNode(node_type="", details={})
    #
    # def recognize_shop(self) -> Shop:
    #     # 使用图像识别获取商店信息
    #     result = self.context.run_recognition("ShopRecognition")
    #     # 解析识别结果并返回 Shop 对象
    #     return Shop(items={}, gold=0)
    #
    # def get_game_state(self) -> GameState:
    #     # 获取完整的游戏状态
    #     return GameState(
    #         map=self.recognize_map(),
    #         monsters=self.recognize_monsters(),
    #         player=self.recognize_player(),
    #         current_node=self.recognize_current_node(),
    #         shop=self.recognize_shop(),
    #     )