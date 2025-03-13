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
from sb3_contrib.ppo_mask import MaskablePPO
from SlayTheSpireRL.slay_the_spire_env import SlayTheSpireEnv
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
            "monsters": [{k: v for k, v in monster.__dict__.items() if k != "box"} for monster in monsters],
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
    players = result_dict.get("players", [])
    events = result_dict.get("events", [])
    cards = result_dict.get("cards", [])
    game_state = json.loads(generate_json(screen_type="EVENT",monsters=monsters,events=events,cards=cards,player=players))
    print(game_state)
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
    #
    # print(f"Action: {chosen_command}")
    #
    # env.close()



if __name__ == "__main__":
    main()