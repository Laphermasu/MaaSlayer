from maa.custom_recognition import CustomRecognition

class EndTurnRecognition(CustomRecognition):

    def analyze(
        self,
        context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        img = context.tasker.controller.post_screencap().wait().get()
        reco_detail = context.run_recognition(
                "结束回合识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "结束回合识别": {
                        "recognition": "OCR",
                        "expected": ["End Turn", "Enemy Turn"],
                        "roi": [1010, 550, 160, 60],
                    }
                }
            )
        if reco_detail:
            exist = str(True)
        else:
            exist = str(False)
        return CustomRecognition.AnalyzeResult(
            box=(0, 0, 0, 0), detail=exist
        )