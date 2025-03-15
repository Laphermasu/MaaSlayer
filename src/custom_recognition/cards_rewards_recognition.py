import re
from ..utils.json_utils import JsonUtils
from maa.resource import Resource
from maa.context import Context
from maa.custom_recognition import CustomRecognition
import matplotlib.pyplot as plt
import numpy as np
from ..utils.json_utils import JsonUtils
from ..core.data_models import Cards
import os
import json

class CardrewardRecognition(CustomRecognition):
    def analyze(
            self,
            context,
            argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # 获取当前屏幕图片
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, '../../cards.json')
        json_path = os.path.normpath(json_path)
        cards_list = json.load(open(json_path))
        img = context.tasker.controller.post_screencap().wait().get()
        best_match = {
            "card": [],  # 匹配的模板索引
            "count": 0,  # 匹配点数
            "box": (0, 0, 0, 0)  # 匹配区域
        }
        cards_exist = True
        filtered_list = []
        while cards_exist:
            reco_detail = context.run_recognition(
                    "卡牌识别_ocr",  # 流水线名称
                    img,  # 输入图像
                    pipeline_override={
                        "卡牌识别_ocr": {
                            "recognition": "OCR",
                            "expected": "",  # 每次只匹配一个模板
                            "roi":[328,275,620,50]
                            # "green_mask": True
                        }
                    }
            )
            # 解析识别结果
            if reco_detail and reco_detail.best_result:
                best_match = {
                    "card": [result.text for result in reco_detail.all_results],
                    "box": reco_detail.box
                }

            if best_match["card"]:
                filtered_list = [item for item in best_match["card"] if not item.isdigit()]
                break

            else:
                card_exist = False
        cards = []
        for strs in filtered_list:
            for data in cards_list:
                if data.get("name")==strs:
                    card = Cards()
                    card.name = data.get("name", "")
                    card.rarity = data.get("rarity", "")
                    card.type = data.get("type", "")
                    cost_str = data.get("cost", "0")
                    card.cost = int(cost_str) if cost_str.isdigit() else 0
                    card.exhausts = data.get("exhausts", False)
                    card.is_playable = data.get("is_playable", False)
                    card.ethereal = data.get("ethereal", False)
                    if '+' in strs:
                        card.upgrades = 1
                    else:
                        card.upgrades = data.get("upgrades", 0)
                    card.has_target = data.get("has_target", False)
                    cards.append(card)
                    break
        cards_str = JsonUtils.serialize_to_str(cards)
        return CustomRecognition.AnalyzeResult(
            box=best_match["box"], detail=str(cards_str)
        )