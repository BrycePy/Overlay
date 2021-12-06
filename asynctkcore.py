import tkinter as tk
from tkinter import ttk
import asyncio
import traceback

class AlphaAnimation:
    def fade_animation_init(self):
        self.target_alpha = 0
        self.current_alpha = 0
        self.attributes("-alpha", 0)

    def get_alpha(self):
        return self.target_alpha

    def set_alpha(self, alpha, force=False):
        if force:
            self.target_alpha = self.current_alpha = alpha
            self.attributes("-alpha", round(self.current_alpha, 4))
        else:
            self.target_alpha = round(alpha, 4)

    def fade_animation(self):
        if self.current_alpha != self.target_alpha:
            if abs(self.current_alpha - self.target_alpha) > 0.01:
                if self.current_alpha > self.target_alpha:
                    self.current_alpha -= max(0.005, (self.current_alpha - self.target_alpha) / 5)
                else:
                    self.current_alpha += max(0.005, (self.target_alpha - self.current_alpha) / 5)
            else:
                self.current_alpha = self.target_alpha
                # print("done",self.target_alpha)
            self.attributes("-alpha", round(self.current_alpha, 4))

    def reset_alpha(self):
        self.current_alpha = 0
        self.attributes("-alpha", 0)

class AsyncTk(tk.Tk, AlphaAnimation):
    def __init__(self, loop, interval=1 / 61):
        super().__init__()
        self.loop = loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = []
        self.tasks.append(self.loop.create_task(self.updater(interval)))
        self.fade_animation_init()
        self.callback_queue = list()

    async def updater(self, interval):
        while True:
            self.update()
            self.fade_animation()
 
            if self.callback_queue:
                for callback in self.callback_queue:
                    self.tasks.append(self.loop.create_task(AsyncTk.patch_callback(callback)))
                self.callback_queue = list()
            
            await asyncio.sleep(interval)
            
    @staticmethod
    async def patch_callback(callback):
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback()
            else:
                callback()
        except Exception:
            traceback.print_exc()

    def append_callback(self, callback):
        self.callback_queue.append(callback)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.destroy()


class AsyncToplevel(tk.Toplevel, AlphaAnimation):
    def __init__(self, root, interval=1 / 61):
        super().__init__(root)
        self.loop = root.loop
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = []
        self.tasks.append(self.loop.create_task(self.updater(interval)))
        self.fade_animation_init()

    async def updater(self, interval):
        #self.update()
        while True:
            self.fade_animation()
            await asyncio.sleep(interval)

    def close(self):
        for task in self.tasks:
            task.cancel()
        self.destroy()
        
class OnHover:
    def __init__(self, widget, field, value):
        self.widget = widget
        self.field = field
        self.target_value = value
        self.restore_value = self.widget.cget(self.field)
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        self.widget.config(**{self.field: self.target_value})

    def leave(self, event=None):
        self.widget.config(**{self.field: self.restore_value})

    def destroy(self):
        self.widget.unbind("<Enter>")
        self.widget.unbind("<Leave>")
        self.widget.unbind("<ButtonPress>")

class Dropdown:
    dd_value = None
    dd_options = None
    dd = None
    def create(self, root, options, command=None):
        self.dd_options = options
        self.dd_value = tk.StringVar(root)
        self.dd_value.set(options[0]) # default value
        if command: self.dd = tk.OptionMenu(root, self.dd_value, *options, command=lambda x,c=self.dd_options: command(c,x))
        else:       self.dd = tk.OptionMenu(root, self.dd_value, *options)
        self.dd.config(highlightthickness = 0)
    def get(self):
        self.dd_value.get()
    def set(self,value):
        self.dd_value.set(value)