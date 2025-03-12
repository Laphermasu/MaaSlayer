from maa.context import Context
from maa.custom_action import CustomAction
from ..utils.json_utils import JsonUtils

class MapAction(CustomAction):

    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        """
        :param argv:
        :param context: 运行上下文
        :return: 是否执行成功。-参考流水线协议 `on_error`
        """
        print("开始识别选择地图节点")
 
        map_list = JsonUtils.load_json("./assets/resource/image/map/map_list.json")
        map_type = JsonUtils.load_json("./assets/resource/image/map/map_type.json")
        img = context.tasker.controller.post_screencap().wait().get()
        
        map_nodes = []
        node_exist = True
        # while(node_exist):
        #     # 初始化最佳匹配结果
        #     best_match = {
        #         "template_index": -1,  # 匹配的模板索引
        #         "count": 0,  # 匹配点数
        #         "box": (0, 0, 0, 0)  # 匹配区域
        #     }
        #     for index, template in enumerate(map_list):
        #         reco_detail = context.run_recognition(
        #             "地图节点识别", 
        #             img,  
        #             pipeline_override={
        #                 "地图节点识别": {
        #                     "recognition": "FeatureMatch",
        #                     "template": [template], 
        #                 }
        #             }
        #         )

        #         if reco_detail and reco_detail.best_result:
        #             current_count = reco_detail.best_result.count
        #             if current_count > best_match["count"]:
        #                 best_match = {
        #                     "template_index": index,
        #                     "count": current_count,
        #                     "box": reco_detail.box
        #                 }
        #     # 检测是否有地图节点
        #     if best_match["template_index"] != -1:
        #         template_index = best_match["template_index"]
        #         map_nodes.append(
        #             {
        #                 "name": map_type[template_index],
        #                 "box": best_match["box"]
        #             }
        #         )
        #     else:
        #         node_exist = False
        # context.run_action("点击",map_nodes[0]["box"]),"点击地图节点",{"点击"：{"action": "Click", ""}}
        # return True
        
            