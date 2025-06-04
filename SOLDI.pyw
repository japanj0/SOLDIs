import ctypes
import threading
import time
import os
import uuid
from tkinter import *
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException
import psutil
import pygetwindow as gw
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import sys

window = Tk()



def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


class App:
    def __init__(self, allowed_sites, password):
        self.allowed_sites = allowed_sites
        self.password = password
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.html_path = os.path.join(self.script_dir, "links.html")
        self.euphoria()
        self.win.protocol("WM_DELETE_WINDOW", self.on_closing)

    def euphoria(self):
        self.mutex = None
        self.driv = None
        self.win = None
        self.crowning = True
        self.scroatch = True
        self.scratch = 1
        self.really()

    def really(self):
        if self.is_browser_already_running():
            return

        self.mutex = self.create_mutex()
        if not self.mutex:
            return
        self.local_page = self.create_links_page()

        self.start_browser()

        self.win = Tk()
        self.win.protocol("WM_DELETE_WINDOW", self.on_closing)

        threading.Thread(target=self.check_tabs_loop, daemon=True).start()
        threading.Thread(target=self.check_window_state_loop, daemon=True).start()
        threading.Thread(target=self.terminate_taskmgr, daemon=True).start()

        self.win.mainloop()

    def create_mutex(self):
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\EdgeBrowserLock")
        if not mutex:
            return None
        return mutex

    def on_closing(self):
        pass

    def release_mutex(self):
        if self.mutex :
            ctypes.windll.kernel32.CloseHandle(self.mutex)
            self.mutex = None

    def is_browser_already_running(self):
        mutex = ctypes.windll.kernel32.OpenMutexW(0x00100000, False, "Global\\EdgeBrowserLock")
        if mutex:
            ctypes.windll.kernel32.CloseHandle(mutex)
            return True
        return False

    def create_links_page(self):
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write("""
<html><head><title>Каталог сайтов</title>
<script>
    window.open = function() {
        alert("Открытие новых окон запрещено.");
        return null;
    };
</script>
</head>
<body style='font-size:24px;'>
<h1>Разрешённые сайты</h1><ul>
""")
            for site in self.allowed_sites:
                f.write(f'<li><a href="https://{site}" target="_self">{site}</a></li>')
            f.write("</ul></body></html>")
        print("файл создан")
        return "file:///" + self.html_path.replace("\\", "/")

    def start_browser(self):
        if self.driv is not None:
            try:
                self.driv.quit()
            except Exception as e:
                pass

            self.driv = None

        options = Options()
        self.user_data_dir = f"C:\\Temp\\EdgePythonProfile_{uuid.uuid4()}"
        os.makedirs(self.user_data_dir, exist_ok=True)
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--no-sandbox")
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-features=msImplicitSignIn")
        options.add_argument("--disable-sync")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--app-name=cara")

        try:
            self.driv = webdriver.Edge(options=options)
            WebDriverWait(self.driv, 3).until(EC.number_of_windows_to_be(1))
            self.driv.get(self.local_page)
            self.driv.implicitly_wait(1)
            self.driv.maximize_window()
            self.driv.execute_script("document.title = 'edgegi';")

            self.scratch = 2
        except Exception as e:
            print(e, 2)
            self.driv = None

    def is_browser_alive(self):
        if self.driv is None:
            return False
        try:
            _ = self.driv.window_handles
            return True
        except WebDriverException:
            return False

    def show_fullscreen_alert(self):
        def close_program():
            if entry.get() == self.password:

                try:
                    if os.path.exists(self.html_path):
                        os.remove(self.html_path)


                except Exception:
                    pass
                self.win.destroy()
                sys.exit()


        def enforce_restrictions():
            while True:

                try:
                    for proc in psutil.process_iter(['pid', 'name']):
                        pname = proc.info['name'].lower()
                        if pname in ["firefox.exe", "chrome.exe", "opera.exe", "roblox.exe",
                                     "minecraft.exe", "taskmgr.exe", "yandex.exe", "tlauncher.exe",
                                     "browser.exe", "rulauncher.exe", "java.exe"]:
                            try:
                                proc.terminate()
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass
                except Exception:
                    pass

                self.kill_other_edge()

                try:
                    for proc in psutil.process_iter(['pid', 'name']):
                        if proc.info['name'].lower() == 'taskmgr.exe':
                            proc.kill()
                except Exception:
                    pass

                try:
                    if self.is_browser_alive():
                        browser_window = gw.getWindowsWithTitle("edgegi")
                        if browser_window:
                            browser_window = browser_window[0]
                            if browser_window.isMinimized:
                                browser_window.restore()
                            if not browser_window.isMaximized:
                                browser_window.maximize()
                except Exception:
                    pass

                time.sleep(1)

        alert = Tk()
        alert.attributes('-fullscreen', True)
        alert.configure(bg='black')

        label = Label(alert, text="Браузер был закрыт!\nВведите пароль, чтобы выйти.",
                      font=("Arial", 30), fg="white", bg="black")
        label.pack(pady=100)

        entry = Entry(alert, font=("Arial", 30), show="*")
        entry.pack()

        button = Button(alert, text="ОК", font=("Arial", 24), command=close_program)
        button.pack(pady=20)

        threading.Thread(target=enforce_restrictions, daemon=True).start()
        alert.mainloop()

    def check_tabs_loop(self):
        while True:
            try:
                if not self.is_browser_alive():
                    print(self.is_browser_alive())
                    self.show_fullscreen_alert()
                    continue
                self.abracadabra()
                self.driv.switch_to.window(self.driv.window_handles[0])
                self.current_url()
                self.check_window_state_loop()
                self.kill_other_edge()
                self.terminate_taskmgr()
            except Exception:
                pass
            if self.crowning:
                time.sleep(0.45)

    def abracadabra(self):
        if self.is_browser_alive() and len(self.driv.window_handles) > 1:
            for handle in self.driv.window_handles[1:]:
                try:
                    self.driv.switch_to.window(handle)
                    print(self.driv.window_handles[1:])
                    self.driv.execute_script("window.close();")
                    self.driv.implicitly_wait(0.05)
                except Exception:
                    pass

    def current_url(self):
        try:

            if not self.is_browser_alive():
                return
            current_url = self.driv.current_url
            if current_url.startswith("file:///") and "links.html" in current_url:
                return
            if not any(site in current_url for site in self.allowed_sites):
                local_page = self.create_links_page()
                print(local_page, "создан")
                self.driv.get(local_page)
                print("открыт")
        except WebDriverException as e:
            print(e, 1)
            self.driv = None

    def kill_other_edge(self):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if "msedge.exe" in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any("--user-data-dir=C:\\Temp\\EdgePythonProfile" in arg for arg in cmdline):
                        pass
                    else:
                        proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    def check_window_state_loop(self):
        try:
            for proc in psutil.process_iter():
                try:
                    if proc.name().lower() in ["firefox.exe", "chrome.exe", "opera.exe", "roblox.exe",
                                               "minecraft.exe", "taskmgr.exe", "yandex.exe", "tlauncher.exe",
                                               "browser.exe", "rulauncher.exe", "java.exe"]:
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            self.kill_other_edge()

            if self.is_browser_alive():
                browser_window = gw.getWindowsWithTitle("edgegi")
                if browser_window:
                    browser_window = browser_window[0]
                    if browser_window.isMinimized:
                        browser_window.restore()
                    if not browser_window.isMaximized:
                        browser_window.maximize()
        except Exception:
            pass

    def terminate_taskmgr(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == 'taskmgr.exe':
                    proc.kill()
        except Exception:
            pass


def request_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()


def main():
    request_admin()


    allowed_sites = []
    password = ""

    labba = Label(window, text="введите допустимые ссылки для посещения", font=("arial", 18))
    labba.pack()
    labba.place(x=1440 // 3 + 25, y=100)
    entrys = Entry(window, font=("arial", 26))
    entrys.pack()
    entrys.place(x=1440 // 3 + 70, y=260)

    def is_trusted_domain(url):
        trusted_tlds = {'com', 'org', 'net', 'gov', 'edu', 'io', 'co', 'ai', 'biz', 'ru', 'su', 'us', 'uk', 'de'}
        parts = url.strip().split('.')
        if len(parts) < 2 or not parts[-2]:
            return False
        tld = parts[-1].lower()
        return tld in trusted_tlds

    def add_site():
        if not entrys.get()=="" and is_trusted_domain(entrys.get()):
            allowed_sites.append(entrys.get())
            entrys.delete(0, END)
        else:
            ctypes.windll.user32.MessageBoxW(
                0,
                "введенная вами строка не похожа сайт",
                "Упс",
                0x0000 | 0x0010 | 0x1000
            )


    def second_act():
        if allowed_sites==[]:
            ctypes.windll.user32.MessageBoxW(
                0,
                "вы не ввели ссылки для посещения",
                "Упс",
                0x0000 | 0x0010 | 0x1000
            )
        else:
            btn_confim.destroy()
            btn_over.config(text="установить пароль", command=add_password, font=("arial", 20))
            labba.config(text="придумайте надёжный пароль\nдля отключения программы")
            labba.place(x=1440 // 3 + 90, y=100)

    def add_password():
        nonlocal password
        password = entrys.get()
        if password=="":
            ctypes.windll.user32.MessageBoxW(
                0,
                "вы не ввели пароль",
                "Упс",
                0x0000 | 0x0010 | 0x1000
            )
        else:
            window.destroy()
            App(allowed_sites, password)

    btn_confim = Button(window, text="ввести ссылку", font=("arial", 18), command=add_site)
    btn_confim.pack()
    btn_confim.place(x=1440 // 2 - 100, y=500)
    btn_over = Button(window, text="окончить ввод ссылок", font=("arial", 16), command=second_act)
    btn_over.place(x=1440 // 2 - 100, y=550)
    window.attributes('-fullscreen', True)
    window.mainloop()


main()
