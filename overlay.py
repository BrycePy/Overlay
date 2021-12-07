import event
import asynctkcore as AsyncTk
import tkinter as tk
import re
import messageprocessor
import asyncio
import traceback
from io import BytesIO
import base64
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageGrab
import uicore
from loglistener import NoClientFoundError, LogListerner
import util
import time
from BlurWindow.blurWindow import GlobalBlur
import sys
from player import Player
import renderer

"""

TODO
- mode selector
- config file
- individual rendering
- async requests

"""

global_image = {}
global_task = []

player_data = {}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    # print(base_path)
    return os.path.join(base_path, relative_path)

font = ImageFont.truetype(font=resource_path("Roboto-Bold-uni.ttf"), size=19)
#font = ImageFont.truetype(font=resource_path("Minecraft-Regular-Symbola.ttf"), size=19)

async def await_global_task():
    while True:
        if global_task:
            done, pending = await asyncio.wait(global_task)
            for task in done:
                await task
                global_task.remove(task)
        await asyncio.sleep(3)

async def log_reader(overlay):
    log_listener = LogListerner()
    mp = messageprocessor.MessageProcessor()

    checked = set()

    def player_list_update(players):
        for player in players:
            if player in checked: continue
            checked.add(player)
            player_obj = player_data[player] = Player(ign=player)
            task = asyncio.get_event_loop().create_task(player_obj.update())
            global_task.append(task)

    def player_leave(username):
        if username in checked:
            checked.remove(username)
        p = player_data.pop(username,None)
        if p: p.active = False

    def queue_join(_):
        checked.clear()
        for ign, p in player_data.items(): p.active = False
        player_data.clear()

    def apikey_new(_):
        pass

    def msg_command(_):
        pass

    def who_command(_):
        pass

    def lobby_join(_):
        pass

    event.subscribe("player_list_update", player_list_update)
    event.subscribe("player_leave", player_leave)
    event.subscribe("queue_join", queue_join)
    event.subscribe("apikey_new", apikey_new)
    event.subscribe("msg_command", msg_command)
    event.subscribe("who_command", who_command)
    event.subscribe("lobby_join", lobby_join)

    while True:
        await asyncio.sleep(0.2)
        for message in log_listener.get_messages():
            print(message)
            await mp.process(message)

class Overlay:
    transparent = "#010503"

    width = 600
    height = 350
    row_height = 20

    def __init__(self):
        self.loop = asyncio.get_event_loop()

        self.root = self.root_root()
        self.bg = self.bg_toplevel(self.root)
        self.fg = self.fg_toplevel(self.root)
        self.stats = self.stats_toplevel(self.root)

        self.root.attributes("-topmost",True)
        self.bg.attributes("-topmost",True)
        self.fg.attributes("-topmost",True)
        self.stats.attributes("-topmost",True)

        self.bg.bind('<Double-Button-1>', self.mouse_double_click)
        self.bg.bind("<Button-1>", lambda e: (self.fg.lift(), self.root.lift(),
                                              self.stats.lift(), self.mouse_click(e)))
        self.bg.bind("<Motion>", self.mouse_hover)

        #self.bg.bind("<Enter>", lambda _: self.stats.set_alpha(1))
        #self.bg.bind("<Leave>", lambda _: self.stats.set_alpha(0, force=True))

        self.root.after(100,  self.root.set_alpha, 0.95)
        self.root.after(100, self.bg.set_alpha, 0.35)
        self.root.after(100, self.fg.set_alpha, 0.95)

        #self.root.after(100, self.stats.set_alpha, 0.95)

        if False: # blur
            GlobalBlur(int(self.fg.frame(),16))
            self.root.after(400, self.fg.geometry, "+0+105")
            self.root.after(500, self.fg.geometry, "+0+105")
            self.root.after(600, self.fg.geometry, "+0+105")

        self.mode = "Bedwars"

        self.root.after(500, event.post, "player_list_update", ["MinuteBrain", "decliner", "Eldenax", "preadolescence"])
        self.root.after(500, event.post, "player_list_update", ["xMqt", "T_H_O_R", "ChristmasRudolph"])
        self.root.after(500, event.post, "player_list_update", ["MerryQuackwy", "_Me", "XMASCHER"])
        self.root.after(500, event.post, "player_list_update", ["cloudalina", "XMASWOLF", "quin_in_the_snow","MinuteBrainN"])
        self.loop.create_task(log_reader(self))
        self.loop.create_task(await_global_task())
        self.loop.create_task(self.render_worker())
        self.loop.create_task(self.follow_worker())

        event.subscribe("player_list_update", self.render_cleanup)
        event.subscribe("render_request",self.render_notification)

        self.loop.run_forever()

    def root_root(self):
        offset = [0, 0, 0 ,0]

        def root_drag(event):
            mouse_x, mouse_y = uicore.get_mouse_pos()
            x = offset[2] + (mouse_x - offset[0])
            y = offset[3] + (mouse_y - offset[1])
            h = root.winfo_height()
            if x<20: x = 0
            self.root.geometry("+%d+%d" % (x, y))
            self.bg.geometry("+%d+%d" % (x, y+h))
            self.fg.geometry("+%d+%d" % (x, y+h))

        def root_click(event):
            self.bg.lift()
            self.fg.lift()
            if event.num == 1:
                offset[0], offset[1] = uicore.get_mouse_pos()
                offset[2] = self.root.winfo_x()
                offset[3] = self.root.winfo_y()
                print(offset)
        
        bg_color = "#111"
        root = AsyncTk.AsyncTk(self.loop)
        root.overrideredirect(1)
        root.geometry(f"{self.width}x20+0+70")
        root.config(background=bg_color)

        close_button = tk.Button(root, background="#a00", width=2, relief="flat", command=self.destroy)
        close_button.pack(fill=tk.Y, side=tk.LEFT)
        AsyncTk.OnHover(close_button, "bg", "#F33")

        self.l_version = tk.Label(root, text="(v3.0.0 dev)", bg=bg_color, fg="gray", relief="flat", font="Arial 10 bold")
        self.l_version.pack(fill=tk.Y, side=tk.RIGHT)

        self.l_title = tk.Label(root, text="BWSTATS OVERLAY", bg=bg_color, fg="white", relief="flat", font="Arial 10 bold")
        self.l_title.pack(fill=tk.Y, side=tk.RIGHT)

        grip_frame = tk.Frame(root, bg=bg_color, relief="flat", cursor="fleur")
        grip_frame.pack(fill=tk.BOTH, expand=True)

        grip_frame.bind("<Button-1>", root_click)
        grip_frame.bind("<B1-Motion>", root_drag)

        root.update()
        #self.loop.create_task(root.updater(1/30))
        return root

    def bg_toplevel(self, root:tk.Toplevel):
        bg_color = "#303"
        top = AsyncTk.AsyncToplevel(root)
        top.geometry(f"{self.width}x{self.height}")
        top.configure(background=bg_color)
        top.overrideredirect(1)
        top.update()

        self.bg_canvas = tk.Canvas(top, background=bg_color, relief="flat", highlightthickness=0)
        self.bg_canvas.pack(fill=tk.BOTH, expand=True)

        w, h = top.winfo_width(), top.winfo_height()
        img = Image.new("RGB", (w, h))
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, w, h), fill="#330033")
        draw.rectangle((0, 0, w//2, h), fill="#000033")

        img = img.filter(ImageFilter.GaussianBlur(300))
        global_image["bg"] = ImageTk.PhotoImage(image=img)
        self.bg_canvas.create_image(0, 0, image=global_image["bg"], anchor="nw")

        return top

    def fg_toplevel(self, root:tk.Toplevel):
        top = AsyncTk.AsyncToplevel(root)
        top.attributes("-transparentcolor", self.transparent)
        top.geometry(f"{self.width}x{self.height}")
        top.configure(background=self.transparent)
        top.overrideredirect(1)

        self.canvas = tk.Canvas(top, background=self.transparent, relief="flat", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas_header = self.canvas.create_image(0, 0, image=None, anchor="nw")

        top.update()
        uicore.set_clickthrough(int(top.frame(),16), True)

        return top

    def stats_toplevel(self, root:tk.Toplevel):
        top = AsyncTk.AsyncToplevel(root)
        top.geometry(f"{self.width//2}x{self.height}")
        top.configure(background="blue")
        top.overrideredirect(1)
        top.update()
        uicore.set_clickthrough(int(top.frame(),16), True)
        top.set_alpha(0)
        return top

    def mouse_click(self, event):
        row_number = event.y // self.row_height
        username = list(player_data)[row_number-1]
        header_image = global_image.get(f"header-raw")
        stats_image = global_image.get(f"stats-{username}-raw")
        img = Image.new("RGB", (header_image.width, header_image.height + stats_image.height), "#000000")
        img.paste(header_image, (0, 0))
        img.paste(stats_image, (0, header_image.height))
        util.set_clipboard_image(img)
        original_alpha = self.bg.get_alpha()
        self.bg.set_alpha(1, force=True)
        self.bg.set_alpha(original_alpha)
        print("clicked", username)

    def mouse_double_click(self, event):
        original_alpha = self.bg.get_alpha()
        self.bg.set_alpha(1, force=True)
        self.bg.update()
        x1, y1 = self.root.winfo_rootx(), self.root.winfo_rooty()
        x2 = self.bg.winfo_rootx() + self.bg.winfo_width()
        y2 = self.bg.winfo_rooty() + self.bg.winfo_height()
        img = ImageGrab.grab((x1, y1, x2, y2))
        self.bg.set_alpha(original_alpha)
        util.set_clipboard_image(img)
        print("double click")

    def mouse_hover(self,event):
        row_number = event.y // self.row_height
        progress = event.x / self.bg.winfo_width()
        #print(row_number, "hovering on", list(player_data)[row_number-1], progress)

    def follow(self, child:tk.Toplevel ,parent:tk.Toplevel, side="S"):
        w, h, x, y = (parent.winfo_width(), parent.winfo_height(), parent.winfo_x(), parent.winfo_y())
        if side == "S":
            child.geometry(f"+{x}+{y+h}")
        elif side == "E":
            child.geometry(f"+{x+w}+{y}")

    def destroy(self):
        self.bg.close()
        self.fg.close()
        self.root.close()
        exit(0)

    rendering = True
    async def render_worker(self):
        while True:
            self.render()
            if self.rendering:
                await asyncio.sleep(1/60)
                #print("render")
            else:
                for i in range(10):
                    if self.rendering: break
                    await asyncio.sleep(0.1)
                #print("idle")

    async def follow_worker(self):
        while True:
            self.follow(self.bg, self.root, "S")
            self.follow(self.fg, self.root, "S")
            self.follow(self.stats, self.bg, "S")
            await asyncio.sleep(1)

    def render_notification(self,_):
        self.rendering = True

    rendered = {}
    current_header = ""

    pil_time_avg_buffer = []

    def render(self):
        canvas = self.canvas
        rendered = self.rendered
        win_width = self.fg.winfo_width()
        updated = False
        for count, ign in enumerate(player_data):
            player = player_data[ign]
            data = player.data
            if ign not in rendered:
                data["canvas"] = canvas.create_image(0, 0)
                canvas.tag_lower(data["canvas"], self.canvas_header)
                rendered[ign] = dict(image_id=data["canvas"])
                rendered[ign]["current_y"] = 0
                rendered[ign]["target_y"] = 0
            player_canvas =  rendered[ign]["image_id"]

            if player.pending_render:
                ref = time.perf_counter()
                updated = True
                img = Image.new("RGBA", (win_width, self.row_height+4), (1,5,3,50))
                renderer.Bedwars.render(img, ign, player, font)

                image_name = f"stats-{ign}"
                global_image[image_name+"-raw"] = img
                global_image[image_name] = ImageTk.PhotoImage(image=img)
                canvas.itemconfigure(player_canvas, image=global_image[image_name], anchor="nw")
                player.render_notification()

                pil_time = time.perf_counter() - ref
                self.pil_time_avg_buffer.append(pil_time)
                if len(self.pil_time_avg_buffer)>10: self.pil_time_avg_buffer.pop(0)
                average = sum(self.pil_time_avg_buffer) / len(self.pil_time_avg_buffer)
                print(f"Generated image for {ign}. (t={pil_time:.3f}s avg={average:.3f}s)")

            rendered[ign]["target_y"] = count*self.row_height + 5 + self.row_height

        all_done = True
        for ign in rendered:
            image_id = rendered[ign]["image_id"]
            target_y = rendered[ign]["target_y"]
            current_y = rendered[ign]["current_y"]
            if -2<target_y-current_y<2:
                if current_y!=target_y:
                    rendered[ign]["current_y"] = target_y
                    canvas.coords(image_id, 0, int(current_y))
            else:
                rendered[ign]["current_y"] = (current_y*6 + target_y)/7
                canvas.coords(image_id, 0, int(current_y))
                self.rendering = True
                all_done = False

        if all_done and self.rendering:
            self.rendering = False

        self.render_header()

    def render_header(self):
        if self.current_header != self.mode:
            self.current_header == self.mode

        win_width = self.fg.winfo_width()
        if self.mode == "Bedwars":
            img = Image.new("RGBA", (win_width, 24), (1,5,3,200))
            renderer.Bedwars.header(img, font)
            global_image["header-raw"] = img
            global_image["header"] = ImageTk.PhotoImage(image=img)
            self.canvas.itemconfigure(self.canvas_header, image=global_image["header"], anchor="nw")

    def render_cleanup(self, _):
        rendered = self.rendered
        for ign in list(rendered):
            if ign not in player_data:
                image_id = rendered[ign]["image_id"]
                rendered.pop(ign, None)
                self.canvas.delete(image_id)
                global_image.pop(f"stats-{ign}", None)
                global_image.pop(f"stats-{ign}-raw", None)
                

if __name__ == '__main__':
    Overlay()