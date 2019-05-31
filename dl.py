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
try: import youtube_dl
except ImportError: print("[Warning] youtube_dl not installed."); pass
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as options

class CannotDownload(BaseException): pass

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

class wait_for_page_load(object):
    def __init__(self, browser, timeout=60):
        self.browser = browser
        self.timeout = timeout
    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name("html")
    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name("html")
        return new_page.id != self.old_page.id

    def wait_for(self, condition_function):
        start_time = time.time()
        while time.time() < start_time + self.timeout:
            if condition_function():
                return True
            else:
                time.sleep(0.1)
        raise Exception ("Timeout waiting for {}".format(condition_function.__name__))
    def __exit__(self, *_):
        self.wait_for(self.page_has_loaded)

tried_iwara_login = False
def iwara_login(driver):
    global tried_iwara_login
    if tried_iwara_login:
        print ("Didn't I just login before?")
        raise CannotDownload;

    tried_iwara_login = True

    username = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "edit-name"))
    )
    username.send_keys(os.environ["IWARA_USER"])
    password = driver.find_element(By.ID, "edit-pass")
    password.send_keys(os.environ["IWARA_PASS"])

    with wait_for_page_load(driver, timeout=60):
        try:
            driver.find_element(By.ID, "edit-submit").click()
        except ElementClickInterceptedException:
            driver.find_element(By.CSS_SELECTOR, ".r18-continue").click()
            driver.find_element(By.ID, "edit-submit").click()


dl_keyword_list = ["download", "drive.google.com", "mega", "mediafire.com", "dl", "1080p", "60fps"]
def iwara_dl(driver, url):
    try:
        driver.get(url)

        try:
            r18 = driver.find_element(By.CSS_SELECTOR, ".r18-continue")
            r18.click()
        except ElementNotInteractableException: pass

        fullpage = BeautifulSoup(driver.execute_script("return document.documentElement.outerHTML;"), "html.parser")
        for h1 in fullpage.find_all("h1"):
            if "Private video" == h1.string:
                print(url + " looks like private video")

                login_url = ""
                for a in fullpage.find_all("a"):
                    if "/user/login" in a.get("href"):
                        login_url = a.get("href")

                print ("log in to", login_url)
                with wait_for_page_load(driver, timeout=60):
                    driver.find_element(By.XPATH, "//a[@href='" + login_url + "']").click()
                iwara_login(driver)
                iwara_dl(driver, url)
                return

        all_links = fullpage.find_all("a")
        for a in all_links:
            if "Show all" == a.string:
                driver.find_element(By.LINK_TEXT, "Show all").click()
                fullpage = BeautifulSoup(driver.execute_script("return document.documentElement.outerHTML;"), "html.parser")
        paragraphs = fullpage.find("div", class_="node-info").find_all("p")

        buf = str()
        have_special_kw = False
        have_link = False
        for paragraph in paragraphs:
            v = str(paragraph).lower()
            for kw in dl_keyword_list:
                if kw in v:
                    have_special_kw = True
                    break
            if paragraph.find("a") != None:
                have_link = True
            buf += paragraph.prettify()

        if have_special_kw and have_link:
            print ("------------ Found better version in description ------------")
            print (buf)
            print ("-------------------------------------------------------------")

        title = fullpage.find("h1", class_="title").string[:75];
        urlid = driver.current_url.split("/")[-1];
        filename = title + "-" + urlid + ".mp4";
        filename = filename.replace("/", "-").replace(":", "-").replace("|", "-").replace("?", "-")
        filename = filename.replace("\"", "").replace(";", "-").replace("\t", "").replace("*", "-")
        filename = filename.replace("<", "-").replace(">", "-")
        if os.path.isfile(filename):
            print (filename, "exist. skip")
            return

        is_youtube_link = False
        for ytdl in fullpage.find_all("iframe"):
            if "youtu" in ytdl.get("src"):
                ydl_opts = {}
                with youtube_dl.YoutubeDL(ydl_opts) as youtube:
                    try:
                        youtube.download([ytdl.get("src")])
                    except youtube_dl.utils.DownloadError:
                        raise CannotDownload(ytdl.get("src"))
                is_youtube_link = True

        if (is_youtube_link):
            return

        wait = WebDriverWait(driver, 60)
        button = wait.until(EC.element_to_be_clickable((By.ID, "download-button")))
        button.click();

        wait = WebDriverWait(driver, 60)
        dl_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Source")))

        fullpage = BeautifulSoup(driver.execute_script("return document.documentElement.outerHTML;"), "html.parser")

        soup = BeautifulSoup(dl_link.get_attribute("outerHTML"), "html.parser")
        dl_link = "https:" + soup.find("a").get("href");
        print ("Downloading:", filename)
        urllib.request.urlretrieve(dl_link, filename, dl_bar())
    except selenium.common.exceptions.TimeoutException:
        print("download " + url + " timeout.")
        raise CannotDownload(url)

def make_driver(args):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    profile = selenium.webdriver.FirefoxProfile(dir_path + "/seluser")
    profile.set_preference("intl.accept_languages", "zh_TW.UTF-8")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/rar;application/zip;application/octet-stream;application/x-zip-compressed;multipart/x-zip;application/x-rar-compressed;application/octet-stream;text/plain;text/html;text/css;text/javascript;image/gif;image/png;image/jpeg;image/bmp;image/webp;video/webm;video/ogg;audio/midi;audio/mpeg;audio/webm;audio/ogg;audio/wav;video/mp4;application/octet-stream;application/mp4;video/x-webm;video/x-sgi-movie;video/x-mpeg;video/mpg;video/quicktime;video/mpeg4;video/x-matroska")

    driver = selenium.webdriver.Remote (
        command_executor     = args.s,
        desired_capabilities = DesiredCapabilities.FIREFOX,
        browser_profile      = profile
    )
    driver.set_page_load_timeout(600)
    atexit.register(cleanup, driver)
    signal.signal(signal.SIGALRM, stop_waiting)
    return driver
