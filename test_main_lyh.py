from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.context import Context
from maa.resource import Resource
from maa.controller import AdbController
from maa.custom_action import CustomAction
from src.core.data_models import Monster, Cards ,Event
from src.core.data_models import Player
from src.custom_recognition.monster_recognition import MonsterRecognition
from src.custom_recognition.player_recognition import PlayerRecognition
from src.custom_recognition.event_recognition import EventRecognition
from src.custom_recognition.cards_recogntion import CardRecognition
from src.utils.json_utils import JsonUtils
from collections import defaultdict
from sb3_contrib.ppo_mask import MaskablePPO
from src.AI_model.SlayTheSpireRL.slay_the_spire_env import SlayTheSpireEnv
import re
import json
import threading
import torch as th
from func import (
    get_available_commands,
    get_deck,
    get_relics,
    get_map
)

resource = Resource()


def generate_json(screen_type ,monsters = None,events = None,cards= None,player=None):
    deck = get_deck()
    relics = get_relics()
    game_map = get_map()
    if screen_type == "NONE":
        available_commands = get_available_commands()
        combat_state = {
            "monsters": [monster.__dict__ for monster in monsters],
            "hand": [card.__dict__ for card in cards],
            "player": {
                "block": player.block,
                "energy": player.energy,
                "powers": player.powers
            }
        }
        game_state = {
            "screen_type": screen_type,
            "screen_state": {},
            "combat_state": combat_state,
            "deck": deck,
            "relics": relics,
            "max_hp": player.max_hp,
            "gold": player.gold,
            "potions": [],
            "current_hp": player.current_hp,
            "floor": player.floor,
            "map": game_map,
            "ascension_level": 0,
        }

        json_data = {
            "available_commands": available_commands,
            "ready_for_command": True,
            "in_game": True,
            "game_state": game_state
        }
        json_result = json.dumps(json_data)

    elif screen_type == "EVENT":
        game_state = {
            "screen_type": screen_type,
            "screen_state": {
                "event_id": events.event_id,
                "options": events.options,
                "deck": deck,
                "relics": relics,
                "max_hp": player.max_hp,
                "gold": player.gold,
                "potions": [],
                "current_hp": player.current_hp,
                "floor": player.floor,
                "map": game_map,
                "ascension_level": 0,
            }
        }

        json_data = {
            "game_state": game_state
        }

        json_result = json.dumps(json_data)

    return json_result


def recognize_monsters(tasker, result_dict):
    print("开始识别怪物")
    pipeline_override = {
        "MyRecongitionEntry": {"recognition": "custom", "custom_recognition": "monsterRecognition"},
    }
    task_detail = tasker.post_task("MyRecongitionEntry", pipeline_override).wait().get()
    monsters = JsonUtils.deserialize_from_str(
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail), Monster
    )
    result_dict["monsters"] = monsters  # 存储到共享字典
    print(f"识别到的怪物: {monsters}")


def recognize_players(tasker, result_dict):
    print("开始识别玩家")
    pipeline_override = {
        "MyRecongitionEntry": {"recognition": "custom", "custom_recognition": "playerRecognition"},
    }
    task_detail = tasker.post_task("MyRecongitionEntry", pipeline_override).wait().get()
    players = JsonUtils.deserialize_from_str(
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail), Player
    )
    result_dict["players"] = players
    print(f"识别到的玩家: {players}")


def recognize_events(tasker, result_dict):
    print("开始识别事件")
    pipeline_override = {
        "MyRecongitionEntry": {"recognition": "custom", "custom_recognition": "eventRecognition"},
    }
    task_detail = tasker.post_task("MyRecongitionEntry", pipeline_override).wait().get()
    events = JsonUtils.deserialize_from_str(
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail), Event
    )
    result_dict["events"] = events
    print(f"识别到的事件: {events}")


def recognize_cards(tasker, result_dict):
    print("开始识别卡牌")
    pipeline_override = {
        "MyRecongitionEntry": {"recognition": "custom", "custom_recognition": "cardRecognition"},
    }
    task_detail = tasker.post_task("MyRecongitionEntry", pipeline_override).wait().get()
    cards = JsonUtils.deserialize_from_str(
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail), Cards
    )
    result_dict["cards"] = cards
    print(f"识别到的卡牌: {cards}")


def main():
    # 初始化 MaaFramework
    user_path = "./"
    resource_path = "./assets/resource"

    Toolkit.init_option(user_path)

    res_job = resource.post_bundle(resource_path)
    res_job.wait()

    # 连接设备
    print("开始连接设备")
    adb_devices = Toolkit.find_adb_devices()
    if not adb_devices:
        print("No ADB device found.")
        exit()

    device = adb_devices[0]
    controller = AdbController(
        adb_path=device.adb_path,
        address=device.address,
        screencap_methods=device.screencap_methods,
        input_methods=device.input_methods,
        config=device.config,
    )
    controller.post_connection().wait()
    print("设备连接成功")

    print("初始化tasker")
    tasker = Tasker()
    # tasker = Tasker(notification_handler=MyNotificationHandler())
    tasker.bind(resource, controller)

    if not tasker.inited:
        print("Failed to init MAA.")
        exit()
    print("tasker初始化完成")

    resource.register_custom_recognition("monsterRecognition", MonsterRecognition())
    resource.register_custom_recognition("playerRecognition", PlayerRecognition())
    resource.register_custom_recognition("eventRecognition", EventRecognition())
    resource.register_custom_recognition("cardRecognition", CardRecognition())
    resource.register_custom_action("ADBAction", ADBAction())


    # 共享字典存储识别结果
    result_dict = {}

    # 创建线程并执行
    threads = [
        threading.Thread(target=recognize_monsters, args=(tasker, result_dict)),
        threading.Thread(target=recognize_players, args=(tasker, result_dict)),
        threading.Thread(target=recognize_events, args=(tasker, result_dict)),
        threading.Thread(target=recognize_cards, args=(tasker, result_dict))
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("所有识别任务完成")

    # 解析 JSON
    monsters = result_dict.get("monsters", [])
    # print(monsters)
    players = result_dict.get("players", [])
    events = result_dict.get("events", [])
    cards = result_dict.get("cards", [])
    game_state = json.loads(generate_json(screen_type="NONE",monsters=monsters,events=events,cards=cards,player=players))
    print(game_state)

    env = SlayTheSpireEnv({})
    device = th.device("cuda" if th.cuda.is_available() else "cpu")
    model = MaskablePPO.load("src/AI_model/maskable_ppo_slay_the_spire.zip", env=env, device=device)

    # 解析 JSON，转换为环境可用的格式
    env.update_game_state(game_state)
    obs = env.flatten_observation(game_state)
    obs_tensor = {key: th.tensor(value, dtype=th.float32).unsqueeze(0).to(device) for key, value in obs.items()}

    action_mask = env.get_invalid_action_mask(game_state)
    action_mask_tensor = th.tensor(action_mask, dtype=th.bool).unsqueeze(0).to(device)
    obs_numpy = {key: value.cpu().numpy() for key, value in obs_tensor.items()}
    action_mask_numpy = action_mask_tensor.cpu().numpy()

    action, _states = model.predict(obs_numpy, action_masks=action_mask_numpy)
    action = int(action)
    chosen_command = env.actions[action]
    print(chosen_command)

    game_state['game_state']['screen_state']['chosen_command'] = chosen_command
    print(game_state)
    print("pipeline定义")
    pipeline_override = {
        "ADBAction": {"action": "custom", "custom_action": "ADBAction", "custom_action_param": game_state},
    }
    print("pipeline选中任务执行")
    tasker.post_task("ADBAction", pipeline_override).wait().get()
    print("任务执行完成")
    # env.close()
    # 主循环
    # while True:
    #     game_state_manager.update_state()
    #     current_state = game_state_manager.get_state()
    #     print("Current Game State:", current_state)
    #     # 这里可以根据游戏状态执行相应的策略


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






@resource.custom_action("ADBAction")
class ADBAction(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) ->bool:
        """
        :param context: 运行的 Context
        :param argv: 自定义参数
        :return: RunResult(success=True/False)
        """
        print("开始执行 ADBAction 自定义动作")
        game_state = argv.custom_action_param
        game_state = json.loads(game_state)
        game_state = game_state["game_state"]

        screen_state =  game_state.get("screen_state", {})
        command = screen_state.get("chosen_command", {})

        combat_state = game_state.get("combat_state", {})
        monsters = combat_state.get("monsters", [])
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
                        "roi": [1000,500,250,250],
                        "action": "Click",
                    }
                }
            )

        elif action_type == "PLAY":
            card_index = int(parts[1]) - 1
            # print(f"打出卡牌：索引 {card_index}")
            card_info = cards[card_index]
            card_name = card_info.get("name", None)
            converted_monster_box = []
            print(card_name)
            if len(parts) > 2:
                target_index = int(parts[2])
                monster_info = monsters[target_index - 1]
                monster_box = monster_info.get("box", None)
                converted_monster_box = [monster_box["x"], monster_box["y"], monster_box["w"], monster_box["h"]]
                # print(converted_monster_box)
            elif len(parts) < 3:
                converted_monster_box = [643,414, 40, 40]  # 默认目标
                # converted_monster_box = [100, 575, 40, 40]  # 默认目
            # img = context.tasker.controller.post_screencap().wait().get()
            context.run_task(
                "Click1",
                pipeline_override={
                    "Click1": {
                        "recognition": "OCR",
                        "expected": card_name,
                        "action": "Click",
                        "next": "Click2"
                    },
                    "Click2": {
                        "action": "Click",
                        "target": converted_monster_box
                    }
                }
            )
            print("123")

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
                        "roi": [200, 150, 400, 50],
                        "expected": index_value,
                        "action": "Click"
                    }
                }
            )

        else:
            print(f"未知的命令: {command}")
        # **调用 execute() 来处理**


        return True




if __name__ == "__main__":
    main()