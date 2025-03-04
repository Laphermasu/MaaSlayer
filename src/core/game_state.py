from .data_models import GameState
from .image_processor import ImageProcessor

class GameStateManager:
    def __init__(self, image_processor: ImageProcessor):
        self.image_processor = image_processor
        self.current_state: GameState = None

    def update_state(self):
        # 更新游戏状态
        self.current_state = self.image_processor.get_game_state()

    def get_state(self) -> GameState:
        # 获取当前游戏状态
        return self.current_state