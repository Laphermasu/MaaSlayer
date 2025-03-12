import time
from maa.controller import AdbController
import numpy as np
from maa.context import Context

class ADBAction:
    def __init__(self, controller: AdbController, context: Context):
        self.controller = controller
        self.context = context
    def execute(self, command: str, cards=None, monsters=None):
        parts = command.split()
        action_type = parts[0]

        if action_type == "START":
            self.start_game(parts[1])  # 例如：START IRONCLAD 0

        elif action_type == "POTION":
            self.use_or_discard_potion(parts)

        elif action_type == "PLAY":
            if cards is None or monsters is None:
                print("cards和 monsters 丢失")
                return
            self.play_card(parts, cards, monsters)

        elif action_type == "END":
            self.end_turn()

        elif action_type == "PROCEED":
            self.proceed()

        elif action_type == "RETURN":
            self.return_to_previous()

        elif action_type == "CONFIRM":
            self.confirm()

        elif action_type == "LEAVE":
            self.leave()

        elif action_type == "CHOOSE":
            self.choose_option(parts[1])
        else:
            print(f"未知的命令: {command}")

    def start_game(self, character: str):
        """点击开始游戏按钮"""
        print(f"开始游戏，选择角色: {character}")
        self.context.run_action(
            "StartGame",
            pipeline_override={
             "StartGame": {
                "recognition": "OCR",
                "expected": "开始游戏",
                "action": "Click",
                "next": "standard"
              },
              "standard": {
                   "recognition": "OCR",
                "expected": "标准模式",
                "action": "Click",
                "next": "character"
              },
                "character": {
                    "recognition": "TemplateMatch",
                    "template": "assets\\resource\\image\\铁甲战士.png",
                    "action": "Click",
                    "next": "embark"
                },
                "embark": {
                     "recognition": "OCR",
                "expected": "启程",
                "action": "Click",
                }
           }
       )

    def use_or_discard_potion(self, parts):
        """使用或丢弃药水"""



    def play_card(self, parts, cards, monsters):
        """打出卡牌"""
        # monsters = [{"name": m.name, "box": m.box} for m in result_dict.get("monsters", [])]
        # cards = [{"name": c.name, "box": c.box} for c in result_dict.get("cards", [])]
        card_index = int(parts[1]) - 1
        print(f"打出卡牌：索引 {card_index}")
        card_info = cards[card_index]  # 例: {"name": "Strike", "box": (x1, y1, x2, y2)}
        card_box = card_info.get("box", None)
        if len(parts) > 2:
            target_index = int(parts[2])
            monster_info = monsters[target_index]  # 例: {"name": "Jaw Worm", "box": (x1, y1, x2, y2)}
            monster_box = monster_info.get("box", None)
        elif len(parts) < 2:
            monster_box = [100, 575, 40, 40]

        self.context.run_action(
            "selectcard",
            pipeline_override={
                "selectcard": {
                    "action": "click",
                    "target": card_box,
                    "next": "selectmonster"
                },
                "selectmonster": {
                    "action": "click",
                    "target": monster_box,
                    "next": "selectmonster"
                },
            }
        )


    def end_turn(self):
        """结束回合"""
        print("结束回合")
        self.context.run_action(
            "end_turn",
            pipeline_override={
                "end_turn": {
                     "recognition": "OCR",
                     "expected": "结束回合",
                     "action": "Click"
                }
            }
        )

    def proceed(self):
        print("前进")
        self.context.run_action(
            "proceed",
            pipeline_override={
                "proceed": {
                    "recognition": "OCR",
                    "expected": "前进",
                    "action": "Click"
                }
            }
        )

    def return_to_previous(self):
        """返回上一级菜单"""
        print("返回")
        self.context.run_action(
            "return_to_previous",
            pipeline_override={
                "return_to_previous": {
                    "recognition": "OCR",
                    "expected": "返回",
                    "action": "Click"
                }
            }
        )

    def confirm(self):
        self.context.run_action(
            "confirm",
            pipeline_override={
                "confirm": {
                    "recognition": "OCR",
                    "expected": "确认",
                    "action": "Click"
                }
            }
        )

    def leave(self):
        """离开当前界面"""
        print("离开")
        self.context.run_action(
            "leave",
            pipeline_override={
                "leave": {
                    "recognition": "OCR",
                    "expected": "离开",
                    "action": "Click"
                }
            }
        )

    def choose_option(self, choice_index):
        """选择事件中的某个选项"""
        self.context.run_action(
            "choose_option",
            pipeline_override={
                "choose_option": {
                    "recognition": "TemplateMatch",
                    "template": "assets\\resource\\image\\option.png",
                    "index": choice_index,
                    "action": "Click"
                }
            }
        )