from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Monster:
    is_gone: bool = False,
    move_hits:int = 1,
    move_base_damage:int = 1,
    half_dead:bool = False,
    move_adjusted_damage: int = -1,
    max_hp:str = "default",
    intent:str = "DEBUG",
    move_id:int = 1,
    name:str = "Spike Slime (S)",
    current_hp:int = 1,
    block:int = 0,
    id:str = "SpikeSlime_S",
    powers:List[str] = field(default_factory=list) # 怪物buff

@dataclass
class Player:
    health: int = "deflult"
    energy: int = "deflult"
    buffs: List[str]= field(default_factory=list)
    hand_cards: List[str]= field(default_factory=list)
    relics: List[str]= field(default_factory=list)
    potions: List[str]= field(default_factory=list)

@dataclass
class MapNode:
    node_type: str  # 如战斗、商店、事件等
    details: Dict[str, str]  # 节点详细信息

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