# PONG

- Two-player paddle controls (W/S and UP/DOWN)
- Opponents: OscillatingBot, FollowBot and SmartBot

![screen capture](https://i.imgur.com/VQqQeKe.mp4)

```sh
git clone git@github.com:romanmikh/PONG.git pong && cd pong
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest
python3 -m game.src.main
```