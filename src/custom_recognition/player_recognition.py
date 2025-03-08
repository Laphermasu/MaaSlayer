import re
from ..utils.json_utils import JsonUtils
from maa.resource import Resource
from maa.context import Context
from maa.custom_recognition import CustomRecognition
import matplotlib.pyplot as plt
import numpy as np
from ..utils.json_utils import JsonUtils
from ..core.data_models import Player

class PlayerRecognition(CustomRecognition):
    def analyze(
            self,
            context,
            argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # 获取当前屏幕图片
        img = context.tasker.controller.post_screencap().wait().get()
        player = Player()
        best_match = {
            "card": [],  # 匹配的模板索引
            "count": 0,  # 匹配点数
            "box": (0, 0, 0, 0)  # 匹配区域
        }
        # 当没有识别到怪物时停止匹配
        hp_exist = True
        while hp_exist:
            reco_detail = context.run_recognition(
                    "卡牌识别_ocr",  # 流水线名称
                    img,  # 输入图像
                    pipeline_override={
                        "卡牌识别_ocr": {
                            "recognition": "OCR",
                            "expected": "",  # 每次只匹配一个模板
                            "roi":[285,549,700,100]
                            # "green_mask": True
                        }
                    }
            )

            health_detail = context.run_recognition(
                "玩家_血量识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "玩家_血量识别": {
                        "recognition": "OCR",
                        "expected": "",
                        #"roi": [888,399,181,133]
                        "roi": [262,500,50,50]
                    }
                }
            )

            health1_detail = context.run_recognition(
                "玩家_最大血量识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "玩家_最大血量识别": {
                        "recognition": "OCR",
                        "expected": "",
                        # "roi": [888,399,181,133]
                        "roi": [320, 500, 30, 30]
                    }
                }
            )

            energy_detail = context.run_recognition(
                "玩家_体力识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "玩家_体力识别": {
                        "recognition": "OCR",
                        "expected": "",
                        "roi": [100, 575, 40, 40]
                    }
                }
            )

            block_detail = context.run_recognition(
                "玩家_格挡识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "玩家_格挡识别": {
                        "recognition": "OCR",
                        "expected": "",
                        "roi": [205, 500, 30, 30]
                    }
                }
            )

            # 解析识别结果
            if reco_detail and reco_detail.best_result:
                best_match = {
                    "card": [result.text for result in reco_detail.all_results],
                    "box": reco_detail.box
                }


            player.block = 0
            if best_match["card"]:
                filtered_list = [item for item in best_match["card"] if not item.isdigit()]
                if health_detail and health_detail.best_result:
                    current_health = health_detail.all_results[0].text
                    current_health = re.sub(r'\D', '', current_health)
                    player.current_hp = current_health
                if health1_detail and health1_detail.best_result:
                    max_health = health1_detail.all_results[0].text
                    max_health = re.sub(r'\D', '', max_health)
                    player.max_hp = max_health
                if energy_detail and energy_detail.best_result:
                    current_energy = energy_detail.all_results[0].text
                    current_energy = re.sub(r'\D', '', current_energy)
                    player.energy = current_energy
                if block_detail and block_detail.best_result:
                    if block_detail.all_results[0].text.isdigit():
                        player.block = block_detail.all_results[0].text
                print(player)
                break

            else:
                hp_exist = False

        # monsters = [
        #     Monster(type="Dragon", health=100, action="Fire Breath", buffs=["Fire Resistance"]),
        #     Monster(type="Goblin", health=20, action="Steal", buffs=["Stealth"]),
        # ]
        # print(monsters_str)
        player_str = JsonUtils.serialize_to_str(player)
        return CustomRecognition.AnalyzeResult(
            box=best_match["box"], detail=str(player_str)
        )