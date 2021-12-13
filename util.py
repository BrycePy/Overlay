
import re
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
from cons import Colors
import time
import asyncio
import keyboard
import win32clipboard
import win32con
from io import BytesIO

async def send_command(command):
    key_to_restore = ["a","s","d","w","space"] + list(keyboard.sided_modifiers)
    keys_state = keyboard.stash_state()
    for key in key_to_restore: keyboard.release(key)
    await asyncio.sleep(2/60) # wait for around 2 game frame
    keyboard.press("t")
    await asyncio.sleep(2/60)
    keyboard.release("t")
    for key in key_to_restore: keyboard.release(key)
    await asyncio.sleep(3/60)
    keyboard.write("\b"*20 + f"/{command}" + "\n")
    keyboard.restore_state(keys_state)

def text(img:Image.Image, xy:tuple, text:str, font:ImageFont.FreeTypeFont, shadow=True, bold=False, anchor="L"):
    text = re.sub("\$[klmnor]", "", text)
    temp = ["f"] + re.split("\$([0-9a-fA-F]|\#[0-9a-fA-F]{6})", text)
    text_only = "".join(temp[1::2])
    size = font.getsize(text = text_only)
    pixel_offset = int(font.size/13)

    adj_size = (size[0] + pixel_offset*len(text_only), size[1])

    temp_image = Image.new("RGBA", adj_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(temp_image)

    cumulative_width = 0
    for t, c in zip(temp[1::2], temp[::2]):
        if not t: continue
        s = font.getsize(text = text_only)
        if len(c) == 1: c = Colors.mc[int(c,16)]
        draw.text((cumulative_width, 0), text=t, font=font, fill=c)
        w, h = font.getsize(text = t)
        cumulative_width += w
        if bold: cumulative_width += pixel_offset

    if anchor == "L":
        xy = xy
    elif anchor == "C":
        xy = (xy[0]-cumulative_width//2, xy[1])
    elif anchor == "R":
        xy = (xy[0]-cumulative_width, xy[1])

    if shadow:
        shadow_img = ImageEnhance.Brightness(temp_image).enhance(0.3)
        shadow_coor = (xy[0] + pixel_offset, xy[1] + pixel_offset)
        img.paste(shadow_img, shadow_coor, shadow_img)

    if bold:
        bold_coor = (xy[0] + pixel_offset, xy[1])
        img.paste(temp_image, bold_coor, temp_image)
        bold_coor = (xy[0] + pixel_offset//2, xy[1])
        img.paste(temp_image, bold_coor, temp_image)

    img.paste(temp_image, xy, temp_image)

    return cumulative_width


def get_star_text(star, b=False):
    star0 = chr(0x2605)
    star1 = chr(0x272A)
    star2 = chr(0x2743)

    if b:
        low_prestiges = lambda star, color: f"${color}[{star}{star0}]"
    else:
        low_prestiges = lambda star, color: f"${color}{star}{star0}"

    zip_color = lambda texts, colors: "".join(f"${c}{t}" for t, c in zip(texts,colors))

    star_str = str(star)

    if star < 100:
        return low_prestiges(star, Colors.gray)

    elif star < 200:
        return low_prestiges(star, Colors.white)

    elif star < 300:
        return low_prestiges(star, Colors.gold)

    elif star < 400:
        return low_prestiges(star, Colors.aqua)

    elif star < 500:
        return low_prestiges(star, Colors.dark_green)

    elif star < 600:
        return low_prestiges(star, Colors.dark_aqua)

    elif star < 700:
        return low_prestiges(star, Colors.dark_red)

    elif star < 800:
        return low_prestiges(star, Colors.light_purple)

    elif star < 900:
        return low_prestiges(star, Colors.blue)

    elif star < 1000:
        return low_prestiges(star, Colors.dark_purple)

    elif star < 1100:
        color = "c6eabd5"
        text = f"[{star}{star1}]"
        return zip_color(text, color)

    elif star < 1200:
        color = "7fd7"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 1300:
        color = "7e67"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 1400:
        color = "7b37"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 1500:
        color = "7a27"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 1600:
        color = "7397"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 1700:
        color = "7c47"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 1800:
        color = "7d57"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 1900:
        color = "7917"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 2000:
        color = "7587"
        text = ["[", str(star), star1, "]"]
        return zip_color(text, color)

    elif star < 2100:
        color = "87ff778"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 2200:
        color = "ffee666"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 2300:
        color = "66ffb33"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 2400:
        color = "55dd6ee"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 2500:
        color = "bbff778"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 2600:
        color = "ffaa222"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 2700:
        color = "44ccdd5"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 2800:
        color = "eeff888"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 2900:
        color = "aa2266e"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    elif star < 3000:
        color = "bb33991"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

    else:
        color = "ee66cc4"
        text = f"[{star}{star2}]"
        return zip_color(text, color)

def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()

def set_clipboard_text(text):
    send_to_clipboard(win32con.CF_UNICODETEXT, text)

def set_clipboard_image(image:Image.Image):
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    send_to_clipboard(win32clipboard.CF_DIB, data)

if __name__ == "__main__":
    ref = time.perf_counter()
    image = Image.new("RGBA", (700,700), (0, 0, 0, 0))
    font = ImageFont.truetype(font="Minecraft-Regular-Symbola.ttf", size=20)
    test_text = "".join([f"${i:x}AA" for i in range(8)])
    for i in range(32):
        text(image, (150*(i//16)+150, 30*(i%16)), get_star_text(i*100 + 1), font, shadow=True, bold=False, anchor="R")

    text(image, (0,650), "§b>§c>§a>§r §6[MVP§2++§6] reynasimp§f §6slid into the lobby! §a<§c<§b<".replace("§","$"), font)
    text(image, (0,620), "█ §2[407?] §6[MVP§0++§6] Ramsy§f: It really is".replace("§","$"), font)

    print(time.perf_counter() - ref)

    image.show()