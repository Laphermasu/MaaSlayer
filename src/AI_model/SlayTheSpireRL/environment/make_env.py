from src.AI_model.SlayTheSpireRL.slay_the_spire_env import SlayTheSpireEnv


def make_env(env_id, rank, seed=0):
    """
    Utility function for multiprocessed env.
    """
    def _init():
        env = SlayTheSpireEnv({})
        env.seed(seed + rank)
        return env
    return _init