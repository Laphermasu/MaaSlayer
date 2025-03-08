from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Monster:
    is_gone: bool = False,
    move_hits:int = 1,
    move_base_damage:int = 1,
    half_dead:bool = False,
    move_adjusted_damage: int = 0,
    max_hp:int = 1,
    intent:str = "DEBUG",
    move_id:int = 1,
    name:str = "Spike Slime (S)",
    current_hp:int = 1,
    block:int = 0,
    id:str = "SpikeSlime_S",
    powers:List[str] = field(default_factory=list)# 怪物buff

@dataclass
class Player:
    current_hp: int = 0
    max_hp: int = 0
    block: int = 0
    energy: int = 0
    orbs: List[str] = field(default_factory=list)
    powers: List[str] = field(default_factory=list)


@dataclass
class Cards:
    name: str = ""
    rarity: str = ""
    type: str = ""
    cost: int = 0
    exhausts: bool = False
    is_playable: bool = False
    ethereal: bool = False
    upgrades: int = 0
    has_target: bool = False


@dataclass
class MapNode:
    details: dict[str, str] = field(default_factory=dict)  # 节点详细信息
    node_type:str = "default" # 如战斗、商店、事件等

@dataclass
class Shop:
    items: Dict[str, int]  # 商品名称和价格
    gold: int

@dataclass
class GameState:
    map: List[MapNode]
    monsters: List[Monster]
    player: Player
    current_node: MapNode
    shop: Shop

@dataclass
class Relic:
    name: str = "default"
    id: str = "default"
    counter: int = -1