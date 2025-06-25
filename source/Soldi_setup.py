import sys
import os
import uuid
from tkinter import *
from tkinter import font as tkfont
from PIL import Image, ImageTk
import tempfile
import atexit
import ctypes
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FireOptions
from selenium.webdriver.edge.service import Service as Edgeservice
from selenium.webdriver.edge.options import Options as Edgeoptions
from selenium.webdriver.chrome.service import Service as Chromeservice
from selenium.webdriver.chrome.options import Options as Chromeoptions
import Edge_control
import Firefox_control
import Chrome_control
import shutil
import threading

BG_COLOR = "#f5f5f5"
BUTTON_COLOR = "#ffffff"
BUTTON_ACTIVE_COLOR = "#e0e0e0"
TEXT_COLOR = "#333333"
ACCENT_COLOR = "#4285f4"
FONT_FAMILY = "Segoe UI"
BUTTON_PADDING = 20


def is_browser_installed(browser_name):
    return shutil.which(browser_name) is not None


def require_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
            sys.exit()
    except Exception as e:
        print(f"Ошибка при запросе прав администратора: {e}")
        sys.exit()


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def extract_temp_image(resource_path):
    if not hasattr(sys, '_MEIPASS'):
        return resource_path

    temp_dir = os.path.join(tempfile.gettempdir(), "soldi_images")
    os.makedirs(temp_dir, exist_ok=True)

    filename = os.path.basename(resource_path)
    temp_path = os.path.join(temp_dir, filename)

    if os.path.exists(temp_path):
        return temp_path

    try:
        with open(resource_path, 'rb') as src, open(temp_path, 'wb') as dst:
            dst.write(src.read())
        return temp_path
    except Exception as e:
        print(f"Ошибка при извлечении изображения: {e}")
        return None


def cleanup_temp_files():
    temp_dir = os.path.join(tempfile.gettempdir(), "soldi_images")
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Ошибка при удалении временного файла {file_path}: {e}")


atexit.register(cleanup_temp_files)


def show_loading_screen(message="Идет загрузка..."):
    clear_window()

    loading_frame = Frame(win, bg=BG_COLOR)
    loading_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(loading_frame,
          text=message,
          font=title_font,
          bg=BG_COLOR,
          fg=TEXT_COLOR).pack()

    progress = Label(loading_frame,
                     text="Пожалуйста, подождите...",
                     font=button_font_large,
                     bg=BG_COLOR,
                     fg=TEXT_COLOR)
    progress.pack(pady=10)

    return progress


def show_error(message):
    clear_window()

    error_frame = Frame(win, bg=BG_COLOR)
    error_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

    Label(error_frame,
          text="ОШИБКА",
          font=("Arial", 32, "bold"),
          bg=BG_COLOR,
          fg="#ff3333").pack(pady=(0, 20))

    Label(error_frame,
          text=message,
          font=("Arial", 18),
          bg=BG_COLOR,
          fg=TEXT_COLOR,
          wraplength=600).pack(pady=30, padx=50)

    button_frame = Frame(error_frame, bg=BG_COLOR)
    button_frame.pack(pady=30)

    retry_btn = Button(button_frame,
                       text="ПОВТОРИТЬ",
                       font=("Arial", 16, "bold"),
                       bg=ACCENT_COLOR,
                       fg="white",
                       activebackground="#3366cc",
                       activeforeground="white",
                       relief=FLAT,
                       bd=0,
                       padx=40,
                       pady=15,
                       command=create_main_interface)
    retry_btn.pack(side=LEFT, padx=20)

    exit_btn = Button(button_frame,
                      text="ВЫХОД",
                      font=("Arial", 16, "bold"),
                      bg="#666666",
                      fg="white",
                      activebackground="#555555",
                      activeforeground="white",
                      relief=FLAT,
                      bd=0,
                      padx=40,
                      pady=15,
                      command=win.destroy)
    exit_btn.pack(side=LEFT, padx=20)

    retry_btn.bind("<Enter>", lambda e: retry_btn.config(bg="#3a7bd5"))
    retry_btn.bind("<Leave>", lambda e: retry_btn.config(bg=ACCENT_COLOR))
    exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg="#777777"))
    exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg="#666666"))


def clear_window():
    for widget in win.winfo_children():
        widget.destroy()
    win.update()


def Edge():
    progress = show_loading_screen("Подготовка Microsoft Edge")

    def edge_thread():
        try:
            progress.config(text="Инициализация драйвера...")
            win.update()

            options = Edgeoptions()
            service = Edgeservice(timeout=3)
            user_data_dir = f"C:\\Temp\\EdgePythonProfile_{uuid.uuid4()}"
            os.makedirs(user_data_dir, exist_ok=True)

            options.add_argument("--remote-debugging-port=9222")
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument("--start-maximized")
            options.add_argument("--no-first-run")
            options.add_argument("--no-remote")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-sync")
            options.add_argument('--headless')
            options.add_argument("--disable-cloud-import")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--app-name=cara")

            progress.config(text="Загрузка браузера...")
            win.update()

            browser_driver = webdriver.Edge(options=options, service=service)
            browser_driver.quit()

            win.after(0, lambda: [win.destroy(), Edge_control.main()])

        except Exception as e:
            win.after(0, lambda: show_error(f"Ошибка при запуске Edge"))

    threading.Thread(target=edge_thread, daemon=True).start()


def Firefox():
    progress = show_loading_screen("Подготовка Firefox")

    def firefox_thread():
        try:
            progress.config(text="Инициализация драйвера...")
            win.update()

            options = FireOptions()
            service = FirefoxService(timeout=3)
            options.add_argument('--headless')
            user_data_dir = f"C:\\Temp\\FirefoxPythonProfile_{uuid.uuid4()}"
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')

            progress.config(text="Загрузка браузера...")
            win.update()

            browser_driver = webdriver.Firefox(options=options, service=service)
            browser_driver.quit()

            win.after(0, lambda: [win.destroy(), Firefox_control.main()])

        except Exception as e:
            win.after(0, lambda: show_error(f"Ошибка при запуске Firefox"))

    threading.Thread(target=firefox_thread, daemon=True).start()


def Chrome():
    progress = show_loading_screen("Подготовка Google Chrome")

    def chrome_thread():
        try:
            progress.config(text="Инициализация драйвера...")
            win.update()

            options = Chromeoptions()
            service = Chromeservice(timeout=3)
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            user_data_dir = f"C:\\Temp\\ChromePythonProfile_{uuid.uuid4()}"
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument('--no-sandbox')

            progress.config(text="Загрузка браузера...")
            win.update()

            browser_driver = webdriver.Chrome(options=options, service=service)
            browser_driver.quit()

            win.after(0, lambda: [win.destroy(), Chrome_control.main()])

        except Exception as e:
            win.after(0, lambda: show_error(f"Ошибка при запуске Chrome"))

    threading.Thread(target=chrome_thread, daemon=True).start()


def create_browser_button(parent, text, image, command):
    btn_frame = Frame(parent, bg=BG_COLOR, padx=20, pady=20)

    btn = Button(btn_frame,
                 text=text,
                 image=image,
                 compound=TOP,
                 font=button_font_large,
                 bg=BUTTON_COLOR,
                 activebackground=BUTTON_ACTIVE_COLOR,
                 fg=TEXT_COLOR,
                 activeforeground=TEXT_COLOR,
                 relief=FLAT,
                 bd=0,
                 padx=40,
                 pady=20,
                 command=command)
    btn.pack(fill=BOTH, expand=True)

    btn.bind("<Enter>", lambda e: btn.config(bg=BUTTON_ACTIVE_COLOR))
    btn.bind("<Leave>", lambda e: btn.config(bg=BUTTON_COLOR))

    return btn_frame


def create_main_interface():
    clear_window()

    main_frame = Frame(win, bg=BG_COLOR)
    main_frame.pack(fill=BOTH, expand=True, padx=50, pady=50)

    title_label = Label(main_frame,
                        text="Выберите браузер для работы",
                        font=title_font,
                        bg=BG_COLOR,
                        fg=TEXT_COLOR)
    title_label.pack(pady=(0, 50))

    buttons_frame = Frame(main_frame, bg=BG_COLOR)
    buttons_frame.pack(fill=BOTH, expand=True)

    button_firefox = create_browser_button(buttons_frame, "Firefox browser", fox_im, Firefox)
    button_edge = create_browser_button(buttons_frame, "Microsoft Edge", ed_im, Edge)
    button_chrome = create_browser_button(buttons_frame, "Google Chrome", chrome_im, Chrome)

    button_firefox.grid(row=0, column=0, padx=30, pady=20, sticky="nsew")
    button_edge.grid(row=0, column=1, padx=30, pady=20, sticky="nsew")
    button_chrome.grid(row=0, column=2, padx=30, pady=20, sticky="nsew")

    buttons_frame.grid_columnconfigure(0, weight=1)
    buttons_frame.grid_columnconfigure(1, weight=1)
    buttons_frame.grid_columnconfigure(2, weight=1)
    buttons_frame.grid_rowconfigure(0, weight=1)

    exit_button = Button(main_frame,
                         text="Закрыть приложение",
                         font=exit_font,
                         bg=BUTTON_COLOR,
                         activebackground=BUTTON_ACTIVE_COLOR,
                         fg=TEXT_COLOR,
                         activeforeground=TEXT_COLOR,
                         relief=FLAT,
                         command=win.destroy,
                         padx=30,
                         pady=15)
    exit_button.pack(pady=(50, 0))


require_admin()

win = Tk()
win.title("Выбор браузера")
win.configure(background=BG_COLOR)
win.attributes('-fullscreen', True)

try:
    title_font = tkfont.Font(family=FONT_FAMILY, size=36, weight="bold")
    button_font_large = tkfont.Font(family=FONT_FAMILY, size=24, weight="bold")
    exit_font = tkfont.Font(family=FONT_FAMILY, size=18)
except:
    title_font = tkfont.Font(size=36, weight="bold")
    button_font_large = tkfont.Font(size=24, weight="bold")
    exit_font = tkfont.Font(size=18)

try:
    edge_path = get_resource_path("logoedge.png")
    fox_path = get_resource_path("fox_im.png")
    chrome_path = get_resource_path("chromelogo.png")

    edge_temp = extract_temp_image(edge_path)
    fox_temp = extract_temp_image(fox_path)
    chrome_temp = extract_temp_image(chrome_path)

    img_size = (128, 128)
    ed_im = ImageTk.PhotoImage(Image.open(edge_temp).resize(img_size)) if edge_temp else None
    fox_im = ImageTk.PhotoImage(Image.open(fox_temp).resize(img_size)) if fox_temp else None
    chrome_im = ImageTk.PhotoImage(Image.open(chrome_temp).resize(img_size)) if chrome_temp else None
except Exception as e:
    print(f"Ошибка при загрузке изображений: {e}")
    img_size = (128, 128)
    ed_im = ImageTk.PhotoImage(Image.new('RGB', img_size, BG_COLOR))
    fox_im = ImageTk.PhotoImage(Image.new('RGB', img_size, BG_COLOR))
    chrome_im = ImageTk.PhotoImage(Image.new('RGB', img_size, BG_COLOR))

create_main_interface()
win.mainloop()