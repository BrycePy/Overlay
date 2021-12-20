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
                self.config_f = json.load(f)
        self.check_default()
        self.dump()

    def get(self, field, default=None):
        return self.config.get(field, default)

    def set(self, field, value):
        self.config[field] = value

    def dump(self):
        text = json.dumps(self.config, indent=2)
        with open(config_path, "w") as f:
            f.write(text)

    def check_default(self):
        def default(key, value):
            if type(self.config_f.get(key)) != type(value):
                self.config[key] = value
            else:
                self.config[key] = self.config_f.get(key, value)

        default("hypixel_api_key", "")

        default("opacity", 0.5)
        default("fade_timeout", 5.0)
        default("key_wake", "tab")
        default("lobby_chat_words", ["your username here", "word1", "BoomZa", "MinuteBrain"])
        default("bg_color_left", "#000033")
        default("bg_color_right", "#330033")
        default("client_profiles",{"Vanila/Forge": r"$APPDATA\.minecraft\logs\latest.log",
                             "Lunar Client (1.8)": r"$USERPROFILE\.lunarclient\offline\1.8\logs\latest.log"})

        d_color = "#7b7b7b #fbf6f6 #f5f500 #d2a100 #ea4b49 #9232cc #5175fe #45ced7 #268400".split()
        r_FKDR=  [0, 1, 2.5, 4, 7, 10, 15, 25, 50]
        r_WLR=   [0, 1, 2, 4, 8, 16, 32, 64, 128]
        r_WS=    [0, 2, 5, 15, 30, 70, 100, 200, 300]
        r_BBLR=  [0, 2, 4, 6, 8, 12, 15, 20, 25]
        r_index = [0, 500, 1000, 3000, 7500, 15000, 30000, 100000, 500000]

        def gen_color_default(name, r, d_color):
            data = [[v, c] for v, c in zip(r ,d_color)]
            default(name, data) 

        gen_color_default("color_bw_ws", r_WS, d_color)
        gen_color_default("color_bw_fkdr", r_FKDR, d_color)
        gen_color_default("color_bw_wlr", r_WLR, d_color)
        gen_color_default("color_bw_bblr", r_BBLR, d_color)
        gen_color_default("color_bw_index", r_index, d_color)


config = Config()

event.subscribe("reload_request", lambda *_: config.load())