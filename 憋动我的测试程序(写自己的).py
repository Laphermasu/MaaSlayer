from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.context import Context
from maa.resource import Resource
from maa.controller import AdbController
from maa.custom_action import CustomAction
from src.core.data_models import Monster, Cards
from src.core.data_models import Player
from src.custom_recognition.monster_recognition import MonsterRecognition
from src.custom_recognition.player_recognition import PlayerRecognition
from src.custom_recognition.event_recognition import EventRecognition
from src.custom_recognition.cards_recogntion import CardRecognition
from src.custom_recognition.map_recognition import MapRecognition
from src.utils.json_utils import JsonUtils

import json


resource = Resource()

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
    # tasker = Tasker(notification_handler=MyNotificationHandler())
    tasker.bind(resource, controller)

    if not tasker.inited:
        print("Failed to init MAA.")
        exit()
    print("tasker初始化完成")

    # 注册自定义识别器
    resource.register_custom_recognition("monsterRecognition", MonsterRecognition())
    resource.register_custom_recognition("MapRecognition", MapRecognition())

    print("重写pipeline")
    pipeline_override = {
        "monsterRecognition": {"recognition": "custom", "custom_recognition": "monsterRecognition"},
        # "StartGame": {
        #         "recognition": "OCR",
        #         "expected": "Play",
        #         "action": "Click",
        # }
        "MapRecognition": {"recognition": "custom", "custom_recognition": "MapRecognition"},
    }
    print("开始执行pipeline中选中任务")
    task_detail = tasker.post_task("monsterRecognition", pipeline_override).wait().get()
    # task_detail = tasker.post_task("MapRecognition", pipeline_override).wait().get()
    print("任务执行完成")
    monsters = JsonUtils.deserialize_from_str(
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail),Monster
    )

    print(monsters)
    # print(task_detail.nodes[0].recognition.best_result.detail)
    
    # 主循环
    # while True:
    #     game_state_manager.update_state()
    #     current_state = game_state_manager.get_state()
    #     print("Current Game State:", current_state)
    #     # 这里可以根据游戏状态执行相应的策略


if __name__ == "__main__":
    main()