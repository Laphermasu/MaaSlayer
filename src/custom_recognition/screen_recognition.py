from maa.custom_recognition import CustomRecognition
from ..utils.json_utils import JsonUtils

class ScreenRecognition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        # 确定屏幕种类
        screen_list = JsonUtils.load_json("./assets/resource/image/screen/screen_list.json")
        screen_type = JsonUtils.load_json("./assets/resource/image/screen/screen_type.json")
        # 获取当前屏幕图片
        img = context.tasker.controller.post_screencap().wait().get()
        
        # 遍历模板列表，逐个匹配
        for index, template in enumerate(screen_list):
                # 调用识别流水线
                reco_detail = context.run_recognition(
                    "屏幕类型识别",  # 流水线名称
                    img,  # 输入图像
                    pipeline_override={
                        "屏幕类型": {
                            "recognition": "FeatureMatch",
                            "template": [template],  # 每次只匹配一个模板
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
        # 根据最佳匹配结果确定当前屏幕类型
        if best_match["template_index"] != -1:
            template_index = best_match["template_index"]
            screen_type = screen_type[template_index]

        return CustomRecognition.AnalyzeResult(
        box=best_match["box"], detail=screen_type
    )
            