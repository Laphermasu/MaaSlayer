from sqlalchemy.orm import Session
from src.AI_model.SlayTheSpireRL.db.models import Game
from src.AI_model.SlayTheSpireRL.db.session import SessionLocal

def update_boss_count(game_state, game_id):
    """
    Update the count of bosses defeated in the database.
    """
    try:
        db: Session = SessionLocal()

        game = db.query(Game).filter(Game.game_id == game_id).first()
        if game:
            game.boss_defated += 1
        db.commit()
        print("Boss count updated in the database.")

        db.close()

    except Exception as e:
        print(f"Error while updating boss count: {e}")