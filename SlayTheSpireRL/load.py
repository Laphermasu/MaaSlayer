from sb3_contrib.ppo_mask import MaskablePPO
import torch as th
from slay_the_spire_env import SlayTheSpireEnv

# 选择设备（CPU 或 GPU）
device = th.device("cuda" if th.cuda.is_available() else "cpu")

# 重新创建环境
env = SlayTheSpireEnv({})  # 确保这个环境与训练时一致

# 加载模型
model = MaskablePPO.load("maskable_ppo_slay_the_spire.zip", env=env, device=device)