import tkinter as tk
from tkinter import scrolledtext
import threading
import time
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
from src.custom_recognition.map_recognition import MapRecognition
from src.custom_action.abd_action import ADBAction
import json
from maa.tasker import Tasker
from src.utils.json_utils import JsonUtils
from src.AI_model.model_run import *
from src.custom_recognition.recognition import recognize
from main_service import main

resource = Resource()

def log_message(msg):
    output_text.insert(tk.END, msg + "\n")
    output_text.see(tk.END)

def run_program():
    threading.Thread(target=_run_program(), daemon=True).start()

def _run_program():
    log_message("程序开始执行...")
    threading.Thread(target=main, daemon=True).start()

    Boss_exist = True
    # 以下为伪代码
    while Boss_exist:  # 主流程
        map_type = (tasker.post_task("MapRecognition", pipeline_override).wait().get()).nodes[
            0].recognition.best_result.detail
        if map_type == "宝箱":
            tasker.post_task("宝箱界面操作", pipeline_local).wait()
            continue
        elif map_type == "商店":
            tasker.post_task("商人界面操作", pipeline_local).wait()
            continue
        elif map_type == "问号":
            # 识别未知内容
            event_type = (tasker.post_task("UnknownRecognition", pipeline_override).wait().get()).nodes[
                0].recognition.best_result.detail
            if event_type == "事件":
                event = recognize(tasker, "event")
                player = recognize(tasker, "player")
                chosen_number = 5
                while chosen_number >= len(event.options):
                    command, game_state = predict_action("EVENT", {}, event, {}, player, env, model, device)
                    chosen_number = int(command.split()[-1])
                log_message(command)
                perform_command(tasker, command, game_state)
            elif event_type == "战斗":
                time.sleep(2)
                while end_turn_exist(tasker) == "True":
                    monsters = recognize(tasker, "monster")
                    player = recognize(tasker, "player")
                    cards = recognize(tasker, "card")
                    card_number = len(cards) + 1
                    monster_number = len(monsters) + 1
                    while card_number > len(cards) and monster_number > len(monsters):
                        command, game_state = predict_action("NONE", monsters, {}, cards, player, env, model, device)
                        part = command.split()
                        action_type = part[0]
                        if action_type == "PLAY":
                            try:
                                card_number = int(part[1])
                                monster_number = int(part[2]) + 1
                            except (IndexError, ValueError):
                                continue  # 出错时继续循环
                        else:
                            break
                    log_message(command)
                    perform_command(tasker, command, game_state, monsters)
                # 战斗结束后奖励领取
                get_reward(tasker, pipeline_local, env, model, device)
            elif event_type == "宝箱":
                tasker.post_task("宝箱界面操作", pipeline_local).wait()
            elif event_type == "商店":
                tasker.post_task("商人界面操作", pipeline_local).wait()
            continue
        elif map_type == "休息":
            tasker.post_task("点击睡觉", pipeline_local).wait()
            continue
        elif map_type == "小怪":
            time.sleep(2)
            while end_turn_exist(tasker) == "True":
                # 战斗流程
                monsters = recognize(tasker, "monster")
                player = recognize(tasker, "player")
                cards = recognize(tasker, "card")
                card_number = len(cards) + 1
                monster_number = len(monsters) + 1
                while card_number > len(cards) and monster_number > len(monsters):
                    command, game_state = predict_action("NONE", monsters, {}, cards, player, env, model, device)
                    part = command.split()
                    action_type = part[0]
                    if action_type == "PLAY":
                        try:
                            card_number = int(part[1])
                            monster_number = int(part[2]) + 1
                        except (IndexError, ValueError):
                            continue  # 出错时继续循环
                    else:
                        break
                log_message(command)
                perform_command(tasker, command, game_state, monsters)
            # 战斗结束后奖励领取
            get_reward(tasker, pipeline_local, env, model, device)
            continue
        elif map_type == "BOSS":
            time.sleep(2)
            while end_turn_exist(tasker) == "True":
                # 战斗流程
                monsters = recognize(tasker, "monster")
                player = recognize(tasker, "player")
                cards = recognize(tasker, "card")
                card_number = len(cards) + 1
                monster_number = len(monsters) + 1
                while card_number > len(cards) and monster_number > len(monsters):
                    command, game_state = predict_action("NONE", monsters, {}, cards, player, env, model, device)
                    part = command.split()
                    action_type = part[0]
                    if action_type == "PLAY":
                        try:
                            card_number = int(part[1])
                            monster_number = int(part[2]) + 1
                        except (IndexError, ValueError):
                            continue  # 出错时继续循环
                    else:
                        break
                log_message(command)
                perform_command(tasker, command, game_state, monsters)
            # 战斗结束后奖励领取
            get_reward(tasker, pipeline_local, env, model, device)
            # run_task("BOSS遗物领取")
            Boss_exist = False
            continue
    print("一层战斗结束")

def select_map():
    threading.Thread(target=_select_map, daemon=True).start()
def _select_map():
    map_type = (tasker.post_task("MapRecognition", pipeline_override).wait().get()).nodes[0].recognition.best_result.detail
    log_message(f"地图选择：{map_type}")

def auto_battle():
    threading.Thread(target=_auto_battle, daemon=True).start()
def _auto_battle():
    log_message("代理战斗开始...")
    time.sleep(2)
    while end_turn_exist(tasker) == "True":
        monsters = recognize(tasker, "monster")
        player = recognize(tasker, "player")
        cards = recognize(tasker, "card")
        card_number = len(cards) + 1
        monster_number = len(monsters) + 1
        while card_number > len(cards) and monster_number > len(monsters):
            command, game_state = predict_action("NONE", monsters, {}, cards, player, env, model, device)
            part = command.split()
            action_type = part[0]
            if action_type == "PLAY":
                try:
                    card_number = int(part[1])
                    monster_number = int(part[2]) + 1
                except (IndexError, ValueError):
                    continue  # 出错时继续循环
            else:
                break
        perform_command(tasker, command, game_state, monsters)
    log_message("代理战斗结束")

def handle_event():
    threading.Thread(target=_handle_event, daemon=True).start()

def _handle_event():
    log_message("处理事件...")
    event = recognize(tasker, "event")
    player = recognize(tasker, "player")
    chosen_number = 5
    while chosen_number >= len(event.options):
        command, game_state = predict_action("EVENT", {}, event, {}, player, env, model, device)
        chosen_number = int(command.split()[-1])
    perform_command(tasker, command, game_state)
    log_message("事件处理完成")

def select_reward():
    threading.Thread(target=_select_reward, daemon=True).start()

def _select_reward():
    log_message("领取奖励...")
    get_reward(tasker, pipeline_local, env, model, device)
    log_message("奖励领取完成")

def rest_decision():
    threading.Thread(target=_rest_decision, daemon=True).start()

def _rest_decision():
    log_message("执行休息决策...")
    tasker.post_task("点击睡觉", pipeline_local).wait()
    log_message("休息完成")

def shop_purchase():
    threading.Thread(target=_shop_purchase, daemon=True).start()

def _shop_purchase():
    log_message("进入商店购买...")
    tasker.post_task("商人界面操作", pipeline_local).wait()
    log_message("商店购买完成")

def exit_program():
    log_message("程序终止...")
    root.quit()

def end_turn_exist(tasker: Tasker) -> bool:
    detail = tasker.post_task(
        "EndTurnRecognition",
        pipeline_override= {
            "EndTurnRecognition": {
                "recognition": "custom",
                "custom_recognition": "EndTurnRecognition"
                }
            }).wait().get()
    return detail.nodes[0].recognition.best_result.detail

def get_reward(tasker: Tasker, pipeline_local: dict ,env,model,device):
    tasker.post_task("奖励领取1", pipeline_local).wait()
    cardreward = recognize(tasker, "cardreward")
    player = recognize(tasker, "player")
    chosen_number = 5
    while chosen_number >= len(cardreward):
        chosen_card, game_state = predict_action("CARD_REWARD", {}, {}, cardreward, player, env, model, device)
        chosen_number = int(chosen_card.split()[-1])
    chosen_card = cardreward[chosen_number].name
    log_message(chosen_card)
    tasker.post_task("选择卡牌",
                    {
                        "选择卡牌": {
                            "recognition": "OCR",
                            "expected": chosen_card,
                            "action": "Click",
                            "next": "点击确认"
                            },
                        "点击确认": {
                            "recognition": "OCR",
                            "action": "Click",
                            "expected": [
                                "Proceed","Confirm"
                            ]
                        }
                    }).wait()
    # tasker.post_task("点击跳过", pipeline_local).wait()

def perform_command(tasker: Tasker,command,game_state,monsters=None):
    # command = "PLAY 1 0"
    game_state['game_state']['screen_state']['chosen_command'] = command
    part = command.split()
    action_type = part[0]
    if action_type == "PLAY":
        monster_json = json.dumps([monster.__dict__ for monster in monsters])
        game_state['game_state']['combat_state']['monster_box'] = monster_json

    # print(game_state)
    pipeline_override = {
        # "ADBAction": {"action": "custom", "custom_action": "ADBAction"},
        "ADBAction": {"action": "custom", "custom_action": "ADBAction", "custom_action_param": game_state},
    }
    log_message("pipeline选中任务执行")
    tasker.post_task("ADBAction", pipeline_override).wait().get()

# 创建 GUI 窗口
root = tk.Tk()
root.title("Slay the Spire AI 控制面板")
root.geometry("600x400")

# 创建左侧输出窗口
output_text = scrolledtext.ScrolledText(root, width=50, height=20, wrap=tk.WORD)
output_text.grid(row=0, column=0, rowspan=8, padx=10, pady=10)

# 创建右侧按钮区域
buttons = [
    ("程序运行", run_program),
    ("地图选择", select_map),
    ("代理战斗", auto_battle),
    ("事件处理", handle_event),
    ("奖励选择", select_reward),
    ("休息决策", rest_decision),
    ("商店购买", shop_purchase),
    ("程序退出", exit_program)
]
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
# tasker = Tasker(notification_handler=MyNotificationHandler()
print("开始绑定资源和控制器")
tasker.bind(resource, controller)
print("资源绑定结束")

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
resource.register_custom_recognition("CardrewardRecognition", CardrewardRecognition())
resource.register_custom_recognition("UnknownRecognition", UnknownRecognition())
resource.register_custom_recognition("MapRecognition", MapRecognition())
resource.register_custom_action("ADBAction", ADBAction())

# 读取本地pipeline
pipeline_local = JsonUtils.load_json("./assets/resource/pipeline/slay_task.json")

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

for i, (text, command) in enumerate(buttons):
    tk.Button(root, text=text, command=command, width=15).grid(row=i, column=1, padx=10, pady=5)

root.mainloop()
