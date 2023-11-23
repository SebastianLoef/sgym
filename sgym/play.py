from sgym.games import _2048
import fire


def game_to_play(name: str = "2048"):
    if name == "2048":
        _2048.play()
    else:
        raise Exception("Game not found")

if __name__ == "__main__":
    fire.Fire(game_to_play)