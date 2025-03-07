from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Monster:
    type: str = "default"
    health: str = "default"
    action: str = "default"
    buffs: List[str] = field(default_factory=list)

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