import json
import os

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

    def get(self, field):
        return self.config.get(field)

    def set(self, field, value):
        self.config[field] = value

    def dump(self):
        text = json.dumps(self.config, indent=2, sort_keys=True)
        with open(config_path, "w") as f:
            f.write(text)

    def check_default(self):
        def default(key, value):
            self.config[key] = self.config.get(key, value)

        default("hypixel_api_key", None)

config = Config()