import re
from ..utils.json_utils import JsonUtils
from maa.resource import Resource
from maa.context import Context
from maa.custom_recognition import CustomRecognition
import matplotlib.pyplot as plt
import numpy as np
from ..utils.json_utils import JsonUtils
from ..core.data_models import Player
from ..core.data_models import MapNode
from collections import defaultdict

def fill_index(input_list):
    pattern = re.compile(r'^[\[［【](.*?)[\]］】](.*)$')
    result_dict = {}
    for item in input_list:
        match = pattern.match(item)
        if match:
            key = match.group(1)
            value = match.group(2).strip()  # 去除前后空格，根据需要可以去掉这行
            result_dict[key] = value if value else ''
    return result_dict

class EventRecognition(CustomRecognition):
    def analyze(
            self,
            context,
            argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        # 获取当前屏幕图片
        img = context.tasker.controller.post_screencap().wait().get()
        player = Player()
        event = MapNode()
        best_match = {
            "card": [],  # 匹配的模板索引
            "count": 0,  # 匹配点数
            "box": (0, 0, 0, 0)  # 匹配区域
        }
        # 当没有识别到怪物时停止匹配
        event_exist = True
        while event_exist:
            reco_detail = context.run_recognition(
                    "事件识别_ocr",  # 流水线名称
                    img,  # 输入图像
                    pipeline_override={
                        "事件识别_ocr": {
                            "recognition": "OCR",
                            "expected": "祈祷",  # 每次只匹配一个模板
                            # "green_mask": True
                        }
                    }
            )

            bracket_pattern = re.compile(r'^[\[【［]')

            # 按y坐标分组
            groups = defaultdict(list)
            for result in reco_detail.all_results:
                y = result.box[1]
                groups[y].append(result)

            result_list = []

            for y in groups:
                current_group = groups[y]
                bracket_items = []
                non_bracket_items = []

                # 分类
                for item in current_group:
                    if bracket_pattern.search(item.text):
                        bracket_items.append(item)
                    else:
                        non_bracket_items.append(item)

                # 按x坐标排序（从左到右）
                bracket_sorted = sorted(bracket_items, key=lambda x: x.box[0])
                non_bracket_sorted = sorted(non_bracket_items, key=lambda x: x.box[0])

                # 合并文本
                combined_text = ''.join([item.text for item in bracket_sorted + non_bracket_sorted])
                result_list.append(combined_text)

            event.node_type = "事件"
            event.details = fill_index(result_list)
            break

        # monsters = [
        #     Monster(type="Dragon", health=100, action="Fire Breath", buffs=["Fire Resistance"]),
        #     Monster(type="Goblin", health=20, action="Steal", buffs=["Stealth"]),
        # ]
        # print(monsters_str)
        event_str = JsonUtils.serialize_to_str(event)
        return CustomRecognition.AnalyzeResult(
            box=best_match["box"], detail=str(event_str)
        )