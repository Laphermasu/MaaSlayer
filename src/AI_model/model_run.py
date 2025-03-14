from sb3_contrib.ppo_mask import MaskablePPO
from src.AI_model.SlayTheSpireRL.slay_the_spire_env import SlayTheSpireEnv
import torch as th
from src.AI_model.func import generate_json



def initialize_model():
    """初始化环境和模型"""
    env = SlayTheSpireEnv({})
    device = th.device("cuda" if th.cuda.is_available() else "cpu")
    model = MaskablePPO.load("maskable_ppo_slay_the_spire", env=env, device=device)
    return env, model, device


def predict_action(screen_type, monsters, events, cards, player, env, model, device):
    """根据游戏状态进行预测，返回选择的动作"""
    game_state = generate_json(screen_type, monsters, events, cards, player)
    env.update_game_state(game_state)
    obs = env.flatten_observation(game_state)
    obs_tensor = {key: th.tensor(value, dtype=th.float32).unsqueeze(0).to(device) for key, value in obs.items()}

    action_mask = env.get_invalid_action_mask(game_state)
    action_mask_tensor = th.tensor(action_mask, dtype=th.bool).unsqueeze(0).to(device)

    obs_numpy = {key: value.cpu().numpy() for key, value in obs_tensor.items()}
    action_mask_numpy = action_mask_tensor.cpu().numpy()

    action, _states = model.predict(obs_numpy, action_masks=action_mask_numpy)
    action = int(action)
    chosen_command = env.actions[action]
    print("************")
    print(chosen_command)
    print("************")
    return chosen_command,game_state


def close_model(env):
    """关闭环境"""
    env.close()
