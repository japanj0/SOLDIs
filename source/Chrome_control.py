import ctypes
import threading
import time
import os
import uuid
from tkinter import *
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import psutil
import pygetwindow as gw
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import sys
import RAMWORKER
from urllib.parse import urlparse
import idna
class App:
    def __init__(self, whitelisted_domains, unlock_password):
        self.whitelisted_domains = whitelisted_domains
        self.unlock_password = unlock_password
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.html_path = os.path.join(self.script_dir, "links.html")
        self.initialize_app_state()
        self.main_window.protocol("WM_DELETE_WINDOW", self.handle_window_close)

    def initialize_app_state(self):
        self.browser_lock_mutex = None
        self.browser_driver = None
        self.main_window = None
        self.is_running = True
        self.is_monitoring_active = True
        self.browser_state = 1
        self.setup_browser_environment()

    def setup_browser_environment(self):
        if self.check_browser_process_running():
            return

        self.browser_lock_mutex = self.create_browser_lock_mutex()
        if not self.browser_lock_mutex:
            return
        self.local_page_url = self.generate_allowed_sites_html()

        self.launch_controlled_browser()

        self.main_window = Tk()
        self.main_window.resizable(False, False)
        self.main_window.iconify()
        self.main_window.protocol("WM_DELETE_WINDOW", self.handle_window_close)

        threading.Thread(target=self.monitor_browser_tabs, daemon=True).start()
        threading.Thread(target=self.enforce_browser_window_state, daemon=True).start()
        threading.Thread(target=self.prevent_task_manager_usage, daemon=True).start()

        self.main_window.mainloop()

    def create_browser_lock_mutex(self):
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\ChromeBrowserLock")
        if not mutex:
            return None
        return mutex

    def handle_window_close(self):
        pass

    def release_browser_lock_mutex(self):
        if self.browser_lock_mutex:
            ctypes.windll.kernel32.CloseHandle(self.browser_lock_mutex)
            self.browser_lock_mutex = None

    def check_browser_process_running(self):
        mutex = ctypes.windll.kernel32.OpenMutexW(0x00100000, False, "Global\\ChromeBrowserLock")
        if mutex:
            ctypes.windll.kernel32.CloseHandle(mutex)
            return True
        return False

    def generate_allowed_sites_html(self):
        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write("""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Каталог разрешённых сайтов</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 40px 20px;
                color: #333;
            }

            .container {
                max-width: 1000px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                padding: 40px;
                position: relative;
                overflow: hidden;
            }

            .container::before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 10px;
                background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
            }

            h1 {
                text-align: center;
                margin-bottom: 30px;
                color: #2c3e50;
                font-size: 2.5rem;
                position: relative;
                padding-bottom: 15px;
            }

            h1::after {
                content: "";
                position: absolute;
                bottom: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 100px;
                height: 3px;
                background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                border-radius: 3px;
            }

            .description {
                text-align: center;
                margin-bottom: 40px;
                font-size: 1.1rem;
                color: #555;
                line-height: 1.6;
            }

            .site-list {
                list-style: none;
                margin-bottom: 40px;
            }

            .site-item {
                margin-bottom: 15px;
                transition: all 0.3s ease;
            }

            .site-item:hover {
                transform: translateX(10px);
            }

            .site-link {
                display: block;
                padding: 15px 20px;
                background: #f8f9fa;
                border-radius: 8px;
                text-decoration: none;
                color: #2c3e50;
                font-size: 1.2rem;
                transition: all 0.3s ease;
                border-left: 4px solid transparent;
            }

            .site-link:hover {
                background: #e9ecef;
                border-left: 4px solid #4b6cb7;
                color: #4b6cb7;
            }

            .footer {
                text-align: center;
                margin-top: 40px;
                color: #777;
                font-size: 0.9rem;
            }

            @media (max-width: 768px) {
                .container {
                    padding: 30px 20px;
                }

                h1 {
                    font-size: 2rem;
                }

                .site-link {
                    font-size: 1rem;
                    padding: 12px 15px;
                }
            }
        </style>
        <script>
            window.open = function() {
                alert("Открытие новых окон запрещено.");
                return null;
            };
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Разрешённые сайты</h1>
            <p class="description">Вы можете посещать только эти веб-сайты. Нажмите на ссылку, чтобы перейти.</p>

            <ul class="site-list">
    """)
            for site in self.whitelisted_domains:
                f.write(
                    f'            <li class="site-item"><a href="https://{site}" target="_self" class="site-link">{site}</a></li>\n')
            f.write("""        </ul>

            <div class="footer">
                <p>Для выхода из программы закройте браузер и введите пароль администратора</p>
            </div>
        </div>
    </body>
    </html>
    """)

        return "file:///" + self.html_path.replace("\\", "/")

    def launch_controlled_browser(self):
        if self.browser_driver is not None:
            try:
                self.browser_driver.quit()
            except Exception as e:
                pass
            self.browser_driver = None

        options = Options()
        self.user_data_dir = f"C:\\Temp\\ChromePythonProfile_{uuid.uuid4()}"
        os.makedirs(self.user_data_dir, exist_ok=True)

        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--start-maximized")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            self.browser_driver = webdriver.Chrome(options=options)
            self.browser_driver.implicitly_wait(3)
            WebDriverWait(self.browser_driver, 3).until(EC.number_of_windows_to_be(1))
            self.browser_driver.get(self.local_page_url)
            self.browser_driver.implicitly_wait(1)
            self.browser_driver.maximize_window()
            self.browser_driver.execute_script("document.title = 'chromegi';")

            self.browser_state = 2
        except Exception as e:
            self.browser_driver = None

    def verify_browser_process_active(self):
        if self.browser_driver is None:
            return False
        try:
            _ = self.browser_driver.window_handles
            return True
        except WebDriverException:
            return False

    def display_security_lock_screen(self):
        def close_program():
            self.is_running=False
            RAMWORKER.clearing_RAM()
            if password_entry.get() == self.unlock_password:
                lock_screen.destroy()
                try:
                    if os.path.exists(self.html_path):
                        os.remove(self.html_path)
                except Exception:
                    pass
                self.main_window.destroy()
                raise SystemExit(0)

        def enforce_security_restrictions():
            while True:
                try:
                    for proc in psutil.process_iter(['pid', 'name']):
                        pname = proc.info['name'].lower()
                        if pname in ["msedge.exe", "firefox.exe", "opera.exe", "roblox.exe",
                                     "minecraft.exe", "taskmgr.exe", "yandex.exe", "tlauncher.exe",
                                     "browser.exe", "rulauncher.exe", "java.exe"]:
                            try:
                                proc.terminate()
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                pass
                except Exception:
                    pass

                self.terminate_unauthorized_chrome_instances()

                try:
                    for proc in psutil.process_iter(['pid', 'name']):
                        if proc.info['name'].lower() == 'taskmgr.exe':
                            proc.kill()
                except Exception:
                    pass

                try:
                    if self.verify_browser_process_active():
                        browser_window = gw.getWindowsWithTitle("chromegi")
                        if browser_window:
                            browser_window = browser_window[0]
                            if browser_window.isMinimized:
                                browser_window.restore()
                            if not browser_window.isMaximized:
                                browser_window.maximize()
                except Exception as e:
                    pass

                time.sleep(1)

        lock_screen = Tk()
        lock_screen.attributes('-fullscreen', True)
        lock_screen.configure(bg='black')

        warning_label = Label(lock_screen, text="Браузер был закрыт!\nВведите пароль, чтобы выйти.",
                              font=("Arial", 30), fg="white", bg="black")
        warning_label.pack(pady=100)

        password_entry = Entry(lock_screen, font=("Arial", 30), show="*")
        password_entry.pack()

        submit_button = Button(lock_screen, text="ОК", font=("Arial", 24), command=close_program)
        submit_button.pack(pady=20)

        threading.Thread(target=enforce_security_restrictions, daemon=True).start()
        lock_screen.mainloop()

    def monitor_browser_tabs(self):
        while self.is_running:
            try:
                if not self.verify_browser_process_active():

                    self.display_security_lock_screen()
                    continue
                self.close_unauthorized_tabs()
                self.browser_driver.switch_to.window(self.browser_driver.window_handles[0])
                self.validate_current_url()
                self.enforce_browser_window_state()
                self.terminate_unauthorized_chrome_instances()
                self.prevent_task_manager_usage()
            except Exception as e:
                pass
            if self.is_running:
                time.sleep(0.43)

    def close_unauthorized_tabs(self):
        if self.verify_browser_process_active() and len(self.browser_driver.window_handles) > 1:
            for handle in self.browser_driver.window_handles[1:]:
                try:
                    self.browser_driver.switch_to.window(handle)
                    self.browser_driver.execute_script("window.close();")
                except Exception:
                    pass

    def validate_current_url(self):
        try:
            if not self.verify_browser_process_active():
                return

            current_url = self.browser_driver.current_url
            if current_url.startswith("file:///") and "links.html" in current_url:
                return

            parsed_url = urlparse(current_url)
            domain = parsed_url.netloc.split(':')[0]

            normalized_domain = domain[4:] if domain.startswith('www.') else domain

            domain_allowed = any(
                allowed_domain == normalized_domain or
                allowed_domain == domain or
                f"www.{allowed_domain}" == domain or
                idna.encode(allowed_domain).decode('ascii') == normalized_domain
                for allowed_domain in self.whitelisted_domains
            )

            if not domain_allowed:
                local_page = self.generate_allowed_sites_html()
                self.browser_driver.get(local_page)

        except WebDriverException as e:
            self.browser_driver = None

    def terminate_unauthorized_chrome_instances(self):
        try:
            controlled_pids = set()
            if self.browser_driver:
                chrome_pid = self.browser_driver.service.process.pid
                controlled_pids.add(chrome_pid)
                try:
                    parent = psutil.Process(chrome_pid)
                    for child in parent.children(recursive=True):
                        controlled_pids.add(child.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == 'chrome.exe' and proc.info['pid'] not in controlled_pids:
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            pass

    def enforce_browser_window_state(self):
        try:
            for proc in psutil.process_iter():
                try:
                    if proc.name().lower() in ["msedge.exe", "firefox.exe", "opera.exe", "roblox.exe",
                                               "minecraft.exe", "taskmgr.exe", "yandex.exe", "tlauncher.exe",
                                               "browser.exe", "rulauncher.exe", "java.exe"]:
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            self.terminate_unauthorized_chrome_instances()

            if self.verify_browser_process_active():
                browser_window = gw.getWindowsWithTitle("chromegi")
                if browser_window:
                    browser_window = browser_window[0]
                    if browser_window.isMinimized:
                        browser_window.restore()
                    if not browser_window.isMaximized:
                        browser_window.maximize()
        except Exception as e:
            pass

    def prevent_task_manager_usage(self):
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == 'taskmgr.exe':
                    proc.kill()
        except Exception:
            pass

def main():
    main_window = Tk()
    whitelisted_domains = []
    unlock_password = ""

    domain_label = Label(main_window, text="Введите допустимые ссылки для посещения", font=("arial", 18))
    domain_label.pack()
    domain_label.place(x=1440 // 3 + 25, y=100)
    domain_entry = Entry(main_window, font=("arial", 26))
    domain_entry.pack()
    domain_entry.place(x=1440 // 3 + 70, y=260)

    def validate_domain_trustworthiness(url):
        trusted_tlds = {'com', 'org', 'net', 'gov', 'edu', 'io', 'co', 'ai', 'biz', 'ru', 'su', 'us', 'uk', 'de', 'рф'}
        parts = url.strip().split('.')
        if len(parts) < 2 or not parts[-2]:
            return False
        tld = parts[-1].lower()
        return tld in trusted_tlds

    def add_allowed_website():
        domain = domain_entry.get().strip()
        if not domain:
            return

        if domain.startswith(('http://', 'https://')):
            domain = domain.split('://')[1]

        domain = domain.split('/')[0]

        normalized_domain = domain[4:] if domain.startswith('www.') else domain

        if validate_domain_trustworthiness(normalized_domain):
            if normalized_domain not in whitelisted_domains:
                whitelisted_domains.append(normalized_domain)
            domain_entry.delete(0, END)
        else:
            ctypes.windll.user32.MessageBoxW(
                0,
                "Введенная вами строка не похожа на сайт",
                "Ошибка",
                0x0000 | 0x0010 | 0x1000
            )

    def prompt_for_password_setup():
        if whitelisted_domains == []:
            ctypes.windll.user32.MessageBoxW(
                0,
                "Вы не ввели ссылки для посещения",
                "Ошибка",
                0x0000 | 0x0010 | 0x1000
            )
        else:
            confirm_button.destroy()
            next_button.config(text="Установить пароль", command=set_unlock_password, font=("arial", 20))
            domain_label.config(text="Придумайте надёжный пароль\nдля отключения программы")
            next_button.place(x=1440 // 2 - 110, y=320)
            domain_label.place(x=1440 // 3 + 90, y=100)

    def set_unlock_password():
        nonlocal unlock_password
        unlock_password = domain_entry.get()
        if unlock_password == "":
            ctypes.windll.user32.MessageBoxW(
                0,
                "Вы не ввели пароль",
                "Ошибка",
                0x0000 | 0x0010 | 0x1000
            )
        else:
            main_window.destroy()
            App(whitelisted_domains, unlock_password)

    confirm_button = Button(main_window, text="Ввести ссылку ", font=("arial", 23), command=add_allowed_website)
    confirm_button.pack()
    confirm_button.place(x=1440 // 2 - 100, y=485)
    next_button = Button(main_window, text="Окончить ввод ссылок ", font=("arial", 16),
                         command=prompt_for_password_setup)
    next_button.place(x=1440 // 2 - 100, y=550)
    exit_button = Button(main_window, text="закрыть приложение", font=("arial", 17), command=lambda: sys.exit())
    exit_button.place(x=1440 // 2 - 100, y=650)
    main_window.attributes('-fullscreen', True)
    main_window.mainloop()

