import sys
import os
import time
import RAMWORKER
from tkinter import *
from tkinter import font as tkfont
from PIL import Image, ImageTk
from process_blocker import ProcessBlocker
import tempfile
import atexit
import ctypes
import subprocess
import UnitedBrowsersModul
import shutil
import psutil
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
    shutil.rmtree(temp_dir, ignore_errors=True)


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
                       text="НАЗАД",
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
    show_loading_screen("Подготовка Microsoft Edge")

    def edge_thread():
        time.sleep(2)
        try:
            os.startfile("msedge")
            subprocess.Popen(
                "taskkill /f /im msedge.exe",
                creationflags=subprocess.CREATE_NO_WINDOW,
                shell=True
            )
            win.after(0, lambda: [win.destroy(), UnitedBrowsersModul.main("edge")])
        except FileNotFoundError:
            win.after(0, lambda: show_error(f"Edge не установлен на вашем ПК"))
        except Exception:
            win.after(0, lambda: show_error(f"Произошла неизвестная ошибка"))

    threading.Thread(target=edge_thread, daemon=True).start()


def Firefox():
    show_loading_screen("Подготовка Firefox")

    def firefox_thread():
        time.sleep(2)
        try:
            os.startfile("firefox")
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "firefox.exe":
                        proc.kill()
            win.after(0, lambda: [win.destroy(), UnitedBrowsersModul.main("firefox")])
        except FileNotFoundError :
            win.after(0, lambda: show_error(f"Firefox не установлен на вашем ПК"))
        except Exception:
            win.after(0, lambda: show_error(f"Произошла неизвестная ошибка"))

    threading.Thread(target=firefox_thread, daemon=True).start()


def Chrome():
    show_loading_screen("Подготовка Google Chrome")

    def chrome_thread():
        time.sleep(2)
        try:
                os.startfile("chrome")
                subprocess.Popen(
                    "taskkill /f /im chrome.exe",
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    shell=True
                )
                win.after(0, lambda: [win.destroy(), UnitedBrowsersModul.main("chrome")])
        except FileNotFoundError:
                win.after(0, lambda: show_error(f"Chrome не установлен на вашем ПК"))
        except Exception:
                win.after(0, lambda: show_error(f"Произошла неизвестная ошибка"))
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
    def only_numbers(new_text):
        if not new_text:
            return True
        if (len(new_text) == 1 and new_text == "0") or \
                (len(new_text) > 1 and new_text[0] == "0") :

            return False
        return new_text.isdigit()
    def write_some():
        if time_entry.get()!="":
            RAMWORKER.write_sldid_file("config", time_entry.get())
            time_entry.delete(0, 'end')
            confirm_button.destroy()
            time_entry.destroy()
            info_lab.config(text="")
            buttons_frame.pack(fill=BOTH, expand=True, pady=50)
            button_firefox.grid(row=0, column=0, padx=30, pady=20, sticky="nsew")
            button_edge.grid(row=0, column=1, padx=30, pady=20, sticky="nsew")
            button_chrome.grid(row=0, column=2, padx=30, pady=20, sticky="nsew")


    clear_window()

    main_frame = Frame(win, bg=BG_COLOR)
    main_frame.pack(fill=BOTH, expand=True, padx=50, pady=50)

    title_label = Label(main_frame,
                        text="Выберите браузер для работы",
                        font=title_font,
                        bg=BG_COLOR,
                        fg=TEXT_COLOR)
    title_label.pack(pady=(0, 30))

    buttons_frame = Frame(main_frame, bg=BG_COLOR)
    buttons_frame.pack(fill=BOTH, expand=True)

    button_firefox = create_browser_button(buttons_frame, "Firefox", fox_im, Firefox)
    button_edge = create_browser_button(buttons_frame, "Edge", ed_im, Edge)
    button_chrome = create_browser_button(buttons_frame, "Chrome", chrome_im, Chrome)

    button_firefox.grid(row=0, column=0, padx=30, pady=20, sticky="nsew")
    button_edge.grid(row=0, column=1, padx=30, pady=20, sticky="nsew")
    button_chrome.grid(row=0, column=2, padx=30, pady=20, sticky="nsew")

    buttons_frame.grid_columnconfigure(0, weight=1)
    buttons_frame.grid_columnconfigure(1, weight=1)
    buttons_frame.grid_columnconfigure(2, weight=1)
    buttons_frame.grid_rowconfigure(0, weight=1)

    time_frame = Frame(main_frame, bg=BG_COLOR)
    time_frame.pack(pady=(30, 0))
    if not RAMWORKER.read_sldid_file("config"):
        info_lab = Label(time_frame,
          text="Введите допустимое время\nиспользования в минутах (по желанию):",
          font=tkfont.Font(family=FONT_FAMILY, size=14, weight="bold"),
          bg=BG_COLOR,
          fg=TEXT_COLOR)
        info_lab.pack()

        validate_cmd = win.register(only_numbers)
        time_entry = Entry(time_frame,
                       font=("Arial", 20),
                       bd=2,
                       relief=FLAT,
                       bg="white",
                       fg="black",
                       insertbackground="#4b6cb7",
                       validate="key",
                       validatecommand=(validate_cmd, '%P'),
                       highlightbackground="black",
                       highlightthickness=2,
                       width=25)
        time_entry.pack(pady=10)

        confirm_button = Button(time_frame,
                            text="Подтвердить",
                            font=tkfont.Font(family=FONT_FAMILY, size=23),
                            bg="#DCDCDC",
                            fg="black",
                            activebackground="gray",
                            relief=FLAT,
                            padx=55,
                            bd=0,
                            pady=1,
                            command=write_some)
        confirm_button.pack(pady=(0, 0), expand=True)

    exit_button = Button(main_frame,
                         text="Закрыть приложение",
                         font=exit_font,
                         bg="#DCDCDC",
                         activebackground="gray",
                         fg=TEXT_COLOR,
                         activeforeground=TEXT_COLOR,
                         relief=FLAT,
                         command=win.destroy,
                         padx=30,
                         bd=0,

                         pady=5)
    exit_button.pack(pady=(5, 0))


win = Tk()
win.title("soldi")
win.iconbitmap(RAMWORKER.get_icon_path("icon.ico"))
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


def is_scheduled_launch():
    return "--scheduled" in sys.argv


if RAMWORKER.read_sldid_file("data"):
    win.destroy()
    ProcessBlocker(password=RAMWORKER.read_sldid_file("data"))
else:
    if is_scheduled_launch():
        sys.exit()
    else:
        RAMWORKER.write_sldid_file("config","")
        require_admin()
        create_main_interface()
        win.mainloop()