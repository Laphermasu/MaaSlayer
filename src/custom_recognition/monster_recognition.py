import matplotlib.pyplot as plt
import numpy as np
from maa.custom_recognition import CustomRecognition
from ..utils.json_utils import JsonUtils
from ..core.data_models import Monster


class MonsterRecognition(CustomRecognition):

    def analyze(
            self,
            context,
            argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        # 先确认怪物是否存在以及怪物的种类
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
                            "green_mask": True
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

            # 根据最佳匹配结果确定怪物种类，并进行对应怪物的后续识别
            if best_match["template_index"] != -1:
                # 新建怪物实例
                monster = Monster()
                # 根据匹配索引获得怪物名称
                template_index = best_match["template_index"]
                monster.name = monster_type.get(str(template_index), "Unknown")
                monster.id = monster_type.get(str(template_index), "Unknown")
                monster.box = best_match["box"]

                # 获得怪物图像区域
                x, y, w, h = best_match["box"]

                # 获得怪物其他信息
                monster.current_hp, monster.max_hp = self.recognize_health(context, img, best_match["box"])
                monster.intent, monster.move_base_damage, monster.move_hits = self.recognize_intent(context, img,
                                                                                                    best_match["box"])

                # 显示处理后的图像（用于调试）
                # cv2.imshow("Thresholded Image", health_img)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                # plt.imshow(health_img, cmap='gray' if len(img.shape) == 2 else None)
                # plt.axis('off')  # 关闭坐标轴
                # plt.show()

                monsters.append(monster)

                # 去掉匹配区域
                img[y:y + h, x:x + w] = 0  # 将匹配区域设置为黑色
                # plt.imshow(img, cmap='gray' if len(img.shape) == 2 else None)
                # plt.axis('off')  # 关闭坐标轴
                # plt.show()

            else:
                monster_exist = False

        monsters_str = JsonUtils.serialize_to_str(monsters)
        return CustomRecognition.AnalyzeResult(
            box=best_match["box"], detail=monsters_str
        )

    def recognize_health(self, context, img: np.ndarray, box: tuple) -> tuple:
        """
        识别怪物血量
        :param context: MaaFramework 上下文
        :param img: 输入图像
        :param box: 怪物区域的边界框 (x, y, w, h)
        :return: 当前血量和最大血量 (current_hp, max_hp)
        """
        x, y, w, h = box

        # 开始血量识别
        health_detail = context.run_recognition(
            "识别怪物_血量识别",  # 流水线名称
            img,  # 输入图像
            pipeline_override={
                "识别怪物_血量识别": {
                    "recognition": "OCR",
                    "roi": [x, y, w, h],
                    "roi_offset": [0, 0, 0, 40]
                }
            }
        )

        # 初始化最佳结果
        best_result = {
            "best_score": 0,
            "health": ""
        }

        # 遍历所有结果，找到最佳匹配
        if health_detail and health_detail.all_results:
            for result in health_detail.all_results:
                if best_result["best_score"] < result.score:
                    best_result = {
                        "best_score": result.score,
                        "health": result.text
                    }

        # 解析血量
        if best_result["health"]:
            try:
                current_health, max_health = best_result["health"].split('/')
                return int(current_health), int(max_health)
            except ValueError:
                return 0, 0
        else:
            return 0, 0  # 如果识别失败，返回默认值

    def recognize_intent(self, context, img: np.ndarray, box: tuple) -> tuple:
        """
        识别怪物动作
        :param context: MaaFramework 上下文
        :param img: 输入图像
        :param box: 怪物区域的边界框 (x, y, w, h)
        :return: 当前意图（intent）
        """
        x, y, w, h = box

        # 模板列表
        intent_list = JsonUtils.load_json("./assets/resource/image/intent/intent_list.json")
        intent_type = JsonUtils.load_json("./assets/resource/image/intent/intent_type.json")

        # 初始化最佳匹配结果
        best_match = {
            "template_index": -1,  # 匹配的模板索引
            "count": 0,  # 匹配点数
            "box": (0, 0, 0, 0)  # 匹配区域
        }

        # 遍历模板列表，逐个匹配
        for index, template in enumerate(intent_list):
            # 调用识别流水线
            reco_detail = context.run_recognition(
                "识别怪物_意图识别",  # 流水线名称
                img,  # 输入图像
                pipeline_override={
                    "识别怪物_意图识别": {
                        "recognition": "FeatureMatch",
                        "template": [template],  # 每次只匹配一个模板
                        "roi": [x, y, w, h],
                        "roi_offset": [0, -80, 0, 80],
                        "green_mask": True
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

        # 根据最佳匹配结果确定动作种类
        if best_match["template_index"] != -1:
            intent = intent_type.get(str(best_match["template_index"]), "DEBUG")
            if intent == "ATTACK":
                #     x, y, w, h = best_match["box"]
                #     attack_detail = context.run_recognition(
                #         "攻击伤害识别",  # 流水线名称
                #         img,  # 输入图像
                #         pipeline_override={
                #             "攻击伤害识别": {
                #                 "recognition": "OCR",
                #                 "roi": [x, y, w, h],
                #                 "roi_offset": [-10, -10, 20, 20]
                #             }
                #         }
                #     )
                #     # 初始化最佳结果
                #     best_result = {
                #         "best_score": 0,
                #         "attack": ""
                #     }
                #
                #     # 遍历所有结果，找到最佳匹配
                #     if attack_detail and attack_detail.all_results:
                #         for result in attack_detail.all_results:
                #             if best_result["best_score"] < result.score:
                #                 best_result = {
                #                     "best_score": result.score,
                #                     "attack": result.text
                #                 }

                # 解析攻击
                # damage, count = self.parse_attack_string(best_result["attack"])
                return intent, 10, 1
            else:
                return intent, 0, 0
        else:
            return "DEBUG", 0, 0  # 如果识别失败，返回默认值

    def parse_attack_string(self, attack_str):
        """
        解析攻击字符串为攻击伤害和攻击次数。
        
        :param attack_str: 包含攻击信息的字符串，例如 '11' 或 '2×5'
        :return: (damage, count)，分别是攻击伤害和攻击次数
        """
        attack_str = attack_str.replace('×', '*')  # 将乘号替换为星号，便于计算
        attack_str = attack_str.replace('x', '*')  # 考虑可能的其他乘号形式

        if '*' in attack_str:
            # 如果字符串包含乘号，分割并计算
            parts = attack_str.split('*')
            try:
                damage = int(parts[0].strip())
                count = int(parts[1].strip())
                return damage, count
            except (ValueError, IndexError):
                print(f"Error parsing attack string: {attack_str}")
                return 0, 0
        else:
            # 只包含一个数字，攻击次数默认为1
            try:
                damage = int(attack_str.strip())
                return damage, 1
            except ValueError:
                print(f"Error parsing attack string: {attack_str}")
                return 0, 0
