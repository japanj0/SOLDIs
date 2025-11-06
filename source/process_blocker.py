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
import win32gui
import win32con


class ProcessBlocker:
    def __init__(self, password, is_notrestarted):
        self.password = password
        self.is_notrestarted = is_notrestarted
        self.running = True
        self.blocked_apps = [
            "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "roblox.exe", "minecraft.exe",
            "yandex.exe", "tlauncher.exe", "browser.exe", "rulauncher.exe", "java.exe", "javaw.exe",
            "iexplore.exe", "taskmgr.exe", "powershell.exe", "regedit.exe", "mmc.exe", "control.exe",
            "discord.exe", "steam.exe", "epicgameslauncher.exe", "battle.net.exe", "telegram.exe",
            "viber.exe", "cmd.exe", "notepad.exe", "wordpad.exe", "WinStore.App.exe",
            "ida.exe", "ida64.exe", "x64dbg.exe", "x32dbg.exe", "ollydbg.exe", "windbg.exe",
            "windbgx.exe", "ghidra.exe", "radare2.exe", "cheatengine.exe", "immunitydebugger.exe",
            "procexp.exe", "procexp64.exe", "processhacker.exe", "processhacker2.exe", "procmon.exe",
            "procmon64.exe", "vmmap.exe", "rammap.exe", "handle.exe", "listdlls.exe",
            "pwsh.exe", "wsl.exe", "bash.exe", "ubuntu.exe", "debian.exe", "kali.exe", "ssh.exe",
            "putty.exe", "kitty.exe", "cygwin.exe", "mingw.exe", "msys2.exe",
            "wireshark.exe", "tshark.exe", "nmap.exe", "netcat.exe", "nc.exe", "tcpdump.exe",
            "msconfig.exe", "regedt32.exe", "autoruns.exe", "autorunsc.exe", "services.exe",
            "tasklist.exe", "systeminfo.exe", "whoami.exe", "net.exe", "ipconfig.exe",
            "hxd.exe", "hexedit.exe", "010editor.exe", "winhex.exe", "resourcehacker.exe",
            "dnspy.exe", "ilspy.exe", "peid.exe", "cffexplorer.exe", "dependencywalker.exe",
            "SystemSettings.exe"
        ]
        RAMWORKER.clearing_RAM(['geckodriver.exe', 'chromedriver.exe', 'msedgedriver.exe'])
        self.monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True).start()

        self.init_ui()

    def init_ui(self):
        self.root = tk.Tk()
        self.root.iconbitmap(RAMWORKER.get_icon_path("icon.ico"))
        self.root.title("soldi")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#1a1a1a')
        if RAMWORKER.read_sldid_file("SC"):
            self.key_kill = keyboard.add_hotkey(f'{RAMWORKER.read_sldid_file("SC")}', self.emergency_exit)

        self.create_lock_screen()
        self.root.mainloop()

    def emergency_exit(self):
        self.cleanup()
        RAMWORKER.delete_sldid_file("config")
        RAMWORKER.delete_sldid_file("status")
        RAMWORKER.delete_sldid_file("SC")
        RAMWORKER.MEI_del()
        RAMWORKER.delete_sldid_file("data")
        RAMWORKER.delete_sldid_file("browser")
        if RAMWORKER.read_sldid_file("SC"):
            keyboard.remove_hotkey(self.key_kill)
        self.running = False
        RAMWORKER.clearing_RAM()

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
        if RAMWORKER.read_sldid_file("status") == "True" and self.is_notrestarted:
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

    def terminate_explorer_safelly(self):
        try:
            def callback(hwnd, _):
                if win32gui.GetClassName(hwnd) == "CabinetWClass":
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

            win32gui.EnumWindows(callback, None)
        except Exception:
            pass

    def check_password(self):
        if hashlib.sha256(self.pass_entry.get().encode('utf-8')).hexdigest() == self.password:
            self.emergency_exit()

    def resume_browser(self):
        try:
            session = RAMWORKER.read_sldid_file("session")
            password = RAMWORKER.read_sldid_file("data")
            time_limit = RAMWORKER.read_sldid_file("config")
            browser = RAMWORKER.read_sldid_file("browser")

            if session and password:
                if RAMWORKER.read_sldid_file("SC"):
                    keyboard.remove_hotkey(self.key_kill)
                whitelist = session.strip().split()
                self.running = False
                self.root.after(0, lambda: [
                    self.root.destroy(),
                    UnitedBrowsersModul.App(whitelist, password, time_limit, browser, True)
                ])
        except Exception as e:
            print(f"Ошибка при восстановлении браузера: {e}")

    def monitor_processes(self):
        while self.running:
            self.terminate_explorer_safelly()
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['name'].lower() in [f.lower() for f in self.blocked_apps]:
                        try:
                            proc.terminate()
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            continue
                except:
                    continue

            time.sleep(1)
