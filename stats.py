class Object():
    pass

class Stats:
    def __init__(self, player):
        self.player = player
        self.bedwars()
        self.general()
        self.player = None

    def bedwars(self):
        player = self.player
        stats = player.get("stats", {})
        bedwars = stats.get("Bedwars", {})
        achievements = player.get("achievements",{})

        mode_prefixs = ["", "eight_one_", "eight_two_", "four_three_", "four_four_", "two_four"]
        mode_name = ["Overall", "Solo", "Double", "3v3v3v3", "4v4v4v4", "4v4"]

        self.bw = [Object() for _ in mode_prefixs]

        for bw, prefix, name in zip(self.bw, mode_prefixs, mode_name):
            bw.mode_name = name
            bw.level = achievements.get("bedwars_level",0)
            bw.final_kills = bedwars.get(prefix+"final_kills_bedwars",0)
            bw.final_deaths = bedwars.get(prefix+"final_deaths_bedwars",0)
            bw.wins = bedwars.get(prefix+"wins_bedwars",0)
            bw.losses = bedwars.get(prefix+"losses_bedwars",0)
            bw.beds_broken = bedwars.get(prefix+"beds_broken_bedwars",0)
            bw.beds_lost = bedwars.get(prefix+"beds_lost_bedwars",0)
            bw.winstreak = bedwars.get(prefix+"winstreak",None)

            bw.fkdr = bw.final_kills / max(1,bw.final_deaths)
            bw.wlr = bw.wins / max(1,bw.losses)
            bw.bblr = bw.beds_broken / max(1,bw.beds_lost)
            bw.index = bw.fkdr * bw.fkdr * bw.level

    def general(self):
        player = self.player

        self.uuid = player.get("uuid")
        self.displayname = player.get("displayname")

        self.higher_rank = player.get("rank","")
        self.rank = player.get("newPackageRank","")
        self.mvppp = player.get("monthlyPackageRank","")
        _name_color = "$7"
        _text_color = "$7"
        if self.rank.startswith("VIP"):
            _name_color = "$a"
            _text_color = "$f"
        elif self.rank.startswith("MVP"):
            if self.mvppp == "SUPERSTAR":
                _name_color = "$6"
                _text_color = "$f"
            else:
                _name_color = "$b"
                _text_color = "$f"
        elif self.higher_rank == "YOUTUBER":
            _name_color = "$c"
            _text_color = "$f"
        self.chat = Object()
        self.chat.name_color = _name_color
        self.chat.text_color = _text_color
        self.chat.channel = player.get("channel","ALL")