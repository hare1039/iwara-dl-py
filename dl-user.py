import atexit
import sys
import argparse
import os
import getpass
import time
import signal
import selenium
import urllib.request
import urllib.parse
import progressbar
import traceback
from dl import iwara_dl, CannotDownload, make_driver, log
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

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)

def stop_waiting(signum, frame):
    raise Exception("End of time")

def cleanup(driver):
    driver.quit()

def parse_user(driver, url):
    driver.get(url)
    o = urllib.parse.urlparse(url)
    net_location = o.scheme + "://" + o.netloc

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
            urls.add(net_location + tag.get("href"))
    return urls

def iwara_dl_by_list(driver, dl_list):
    not_downloaded = []
    for dl in dl_list:
        log (dl)
        try:
            iwara_dl(driver, dl)
        except CannotDownload:
            not_downloaded.append(dl)
        except Exception as e:
            not_downloaded.append(dl)
            log (e)
            if not os.environ.get("IWARA_DL_QUIET"):
                traceback.print_exc()

    if (not_downloaded):
        print("These urls cannot download:")
        for ndl in not_downloaded:
            print(ndl)

def iwara_dl_by_username(driver, user_name):
    print ("[" + user_name + "]")
    url = "https://ecchi.iwara.tv/users/" + urllib.parse.quote(user_name) + "/videos"
    pageurls = parse_user(driver, url)
    os.environ["IWARA_DL_QUIET"] = "TRUE"
    iwara_dl_by_list(driver, pageurls)
