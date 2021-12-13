import re
from tkinter import Message
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import util

def highlight(message,color):
    if "_Me" in message:
        message = "$e"+message
        color = "$e"

    message = re.sub("(\d)\/(\d)",lambda match: f"$e{match.group(1)}/$6{match.group(2)}{color}",message)
    message = message.replace("OOF", f"$cOOF{color}") 
    message = message.replace("( ???)/", f"$d(^{chr(9697)}^)/{color}")
    return message

def rainbow(text):
    color_pattern = "c6ea9b5" * (len(text)//7+1)
    zip_color = lambda texts, colors: "".join(f"${c}{t}" for t, c in zip(texts,colors))
    return zip_color(text, color_pattern)

def grayout_dec(num):

    if num >= 1000: num = round(num)
    elif num >= 100: num = round(num, 1)
    elif num >= 0: num = round(num, 2)

    if num>=1000:
        return f"{num}"
    elif num>=100:
        return f"{num:.1f}".replace(".","$c.$7")
    else:
        return f"{num:.2f}".replace(".","$c.$7")

class Bedwars:
    def render(img, ign, player, font):
        data = player.data
        bedwars = data.get("hypixel",{}).get("stats",{}).get("Bedwars",{})

        def render_skin():
            if data.get("skin"):
                skin = data.get("skin")
                img.paste(skin, (3, -6), skin)

        def render_nick():
            util.text(img, (65,0), f"$c< Nicked >", font, anchor="C")
            util.text(img, (200,0), f"{ign}", font, anchor="C")

        def render_normal():
            hypixel = data.get("hypixel")
            star = util.get_star_text(hypixel.get("achievements").get("bedwars_level",0))
            util.text(img, (30,0), f"{star}", font, anchor="L")

            rank = hypixel.get("newPackageRank","")
            mvppp = hypixel.get("monthlyPackageRank","")
            name_color = "$7"
            if rank.startswith("VIP"): name_color = "$a"
            elif rank.startswith("MVP"): name_color = "$b"
            if rank.startswith("MVP") and mvppp.startswith("SUPERSTAR"): name_color = "$6"

            util.text(img, (200,0), f"{name_color}{ign}", font, anchor="C")
            

            ws = bedwars.get("winstreak","$8-")
            fkdr = bedwars.get("final_kills_bedwars",0) / max(1,bedwars.get("final_deaths_bedwars",1))
            wlr = bedwars.get("wins_bedwars",0) / max(1,bedwars.get("losses_bedwars",1))
            bblr = bedwars.get("beds_broken_bedwars",0) / max(1,bedwars.get("beds_lost_bedwars",1))

            util.text(img, (330,0), f"$8-", font, anchor="C")
            util.text(img, (390,0), f"{ws}", font, anchor="C")
            util.text(img, (450+24,0), f"{grayout_dec(fkdr)}", font, anchor="R")
            util.text(img, (510+24,0), f"{grayout_dec(wlr)}", font, anchor="R")
            util.text(img, (570+24,0), f"{grayout_dec(bblr)}", font, anchor="R")

        def render_error():
            util.text(img, (65,0), f"$c(error)", font, anchor="C")
            util.text(img, (200,0), f"$7{ign}", font, anchor="C")
            util.text(img, (330,0), f"$8{player.error_message}", font, anchor="L")

        def render_loading():
            util.text(img, (70,0), f"$8{ign} (fetching stats..)", font)

        if player.nicked:
            render_nick()
        elif data.get("hypixel"):
            render_normal()
        elif player.error_message:
            render_error()
        else:
            render_loading()

        render_skin()
                    

    def header(img, font):
        util.text(img, (65,0), "$bLEVEL", font, anchor="C", bold=True)
        util.text(img, (200,0), "$bUSERNAME", font, anchor="C", bold=True)
        util.text(img, (330,0), "$bTAG", font, anchor="C", bold=True)
        util.text(img, (390,0), "$bWS", font, anchor="C", bold=True)
        util.text(img, (450,0), "$bFKDR", font, anchor="C", bold=True)
        util.text(img, (510,0), "$bWLR", font, anchor="C", bold=True)
        util.text(img, (570,0), "$bBBLR", font, anchor="C", bold=True)

    def sort_function(player):
        hypixel = player.data.get("hypixel",{})
        if player.nicked: return 99999999999999
        if not hypixel: return -99999999999999
        bedwars = hypixel.get("stats",{}).get("Bedwars",{})
        return bedwars.get("wins_bedwars", 0)

    def sort(players):
        return sorted(list(players), key=lambda ign: Bedwars.sort_function(players[ign]), reverse=True)


class LobbyChat:
    def render(img, ign, player, font):
        data = player.data
        bedwars = data.get("hypixel",{}).get("stats",{}).get("Bedwars",{})

        def render_skin():
            if data.get("skin"):
                skin = data.get("skin")
                img.paste(skin, (3, -6), skin)

        def render_nick():
            util.text(img, (65,0), f"$c< Nicked >", font, anchor="C")
            util.text(img, (200,0), f"{ign}", font, anchor="C")

        def render_normal():
            hypixel = data.get("hypixel")

            rank = hypixel.get("newPackageRank","")
            mvppp = hypixel.get("monthlyPackageRank","")
            name_color = "$7"
            text_color = "$7"
            if rank.startswith("VIP"):
                name_color = "$a"
                text_color = "$f"
            elif rank.startswith("MVP"):
                name_color = "$b"
                text_color = "$f"
            if rank.startswith("MVP") and mvppp.startswith("SUPERSTAR"):
                name_color = "$6"
                text_color = "$f"

            username = player.ign
            ws = bedwars.get("winstreak","$8-")
            fkdr = bedwars.get("final_kills_bedwars",0) / max(1,bedwars.get("final_deaths_bedwars",1))
            wlr = bedwars.get("wins_bedwars",0) / max(1,bedwars.get("losses_bedwars",1))
            bblr = bedwars.get("beds_broken_bedwars",0) / max(1,bedwars.get("beds_lost_bedwars",1))

            star = util.get_star_text(hypixel.get("achievements").get("bedwars_level",0), True)

            message = data.get("latest_message",":-").split(":",1)[-1]
            message = highlight(message,text_color)

            util.text(img, (70,0), f"{ws}", font, anchor="R")
            util.text(img, (130,0), f"{grayout_dec(wlr)}", font, anchor="R")
            util.text(img, (190,0), f"{grayout_dec(fkdr)}", font, anchor="R")
            util.text(img, (200,0), f"{star} {name_color}{username}$f: {text_color}{message}", font, anchor="L")

        def render_error():
            util.text(img, (65,0), f"$c(error)", font, anchor="C")
            util.text(img, (200,0), f"$7{ign}", font, anchor="C")
            util.text(img, (330,0), f"$8{player.error_message}", font, anchor="L")

        def render_loading():
            util.text(img, (70,0), f"$8{ign} (fetching stats..)", font)

        if player.nicked:
            render_nick()
        elif data.get("hypixel"):
            render_normal()
        elif player.error_message:
            render_error()
        else:
            render_loading()

        render_skin()
                    

    def header(img, font):
        util.text(img, (70,0), f"$bWS", font, anchor="R", bold=True)
        util.text(img, (130,0), f"$bWLR", font, anchor="R", bold=True)
        util.text(img, (190,0), f"$bFKDR", font, anchor="R", bold=True)

    def sort_function(player):
        return player.ign

    def sort(players):
        return list(players)

# import os

# def resource_path(relative_path):
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
#     # print(base_path)
#     return os.path.join(base_path, relative_path)

# font = ImageFont.truetype(font=resource_path("Roboto-Bold-uni.ttf"), size=19)

# def generate_card(overlay,player):
#     height = overlay.bg.winfo_height()
#     img = Image.new("RGB", (1000, height), "#000000")

#     player_skin = player.data.get("skin")
#     if player_skin:
#         img.paste(player_skin.resize((100,100), resample=Image.NEAREST))

#     name = player.ign
#     util.text(img, (50,100), name, font)

#     return img