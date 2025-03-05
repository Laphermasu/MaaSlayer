from maa.tasker import Tasker
from maa.toolkit import Toolkit
from maa.context import Context
from maa.resource import Resource
from maa.controller import AdbController
from maa.custom_action import CustomAction
from src.core.data_models import Monster
from src.custom_recognition.monster_recognition import MonsterRecognition
from src.utils.json_utils import JsonUtils

resource = Resource()

def main():
    # 初始化 MaaFramework
    user_path = "./"
    resource_path = "./assets/resource"

    Toolkit.init_option(user_path)

    res_job = resource.post_bundle(resource_path)
    res_job.wait()

    # 连接设备
    print("开始连接设备")
    adb_devices = Toolkit.find_adb_devices()
    if not adb_devices:
        print("No ADB device found.")
        exit()

    device = adb_devices[0]
    controller = AdbController(
        adb_path=device.adb_path,
        address=device.address,
        screencap_methods=device.screencap_methods,
        input_methods=device.input_methods,
        config=device.config,
    )
    controller.post_connection().wait()
    print("设备连接成功")

    print("初始化tasker")
    tasker = Tasker()
    # tasker = Tasker(notification_handler=MyNotificationHandler())
    tasker.bind(resource, controller)

    if not tasker.inited:
        print("Failed to init MAA.")
        exit()
    print("tasker初始化完成")

    resource.register_custom_recognition("MonsterRecognition", MonsterRecognition())
    
    # 测试图片检测输出
    pipeline_override = {
        "MyCustomEntry": {"action": "custom", "custom_action": "MonsterRecognitionAction"},
        "MyRecognitionEntry": {"recognition": "custom", "custom_recognition": "MonsterRecognition"},
    }
    print("开始执行流水线")
    task_detail = tasker.post_task("MyRecognitionEntry", pipeline_override).wait().get()
    detail = JsonUtils.serialize_to_str(task_detail.nodes[0].recognition.best_result.detail)
    monsters = JsonUtils.deserialize_from_str(detail, Monster)
    print(monsters)

    # 主循环
    # while True:
    #     game_state_manager.update_state()
    #     current_state = game_state_manager.get_state()
    #     print("Current Game State:", current_state)
    #     # 这里可以根据游戏状态执行相应的策略


@resource.custom_action("MonsterRecognitionAction")
class MonsterRecognitionAction(CustomAction):

    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        """
        Perform custom action to recognize bounty monsters.
        :param argv: Custom arguments
        :param context: Running context
        :return: True if executed successfully, otherwise False.
        """
        print("开始执行自定义动作：识别怪物类别")

        # 识别怪物
        img = context.tasker.controller.post_screencap().wait().get()
        # 获得识别区域与结果
        reco_detail = context.run_recognition(
                "识别怪物_图片识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "识别怪物_图片识别": {
                        "recognition": "FeatureMatch",
                        "template": "monster\\大颚虫.png",  # 每次只匹配一个模板
                    }
                }
            )
        # 排除识别区域后再次进行多次识别确认怪物数量
        
        print("识别完成")
        return True

if __name__ == "__main__":
    main()