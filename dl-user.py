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
from dl import iwara_dl, CannotDownload, make_driver
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

def parse_user(driver, url):
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
    return urls
