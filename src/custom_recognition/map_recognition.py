import matplotlib.pyplot as plt
import numpy as np
import cv2
import time
from maa.context import Context
from maa.custom_recognition import CustomRecognition
from ..utils.json_utils import JsonUtils


class MapRecognition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        target = list(self.find_clickable_center(context))
        map = "Unknown"
        # 模板列表
        map_list = JsonUtils.load_json("./assets/resource/image/map/map_list.json")
        map_type = JsonUtils.load_json("./assets/resource/image/map/map_type.json")
        # 获取当前屏幕图片
        img = context.tasker.controller.post_screencap().wait().get()
        
        # 初始化最佳匹配结果
        best_match = {
            "template_index": -1,  # 匹配的模板索引
            "count": 0,  # 匹配点数
            "box": (0, 0, 0, 0)  # 匹配区域
        }

        # 遍历模板列表，逐个匹配
        for index, template in enumerate(map_list):
            # 调用识别流水线
            reco_detail = context.run_recognition(
                "识别地图节点",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "识别地图节点": {
                        "recognition": "FeatureMatch",
                        "template": [template],  # 每次只匹配一个模板
                        "roi": [target[0] - 55, target[1] - 60, 110, 120],
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

        # 根据最佳匹配结果确定地图节点
        if best_match["template_index"] != -1:
            # 根据匹配索引获得地图名称
            template_index = best_match["template_index"]
            map = str(map_type.get(str(template_index), "Unknown"))

        context.run_task(
            "点击识别到的节点",
            pipeline_override= {
                "点击识别到的节点": {
                    "action": "Click",
                    "target": [target[0], target[1], 2, 2]
                }
            }
        )

        return CustomRecognition.AnalyzeResult(
            box=best_match["box"], detail=map
        )
    
    def find_clickable_center(self, context: Context):
        # 加载图像
        img1 = context.tasker.controller.post_screencap().wait().get()
        time.sleep(0.5)
        img2 = context.tasker.controller.post_screencap().wait().get()

        # 转换为灰度图
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # 计算图像差异
        diff = cv2.absdiff(gray1, gray2)

        # 阈值处理
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        # 识别轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 初始化最大区域和中心点
        max_area = 0
        target_center = None

        for contour in contours:
            # 获取包围框
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            # 寻找最大面积的轮廓
            if area > max_area:
                max_area = area
                target_center = (x + w // 2, y + h // 2)

        return target_center