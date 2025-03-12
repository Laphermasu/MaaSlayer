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
from sb3_contrib.ppo_mask import MaskablePPO
from src.custom_action.adb_action import ADBAction
from SlayTheSpireRL.slay_the_spire_env import SlayTheSpireEnv
import json
import threading
import torch as th
from func import (
    get_available_commands,
    get_screen,
    get_hand,
    get_monsters,
    get_player,
    get_deck,
    get_relics,
    get_potions,
    get_map,
    get_info
)

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
        input_methods=device.input_methods,
        config=device.config,
    )
    controller.post_connection().wait()
    print("设备连接成功")
    context_handle = Library.framework().MaaContextCreate()
    context = Context(context_handle)
    adb_action = ADBAction(controller, context)
    print("初始化tasker")
    tasker = Tasker()
    # tasker = Tasker(notification_handler=MyNotificationHandler())
    tasker.bind(resource, controller)

    if not tasker.inited:
        print("Failed to init MAA.")
        exit()
    print("tasker初始化完成")

    # 注册自定义识别器
    resource.register_custom_recognition("monsterRecognition", MonsterRecognition())
    # resource.register_custom_recognition("playerRecognition", PlayerRecognition())
    # resource.register_custom_recognition("eventRecognition", EventRecognition())
    resource.register_custom_recognition("cardRecognition", CardRecognition())


    # 共享字典存储识别结果
    result_dict = {}

    # 创建线程并执行
    threads = [
        threading.Thread(target=recognize_monsters, args=(tasker, result_dict)),
        # threading.Thread(target=recognize_players, args=(tasker, result_dict)),
        # threading.Thread(target=recognize_events, args=(tasker, result_dict)),
        threading.Thread(target=recognize_cards, args=(tasker, result_dict))
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print("所有识别任务完成")

    # 解析 JSON
    monsters = result_dict.get("monsters", [])
    # players = result_dict.get("players", [])
    # events = result_dict.get("events", [])
    cards = result_dict.get("cards", [])

    game_state = json.loads(generate_json(monsters,cards))
    print(game_state)
    env = SlayTheSpireEnv({})
    device = th.device("cuda" if th.cuda.is_available() else "cpu")
    model = MaskablePPO.load("maskable_ppo_slay_the_spire1.zip", env=env, device=device)

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
    print(f"Action: {chosen_command}")
    adb_action.execute(chosen_command, cards, monsters)


    env.close()
    # 主循环
    # while True:
    #     game_state_manager.update_state()
    #     current_state = game_state_manager.get_state()
    #     print("Current Game State:", current_state)
    #     # 这里可以根据游戏状态执行相应的策略


@resource.custom_action("MonsterRecognitionAction")
class MonsterRecognitionAction(CustomAction):

    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        """
        Perform custom action to recognize bounty monsters.
        :param argv: Custom arguments
        :param context: Running context
        :return: True if executed successfully, otherwise False.
        """
        print("开始执行自定义动作：识别怪物类别")

        # 识别怪物
        img = context.tasker.controller.post_screencap().wait().get()
        # 获得识别区域与结果
        reco_detail = context.run_recognition(
                "识别怪物_图片识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "识别怪物_图片识别": {
                        "recognition": "FeatureMatch",
                        "template": "monster\\大颚虫.png",  # 每次只匹配一个模板
                    }
                }
            )
        # 排除识别区域后再次进行多次识别确认怪物数量

        print("识别完成")
        return True

if __name__ == "__main__":
    main()