# iwara-dl
This program downloads ecchi.iwara.tv videos

(It only downloads public videos)

# Usage:
```
user.py -h
usage: dl-user.py [-h] [-s [S]] [url [url ...]]

positional arguments:
  url

optional arguments:
  -h, --help  show this help message and exit
  -s [S]      selenium driver host, default: http://127.0.0.1:4444/wd/hub
```

```
# download userpage
python3 dl-user.py -s http://192.168.1.120:4444/wd/hub https://ecchi.iwara.tv/users/xyz/videos

# download video url
python3 dl.py -s http://192.168.1.120:4444/wd/hub https://ecchi.iwara.tv/videos/123456789qwed
```
