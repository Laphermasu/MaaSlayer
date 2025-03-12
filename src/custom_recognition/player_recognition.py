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
        img = context.tasker.controller.post_screencap().wait().get()
        player = Player()
        best_match = {
            "card": [],
            "count": 0,
            "box": (0, 0, 0, 0)
        }
        # 当没有识别到怪物时停止匹配
        hp_exist = True
        while hp_exist:
            reco_detail = context.run_recognition(
                    "卡牌识别_ocr",
                    img,
                    pipeline_override={
                        "卡牌识别_ocr": {
                            "recognition": "OCR",
                            "expected": "",
                            "roi":[285,549,700,100]
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
            gold_detail = context.run_recognition(
                "玩家_金钱识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "玩家_金钱识别": {
                        "recognition": "OCR",
                        "expected": "",
                        "roi": [315, 15, 30, 30]
                    }
                }
            )
            floor_detail = context.run_recognition(
                "玩家_楼层识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "玩家_楼层识别": {
                        "recognition": "OCR",
                        "expected": "",
                        "roi": [625, 15, 30, 30]
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
                if gold_detail and gold_detail.best_result:
                    if gold_detail.all_results[0].text.isdigit():
                        player.gold = gold_detail.all_results[0].text
                if floor_detail and floor_detail.best_result:
                    if floor_detail.all_results[0].text.isdigit():
                        player.floor = floor_detail.all_results[0].text
                print(player)
                break

            else:
                hp_exist = False

        player_str = JsonUtils.serialize_to_str(player)
        return CustomRecognition.AnalyzeResult(
            box=best_match["box"], detail=str(player_str)
        )