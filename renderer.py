from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import util

def grayout_dec(num):

    if num >= 1000: num = round(num)
    elif num >= 100: num = round(num, 1)
    elif num >= 0: num = round(num, 2)

    if num>=1000:
        return f"{num}"
    else:
        return f"{num:.2f}".replace(".","$c.$8")

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
            util.text(img, (65,0), f"{star}", font, anchor="C")
            util.text(img, (200,0), f"$7{ign}", font, anchor="C")

            
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
        util.text(img, (450,0), "$bFDKR", font, anchor="C", bold=True)
        util.text(img, (510,0), "$bWLR", font, anchor="C", bold=True)
        util.text(img, (570,0), "$bBBLR", font, anchor="C", bold=True)