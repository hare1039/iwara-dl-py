import atexit
import sys
import argparse
import os
import getpass
import time
import signal
import selenium
import urllib.request
import progressbar
from dl import iwara_dl, CannotDownload
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as options

def stop_waiting(signum, frame):
    raise Exception("End of time")

def cleanup(driver):
    driver.quit()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-s", nargs="?", help="selenium driver host, default: http://127.0.0.1:4444/wd/hub")
    p.add_argument("url", nargs="*")
    args = p.parse_args()

    if not args.url:
        assert False, "[ERROR] Give me a link"
    if not args.s:
        args.s = "http://127.0.0.1:4444/wd/hub"

    opt = options();

    profile = selenium.webdriver.FirefoxProfile()
    profile.set_preference("intl.accept_languages", "zh_TW.UTF-8")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/rar;application/zip;application/octet-stream;application/x-zip-compressed;multipart/x-zip;application/x-rar-compressed;application/octet-stream;text/plain;text/html;text/css;text/javascript;image/gif;image/png;image/jpeg;image/bmp;image/webp;video/webm;video/ogg;audio/midi;audio/mpeg;audio/webm;audio/ogg;audio/wav;video/mp4;application/octet-stream;application/mp4;video/x-webm;video/x-sgi-movie;video/x-mpeg;video/mpg;video/quicktime;video/mpeg4;video/x-matroska")

    driver = selenium.webdriver.Remote (
        command_executor=args.s,
        desired_capabilities=DesiredCapabilities.FIREFOX,
        browser_profile=profile
    )
    driver.set_page_load_timeout(600)
    atexit.register(cleanup, driver)
    signal.signal(signal.SIGALRM, stop_waiting)

    not_downloaded = [];
    for url in args.url:
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 60)
            r18 = driver.find_element(By.CSS_SELECTOR, ".r18-continue")
            r18.click()
        except ElementNotInteractableException:
            print("No R18 button found... continue")

        fullpage = BeautifulSoup(driver.execute_script("return document.documentElement.outerHTML;"), "html.parser")
        a_tags = fullpage.find_all("a");

        urls = set()
        for tag in a_tags:
            if "/videos/" in tag.get("href"):
                urls.add("https://ecchi.iwara.tv" + tag.get("href"))

        for u in urls:
            print (u)
            try:
                iwara_dl(driver, u)
            except:
                not_downloaded.append(u)

    if (not_downloaded):
        print("These url cannot download:")
        for ndl in not_downloaded:
            print(ndl)
