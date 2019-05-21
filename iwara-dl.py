import argparse
from dl import iwara_dl, CannotDownload, make_driver
import importlib
dluser = importlib.import_module("dl-user")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-s", nargs="?", help="selenium driver host, default: http://127.0.0.1:4444/wd/hub")
    p.add_argument("url", nargs="*")
    args = p.parse_args()

    if not args.url:
        assert False, "[ERROR] Give me a link"
    if not args.s:
        args.s = "http://127.0.0.1:4444/wd/hub"

    driver = make_driver(args)
    dl_list = set()

    for url in args.url:
        if "/users/" in url:
            print(url, "looks like userpage")
            pageurls = dluser.parse_user(driver, url)
            for page in pageurls:
                dl_list.add(page)
        else:
             dl_list.add(url)

    not_downloaded = []
    for dl in dl_list:
        print (dl)
        try:
            iwara_dl(driver, dl)
        except:
            not_downloaded.append(dl)

    if (not_downloaded):
        print("These url cannot download:")
        for ndl in not_downloaded:
            print(ndl)
