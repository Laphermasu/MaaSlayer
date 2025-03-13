from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.context import Context
from maa.resource import Resource
from maa.controller import AdbController
from maa.library import Library
from maa.custom_action import CustomAction
from src.core.data_models import Monster, Cards
from src.core.data_models import Player
from src.custom_recognition.monster_recognition import MonsterRecognition
from src.custom_recognition.player_recognition import PlayerRecognition
from src.custom_recognition.event_recognition import EventRecognition
from src.custom_recognition.cards_recogntion import CardRecognition
from src.utils.json_utils import JsonUtils
# from sb3_contrib.ppo_mask import MaskablePPO
# from src.custom_action.adb_action import ADBAction
# from SlayTheSpireRL.slay_the_spire_env import SlayTheSpireEnv
import json
import threading
# import torch as th
# from func import (
#     get_available_commands,
#     get_screen,
#     get_hand,
#     get_monsters,
#     get_player,
#     get_deck,
#     get_relics,
#     get_potions,
#     get_map,
#     get_info
# )

resource = Resource()

def generate_json(monsters, cards):
    available_commands = get_available_commands()
    screen = get_screen()
    combat_state = {
        "monsters": [monster.__dict__ for monster in monsters],
        # "monsters": get_monsters(),
        "hand": [card.__dict__ for card in cards],
        # "hand": get_hand(),
        # "player": [player.__dict__ for player in players],
        "player": get_player(),
    }
    deck = get_deck()
    relics = get_relics()
    max_hp, gold, current_hp, floor, room_type = get_info()
    potions = get_potions()
    game_map = get_map()

    game_state = {
        "screen_type": screen['type'],
        "screen_state": screen['state'],
        "combat_state": combat_state,
        "deck": deck,
        "relics": relics,
        "max_hp": max_hp,
        "gold": gold,
        "potions": potions,
        "current_hp": current_hp,
        "floor": floor,
        "map": game_map,
        "room_type": room_type,
    }

    json_data = {
        "available_commands": available_commands,
        "ready_for_command": True,
        "in_game": True,
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
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail),Monster
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
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail)
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
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail)
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
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail),Cards
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
        input_methods= 1,
        config=device.config,
    )
    controller.post_connection().wait()
    print("设备连接成功")
    print("初始化tasker")
    tasker = Tasker()
    # tasker = Tasker(notification_handler=MyNotificationHandler())
    tasker.bind(resource, controller)
    # adb_action = ADBAction(controller, Context(resource))
    if not tasker.inited:
        print("Failed to init MAA.")
        exit()
    print("tasker初始化完成")

    # 注册自定义识别器
    resource.register_custom_recognition("monsterRecognition", MonsterRecognition())
    # resource.register_custom_recognition("playerRecognition", PlayerRecognition())
    # resource.register_custom_recognition("eventRecognition", EventRecognition())
    resource.register_custom_recognition("cardRecognition", CardRecognition())
    resource.register_custom_action("ADBAction", ADBAction())

    # 共享字典存储识别结果
    # result_dict = {}
    #
    # # 创建线程并执行
    # threads = [
    #     threading.Thread(target=recognize_monsters, args=(tasker, result_dict)),
    #     threading.Thread(target=recognize_players, args=(tasker, result_dict)),
    #     threading.Thread(target=recognize_events, args=(tasker, result_dict)),
    #     threading.Thread(target=recognize_cards, args=(tasker, result_dict))
    # ]
    #
    # for thread in threads:
    #     thread.start()
    #
    # for thread in threads:
    #     thread.join()
    #
    # print("所有识别任务完成")
    #
    # # 解析 JSON
    # monsters = result_dict.get("monsters", [])
    # players = result_dict.get("players", [])
    # events = result_dict.get("events", [])
    # cards = result_dict.get("cards", [])
    #
    # game_state = json.loads(generate_json(monsters,cards))
    # print(game_state)
    # env = SlayTheSpireEnv({})
    # device = th.device("cuda" if th.cuda.is_available() else "cpu")
    # model = MaskablePPO.load("maskable_ppo_slay_the_spire1.zip", env=env, device=device)
    #
    # # 解析 JSON，转换为环境可用的格式
    # env.update_game_state(game_state)
    # obs = env.flatten_observation(game_state)
    # obs_tensor = {key: th.tensor(value, dtype=th.float32).unsqueeze(0).to(device) for key, value in obs.items()}
    #
    # action_mask = env.get_invalid_action_mask(game_state)
    # action_mask_tensor = th.tensor(action_mask, dtype=th.bool).unsqueeze(0).to(device)
    # obs_numpy = {key: value.cpu().numpy() for key, value in obs_tensor.items()}
    # action_mask_numpy = action_mask_tensor.cpu().numpy()
    #
    # action, _states = model.predict(obs_numpy, action_masks=action_mask_numpy)
    # action = int(action)
    # chosen_command = env.actions[action]
    # print(f"Action: {chosen_command}")
    # adb_action.execute(chosen_command, cards, monsters)
    print("pipeline定义")
    pipeline_override = {
        "ADBAction": {"action": "custom", "custom_action": "ADBAction"},
    }
    # "ADBAction": {"action": "custom", "custom_action": "ADBAction", "custom_action_param": game_state},
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


@resource.custom_action("ADBAction")
class ADBAction(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) ->bool:
        """
        :param context: 运行的 Context
        :param argv: 自定义参数
        :return: RunResult(success=True/False)
        """
        print("开始执行 ADBAction 自定义动作")
        command = "START 1234"
        # command = argv.args[0] if argv.args else None
        parts = command.split()
        action_type = parts[0]

        if action_type == "START":
            """点击开始游戏按钮"""
            print("开始游戏")
            img = context.tasker.controller.post_screencap().wait().get()
            # 下面这个run_task是能够成功点击到Play的
            context.run_task("StartGame",pipeline_override={
                    "Click": {
                        "action": "Click",
                        "target": [72,423,86,49]
                    },
                    "StartGame": {
                        "recognition": "OCR",
                        "expected": "Play",
                        "action": "Click"
                }})
            # 下面的只做了识别，没有点击到Play
            reco_detail = context.run_recognition(
                "StartGame",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "StartGame": {
                        "recognition": "OCR",
                        "expected": "Play",
                        "action": "Click"
                }}
            )
            # 下面的只做了点击[0,0,0,0]，没有识别到Play
            detail = context.run_action(
                "StartGame",
                pipeline_override={
                    "StartGame": {
                        "recognition": "OCR",
                        "expected": "Play",
                        "action": "Click"
                        # "next": "standard"/
                    },
                    "standard": {
                        "recognition": "OCR",
                        "expected": "Standard",
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
                        "expected": "Embark",
                        "action": "Click",
                    }
                }
            )
        elif action_type == "PLAY":
            card_index = int(parts[1]) - 1
            print(f"打出卡牌：索引 {card_index}")

            card_info = cards[card_index]
            card_box = card_info.get("box", None)

            if len(parts) > 2:
                target_index = int(parts[2])
                if target_index < 0 or target_index >= len(monsters):
                    print(f"错误: 目标索引 {target_index} 超出范围")
                    return
                monster_info = monsters[target_index]
                monster_box = monster_info.get("box", None)
            else:
                monster_box = [100, 575, 40, 40]  # 默认目标

                context.run_action(
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
                    },
                }
                )

        elif action_type == "END":
            """结束回合"""
            print("结束回合")
            context.run_action(
                "end_turn",
                pipeline_override={
                    "end_turn": {
                        "recognition": "OCR",
                        "expected": "结束回合",
                        "action": "Click"
                    }
                }
            )

        elif action_type == "PROCEED":
            print("前进")
            context.run_action(
                "proceed",
                pipeline_override={
                    "proceed": {
                        "recognition": "OCR",
                        "expected": "前进",
                        "action": "Click"
                    }
                }
            )

        elif action_type == "RETURN":
            """返回上一级菜单"""
            print("返回")
            context.run_action(
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
            context.run_action(
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
            """选择事件中的某个选项"""
            context.run_action(
                "choose_option",
                pipeline_override={
                    "choose_option": {
                        "recognition": "TemplateMatch",
                        "template": "assets\\resource\\image\\option.png",
                        "index": int(parts[1]),
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