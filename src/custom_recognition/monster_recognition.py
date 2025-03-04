from ..utils.json_utils import JsonUtils
from maa.resource import Resource
from maa.context import Context
from maa.custom_recognition import CustomRecognition
import matplotlib.pyplot as plt
import numpy as np
from ..utils.json_utils import JsonUtils
from ..core.data_models import Monster


class MonsterRecognition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        
        # 模板列表
        monster_list = JsonUtils.load_json("./assets/resource/image/monster/monster_list.json")
        monster_type = JsonUtils.load_json("./assets/resource/image/monster/monster_type.json")
        # 获取当前屏幕图片
        img = context.tasker.controller.post_screencap().wait().get()
        # 怪物列表
        monsters = []

        # 当没有识别到怪物时停止匹配
        monster_exist = True
        while monster_exist:

            # 初始化最佳匹配结果
            best_match = {
                "template_index": -1,  # 匹配的模板索引
                "count": 0,  # 匹配点数
                "box": (0, 0, 0, 0)  # 匹配区域
            }

            # 遍历模板列表，逐个匹配
            for index, template in enumerate(monster_list):
                # 调用识别流水线
                reco_detail = context.run_recognition(
                    "识别怪物_图片识别",  # 流水线名称
                    img,  # 输入图像
                    pipeline_override={
                        "识别怪物_图片识别": {
                            "recognition": "FeatureMatch",
                            "template": [template],  # 每次只匹配一个模板
                            # "green_mask": True
                        }
                    }
                )

                # 解析识别结果
                if reco_detail and reco_detail.best_result:
                    current_count = reco_detail.best_result.count  # 当前模板的匹配点数
                    if current_count > best_match["count"]:
                        best_match = {
                            "template_index": index,
                            "count": current_count,
                            "box": reco_detail.box
                        }

            # 根据最佳匹配结果确定怪物种类
            if best_match["template_index"] != -1:
                monster = Monster()
                template_index = best_match["template_index"]
                monster.type = monster_type.get(str(template_index), "Unknown")

                x, y, w, h = best_match["box"]

                # 获得怪物的血量
                # reco_detail = context.run_recognition(
                #     "识别怪物_血量识别",  # 流水线名称
                #     img,  # 输入图像
                #     pipeline_override={
                #         "识别怪物_血量识别": {
                #             "recognition": "OCR",
                #             "roi": [x, y, w, h],
                #             "roi_offset": [0, h - y, 0, 40]
                #         }
                #     }
                # )

                monsters.append(monster)

                # 去掉匹配区域

                img[y:y+h, x:x+w] = 0  # 将匹配区域设置为黑色
                # plt.imshow(img, cmap='gray' if len(img.shape) == 2 else None)
                # plt.axis('off')  # 关闭坐标轴
                # plt.show()

            else:
                monster_type = "Unknown"
                monster_exist = False

        # monsters = [
        #     Monster(type="Dragon", health=100, action="Fire Breath", buffs=["Fire Resistance"]),
        #     Monster(type="Goblin", health=20, action="Steal", buffs=["Stealth"]),
        # ]
        monsters_str =  JsonUtils.serialize_to_str(monsters)
        # print(monsters_str)
        return CustomRecognition.AnalyzeResult(
            box=best_match["box"], detail=monsters_str
        )