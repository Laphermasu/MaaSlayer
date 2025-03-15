from maa.context import Context
from maa.custom_action import CustomAction
from collections import defaultdict
import re
from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.resource import Resource
from maa.controller import AdbController
from sympy import print_rcode

from src.core.data_models import Monster, Cards, Event
from src.core.data_models import Player
from src.custom_recognition.monster_recognition import MonsterRecognition
from src.custom_recognition.player_recognition import PlayerRecognition
from src.custom_recognition.event_recognition import EventRecognition
from src.custom_recognition.cards_recogntion import CardRecognition
from src.utils.json_utils import JsonUtils
import threading
from src.AI_model.model_run import *
import json

def fill_index(input_list):
    pattern = re.compile(r'^[\[［【](.*?)[\]］】](.*)$')
    result_list = []

    for item in input_list:
        match = pattern.match(item)
        if match:
            key = match.group(1)  # 括号内的内容（索引）
            value = match.group(2).strip()  # 括号外的内容（选项名称）
            result_list.append({"index": key, "text": value})  # 存入列表

    return result_list


class ADBAction(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        """
        :param context: 运行的 Context
        :param argv: 自定义参数
        :return: RunResult(success=True/False)
        """
        print("开始执行 ADBAction 自定义动作")
        game_state = argv.custom_action_param
        game_state = json.loads(game_state)
        game_state = game_state["game_state"]
        print(game_state)
        screen_state = game_state.get("screen_state", {})
        command = screen_state.get("chosen_command", {})

        # command = "PLAY 1 1"

        print(command)
        combat_state = game_state.get("combat_state", {})
        monsters = combat_state.get("monster_box", [])
        cards = combat_state.get("hand", [])

        parts = command.split()
        action_type = parts[0]

        if action_type == "START":
            """点击开始游戏按钮"""
            print("开始游戏")
            img = context.tasker.controller.post_screencap().wait().get()
            # 下面这个run_task是能够成功点击到Play的
            context.run_task(
                "StartGame",
                pipeline_override={
                    "StartGame": {
                        "recognition": "OCR",
                        "expected": "Play",
                        "action": "Click",
                        "next": "standard"
                    },
                    "standard": {
                        "recognition": "OCR",
                        "expected": "Standard",
                        "action": "Click",
                        "next": "character"
                    },
                    "character": {
                        "recognition": "TemplateMatch",
                        "template": "铁甲战士.png",
                        "action": "Click",
                        "next": "embark"
                    },
                    "embark": {
                        "recognition": "OCR",
                        "expected": "Embark",
                        "roi": [1000, 500, 250, 250],
                        "action": "Click",
                    }
                }
            )

        elif action_type == "PLAY":
            card_index = int(parts[1]) - 1
            target_index = int(parts[2])
            # print(f"打出卡牌：索引 {card_index}")
            card_info = cards[card_index]
            card_name = card_info.get("name", None)
            card_type = card_info.get("type", None)
            # print(card_type)
            if card_type == "Attack":
                target_index = target_index + 1
            converted_monster_box = []
            monster_box = {}

            if isinstance(monsters, str):
                monsters = json.loads(monsters)
            if len(parts) > 2:
                if target_index == 0:
                    converted_monster_box = [467, 180, 40, 40]
                elif target_index > 0:
                    monster_box = monsters[target_index - 1].get("box", None)
                    print(monster_box)
                    converted_monster_box = [monster_box["x"], monster_box["y"], monster_box["w"] / 2,
                                             monster_box["h"] / 2]
            # print(converted_monster_box)
            # img = context.tasker.controller.post_screencap().wait().get()
            print(converted_monster_box)
            retail = context.run_task(
                "Click1",
                pipeline_override={
                    "Click1": {
                        "recognition": "OCR",
                        "expected": card_name,
                        "action": "Swipe",
                        "end": converted_monster_box
                    },
                    "Click2": {
                        "action": "Click",
                        "target": converted_monster_box
                    }
                }
            )
            # print("123")

        elif action_type == "END":
            """结束回合"""
            print("结束回合")
            context.run_task(
                "end_turn",
                pipeline_override={
                    "end_turn": {
                        "recognition": "OCR",
                        "expected": "End Turn",
                        "action": "Click"
                    }
                }
            )

        elif action_type == "PROCEED":
            print("前进")
            context.run_task(
                "proceed",
                pipeline_override={
                    "proceed": {
                        "recognition": "OCR",
                        "expected": "PROCEED",
                        "action": "Click"
                    }
                }
            )

        elif action_type == "RETURN":
            """返回上一级菜单"""
            print("返回")
            context.run_task(
                "return_to_previous",
                pipeline_override={
                    "return_to_previous": {
                        "recognition": "OCR",
                        "expected": "返回",
                        "action": "Click"
                    }
                }
            )

        elif action_type == "CONFIRM":
            context.run_task(
                "confirm",
                pipeline_override={
                    "confirm": {
                        "recognition": "OCR",
                        "expected": "确认",
                        "action": "Click"
                    }
                }
            )

        elif action_type == "LEAVE":
            """离开当前界面"""
            print("离开")
            context.run_action(
                "leave",
                pipeline_override={
                    "leave": {
                        "recognition": "OCR",
                        "expected": "离开",
                        "action": "Click"
                    }
                }
            )

        elif action_type == "CHOOSE":

            img = context.tasker.controller.post_screencap().wait().get()
            event = Event()
            best_match = {
                "card": [],
                "count": 0,
                "box": (0, 0, 0, 0)
            }
            # 当没有识别到怪物时停止匹配

            reco_detail = context.run_recognition(
                "事件识别_ocr",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "事件识别_ocr": {
                        "recognition": "OCR",
                        "expected": "",  # 每次只匹配一个模板
                        # "green_mask": True
                    }
                }
            )
            eventname_detail = context.run_recognition(
                "事件名称识别_ocr",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "事件名称识别_ocr": {
                        "recognition": "OCR",
                        "expected": "",  # 每次只匹配一个模板
                        "roi": [200, 150, 400, 50]
                        # "green_mask": True
                    }
                }
            )

            bracket_pattern = re.compile(r'^[\[【［]')

            # 按y坐标分组
            groups = defaultdict(list)
            for result in reco_detail.all_results:
                y = result.box[1]
                groups[y].append(result)

            result_list = []

            for y in groups:
                current_group = groups[y]
                bracket_items = []
                non_bracket_items = []

                # 分类
                for item in current_group:
                    if bracket_pattern.search(item.text):
                        bracket_items.append(item)
                    else:
                        non_bracket_items.append(item)

                # 按x坐标排序（从左到右）
                bracket_sorted = sorted(bracket_items, key=lambda x: x.box[0])
                non_bracket_sorted = sorted(non_bracket_items, key=lambda x: x.box[0])

                # 合并文本
                combined_text = ''.join([item.text for item in bracket_sorted + non_bracket_sorted])
                result_list.append(combined_text)

            list0 = fill_index(result_list)
            print(list0)
            index_value = list0[0]["index"]
            print(index_value)

            """选择事件中的某个选项"""
            context.run_task(
                "choose_option",
                pipeline_override={
                    "choose_option": {
                        "recognition": "OCR",
                        # "roi": [200, 150, 400, 50],
                        "expected": index_value,
                        "action": "Click"
                    }
                }
            )
        else:
            print(f"未知的命令: {command}")
        # **调用 execute() 来处理**

        return True