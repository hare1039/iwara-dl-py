import os
import argparse
from dl import iwara_dl, CannotDownload, make_driver
import importlib
import traceback

dluser = importlib.import_module("dl-user")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-s", nargs="?", help="selenium driver host, default: http://127.0.0.1:4444/wd/hub")
    p.add_argument("-u", nargs="?", help="username")
    p.add_argument("-p", nargs="?", help="password")
    p.add_argument("-t", action="store_true", help="treat input url as usernames")
    p.add_argument("-c", action="store_true", help="cd to each username folder. Used only when specify -t")
    p.add_argument("url", nargs="*")
    args = p.parse_args()

    if not args.url:
        assert False, "[ERROR] Give me a link"
    if not args.s:
        args.s = "http://127.0.0.1:4444/wd/hub"

    if args.u:
        os.environ["IWARA_USER"] = args.u

    if args.p:
        os.environ["IWARA_PASS"] = args.p

    driver = make_driver(args)

    if args.t:
        folders = set()
        for name in args.url:
            if args.c:
                try:
                    with dluser.cd(name):
                        dluser.iwara_dl_by_username(driver, name)
                except FileNotFoundError:
                    folders.add(name)
            else:
                dluser.iwara_dl_by_username(driver, name)
        if folders:
            print("These user cannot download")
            for folder in folders:
                print(folder)
        exit(0)

    dl_list = set()
    for url in args.url:
        if "/videos/" in url:
            dl_list.add(url)
        else:
            print(url, "doesn't look like a video page. Try parsing it")
            pageurls = dluser.parse_user(driver, url)
            for page in pageurls:
                dl_list.add(page)

    dluser.iwara_dl_by_list(driver, dl_list)
