import matplotlib.pyplot as plt
import numpy as np
from maa.custom_recognition import CustomRecognition
from ..utils.json_utils import JsonUtils
from ..core.data_models import Relic


class RelicRecognition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        # 模板列表
        relic_list = JsonUtils.load_json("./assets/resource/image/relic/relic_list.json")
        relic_type = JsonUtils.load_json("./assets/resource/image/relic/relic_type.json")
        # 获取当前屏幕图片
        img = context.tasker.controller.post_screencap().wait().get()
        # 遗物列表
        relics = []

        # 当没有识别到遗物时停止匹配
        relic_exist = True
        while relic_exist:

            # 初始化最佳匹配结果
            best_match = {
                "template_index": -1,  # 匹配的模板索引
                "count": 0,  # 匹配点数
                "box": (0, 0, 0, 0)  # 匹配区域
            }

            # 遍历模板列表，逐个匹配
            for index, template in enumerate(relic_list):
                # 调用识别流水线
                reco_detail = context.run_recognition(
                    "识别遗物_图片识别",  # 流水线名称
                    img,  # 输入图像
                    pipeline_override={
                        "识别遗物_图片识别": {
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

            # 根据最佳匹配结果确定遗物种类
            if best_match["template_index"] != -1:
                # 新建遗物实例
                relic = Relic()
                # 根据匹配索引获得遗物名称
                template_index = best_match["template_index"]
                relic.name = relic_type.get(str(template_index), "Unknown")

                # 获得遗物图像区域
                x, y, w, h = best_match["box"]

                relics.append(relic)

                # 去掉匹配区域
                img[y:y + h, x:x + w] = 0  # 将匹配区域设置为黑色
                # plt.imshow(img, cmap='gray' if len(img.shape) == 2 else None)
                # plt.axis('off')  # 关闭坐标轴
                # plt.show()

            else:
                relic_type = "Unknown"
                relic_exist = False


        relics_str = JsonUtils.serialize_to_str(relics)

        return CustomRecognition.AnalyzeResult(
            box=best_match["box"], detail=relics_str
        )