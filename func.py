def get_available_commands():
    return [
        "play",
        "end",
        "key",
        "click",
        "wait",
        "state"
    ]

def get_screen():
    return {
        "type": "NONE",
        "state": {}
    }

def get_monsters():
    return [
        {
            "is_gone": False,
            "move_hits": 1,
            "move_base_damage": 5,
            "half_dead": False,
            "move_adjusted_damage": -1,
            "max_hp": 12,
            "intent": "DEBUG",
            "move_id": 1,
            "name": "Spike Slime (S)",
            "current_hp": 1,
            "block": 0,
            "id": "SpikeSlime_S",
            "powers": []
        },
        {
            "is_gone": False,
            "move_hits": 1,
            "move_base_damage": 10,
            "half_dead": False,
            "move_adjusted_damage": -1,
            "max_hp": 29,
            "intent": "DEBUG",
            "move_id": 2,
            "name": "Acid Slime (M)",
            "current_hp": 1,
            "block": 0,
            "id": "AcidSlime_M",
            "powers": []
        }
    ]

def get_hand():
    return [
        {
            "exhausts": False,
            "is_playable": True,
            "cost": 1,
            "name": "Strike",
            "id": "Strike_R",
            "type": "AttACK",
            "ethereal": False,
            "uuid": "4f670a18-0610-465b-ad03-1cdb4492781a",
            "upgrades": 0,
            "rarity": "BASIC",
            "has_target": True
        },
        {
            "exhausts": False,
            "is_playable": True,
            "cost": 1,
            "name": "Strike",
            "id": "Strike_R",
            "type": "AttACK",
            "ethereal": False,
            "uuid": "d4a92e0e-a7ee-42db-8fa0-438a1262a4a7",
            "upgrades": 0,
            "rarity": "BASIC",
            "has_target": True
        }
    ]

def get_player():
    return {
        "orbs": [],
        "current_hp": 80,
        "block": 0,
        "max_hp": 80,
        "powers": [],
        "energy": 3
    }

def get_deck():
    return [
        {
            "exhausts": False,
            "is_playable": True,
            "cost": 1,
            "name": "Strike",
            "id": "Strike_R",
            "type": "AttACK",
            "ethereal": False,
            "uuid": "225d607f-ff94-4292-be69-a0793d3f90f8",
            "upgrades": 0,
            "rarity": "BASIC",
            "has_target": True
        },
        {
            "exhausts": False,
            "is_playable": True,
            "cost": 1,
            "name": "Strike",
            "id": "Strike_R",
            "type": "AttACK",
            "ethereal": False,
            "uuid": "53fb8b29-fbd3-496b-b2d4-fb6bc4dca689",
            "upgrades": 0,
            "rarity": "BASIC",
            "has_target": True
        }
    ]

def get_relics():
    return [
        {
            "name": "Burning Blood",
            "counter": -1
        },
        {
            "name": "Neow's Lament",
            "counter": 2
        }
    ]

def get_potions():
    return [
        {
            "requires_target": False,
            "can_use": False,
            "can_discard": False,
            "name": "Potion Slot",
            "id": "Potion Slot"
        }
    ]

def get_info():
    return 80, 99, 80, 1, "MonsterRoom"

def get_map():
    return [
        {
            "symbol": "M",
            "children": [
                {"x": 0, "y": 1},
                {"x": 1, "y": 1}
            ],
            "x": 1,
            "y": 0,
            "parents": []
        },
        {
            "symbol": "M",
            "children": [
                {"x": 4, "y": 1}
            ],
            "x": 3,
            "y": 0,
            "parents": []
        }
    ]
