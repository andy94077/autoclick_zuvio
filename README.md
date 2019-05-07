# autoclick_zuvio
autoclick - a python script that answers multiple choices questions automatically on irs.zuvio.com.tw

## Dependencies
- For normal PCs/laptops:
  ```
  pip3 install selenium
  sudo apt-get install chrome
  ```
  You also need to download the [chrome driver](https://sites.google.com/a/chromium.org/chromedriver/). Make sure you add it into PATH.

- For servers:
  ```
  pip3 install selenium pyvirtualdisplay
  sudo apt-get install firefox Xvfb
  ```
  You also need to download the [firefox driver](https://github.com/mozilla/geckodriver/releases). Make sure you add it into PATH.

## Usage
```
Usage: python3 autoclick.py [url] [-n seconds]
Options:
  -n  SECONDS        refresh the website every SECONDS seconds (default: 3)
  --no-sign-in       the script will not try to sign in the course
```
The usage of `autoclick_server.py` is the same as `autoclick.py`.
