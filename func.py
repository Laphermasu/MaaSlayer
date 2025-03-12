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
                        "uuid": "82fc6dfa-3cad-497d-95d9-078d987d24d5",
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
                    },
                    {
                        "exhausts": False,
                        "is_playable": True,
                        "cost": 1,
                        "name": "Defend",
                        "id": "Defend_R",
                        "type": "SKILL",
                        "ethereal": False,
                        "uuid": "884af31e-cfdb-444d-9a3f-ae4d7ae579b1",
                        "upgrades": 0,
                        "rarity": "BASIC",
                        "has_target": False
                    },
                    {
                        "exhausts": False,
                        "is_playable": True,
                        "cost": 1,
                        "name": "Defend",
                        "id": "Defend_R",
                        "type": "SKILL",
                        "ethereal": False,
                        "uuid": "a7b9ea11-b291-47ac-b3cf-784e41faf909",
                        "upgrades": 0,
                        "rarity": "BASIC",
                        "has_target": False
                    },
                    {
                        "exhausts": False,
                        "is_playable": True,
                        "cost": 1,
                        "name": "Defend",
                        "id": "Defend_R",
                        "type": "SKILL",
                        "ethereal": False,
                        "uuid": "2a00a80f-56ea-437d-b9c6-41bdf802e545",
                        "upgrades": 0,
                        "rarity": "BASIC",
                        "has_target": False
                    },
                    {
                        "exhausts": False,
                        "is_playable": True,
                        "cost": 1,
                        "name": "Defend",
                        "id": "Defend_R",
                        "type": "SKILL",
                        "ethereal": False,
                        "uuid": "721e3234-5d07-40df-978d-2b7b6413267a",
                        "upgrades": 0,
                        "rarity": "BASIC",
                        "has_target": False
                    },
                    {
                        "exhausts": False,
                        "is_playable": True,
                        "cost": 2,
                        "name": "Bash",
                        "id": "Bash",
                        "type": "AttACK",
                        "ethereal": False,
                        "uuid": "7237894e-ce58-4621-a4ef-b240341d531f",
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
