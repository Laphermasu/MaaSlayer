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
from src.custom_recognition.end_turn_recognition import EndTurnRecognition
from src.utils.json_utils import JsonUtils
from src.AI_model.model_run import *
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

    env, model, device = initialize_model()

    # 注册自定义行为
    resource.register_custom_recognition("EndTurnRecognition", EndTurnRecognition())
    resource.register_custom_recognition("monsterRecognition", MonsterRecognition())
    resource.register_custom_recognition("playerRecognition", PlayerRecognition())
    resource.register_custom_recognition("eventRecognition", EventRecognition())
    resource.register_custom_recognition("cardRecognition", CardRecognition())

    # 读取本地pipeline
    pipeline_local = JsonUtils.load_json("./assets/resource/pipelin/slay_task.json")

    # 定义pipeline_override
    pipeline_override = {
            "monsterRecognition": {"recognition": "custom", "custom_recognition": "monsterRecognition"},
            "MapRecognition": {"recognition": "custom", "custom_recognition": "MapRecognition"},
        }

    Boss_exist = True
    # 以下为伪代码
    while Boss_exist: # 主流程
        map_type = (tasker.post_task("MapRecognition", pipeline_override).wait().get()).nodes[0].recognition.best_result.detail
        if map_type == "宝箱":
            tasker.post_task("宝箱界面操作", pipeline_local).wait()
            continue
        elif map_type == "商店":
            tasker.post_task("商人界面操作", pipeline_local).wait()
            continue
        elif map_type == "问号":
            #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
            #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
            # 待实现
            event_type = run_task("问号识别")
            #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
            #↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

            if event_type == "event":
                event = run_task("事件流程")
                player = run_task("角色信息识别")
                command = predict_action("EVENT", {}, event,{}, player, env, model, device)
                perform_command(command)
            elif event_type == "monster":
                while end_turn_exist(tasker):
                    #↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
                    # 战斗流程根据实际代码实现下面功能
                    monsters = run_task("怪物识别")
                    player = run_task("角色信息识别")
                    cards = run_task("卡牌识别")
                    command = predict_action("NONE", monsters, {}, cards, player, env, model, device)
                    perform_command(command)
                # 战斗结束后奖励领取
                get_reward(tasker, pipeline_local ,env,model,device)
            continue
        elif map_type == "休息":
            tasker.post_task("点击睡觉", pipeline_local).wait()
            continue
        elif map_type == "小怪":
            while end_turn_exist(tasker):
                # 战斗流程
                monsters = run_task("怪物识别")
                player = run_task("角色信息识别")
                cards = run_task("卡牌识别")
                command = predict_action("NONE", monsters, {}, cards, player, env, model, device)
                perform_command(command)
            # 战斗结束后奖励领取
            get_reward(tasker, pipeline_local,env,model,device)
            continue
        elif map_type == "BOSS":
            while end_turn_exist(tasker):
                # 战斗流程
                player = run_task("角色信息识别")
                monsters = run_task("怪物识别")
                cards = run_task("卡牌识别")
                command = predict_action("NONE",monsters,{},cards ,player,env,model,device)
                perform_command(command)
            # 战斗结束后奖励领取
            get_reward(tasker, pipeline_local ,env,model,device)
            run_task("BOSS遗物领取")
            Boss_exist = False
            continue
    print("一层战斗结束")

def end_turn_exist(tasker: Tasker) -> bool:
    detail = tasker.post_task(
        "EndTurnRecognition", 
        pipeline_override= {
            "EndTurnRecognition": {
                "recognition": "custom", 
                "custom_recognition": "EndTurnRecognition"
                }
            }).wait().get()
    return bool(detail.nodes[0].recognition.best_result.detail)

def get_reward(tasker: Tasker, pipeline_local: dict ,env,model,device):
    tasker.post_task("奖励领取1", pipeline_local).wait()
    cards = run_task("卡牌识别")  # 超
    player = run_task("角色信息识别")  # 超
    chosen_card = predict_action("CARD_REWARD",{}, {}, cards,player,env,model,device)
    tasker.post_task("选择卡牌", 
                    pipeline = {
                        "选择卡牌": {
                            "recognition": "OCR",
                            "expected": chosen_card,
                            "action": "Click",
                            "next": "确认"
                            },
                        "点击确认": {
                            "recognition": "OCR",
                            "action": "Click",
                            "expected": [
                                "Proceed"
                            ]
                        }
                    }).wait()
    tasker.post_task("点击跳过", pipeline_local).wait()

if __name__ == "__main__":
    main()