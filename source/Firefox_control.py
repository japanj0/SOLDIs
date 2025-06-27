import ctypes
import threading
import time
import os
import uuid
from tkinter import *
from urllib.parse import urlparse
import idna
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
import psutil
import pygetwindow as gw
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import RAMWORKER


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
        threading.Thread(target=self.enforce_security_restrictions, daemon=True).start()
        threading.Thread(target=self.prevent_task_manager_usage, daemon=True).start()

        self.main_window.mainloop()

    def create_browser_lock_mutex(self):
        mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\FirefoxBrowserLock")
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
        mutex = ctypes.windll.kernel32.OpenMutexW(0x00100000, False, "Global\\FirefoxBrowserLock")
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
        self.user_data_dir = f"C:\\Temp\\FirefoxPythonProfile_{uuid.uuid4()}"
        os.makedirs(self.user_data_dir, exist_ok=True)

        options.set_preference("remote-debugging-port", 9222)
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        options.add_argument("--start-maximized")
        options.add_argument("--no-remote")
        options.add_argument("--new-instance")
        options.add_argument("--ignore-certificate-errors")
        options.set_preference("app.update.auto", False)
        options.set_preference("app.update.enabled", False)

        try:
            self.browser_driver = webdriver.Firefox(options=options)
            self.browser_driver.implicitly_wait(3)
            WebDriverWait(self.browser_driver, 3).until(EC.number_of_windows_to_be(1))
            self.browser_driver.get(self.local_page_url)
            self.browser_driver.implicitly_wait(1)
            self.browser_driver.maximize_window()
            self.browser_driver.execute_script("document.title = 'firefoxgi';")

            self.browser_state = 2
        except Exception as e:
            print(e)
            self.browser_driver = None

    def verify_browser_process_active(self):
        if self.browser_driver is None:
            return False
        try:
            _ = self.browser_driver.window_handles
            return True
        except WebDriverException:
            return False

    def enforce_security_restrictions(self):

        while self.is_running:
            try:
                self.terminate_unauthorized_apps()
                self.terminate_unauthorized_firefox_instances()

                if self.verify_browser_process_active():
                    browser_window = gw.getWindowsWithTitle("firefoxgi")
                    if browser_window:
                        browser_window = browser_window[0]
                        if browser_window.isMinimized:
                            browser_window.restore()
                        if not browser_window.isMaximized:
                            browser_window.maximize()
            except Exception as e:
                print(f"Security restriction error: {e}")
            time.sleep(0.5)

    def terminate_unauthorized_apps(self):

        forbidden_apps = ["msedge.exe", "chrome.exe", "opera.exe", "roblox.exe",
                          "minecraft.exe", "yandex.exe", "tlauncher.exe",
                          "browser.exe", "rulauncher.exe", "java.exe"]

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() in forbidden_apps:
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    def display_security_lock_screen(self):
        def close_program():

            self.is_running = False
            RAMWORKER.clearing_RAM()
            RAMWORKER.write_txt_file("config.txt","1")
            if password_entry.get() == self.unlock_password:
                lock_screen.destroy()
                try:
                    if os.path.exists(self.html_path):
                        os.remove(self.html_path)
                except Exception:
                    pass
                self.main_window.destroy()
                raise SystemExit(0)

        lock_screen = Tk()
        lock_screen.protocol("WM_DELETE_WINDOW", self.handle_window_close)
        lock_screen.attributes('-fullscreen', True)
        lock_screen.configure(bg='#1a1a1a')

        content_frame = Frame(lock_screen, bg='#2d2d2d', bd=0, highlightthickness=0,
                              relief='flat', padx=40, pady=40)
        content_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        warning_label = Label(content_frame,
                              text="Браузер был закрыт!\nВведите пароль, чтобы выйти.",
                              font=("Arial", 24, 'bold'),
                              fg="#ffffff",
                              bg="#2d2d2d",
                              justify=CENTER)
        warning_label.pack(pady=(0, 30))

        password_entry = Entry(content_frame,
                               font=("Arial", 20),
                               show="*",
                               bd=2,
                               relief=FLAT,
                               bg="#3d3d3d",
                               fg="white",
                               insertbackground="white",
                               width=25)
        password_entry.pack(ipady=10, pady=(0, 20))

        submit_button = Button(content_frame,
                               text="ПОДТВЕРДИТЬ",
                               font=("Arial", 16, 'bold'),
                               command=close_program,
                               bg="#4b6cb7",
                               fg="white",
                               activebackground="#3a5a99",
                               activeforeground="white",
                               bd=0,
                               relief=FLAT,
                               padx=30,
                               pady=10)
        submit_button.pack()

        separator = Frame(content_frame, height=2, bg="#4b6cb7", bd=0)
        separator.pack(fill=X, pady=20)

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
            except Exception as e:
                print(f"Browser monitoring error: {e}")
            time.sleep(0.5)

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

    def terminate_unauthorized_firefox_instances(self):
        try:
            controlled_pids = set()
            if self.browser_driver:
                firefox_pid = self.browser_driver.service.process.pid
                controlled_pids.add(firefox_pid)
                try:
                    parent = psutil.Process(firefox_pid)
                    for child in parent.children(recursive=True):
                        controlled_pids.add(child.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == 'firefox.exe' and proc.info['pid'] not in controlled_pids:
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Error in terminate_unauthorized_firefox_instances: {e}")

    def prevent_task_manager_usage(self):

        while self.is_running:
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'].lower() == 'taskmgr.exe':
                        proc.kill()
            except Exception:
                pass
            time.sleep(0.5)


def main():
    main_window = Tk()
    whitelisted_domains = []
    unlock_password = ""

    main_window.configure(bg='#f0f2f5')

    container = Frame(main_window, bg='#ffffff', padx=40, pady=40, bd=0,
                      highlightthickness=0, relief='flat')
    container.place(relx=0.5, rely=0.5, anchor=CENTER)

    header_frame = Frame(container, bg='#ffffff', bd=0)
    header_frame.pack(pady=(0, 30))

    domain_label = Label(header_frame,
                         text="Введите допустимые ссылки для посещения",
                         font=("Arial", 18, 'bold'),
                         fg="#2c3e50",
                         bg="#ffffff")
    domain_label.pack()

    input_frame = Frame(container, bg='#ffffff', bd=0)
    input_frame.pack(pady=(0, 30))

    domain_entry = Entry(input_frame,
                         font=("Arial", 18),
                         bd=2,
                         relief=FLAT,
                         bg="#E0FFFF",
                         fg="#333333",
                         insertbackground="#4b6cb7",
                         width=40,
                         highlightthickness=2,
                         highlightbackground="black")
    domain_entry.pack(ipady=8, padx=10)

    buttons_frame = Frame(container, bg='#ffffff', bd=0)
    buttons_frame.pack()

    def validate_domain_trustworthiness(url):
        trusted_tlds = {'com', 'org', 'net', 'gov', 'edu', 'io', 'co', 'ai', 'biz', 'ru', 'su', 'us', 'uk', 'de', 'рф'}
        parts = url.strip().split('.')
        if len(parts) < 2 or not parts[-2]:
            return False
        tld = parts[-1].lower()
        return tld in trusted_tlds

    def add_allowed_website():
        def des_and_conf():
            bad_label.destroy()
            confirm_button.config(state="normal")

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
                success_label = Label(input_frame,
                                      text=f"Добавлен: {normalized_domain}",
                                      fg="#4CAF50",
                                      bg="#ffffff",
                                      font=("Arial", 12))
                success_label.pack()
                main_window.after(1000, success_label.destroy)
            else:
                domain_entry.delete(0, END)
                confirm_button.config(state="disabled")
                bad_label = Label(input_frame,
                                  text=f"ВНИМАНИЕ! Вы уже вводили данный сайт",
                                  fg="#F4A900",
                                  bg="#ffffff",
                                  font=("Arial", 12))
                bad_label.pack()
                main_window.after(2000, des_and_conf)
        else:
            domain_entry.delete(0, END)
            confirm_button.config(state="disabled")
            bad_label = Label(input_frame,
                                  text=f"ОШИБКА! ВВЕДЕННАЯ ВАМИ СТРОКА - НЕ САЙТ!",
                                  fg="red",
                                  bg="#ffffff",
                                  font=("Arial", 12))
            bad_label.pack()
            main_window.after(2000, des_and_conf)

    def prompt_for_password_setup():
        if not whitelisted_domains:
            ctypes.windll.user32.MessageBoxW(
                0,
                "Вы не ввели ссылки для посещения",
                "Ошибка",
                0x0000 | 0x0010 | 0x1000
            )
        else:
            confirm_button.destroy()
            next_button.config(text="УСТАНОВИТЬ ПАРОЛЬ",
                               command=set_unlock_password,
                               font=("Arial", 14, 'bold'),
                               bg="#4b6cb7",
                               fg="white",
                               activebackground="#3a5a99",
                               activeforeground="white")
            domain_label.config(text="Придумайте надёжный пароль\nдля отключения программы")
            next_button.pack(pady=(20, 10))
            domain_label.config(font=("Arial", 16, 'bold'))

    def set_unlock_password():
        nonlocal unlock_password
        unlock_password = domain_entry.get()
        if not unlock_password:
            ctypes.windll.user32.MessageBoxW(
                0,
                "Вы не ввели пароль",
                "Ошибка",
                0x0000 | 0x0010 | 0x1000
            )
        else:
            main_window.destroy()
            App(whitelisted_domains, unlock_password)

    confirm_button = Button(buttons_frame,
                            text="ДОБАВИТЬ ССЫЛКУ",
                            font=("Arial", 14, 'bold'),
                            command=add_allowed_website,
                            bg="#4CAF50",
                            fg="white",
                            activebackground="#3e8e41",
                            activeforeground="white",
                            bd=0,
                            relief=FLAT,
                            padx=20,
                            pady=10)
    confirm_button.pack(pady=(0, 15), fill=X)

    next_button = Button(buttons_frame,
                         text="ЗАВЕРШИТЬ ВВОД",
                         font=("Arial", 14, 'bold'),
                         command=prompt_for_password_setup,
                         bg="#FF9800",
                         fg="white",
                         activebackground="#e68a00",
                         activeforeground="white",
                         bd=0,
                         relief=FLAT,
                         padx=20,
                         pady=10)
    next_button.pack(pady=(0, 15), fill=X)

    exit_button = Button(buttons_frame,
                         text="ЗАКРЫТЬ ПРИЛОЖЕНИЕ",
                         font=("Arial", 14, 'bold'),
                         command=lambda: main_window.destroy(),
                         bg="#f44336",
                         fg="white",
                         activebackground="#d32f2f",
                         activeforeground="white",
                         bd=0,
                         relief=FLAT,
                         padx=20,
                         pady=10)
    exit_button.pack(fill=X)

    separator = Frame(container, height=2, bg="#e0e0e0", bd=0)
    separator.pack(fill=X, pady=20)

    footer_label = Label(container,
                         text="Контроль доступа в интернет",
                         font=("Arial", 10),
                         fg="#757575",
                         bg="#ffffff")
    footer_label.pack()

    main_window.attributes('-fullscreen', True)
    main_window.mainloop()


