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
import win32gui, win32con
from config import config
import keyboard
import mouse

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
player_order = []

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
        overlay.render_mode = renderer.Bedwars
        overlay.new_from_top = True
        for player in players:
            if player in checked: continue
            checked.add(player)
            player_order.append(player)
            player_obj = player_data[player] = Player(ign=player)
            task = asyncio.get_event_loop().create_task(player_obj.update())
            global_task.append(task)

    def player_leave(username):
        if username in checked:
            checked.remove(username)
            player_order.remove(username)
        p = player_data.pop(username,None)
        if p: p.active = False
        overlay.render_notification()

    def queue_join(_):
        checked.clear()
        for ign, p in player_data.items(): p.active = False
        player_data.clear()
        player_order.clear()

    def apikey_new(key):
        Player.set_apikey(key)
        for ign, player_obj in player_data.items():
            task = asyncio.get_event_loop().create_task(player_obj.update())
            global_task.append(task)

    def msg_command(_):
        pass

    def who_command(players):
        for player in list(player_data):
            if player not in players:
                event.post("player_leave",player)

    def lobby_join(_):
        pass

    def chat(data):
        overlay.new_from_top = False
        player, message = data
        if "PARTY" not in message:
            overlay.render_mode = renderer.LobbyChat
        if player in player_order:
            player_order.remove(player)
            player_data[player].data["latest_message"] = message
            if overlay.render_mode == renderer.LobbyChat:
                player_data[player].render_request()
        player_order.insert(0, player)

        if player in checked: return

        if len(player_order) > 30:
            pending_remove = player_order[-1]
            event.post("player_leave", pending_remove)
            print("removing", pending_remove)

        checked.add(player)
        player_obj = player_data[player] = Player(ign=player)
        player_obj.data["latest_message"] = message
        task = asyncio.get_event_loop().create_task(player_obj.update())
        global_task.append(task)
        overlay.render_cleanup(0)


    event.subscribe("player_list_update", player_list_update)
    event.subscribe("player_leave", player_leave)
    event.subscribe("queue_join", queue_join)
    event.subscribe("apikey_new", apikey_new)
    event.subscribe("msg_command", msg_command)
    event.subscribe("who_command", who_command)
    event.subscribe("lobby_join", lobby_join)
    event.subscribe("chat", chat)

    while True:
        await asyncio.sleep(0.05)
        for message in log_listener.get_messages():
            print(message)
            await mp.process(message)
            await asyncio.sleep(0.05)

class Overlay:
    transparent = "#010503"

    width = 600
    height = 350
    row_height = 20
    scroll_offset = 0
    new_from_top = True
    hide_schedule = None

    def __init__(self):
        pass

    def start(self):
        global puro
        self.loop = asyncio.get_event_loop()

        self.root = self.root_root()
        puro = tk.PhotoImage(file=resource_path('puro.png'))
        self.bg = self.bg_toplevel(self.root)
        self.fg = self.fg_toplevel(self.root)
        self.stats = self.stats_toplevel(self.root)

        self.root.attributes("-topmost",True)
        self.bg.attributes("-topmost",True)
        self.fg.attributes("-topmost",True)
        self.stats.attributes("-topmost",True)

        #self.bg.bind('<Double-Button-1>', self.mouse_double_click)
        self.bg.bind("<Button-1>", lambda e: (self.fg.lift(), self.root.lift(),
                                              self.stats.lift(), self.mouse_click(e)))
        self.bg.bind("<Motion>", self.mouse_hover)

        def set_mode(mode):
            self.render_notification()
            self.render_mode = mode

        # self.bg.bind("b", lambda x: set_mode(renderer.Bedwars))
        # self.bg.bind("c", lambda x: set_mode(renderer.LobbyChat))

        def on_mousewheel(event):
            if event.delta > 0: self.scroll_offset += self.row_height*3
            else:               self.scroll_offset -= self.row_height*3
            if self.scroll_offset<0: self.scroll_offset=0
            self.render_notification()

        def on_leave(event):
            self.scroll_offset = 0
            self.render_notification()
            #self.stats.set_alpha(0)

        self.bg.bind("<MouseWheel>", on_mousewheel)
        self.bg.bind("<Leave>", on_leave)
        self.root.bind("<Motion>", lambda e: self.wake())

        #self.bg.bind("<Enter>", lambda _: self.stats.set_alpha(1))

        self.root.after(100,  self.root.set_alpha, 0.95)
        self.root.after(100, self.bg.set_alpha, 0.5)
        self.root.after(100, self.fg.set_alpha, 0.95)

        #self.root.after(100, self.stats.set_alpha, 0.95)

        if False: # blur
            GlobalBlur(int(self.fg.frame(),16))
            self.root.after(400, self.fg.geometry, "+0+105")
            self.root.after(500, self.fg.geometry, "+0+105")
            self.root.after(600, self.fg.geometry, "+0+105")

        self.render_mode = renderer.Bedwars

        self.root.after(500, event.post, "player_list_update", ["MinuteBrain", "decliner", "Eldenax", "preadolescence"])
        self.root.after(600, event.post, "player_list_update", ["xMqt", "T_H_O_R", "ChristmasRudolph"])
        self.root.after(700, event.post, "player_list_update", ["MerryQuackwy", "_Me", "XMASCHER"])
        self.root.after(800, event.post, "player_list_update", ["GreenEggsAndJan", "XMASWOLF", "quin_in_the_snow","MinuteBrainN"])

        self.loop.create_task(log_reader(self))
        self.loop.create_task(await_global_task())
        self.loop.create_task(self.render_worker())
        self.loop.create_task(self.follow_worker())
        self.loop.create_task(self.foreground_app_monitor())

        event.subscribe("player_list_update", lambda e: self.wake())
        event.subscribe("chat", lambda e: self.wake())
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
            if 0<x<20: x = 0
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

        size_frame = tk.Frame(root, bg=bg_color, relief="flat", cursor="sizing", width=3)
        size_frame.pack(fill=tk.Y, side=tk.RIGHT)

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
        self.bg_canvas.create_image(0, 0, image=puro, anchor="nw")

        top.update()
        uicore.set_clickthrough(int(top.frame(),16), True)
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
        top.set_alpha(0, force=True)

        self.floating_canvas = tk.Canvas(top, background=self.transparent, relief="flat", highlightthickness=0)
        self.floating_canvas.pack(fill=tk.BOTH, expand=True)
        self.floating_stats = self.floating_canvas.create_image(0, 0, image=None, anchor="nw")

        return top

    def mouse_click(self, event):
        return
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
        img = ImageGrab.grab((x1, y1, x2, y2), all_screens=True)
        self.bg.set_alpha(original_alpha)
        util.set_clipboard_image(img)
        print("Take screenshot")

    def mouse_hover(self,event):
        pass
        # corrected_y = self.fg.winfo_height() - event.y
        # row_number = (corrected_y+self.scroll_offset-5) // self.row_height
        # progress = event.x / self.bg.winfo_width()

        # if 0<=row_number<len(player_data):
        #     hovering_ign = list(player_order)[row_number]
        #     canvas = self.floating_canvas
        #     image_id = self.floating_stats
        #     global_image["floating-stats-raw"] = renderer.generate_card(self, player_data[hovering_ign])
        #     global_image["floating-stats"] = ImageTk.PhotoImage(image=global_image["floating-stats-raw"])
        #     canvas.itemconfigure(image_id, image = global_image["floating-stats"])

        #     print(row_number, "hovering on", hovering_ign, progress)
        # else:
        #     print(row_number, "hovering on", None, progress)

    def follow(self, child:tk.Toplevel ,parent:tk.Toplevel, side="S"):
        w, h, x, y = (parent.winfo_width(), parent.winfo_height(), parent.winfo_x(), parent.winfo_y())
        if side == "S":
            child.geometry(f"+{x}+{y+h}")
        elif side == "E":
            child.geometry(f"+{x+w}+{y}")

    def destroy(self):
        self.fg.set_alpha(0)
        self.bg.set_alpha(0)
        self.root.set_alpha(0)
        self.root.after(300, self.bg.close)
        self.root.after(300, self.fg.close)
        self.root.after(300, self.root.close)
        sys.exit(0)

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
            self.follow(self.stats, self.bg, "E")
            await asyncio.sleep(1)

    def render_notification(self,_=0):
        self.rendering = True
        if self.new_from_top:
            self.test_sort()

    rendered = {}
    current_header = ""

    pil_time_avg_buffer = []

    def render(self):
        canvas = self.canvas
        rendered = self.rendered
        win_width = self.fg.winfo_width()
        win_height = self.fg.winfo_height()
        updated = False
        for count, ign in enumerate(player_order):
            player = player_data[ign]
            data = player.data
            if ign not in rendered:
                data["canvas"] = canvas.create_image(0, 0)
                canvas.tag_lower(data["canvas"], self.canvas_header)
                rendered[ign] = dict(image_id=data["canvas"])
                if self.new_from_top:
                    rendered[ign]["current_y"] = -20
                    rendered[ign]["target_y"] = -20
                else:
                    rendered[ign]["current_y"] = win_height + self.row_height
                    rendered[ign]["target_y"] = win_height + self.row_height
            player_canvas =  rendered[ign]["image_id"]

            if player.pending_render:
                ref = time.perf_counter()
                updated = True
                img = Image.new("RGBA", (win_width, self.row_height+4), (1,5,3,50))
                self.render_mode.render(img, ign, player, font)

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

            rendered[ign]["target_y"] = win_height - (count*self.row_height + 5 + self.row_height - self.scroll_offset)

        all_done = True
        for ign in rendered:
            image_id = rendered[ign]["image_id"]
            target_y = rendered[ign]["target_y"]
            current_y = rendered[ign]["current_y"]

            out_of_frame = lambda y: y<-100 or y>win_height+100

            if out_of_frame(current_y) and out_of_frame(target_y):
                if current_y != target_y:
                    rendered[ign]["current_y"] = target_y
                    canvas.coords(image_id, 0, int(current_y))
                continue

            if -3<target_y - current_y<3:
                if current_y!=target_y:
                    rendered[ign]["current_y"] = target_y
                    canvas.coords(image_id, 0, int(target_y))
            else:
                rendered[ign]["current_y"] = (current_y*3 + target_y)/4
                canvas.coords(image_id, 0, int(current_y))
                self.rendering = True
                all_done = False

        if all_done and self.rendering:
            self.rendering = False

        self.render_header()

    def render_header(self):
        if self.current_header != self.render_mode:
            self.current_header = self.render_mode

            win_width = self.fg.winfo_width()
            img = Image.new("RGBA", (win_width, 24), (1,5,3,170))
            self.render_mode.header(img, font)
            global_image["header-raw"] = img
            global_image["header"] = ImageTk.PhotoImage(image=img)
            self.canvas.itemconfigure(self.canvas_header, image=global_image["header"], anchor="nw")

            for player in player_order:
                player_obj = player_data.get(player)
                player_obj.render_request()

            if self.new_from_top:
                self.test_sort()

    def render_cleanup(self, _):
        rendered = self.rendered
        for ign in list(rendered):
            if ign not in player_data:
                image_id = rendered[ign]["image_id"]
                rendered.pop(ign, None)
                self.canvas.delete(image_id)
                global_image.pop(f"stats-{ign}", None)
                global_image.pop(f"stats-{ign}-raw", None)

    def test_sort(self):
        temp = self.render_mode.sort(player_data)
        player_order.clear()
        player_order.extend(temp)

    async def foreground_app_monitor(self):
        await asyncio.sleep(1)
        def on_window_change(is_mc):
            if is_mc:
                self.root.attributes("-topmost", True)
                self.bg.attributes("-topmost", True)
                self.fg.attributes("-topmost", True)
                self.fg.lift(self.bg)
                uicore.set_clickthrough(int(self.bg.frame(),16), True)
            else:
                self.root.attributes("-topmost", False)
                self.bg.attributes("-topmost", False)
                self.fg.attributes("-topmost", False)
                win32gui.BringWindowToTop(hwnd)
                self.root.after(100, self.fg.lift, self.bg)
                uicore.set_clickthrough(int(self.bg.frame(),16), False)

        is_mc_pre = None
        while True:
            try:
                hwnd = win32gui.GetForegroundWindow()
                try:    class_name = win32gui.GetClassName(hwnd)
                except: class_name = None
                if class_name:
                    is_mc = class_name == "LWJGL" or class_name == "TkTopLevel"
                    if is_mc_pre != is_mc:
                        is_mc_pre = is_mc
                        on_window_change(is_mc)

                    if class_name == "LWJGL":
                        if win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE) & 0x80000000:
                            global _fullscreen
                            await asyncio.sleep(0.5)
                            keyboard.press(87)
                            keyboard.release(87)
                            await asyncio.sleep(1)
                            uicore.set_borderless(uicore.get_minecraft_hwnd(), True)
                            _fullscreen = True

                    if not is_mc:
                        self.wake()

            except: pass
            await asyncio.sleep(0.5)
    def hide(self):
        self.bg.set_alpha(0)
        self.fg.set_alpha(0)
        self.root.set_alpha(0.1)

    def unhide(self):
        self.bg.set_alpha(config.get("opacity"))
        self.fg.set_alpha(1)
        self.root.set_alpha(0.9)

    def wake(self):
        if self.hide_schedule:
            self.root.after_cancel(self.hide_schedule)
            self.hide_schedule = None
        self.unhide()
        fade_timeout_ms = int(config.get("fade_timeout", 5)*1000)
        self.hide_schedule = self.root.after(fade_timeout_ms, self.hide)

    async def double_click_check(self):
        if hovering(self.bg) and self.bg.get_alpha() != 0:
            self.mouse_double_click(None)

def hovering(root):
    rx, ry = relative_pos(root)
    w, h = root.winfo_width(), root.winfo_height()
    return (0 <= rx < w) and (0 <= ry < h)

def relative_pos(root):
    mx, my = uicore.get_mouse_pos()
    x, y = root.winfo_x(), root.winfo_y()
    return mx-x, my-y

if __name__ == '__main__':
    runner = asyncio.get_event_loop().create_task
    overlay = Overlay()

    _fullscreen = False
    def keyboard_handle(event):
        global _fullscreen
        if uicore.is_minecraft():
            if event.event_type == "down":
                _fullscreen = not _fullscreen
                if _fullscreen:
                    uicore.set_borderless(uicore.get_minecraft_hwnd(), True)
                else:
                    uicore.set_borderless(uicore.get_minecraft_hwnd(), False)
                    uicore.free_cursor()
        else:
            if event.event_type == "down": keyboard.press(event.scan_code)
            elif event.event_type == "up": keyboard.release(event.scan_code)

    keyboard.hook_key(87, keyboard_handle, suppress=True)
    mouse.on_double_click(lambda: global_task.append(runner(overlay.double_click_check())))

    try:
        overlay.start()
    finally:
        if _fullscreen:
            uicore.set_borderless(uicore.get_minecraft_hwnd(), False)
            uicore.free_cursor()
