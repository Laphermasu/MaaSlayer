from maa.custom_recognition import CustomRecognition
from ..utils.json_utils import JsonUtils

class UnknownRecognition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        unknown_list = JsonUtils.load_json("./assets/resource/image/unknown/unknown_list.json")
        unknown_type = JsonUtils.load_json("./assets/resource/image/unknown/unknown_type.json")
        img = context.tasker.controller.post_screencap().wait().get()
        # 初始化最佳匹配结果
        best_match = {
            "template_index": -1,  # 匹配的模板索引
            "count": 0,  # 匹配点数
            "box": (0, 0, 0, 0)  # 匹配区域
        }
        type = "Unknown"

        for index, template in enumerate(unknown_list):
            reco_detail = context.run_recognition(
                "未知识别", 
                img,  
                pipeline_override={
                    "未知识别": {
                        "recognition": "FeatureMatch",
                        "template": [template], 
                    }
                }
            )

            if reco_detail and reco_detail.best_result:
                current_count = reco_detail.best_result.count
                if current_count > best_match["count"]:
                    best_match = {
                        "template_index": index,
                        "count": current_count,
                        "box": reco_detail.box
                    }

        if best_match["template_index"] != -1:
            template_index = best_match["template_index"]
            type = unknown_type[template_index]
        
        else:
            type = "事件"

        return CustomRecognition.AnalyzeResult(
        box=best_match["box"], detail=type
)