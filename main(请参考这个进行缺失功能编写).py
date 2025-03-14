from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.resource import Resource
from maa.controller import AdbController
from src.custom_recognition.monster_recognition import MonsterRecognition
from src.custom_recognition.player_recognition import PlayerRecognition
from src.custom_recognition.event_recognition import EventRecognition
from src.custom_recognition.cards_recogntion import CardRecognition
from src.custom_recognition.end_turn_recognition import EndTurnRecognition
from src.custom_recognition.unknown_recognition import UnknownRecognition
from src.custom_recognition.cards_rewards_recognition import CardrewardRecognition
from src.utils.json_utils import JsonUtils
from src.AI_model.model_run import *
from src.custom_recognition.recognition import recognize
from src.custom_action.abd_action import ADBAction
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
    resource.register_custom_recognition("CardrewardRecognition",CardrewardRecognition())
    resource.register_custom_recognition("UnknownRecognition", UnknownRecognition())
    resource.register_custom_action("ADBAction", ADBAction())

    # 读取本地pipeline
    pipeline_local = JsonUtils.load_json("./assets/resource/pipelin/slay_task.json")

    # 定义pipeline_override
    pipeline_override = {
            "monsterRecognition": {"recognition": "custom", "custom_recognition": "monsterRecognition"},
            "MapRecognition": {"recognition": "custom", "custom_recognition": "MapRecognition"},
            "EndTurnRecognition": {"recognition": "custom", "custom_recognition": "EndTurnRecognition"},
            "playerRecognition": {"recognition": "custom", "custom_recognition": "playerRecognition"},
            "eventRecognition": {"recognition": "custom", "custom_recognition": "eventRecognition"},
            "cardRecognition": {"recognition": "custom", "custom_recognition": "cardRecognition"},
            "UnknownRecognition": {"recognition": "custom", "custom_recognition": "UnknownRecognition"}
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
            # 识别未知内容
            event_type = (tasker.post_task("UnknownRecognition", pipeline_override).wait().get()).nodes[0].recognition.best_result.detail
            if event_type == "事件":
                run_task("事件流程")
                event = recognize(tasker,"event")
                player = recognize(tasker,"player")
                command,game_state= predict_action("EVENT", {}, event,{}, player, env, model, device)
                perform_command(tasker,command,game_state)
            elif event_type == "monster":
                command,game_state = predict_action("EVENT", {}, event, player, env, model, device)
                perform_command(tasker,command,game_state)
            elif event_type == "战斗":
                while end_turn_exist(tasker):
                    monsters = recognize(tasker,"monster")
                    player = recognize(tasker,"player")
                    cards = recognize(tasker,"card")
                    command,game_state = predict_action("NONE", monsters, {}, cards, player, env, model, device)
                    perform_command(tasker,command,game_state,monsters)
                # 战斗结束后奖励领取
                get_reward(tasker, pipeline_local ,env,model,device)
            elif event_type == "宝箱":
                tasker.post_task("宝箱界面操作", pipeline_local).wait()
            elif event_type == "商店":
                tasker.post_task("商人界面操作", pipeline_local).wait()
            continue
        elif map_type == "休息":
            tasker.post_task("点击睡觉", pipeline_local).wait()
            continue
        elif map_type == "小怪":
            while end_turn_exist(tasker):
                # 战斗流程
                monsters = recognize(tasker,"monster")
                player = recognize(tasker,"player")
                cards = recognize(tasker,"card")
                command,game_state = predict_action("NONE", monsters, {}, cards, player, env, model, device)
                perform_command(tasker,command,game_state,monsters)
            # 战斗结束后奖励领取
            get_reward(tasker, pipeline_local,env,model,device)
            continue
        elif map_type == "BOSS":
            while end_turn_exist(tasker):
                # 战斗流程
                monsters = recognize(tasker, "monster")
                player = recognize(tasker, "player")
                cards = recognize(tasker, "card")
                command,game_state = predict_action("NONE",monsters,{},cards ,player,env,model,device)
                perform_command(tasker,command,game_state,monsters)
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
    cardreward = recognize(tasker, "cardreward")
    player = recognize(tasker, "player")
    chosen_card = predict_action("CARD_REWARD",{}, {}, cardreward,player,env,model,device)
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

def perform_command(tasker: Tasker,command,game_state,monsters=None):
    # command = "PLAY 1 0"
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