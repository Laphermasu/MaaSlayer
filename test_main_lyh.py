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
from src.custom_action.abd_action import ADBAction
import threading
from src.AI_model.model_run import *
import json

resource = Resource()


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
        input_methods=1,
        config=device.config,
    )
    controller.post_connection().wait()
    print("设备连接成功")

    print("初始化tasker")
    tasker = Tasker()
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
    print(monsters)
    players = result_dict.get("players", [])
    events = result_dict.get("events", [])
    cards = result_dict.get("cards", [])

    env, model, device = initialize_model()

    chosen_command, game_state = predict_action("NONE", monsters, events, cards, players, env, model, device)
    print(f"Action: {chosen_command}")
    perform_command(tasker, chosen_command, game_state, monsters)
    print("任务执行完成")
    close_model(env)
    # 主循环
    # while True:
    #     game_state_manager.update_state()
    #     current_state = game_state_manager.get_state()
    #     print("Current Game State:", current_state)
    #     # 这里可以根据游戏状态执行相应的策略

def perform_command(tasker: Tasker,command,game_state,monsters=None):
    command = "CHOOSE 0"
    game_state['game_state']['screen_state']['chosen_command'] = command
    part = command.split()
    action_type = part[0]
    if action_type == "PLAY":
        monster_json = json.dumps([monster.__dict__ for monster in monsters])
        game_state['game_state']['combat_state']['monster_box'] = monster_json

    print(game_state)
    pipeline_override = {
        # "ADBAction": {"action": "custom", "custom_action": "ADBAction"},
        "ADBAction": {"action": "custom", "custom_action": "ADBAction", "custom_action_param": game_state},
    }
    print("pipeline选中任务执行")
    tasker.post_task("ADBAction", pipeline_override).wait().get()

if __name__ == "__main__":
    main()