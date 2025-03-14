from src.core.data_models import Monster, Cards, Event, Player
from src.utils.json_utils import JsonUtils

def recognize(tasker, recognition_type):
    """
    通用识别函数，根据传入的 recognition_type 进行不同类型的识别。

    :param tasker: 任务执行器对象
    :param recognition_type: 识别类型，可选值 ["monster", "player", "event", "card", "cardreward"]
    :return: 识别的对象（Monster、Player、Event、Cards），或者 None（如果识别失败）
    """
    recognition_map = {
        "monster": ("monsterRecognition", Monster),
        "player": ("playerRecognition", Player),
        "event": ("eventRecognition", Event),
        "card": ("cardRecognition", Cards),
        "cardreward": ("CardrewardRecognition",Cards)
    }

    if recognition_type not in recognition_map:
        print(f"无效的识别类型: {recognition_type}")
        return None

    recognition_key, data_model = recognition_map[recognition_type]
    print(f"开始识别 {recognition_type}")

    pipeline_override = {
        "MyRecongitionEntry": {"recognition": "custom", "custom_recognition": recognition_key},
    }

    task_detail = tasker.post_task("MyRecongitionEntry", pipeline_override).wait().get()
    recognized_data = JsonUtils.deserialize_from_str(
        JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail), data_model
    )

    print(f"识别到的{recognition_type}: {recognized_data}")

    return recognized_data