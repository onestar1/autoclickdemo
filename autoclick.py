import threading
import time
import tkinter as tk
import random
import pyautogui
from pynput import keyboard
import win32api
import win32con

pyautogui.FAILSAFE = False  # 禁用 pyautogui 的 fail-safe 功能

class AutoClicker:
    def __init__(self):
        self.clicking = False
        self.click_count = 0
        self.listener = None
        self.stop_event = False
        self.root = tk.Tk()
        self.root.title("Auto Clicker")
        self.root.geometry("300x400")  # 设置窗口大小
        self.label = tk.Label(self.root, text="点击次数: 0", font=("Arial", 14))
        self.label.pack(pady=10)
        self.instructions = tk.Label(self.root, text="按 F8 开始/暂停，按 F10 停止并清空计数", font=("Arial", 12))
        self.instructions.pack(pady=10)
        self.offset_label = tk.Label(self.root, text="上下浮动像素:", font=("Arial", 12))
        self.offset_label.pack(pady=5)
        self.offset_entry = tk.Entry(self.root)
        self.offset_entry.pack(pady=5)
        self.offset_entry.insert(0, "100")  # 默认浮动像素
        self.click_interval_label = tk.Label(self.root, text="点击间隔(秒):", font=("Arial", 12))
        self.click_interval_label.pack(pady=5)
        self.click_interval_entry = tk.Entry(self.root)
        self.click_interval_entry.pack(pady=5)
        self.click_interval_entry.insert(0, "0.5")  # 默认点击间隔
        self.move_interval_label = tk.Label(self.root, text="移动间隔(秒):", font=("Arial", 12))
        self.move_interval_label.pack(pady=5)
        self.move_interval_entry = tk.Entry(self.root)
        self.move_interval_entry.pack(pady=5)
        self.move_interval_entry.insert(0, "0.05")  # 默认移动间隔
        self.background_mode = tk.BooleanVar()
        self.background_check = tk.Checkbutton(self.root, text="后台模式", variable=self.background_mode)
        self.background_check.pack(pady=5)
        self.start_stop_key = keyboard.Key.f8
        self.exit_key = keyboard.Key.f10
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # 处理窗口关闭事件
        self.locked_position = None
        self.target_window_title = None

    def send_click(self, x, y):
        if self.background_mode.get() and self.target_window_title:
            windows = pyautogui.getWindowsWithTitle(self.target_window_title)
            if windows:
                hwnd = windows[0]._hWnd
                lParam = win32api.MAKELONG(x, y)
                win32api.PostMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lParam)
                time.sleep(self.move_interval)  # 添加移动间隔
                win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
                time.sleep(self.click_interval)  # 添加点击间隔
                win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)
            else:
                print(f"未找到标题为 '{self.target_window_title}' 的窗口")
        else:
            pyautogui.click(x, y)

    def start_clicking(self):
        if self.clicking and self.locked_position:
            self.click_count += 1
            self.label.config(text=f"点击次数: {self.click_count}")
            self.root.update()
            x, y = self.locked_position
            offset = int(self.offset_entry.get())
            self.click_interval = float(self.click_interval_entry.get())
            self.move_interval = float(self.move_interval_entry.get())
            # 向上移动并点击
            for i in range(offset):
                if not self.clicking:
                    return
                self.send_click(x, y - i)
                time.sleep(self.move_interval + random.uniform(-0.005, 0.005))
            # 向下移动回到原始位置并点击
            for i in range(offset):
                if not self.clicking:
                    return
                self.send_click(x, y - offset + i)
                time.sleep(self.move_interval + random.uniform(-0.005, 0.005))
            # 继续向下移动并点击
            for i in range(offset):
                if not self.clicking:
                    return
                self.send_click(x, y + i)
                time.sleep(self.move_interval + random.uniform(-0.005, 0.005))
            # 向上移动回到原始位置并点击
            for i in range(offset):
                if not self.clicking:
                    return
                self.send_click(x, y + offset - i)
                time.sleep(self.move_interval + random.uniform(-0.005, 0.005))
            time.sleep(self.click_interval + random.uniform(-0.05, 0.05))
        self.root.after(100, self.start_clicking)

    def on_key_press(self, key):
        if key == self.start_stop_key:
            self.clicking = not self.clicking
            if self.clicking:
                self.locked_position = pyautogui.position()
                if self.background_mode.get():
                    windows = pyautogui.getWindowsAt(self.locked_position[0], self.locked_position[1])
                    if windows:
                        self.target_window_title = windows[0].title
        elif key == self.exit_key:
            self.clicking = False
            self.click_count = 0
            self.label.config(text="点击次数: 0")
            self.on_closing()

    def on_closing(self):
        self.stop_event = True
        self.keyboard_listener.stop()
        self.root.destroy()

    def run(self):
        self.root.after(100, self.start_clicking)
        self.root.mainloop()

if __name__ == "__main__":
    auto_clicker = AutoClicker()
    auto_clicker.run()