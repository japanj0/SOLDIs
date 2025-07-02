import os
import requests
import zipfile
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FireOptions
from selenium.webdriver.edge.service import Service as Edgeservice
from selenium.webdriver.edge.options import Options as Edgeoptions
from selenium.webdriver.chrome.service import Service as Chromeservice
from selenium.webdriver.chrome.options import Options as Chromeoptions


def get_latest_geckodriver_url():
    try:
        response = requests.get("https://api.github.com/repos/mozilla/geckodriver/releases/latest")
        response.raise_for_status()
        assets = response.json()["assets"]
        for asset in assets:
            if "win64.zip" in asset["name"]:
                return asset["browser_download_url"]
        raise Exception("Не найден win64.zip в релизе")
    except Exception as e:
        raise Exception(f"Ошибка при проверке версии: {e}")


def setup_geckodriver():

    temp_dir = os.path.join(os.environ["TEMP"], "geckodriver")
    os.makedirs(temp_dir, exist_ok=True)
    driver_path = os.path.join(temp_dir, "geckodriver.exe")

    if os.path.exists(driver_path):
        return driver_path

    try:
        download_url = get_latest_geckodriver_url()
        zip_path = os.path.join(temp_dir, "geckodriver.zip")
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extract("geckodriver.exe", temp_dir)

        os.remove(zip_path)
        return driver_path

    except Exception as e:
        raise Exception(f"Ошибка загрузки: {e}")

if __name__ == "__main__":
    try:
        path = setup_geckodriver()
        print(f"Geckodriver готов: {path}")

        service = FirefoxService(executable_path=path)
        driver = webdriver.Firefox(service=service)
        driver.get("https://google.com")
        print("Успех! Firefox запущен.")
        driver.quit()
    except Exception as e:
        print(f"Критическая ошибка: {e}")