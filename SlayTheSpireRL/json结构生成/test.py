import json
import torch as th
from sb3_contrib.ppo_mask import MaskablePPO
from slay_the_spire_env import SlayTheSpireEnv
from func import (
    get_available_commands,
    get_screen,
    get_monsters,
    get_hand,
    get_player,
    get_deck,
    get_relics,
    get_potions,
    get_map,
    get_info
)

def generate_json():
    available_commands = get_available_commands()
    screen = get_screen()
    combat_state = {
        "monsters": get_monsters(),
        "hand": get_hand(),
        "player": get_player(),
    }
    deck = get_deck()
    relics = get_relics()
    max_hp, gold, current_hp, floor, room_type = get_info()
    potions = get_potions()
    game_map = get_map()

    game_state = {
        "screen_type": screen['type'],
        "screen_state": screen['state'],
        "combat_state": combat_state,
        "deck": deck,
        "relics": relics,
        "max_hp": max_hp,
        "gold": gold,
        "potions": potions,
        "current_hp": current_hp,
        "floor": floor,
        "map": game_map,
        "room_type": room_type,
    }

    json_data = {
        "available_commands": available_commands,
        "ready_for_command": True,
        "in_game": True,
        "game_state": game_state
    }


    json_result = json.dumps(json_data, indent=4)

    return json_result




def main():
    game_state = json.loads(generate_json())
    print(game_state)
    env = SlayTheSpireEnv({})
    device = th.device("cuda" if th.cuda.is_available() else "cpu")
    model = MaskablePPO.load("../maskable_ppo_slay_the_spire1.zip", env=env, device=device)

    # 解析 JSON，转换为环境可用的格式
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

    print(f"Action: {chosen_command}")

    env.close()

if __name__ == "__main__":
    main()

