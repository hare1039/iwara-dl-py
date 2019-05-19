import atexit
import sys
import argparse
import os
import os.path
import getpass
import time
import signal
import selenium
import urllib.request
import progressbar
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as options

class dl_bar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()

def stop_waiting(signum, frame):
    raise Exception("End of time")

def cleanup(driver):
    driver.quit()

def iwara_dl(driver, url):
    driver.get(url)

    try:
        wait = WebDriverWait(driver, 60)
        r18 = driver.find_element(By.CSS_SELECTOR, ".r18-continue")
        r18.click()
    except ElementNotInteractableException: pass

    fullpage = BeautifulSoup(driver.execute_script("return document.documentElement.outerHTML;"), "html.parser")
    for h1 in fullpage.find_all("h1"):
        if "Private video" == h1.string:
            print(url + " looks like private video")
            return

    button = wait.until(EC.element_to_be_clickable((By.ID, "download-button")))
    button.click();

    wait = WebDriverWait(driver, 60)
    dl_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Source")))

    fullpage = BeautifulSoup(driver.execute_script("return document.documentElement.outerHTML;"), "html.parser")
    title = fullpage.find("h1", class_="title").string;
    urlid = driver.current_url.split("/")[-1];
    filename = title + "-" + urlid + ".mp4";

    soup = BeautifulSoup(dl_link.get_attribute("outerHTML"), "html.parser")
    dl_link = "https:" + soup.find("a").get("href");
    filename = filename.replace("/", "-").replace(":", "-")
    if os.path.isfile(filename):
        print (filename, "exist. skip")
        return
    else:
        print ("Downloading:", filename)
    urllib.request.urlretrieve(dl_link, filename, dl_bar())

def iwara_dl_safe(driver, url):
    try:
        iwara_dl(driver, url)
    except selenium.common.exceptions.TimeoutException:
        print("download " + url + " timeout. Maybe this video is private.")

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

    for url in args.url:
        iwara_dl_safe(driver, url)
