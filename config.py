import json
import os
import event

home_path = os.path.join(os.getenv('APPDATA'),"MinuteBrain")
config_path = os.path.join(home_path, "config.json")

if not os.path.exists(home_path):
    os.makedirs(home_path)

class Config:
    def __init__(self):
        self.config = {}
        self.load()

    def load(self):
        if os.path.isfile(config_path):
            with open(config_path, "r") as f:
                self.config = json.load(f)
        self.check_default()
        self.dump()

    def get(self, field, default=None):
        return self.config.get(field, default)

    def set(self, field, value):
        self.config[field] = value

    def dump(self):
        text = json.dumps(self.config, indent=2, sort_keys=True)
        with open(config_path, "w") as f:
            f.write(text)

    def check_default(self):
        def default(key, value):
            if type(self.config.get(key)) != type(value):
                self.config[key] = value
            else:
                self.config[key] = self.config.get(key, value)

        default("opacity", 0.5)
        default("fade_timeout", 5.0)
        default("hypixel_api_key", "")
        default("lobby_chat_words", ["your username here", "word1", "BoomZa", "MinuteBrain"])

config = Config()

event.subscribe("reload_request", lambda *_: config.load())