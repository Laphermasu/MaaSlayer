
from maa.tasker import Tasker
class CmdPerformer:

        def __init__(self, tasker: Tasker):
            self.tasker = tasker

        # 解析输入指令
        def setCmd(self, cmd: str):
            a = b =c =1
            return a, b, c

        def performCmd(self, cmd: str):
            a ,b ,c = self.setCmd(cmd)
            # 这里可以进行一个判断，看是类型的指令再重写pipeline_override
            pipeline_override = {
                "第一次点击": {
                     "action": "click",
                     # 这里根据解析出来的指令自动赋值
                     "expected": a,
                     # 加点执行delay
                     "post_delay": 0.2 ,
                     "next": "第二次点击"
                },
                "第二次点击": {
                     "action": "click",
                     # 这里根据解析出来的指令自动赋值
                     "expected": b
                }
            }
            task_detail = self.tasker.post_task("第一次点击", pipeline_override).wait().get()
            print("Performing command: " + self.cmd)