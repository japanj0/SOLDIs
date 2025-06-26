import psutil
import os
def clearing_RAM():
    drivers = ['geckodriver.exe', 'chromedriver.exe', 'msedgedriver.exe','msedge.exe']
    for proc in psutil.process_iter(['name']):
        print(proc)
        if proc.info['name'] in drivers:
            try:
                proc.terminate()
                print(proc.info['name'])
            except Exception as e:
                print(e)
def read_txt_file(filename: str) -> str:
    """Reads content from a text file in AppData/Local/MyApp"""
    try:
        file_path = create_txt_file(filename)  # Ensures file exists
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Read error: {e}")
        return ""
