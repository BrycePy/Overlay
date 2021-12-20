import re
from tkinter import Message
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import util
from config import config

def highlight(message,color):
    words = config.get("lobby_chat_words")
    for word in words:
        if word.lower() in message.lower():
            message = "$e"+message
            color = "$e"
            break

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
        #return f"{num:.1f}".replace(".","$c.$7")
        return f"{num:.1f}"
    else:
        #return f"{num:.2f}".replace(".","$c.$7")
        return f"{num:.2f}"

class Bedwars:
    def render(img, ign, player, font):
        data = player.data
        hypixel = data.get("hypixel")

        def render_skin():
            if data.get("skin"):
                skin = data.get("skin")
                img.paste(skin, (3, 0), skin)

        def render_nick():
            util.text(img, (65,0), f"$c< Nicked >", font, anchor="C")
            util.text(img, (200,0), f"{ign}", font, anchor="C")

        def render_normal():
            bw = hypixel.bw[0]
            star = util.get_star_text(bw.level)
            display_name = f"{hypixel.chat.name_color}{ign}"

            ws = bw.winstreak or "-"
            fkdr = bw.fkdr
            wlr = bw.wlr
            bblr = bw.bblr
            index = bw.index

            if bw.winstreak:
                ws_color = "$" + util.get_string_from_range(config.get("color_bw_ws"), ws)
            else:
                ws_color = "$8"
            fkdr_color = "$" + util.get_string_from_range(config.get("color_bw_fkdr"), fkdr)
            wlr_color = "$" + util.get_string_from_range(config.get("color_bw_wlr"), wlr)
            bblr_color = "$" + util.get_string_from_range(config.get("color_bw_bblr"), bblr)
            index_color = "$" + util.get_string_from_range(config.get("color_bw_index"), index)

            tag = f"$8-"

            util.text(img, (30,0), f"{index_color}{chr(9609)}{star}", font, anchor="L")
            util.text(img, (200,0), f"{display_name}", font, anchor="C")
            util.text(img, (330,0), f"{tag}", font, anchor="C")
            util.text(img, (390,0), f"{ws_color}{ws}", font, anchor="C")
            util.text(img, (450+24,0), f"{fkdr_color}{grayout_dec(fkdr)}", font, anchor="R")
            util.text(img, (510+24,0), f"{wlr_color}{grayout_dec(wlr)}", font, anchor="R")
            util.text(img, (570+24,0), f"{bblr_color}{grayout_dec(bblr)}", font, anchor="R")

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
        hypixel = player.data.get("hypixel")
        if player.nicked: return 99999999999999
        if not hypixel: return -99999999999999
        return hypixel.bw[0].index

    def sort(players):
        return sorted(list(players), key=lambda ign: Bedwars.sort_function(players[ign]), reverse=True)


class LobbyChat:
    def render(img, ign, player, font):
        data = player.data
        hypixel = data.get("hypixel")

        username = player.ign

        def render_skin():
            if data.get("skin"):
                skin = data.get("skin")
                img.paste(skin, (3, 0), skin)

        def render_nick():
            util.text(img, (65,0), f"$c< Nicked >", font, anchor="C")
            util.text(img, (200,0), f"{ign}", font, anchor="C")

        def render_normal():
            bw = hypixel.bw[0]
            star = util.get_star_text(bw.level, True)
            ws = bw.winstreak or "-"
            fkdr = bw.fkdr
            wlr = bw.wlr
            index = bw.index

            if bw.winstreak:
                ws_color = "$" + util.get_string_from_range(config.get("color_bw_ws"), ws)
            else:
                ws_color = "$8"
            fkdr_color = "$" + util.get_string_from_range(config.get("color_bw_fkdr"), fkdr)
            wlr_color = "$" + util.get_string_from_range(config.get("color_bw_wlr"), wlr)
            index_color = "$" + util.get_string_from_range(config.get("color_bw_index"), index)

            message = data.get("latest_message",":-").split(":",1)[-1]
            message = highlight(message,hypixel.chat.text_color)

            util.text(img, (70,0), f"{ws_color}{ws}", font, anchor="R")
            util.text(img, (130,0), f"{wlr_color}{grayout_dec(wlr)}", font, anchor="R")
            util.text(img, (190,0), f"{fkdr_color}{grayout_dec(fkdr)}", font, anchor="R")
            util.text(img, (200,0), f"{index_color}{chr(9609)}{star} {hypixel.chat.name_color}{username}$f: {hypixel.chat.text_color}{message}", font, anchor="L")

        def render_error():
            util.text(img, (65,0), f"$c(error)", font, anchor="C")
            util.text(img, (200,0), f"$7{ign}", font, anchor="C")
            util.text(img, (330,0), f"$8{player.error_message}", font, anchor="L")

        def render_loading():
            message = data.get("latest_message",":-").split(":",1)[-1]
            message = highlight(message,"$7")
            util.text(img, (95,0), f"$7< fetching stats >", font, anchor="C")
            util.text(img, (200,0), f"$8[????] $7{username}$f: $f{message}", font, anchor="L")


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