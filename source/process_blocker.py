import tkinter as tk
import psutil
import time
import threading
import RAMWORKER
import hashlib
import UnitedBrowsersModul
import os
import keyboard
import shutil
import sys
import ctypes


class ProcessBlocker:
    def __init__(self, password):
        self.password = password
        self.running = True
        self.blocked_apps = [
            "msedge.exe", "chrome.exe", "firefox.exe",
            "opera.exe", "yandex.exe", "iexplore.exe",
            "taskmgr.exe", "powershell.exe",
            "regedit.exe", "mmc.exe", "control.exe",
            "roblox.exe", "minecraft.exe", "tlauncher.exe",
            "rulauncher.exe", "javaw.exe", "java.exe",
            "discord.exe", "steam.exe", "epicgameslauncher.exe",
            "battle.net.exe", "telegram.exe", "viber.exe",
            "browser.exe", "cmd.exe", "powershell.exe"
        ]

        self.monitor_thread = threading.Thread(target=self.monitor_processes)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        self.init_ui()

    def init_ui(self):
        self.root = tk.Tk()
        self.root.iconbitmap(RAMWORKER.get_icon_path("icon.ico"))
        self.root.title("soldi")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#1a1a1a')

        self.key_kill = keyboard.add_hotkey('ctrl+shift+alt+p+q+n', self.emergency_exit)

        self.create_lock_screen()
        self.root.mainloop()

    def emergency_exit(self):
        keyboard.remove_hotkey(self.key_kill)
        RAMWORKER.MEI_del()
        RAMWORKER.delete_sldid_file("data")
        RAMWORKER.delete_sldid_file("config")
        self.cleanup()
        RAMWORKER.clearing_RAM()
        self.root.destroy()
        sys.exit()

    def cleanup(self):
        temp_dir = r"C:\Temp"
        if os.path.exists(temp_dir):
            for item in os.listdir(temp_dir):
                if item.startswith(("EdgePythonProfile_", "ChromePythonProfile_", "FirefoxPythonProfile_")):
                    shutil.rmtree(os.path.join(temp_dir, item), ignore_errors=True)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(script_dir, "links.html")
        if os.path.exists(html_path):
            os.remove(html_path)

    def create_lock_screen(self):
        content_frame = tk.Frame(self.root, bg='#2d2d2d', bd=0, highlightthickness=0, padx=40, pady=40)
        content_frame.place(relx=0.5, rely=0.5, anchor='center')

        warning_label = tk.Label(content_frame,
                                 text="Доступ ограничен!\nВведите пароль для разблокировки.",
                                 font=("Arial", 24, 'bold'),
                                 fg="#ffffff",
                                 bg="#2d2d2d",
                                 justify='center')
        warning_label.pack(pady=(0, 30))

        self.pass_entry = tk.Entry(content_frame,
                                   font=("Arial", 20),
                                   show="*",
                                   bd=2,
                                   relief='flat',
                                   bg="#3d3d3d",
                                   fg="white",
                                   insertbackground="white",
                                   width=25)
        self.pass_entry.pack(ipady=10, pady=(0, 20))

        submit_button = tk.Button(content_frame,
                                  text="ПОДТВЕРДИТЬ",
                                  font=("Arial", 16, 'bold'),
                                  command=self.check_password,
                                  bg="#4b6cb7",
                                  fg="white",
                                  activebackground="#3a5a99",
                                  activeforeground="white",
                                  bd=0,
                                  relief='flat',
                                  padx=30,
                                  pady=10)
        submit_button.pack()
        resume_button = tk.Button(content_frame,
                                  text="ВОЗОБНОВИТЬ\nБРАУЗЕР",
                                  font=("Arial", 16, 'bold'),
                                  command=self.resume_browser,
                                  bg="#4b6cb7",
                                  fg="white",
                                  activebackground="#3a5a99",
                                  activeforeground="white",
                                  bd=0,
                                  relief='flat',
                                  padx=29,
                                  pady=10)
        resume_button.pack(pady=(10, 0))

        separator = tk.Frame(content_frame, height=2, bg="#4b6cb7", bd=0)
        separator.pack(fill='x', pady=20)

    def check_password(self):
        if hashlib.sha256(self.pass_entry.get().encode('utf-8')).hexdigest() == self.password:
            RAMWORKER.delete_sldid_file("config")
            RAMWORKER.MEI_del()
            RAMWORKER.delete_sldid_file("data")
            keyboard.remove_hotkey(self.key_kill)
            self.cleanup()
            self.running = False
            RAMWORKER.clearing_RAM()
            self.root.destroy()

    def resume_browser(self):

        try:
            RAMWORKER.MEI_del()
            session = RAMWORKER.read_sldid_file("session")
            password = RAMWORKER.read_sldid_file("data")
            time_limit = RAMWORKER.read_sldid_file("config")
            browser = RAMWORKER.read_sldid_file("browser")

            if session and password and not time_limit:
                keyboard.remove_hotkey(self.key_kill)
                whitelist = session.strip().split()
                self.running = False
                if self.monitor_thread.is_alive():
                    self.monitor_thread.join(timeout=1)
                self.root.after(0,lambda: [self.root.destroy(), UnitedBrowsersModul.App(whitelist, password, time_limit, browser, True)])
            else:
                ctypes.windll.user32.MessageBoxW(0, "Администратор компьютера запретил\nвосстанавливать браузер\nиз-за ограничения по времени", "Ошибка", 0x0000 | 0x0010 | 0x1000)

        except Exception as e:
            print(f"Ошибка при восстановлении браузера: {e}")

    def monitor_processes(self):
        while self.running:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in self.blocked_apps:
                        proc.kill()
                except:
                    pass
            time.sleep(1)