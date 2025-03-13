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

    Boss_exist = True
    # 以下为伪代码
    while Boss_exist: # 主流程
        map_type = run_task("随机选择可用地图节点")
        if map_type == "chest":
            run_task("宝箱自动流程")
            continue
        elif map_type == "shop":
            run_task("商人自动流程")
            continue
        elif map_type == "问号":
            event_type = run_task("问号识别")
            if event_type == "event":
                run_task("事件流程")
            elif event_type == "monster":
                while monsters = run_task("怪物识别"):
                    player = run_task("角色信息识别")
                    command = ai_command(monsters, player)
                    perform_command(command)
                run_task("奖励领取")
            continue
        elif map_type == "rest":
            run_task("休息流程")
            continue
        elif map_type == "monster":
            while run_task("怪物识别"):
                player = run_task("角色信息识别")
                command = ai_command(monsters, player)
                perform_command(command)
            run_task("奖励领取")
            continue
        elif map_type == "BOSS":
            while run_task("怪物识别"):
                player = run_task("角色信息识别")
                command = ai_command(monsters, player)
                perform_command(command)
            run_task("奖励领取")
            run_task("BOSS遗物领取")
            Boss_exist = False
            continue
    print("一层战斗结束")

if __name__ == "__main__":
    main()