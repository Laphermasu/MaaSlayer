from maa.custom_recognition import CustomRecognition
from ..utils.json_utils import JsonUtils

class ScreenRecognition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:


        screen_list = JsonUtils.load_json("./assets/resource/image/map/map_list.json")
        screen_type = JsonUtils.load_json("./assets/resource/image/map/map_type.json")
        img = context.tasker.controller.post_screencap().wait().get()
        

        for index, template in enumerate(screen_list):

                reco_detail = context.run_recognition(
                    "地图节点识别", 
                    img,  
                    pipeline_override={
                        "地图节点识别": {
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
            map_type = map_type[template_index]

        return CustomRecognition.AnalyzeResult(
        box=best_match["box"], detail=map_type
    )
            