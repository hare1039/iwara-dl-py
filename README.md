# iwara-dl
This program downloads ecchi.iwara.tv videos

# Usage:
```
usage: iwara-dl.py [-h] [-s [S]] [-u [U]] [-p [P]] [url [url ...]]

positional arguments:
  url

optional arguments:
  -h, --help  show this help message and exit
  -s [S]      selenium driver host, default: http://127.0.0.1:4444/wd/hub
  -u [U]      username
  -p [P]      password
```

```
# Download. Video page and user page are supported
python3 iwara-dl.py -s http://192.168.1.120:4444/wd/hub https://ecchi.iwara.tv/videos/ooxxzz

# You can also use env to set your login cred
IWARA_USER="Jacky" IWARA_PASS="password" python3 iwara-dl.py https://ecchi.iwara.tv/users/ooox/videos
```
